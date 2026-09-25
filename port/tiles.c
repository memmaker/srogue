/* Which NetHack tile shows a map cell (RVIP step 4), for the classic Rogue
 * data structures of Super-Rogue (linked lists; stdscr holds the real map). The screen only has characters, so
 * look up the monster/object that is really there. */
#include <curses.h>
#include "../rogue.h"
#include "../rogue.ext"
#include "tilemap.h"

#define N(a) ((int)(sizeof a / sizeof *a))

static int hash_tile(const char *s, int first, int n)
{
    unsigned h = 5381;
    if (!s) return first;
    while (*s) h = h * 33 + (unsigned char)*s++;
    return first + h % n;
}

static int obj_tile(struct object *o)
{
    int w = o->o_which;
    if (w < 0) return -1;
    switch (o->o_type) {
    case WEAPON: return w < N(weap_tile) ? weap_tile[w] : -1;
    case ARMOR:  return w < N(armor_tile) ? armor_tile[w] : -1;
    case POTION: return w < MAXPOTIONS ? hash_tile(p_colors[w], POTION_TILES, POTION_NTILES) : -1;
    case SCROLL: return w < MAXSCROLLS ? hash_tile(s_names[w], SCROLL_TILES, SCROLL_NTILES) : -1;
    case RING:   return w < MAXRINGS ? hash_tile(r_stones[w], RING_TILES, RING_NTILES) : -1;
    case STICK:  return w < MAXSTICKS ? hash_tile(ws_stuff[w].ws_made, WAND_TILES, WAND_NTILES) : -1;
    }
    return -1;
}

/* Neighbours come from the real map (stdscr), so a monster or the player
   standing next to a wall does not change its shape. */
static int real(int y, int x)
{
    return (y < 1 || y >= LINES - WC_STATUS_ROWS || x < 0 || x >= COLS) ? ' '
        : stdscr->c[y * stdscr->maxx + x] & A_CHARTEXT;
}

#define HWALLISH(c) ((c) == '-' || (c) == DOOR || (c) == SECRETDOOR)
#define VWALLISH(c) ((c) == '|' || (c) == DOOR || (c) == SECRETDOOR)

static int terrain(int y, int x, int ch)
{
    int l, r;
    switch (ch) {
    case '-':
        l = real(y, x - 1); r = real(y, x + 1);
        if (HWALLISH(l) && HWALLISH(r)) return T_HWALL;
        if (VWALLISH(real(y + 1, x)))
            return HWALLISH(r) ? T_TL : T_TR;
        if (VWALLISH(real(y - 1, x)))
            return HWALLISH(r) ? T_BL : T_BR;
        return T_HWALL;
    case '|': return T_VWALL;
    case DOOR: return T_FLOOR;   /* Rogue doors are just gaps in the wall */
    }
    return ch < 128 ? terrain_tile[ch] : -1;
}

/* The floor under a monster or item: what the real map (stdscr) has. */
static int floor_under(int y, int x)
{
    int c = stdscr->c[y * stdscr->maxx + x] & A_CHARTEXT;
    if (c == PASSAGE) return T_CORR;
    if (c == DOOR) return T_FLOOR;
    if (c == STAIRS || strchr("\\>{$}~`\"^", c)) return terrain_tile[c];  /* srogue: one char per trap */
    return T_FLOOR;
}

int tile_for(int y, int x, int ch, int *under)
{
    struct linked_list *l;
    int t;

    *under = -1;
    if (!wc_mapwin || ch == ' ' || ch >= 128) return -1;
    if (ch == PLAYER) {
        if (y != hero.y || x != hero.x) return -1;
        *under = floor_under(y, x);
        return class_tile[0];
    }
    if (isalpha(ch)) {                  /* A-Z, a-z: 52 monsters (midx) */
        *under = floor_under(y, x);
        return mon_tile[midx(ch)];
    }
    if (generic_tile[ch] >= 0) {
        *under = floor_under(y, x);
        for (l = lvl_obj; l; l = next(l)) {
            struct object *o = OBJPTR(l);
            if (o->o_pos.y == y && o->o_pos.x == x && o->o_type == ch && (t = obj_tile(o)) >= 0)
                return t;
        }
        if (ch != GOLD || (stdscr->c[y * stdscr->maxx + x] & A_CHARTEXT) == GOLD) return generic_tile[ch];
        *under = -1;          /* '*' without gold: a bolt, draw as text */
        return -1;
    }
    return terrain(y, x, ch);
}

int wc_is_thing(int y, int x)
{
    struct linked_list *l;
    if (hero.y == y && hero.x == x) return 1;
    for (l = mlist; l; l = next(l))
        if ((THINGPTR(l))->t_pos.y == y && (THINGPTR(l))->t_pos.x == x) return 1;
    for (l = lvl_obj; l; l = next(l))
        if ((OBJPTR(l))->o_pos.y == y && (OBJPTR(l))->o_pos.x == x) return 1;
    return 0;
}

/* Item kinds: name and Angband colour (RVIP W0: colours come from the game) */
static const struct wc_kind K[] = {
    { POTION, "potion", "#40a0ff" }, { SCROLL, "scroll", "#ffffff" },
    { RING, "ring", "#ff4040" },     { STICK, "wand", "#40d040" },
    { FOOD, "food", "#d09050" },     { ARMOR, "armor", "#a07040" },
    { WEAPON, "weapon", "#b0b0b8" }, { GOLD, "gold", "#ffe040" },
#ifdef AMULET
    { AMULET, "amulet", "#ff9000" },
#endif
#ifdef MM
    { MM, "magic item", "#c0c0c0" },
#endif
#ifdef RELIC
    { RELIC, "relic", "#ff9000" },
#endif
#ifdef ARTIFACT
    { ARTIFACT, "artifact", "#ff9000" },
#endif
    { 0, "something", "" }
};
const struct wc_kind *wc_kind(int type)
{
    const struct wc_kind *k = K;
    while (k->type && k->type != type) k++;
    return k;
}

/* Inventory pane: the pack, lettered like inventory(), plus gold.
 * inv_name() writes the game's shared prbuf, so keep it intact. */
void wc_inv(WINDOW *p)
{
    char save[LINLEN];		/* srogue: prbuf is char[LINLEN] */
    struct linked_list *l;
    int y = 0, ch = 'a', n = 0;

    for (l = pack; l; l = next(l)) n++;
    memcpy(save, prbuf, sizeof save);
    for (l = pack; l && y < p->maxy - 1; l = next(l), y++, ch = npch(ch)) {
        mvwprintw(p, y, 0, "%c) %s", ch, inv_name(OBJPTR(l), FALSE));
        wclrtoeol(p);
        be_invfg(y, wc_kind((OBJPTR(l))->o_type)->css);
    }
    for (; y < p->maxy; y++) { be_invfg(y, ""); if (y < p->maxy - 1) { wmove(p, y, 0); wclrtoeol(p); } }
    mvwprintw(p, y, 0, "%d/%d items, %d gold", n, MAXPACK, purse);
    wclrtoeol(p);
    memcpy(prbuf, save, sizeof save);
}
