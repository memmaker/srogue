/*
    rvip.c  -  auto-explore ('x') and walking to the nearest known
    staircase, Enter command menu, inventory cursor. RVIP port.

    Only uses what the player can see (the cw window), one step per turn.
*/

#include <curses.h>
#include "rogue.h"
#include "rogue.ext"

/* command keys of games without C_* names (older Rogues) */
#ifndef C_QUAFF
#define C_QUAFF 'q'
#define C_READ 'r'
#define C_EAT 'e'
#define C_WIELD 'w'
#define C_WEAR 'W'
#define C_TAKEOFF 'T'
#define C_ZAP 'z'
#define C_DROP 'd'
#define C_DIP 'D'
#define C_USE CTRL('U')
#endif
#ifndef ISFRIENDLY
#define ISFRIENDLY 0
#endif
/* item classes some games don't have */
#ifndef MM
#define MM (-2)
#endif
#if !defined(RELIC) && defined(ARTIFACT)
#define RELIC ARTIFACT
#endif
#ifndef RELIC
#define RELIC (-4)
#endif
#ifndef IPLAYER
#define IPLAYER PLAYER
#endif
#ifndef LINELEN
#define LINELEN 160
#endif
#ifndef min
#define min(a, b) ((a) < (b) ? (a) : (b))
#define max(a, b) ((a) > (b) ? (a) : (b))
#endif
#ifndef FOREST
#define FOREST (-3)
#endif
#ifndef MAXPACK
#define MAXPACK 52
#endif
#ifndef CTRL
#define CTRL(c) ((c) & 037)
#endif
#ifndef ESC
#define ESC ESCAPE
#endif
#define EMAXL 128
#define EMAXC 256

extern struct h_list helpstr[];

int explore_mode = 0;           /* 0 off, 'x' explore, '<' / '>' stairs */
static char visited[EMAXL][EMAXC];      /* stood here */

void
explore_reset()
{
    explore_mode = 0;
    memset(visited, 0, sizeof visited);
}

static int
seen(y, x)
int y, x;
{
    if (y < 1 || y >= LINES - WC_STATUS_ROWS || x < 0 || x >= COLS) return ' ';
    return mvwinch(cw, y, x) & A_CHARTEXT;
}

static int
is_item(c)
int c;
{
    return c == GOLD || c == POTION || c == SCROLL || c == FOOD ||
           c == WEAPON || c == ARMOR || c == MM || c == RELIC ||
           c == RING || c == STICK;
}

/* Can the explorer step here? Known, not a wall, trap, pool or monster. */
static int
walkable(y, x)
int y, x;
{
    int c = seen(y, x);
    return c == FLOOR || c == PASSAGE || c == DOOR || c == STAIRS ||
           c == FOREST || c == PLAYER || c == IPLAYER || is_item(c) ||
           (y == hero.y && x == hero.x);
}

/* Diagonal moves follow diag_ok(): not when exactly one side is open. */
static int
diag_open(y, x, ny, nx)
int y, x, ny, nx;
{
    if (y == ny || x == nx) return TRUE;
    return walkable(ny, x) == walkable(y, nx);
}

static int
is_target(y, x)
int y, x;
{
    int dy, dx, c = seen(y, x);

    if (explore_mode == '<' || explore_mode == '>')
        return c == STAIRS;
    /* dark corridors and rooms only show what is next to you: a cell at
     * the edge of the unknown stays a target until you stood on it */
    if (visited[y][x]) return FALSE;
    if (is_item(c)) return TRUE;
    for (dy = -1; dy <= 1; dy++)
        for (dx = -1; dx <= 1; dx++)
            if (seen(y + dy, x + dx) == ' ' &&
                y + dy >= 1 && y + dy < LINES - WC_STATUS_ROWS &&
                x + dx >= 0 && x + dx < COLS)
                return TRUE;
    return FALSE;
}

/* A monster the player can see (not a friend) stops everything. */
int
monster_in_view()
{
    struct linked_list *item;
    struct thing *tp;

    for (item = mlist; item != NULL; item = next(item)) {
        tp = THINGPTR(item);
        if (on(*tp, ISFRIENDLY)) continue;
        if (seen(tp->t_pos.y, tp->t_pos.x) == tp->t_type) return TRUE;
    }
    return FALSE;
}

static char dirkey[3][3] = { { 'y', 'k', 'u' }, { 'h', '.', 'l' }, { 'b', 'j', 'n' } };

/*
 * explore_step:
 *      The next command for auto-explore / stair walking, or 0 when it
 *      stops (with a message saying why).
 */
int
explore_step()
{
    static short qy[EMAXL * EMAXC], qx[EMAXL * EMAXC];
    static signed char from[EMAXL][EMAXC];  /* first step dir index, -1 unseen */
    int head = 0, tail = 0, y, x, dy, dx, mode = explore_mode;

    if (!mode) return 0;
    if (mpos != 0) {                /* something happened: stop and look */
        explore_mode = 0;
        return 0;
    }
    if (wc_kbhit()) {               /* any key stops it */
        flushinp();
        explore_mode = 0;
        return 0;
    }
    if (monster_in_view()) {
        explore_mode = 0;
        msg(mode == 'x' ? "You see a monster; exploring stops."
                        : "You see a monster; you stop walking.");
        return 0;
    }
    if (LINES > EMAXL || COLS > EMAXC) { explore_mode = 0; return 0; }

    visited[hero.y][hero.x] = TRUE;

    if ((mode == '<' || mode == '>') &&
        (mvwinch(stdscr, hero.y, hero.x) & A_CHARTEXT) == STAIRS) {
        explore_mode = 0;
        return mode;                /* take them */
    }

    memset(from, -1, sizeof from);
    from[hero.y][hero.x] = 4;
    qy[tail] = hero.y; qx[tail++] = hero.x;
    while (head < tail) {
        y = qy[head]; x = qx[head++];
        if ((y != hero.y || x != hero.x) && is_target(y, x)) {
            int d = from[y][x];
            return dirkey[d / 3][d % 3];
        }
        for (dy = -1; dy <= 1; dy++)
            for (dx = -1; dx <= 1; dx++) {
                int ny = y + dy, nx = x + dx;
                if ((!dy && !dx) || ny < 1 || ny >= LINES - WC_STATUS_ROWS || nx < 0 || nx >= COLS)
                    continue;
                if (from[ny][nx] >= 0 || !walkable(ny, nx) || !diag_open(y, x, ny, nx))
                    continue;
                from[ny][nx] = (y == hero.y && x == hero.x) ? (dy + 1) * 3 + dx + 1
                                                            : from[y][x];
                qy[tail] = ny; qx[tail++] = nx;
            }
    }
    explore_mode = 0;
    if (mode == 'x')
        msg("Nothing left to explore. Search (s) for secret doors, or take the stairs (>).");
    else
        msg("You don't know where any stairs are yet.");
    return 0;
}

/*
 * explore_stairs:
 *      '<' or '>' pressed. TRUE if the player is where the command works
 *      as before (on stairs or another way through); otherwise start
 *      walking to the nearest known staircase and return FALSE.
 */
int
explore_stairs(key)
int key;
{
    int c = mvwinch(stdscr, hero.y, hero.x) & A_CHARTEXT;

    if (c == STAIRS)
        return TRUE;
    explore_mode = key;
    return FALSE;
}

/*
 * cmd_menu:
 *      Enter: a floating menu of every command (RVIP), the groups of the
 *      '*' help list, then the commands of a group.  Returns the key of
 *      the chosen command, or ESC.
 */

/* groups of the help list, each starting at the key in grp_start[] */
static char *cmd_groups[] = {
    "Help", "Move and run", "Explore and act", "Items", "Game"
};
static int grp_start[] = { '?', 'h', 'x', 'i', 'O' };
#define NGRP (sizeof grp_start / sizeof grp_start[0])

/* Arrow keys / numpad 8 2 move, Enter / 5 / Space / 6 choose, Esc / 4 / 0
 * / . back.  A key of an entry chooses it; + - * choose the highlighted
 * one.  Returns the index (menu_key says how) or -1. */
int menu_key;

int
menu(title, items, keys, n)
char *title, **items, *keys;
int n;
{
    int cur = 0, top = 0, rows = min(n, LINES - 2), w = strlen(title), i, c;

    for (i = 0; i < n; i++) w = max(w, (int)strlen(items[i]));
    for (;;) {
        if (cur < top) top = cur;
        if (cur >= top + rows) top = cur - rows + 1;
        werase(hw);
        mvwaddstr(hw, 0, 0, title);
        for (i = top; i < top + rows; i++) {
            wmove(hw, i - top + 1, 0);
            if (i == cur) wstandout(hw);
            wprintw(hw, "%-*s", w, items[i]);
            if (i == cur) wstandend(hw);
        }
        wmove(hw, cur - top + 1, 0);
        wrefresh(hw);
        menu_key = c = wgetch(hw);
        if (c == KEY_UP) cur = (cur + n - 1) % n;
        else if (c == KEY_DOWN) cur = (cur + 1) % n;
        else if (c == '\r' || c == '\n' || c == ' ' || c == KEY_B2 || c == KEY_RIGHT) {
            menu_key = '\r';
            return cur;
        }
        else {
            for (i = 0; keys && i < n; i++) if (keys[i] == c) return i;
            if (c == '+' || c == '-' || c == '*') return cur;
            if (c == ESC || c == KEY_LEFT || c == '0' || c == '.') return -1;
        }
    }
}

int
cmd_menu()
{
    struct h_list *h;
    char *items[80], keys[80], text[80][48];
    int g, n, i, grp;

    for (;;) {
        char *gi[NGRP], gk[NGRP], gt[NGRP][40];
        for (g = 0; g < NGRP; g++) {
            sprintf(gt[g], "%c) %s", 'a' + g, cmd_groups[g]);
            gi[g] = gt[g]; gk[g] = 'a' + g;
        }
        if ((g = menu("Commands", gi, gk, NGRP)) < 0) break;
        for (grp = -1, n = 0, h = helpstr; h->h_ch && h->h_desc && n < 80; h++) {
            if (grp + 1 < (int)NGRP && h->h_ch == grp_start[grp + 1]) grp++;
            if (grp != g || h->h_ch == '\r' || h->h_ch == ESC) continue;
            {
                char *d = h->h_desc, k[12];
                strcpy(k, unctrl(h->h_ch));
                while (*d == '\t') d++;
                if (!strncmp(d, "<dir>", 5)) { strcat(k, "<dir>"); d += 5; }
                while (*d == ' ' || *d == '\t') d++;
                sprintf(text[n], " %-8s %s", k, d);
            }
            items[n] = text[n]; keys[n++] = h->h_ch;
        }
        if ((i = menu(cmd_groups[g], items, keys, n)) >= 0 && menu_key != '-' && menu_key != '+') {
            touchwin(cw);
            return keys[i];
        }
    }
    touchwin(cw);
    return ESC;
}

/*
 * Inventory with a cursor (RVIP 3c).  inv_menu() returns the command key
 * for the chosen action and leaves the item in inv_pick, which get_item()
 * hands to that command.  inv_again reopens the list afterwards.
 */

struct linked_list *inv_pick;
int inv_again;

static int
worn(o)
struct object *o;
{
    int i;
    if (o == cur_weapon || o == cur_armor) return TRUE;
#ifdef NUM_FINGERS
    for (i = 0; i < NUM_FINGERS; i++) if (cur_ring[i] == o) return TRUE;
#elif defined(RIGHT_5)
    for (i = LEFT_1; i <= RIGHT_5; i++) if (cur_ring[i] == o) return TRUE;
#endif
#ifdef NUM_MM
    for (i = 0; i < NUM_MM; i++) if (cur_misc[i] == o) return TRUE;
#endif
    return FALSE;
}

/* The actions that fit an item, main one first.  The commands do their
 * own checks, so offering one too many is harmless. */
static int
item_actions(o, keys, names)
struct object *o;
char *keys, **names;
{
    int n = 0;
#define ACT(k, s) (keys[n] = (k), names[n++] = (s))
    if (o == cur_armor) ACT(C_TAKEOFF, "Take off");
    switch (o->o_type) {
        case POTION: ACT(C_QUAFF, "Quaff"); break;
        case SCROLL: ACT(C_READ, "Read"); break;
        case FOOD:   ACT(C_EAT, "Eat"); break;
        case WEAPON: if (o != cur_weapon) ACT(C_WIELD, "Wield");
                     ACT('t', "Throw"); break;
        case ARMOR:  if (!worn(o)) ACT(C_WEAR, "Wear"); break;
        case RING:   if (!worn(o)) ACT('P', "Put on");
                     else ACT('R', "Remove");
                     break;
        case STICK:  ACT(C_ZAP, "Zap"); break;
        case MM:
        case RELIC:  ACT(C_USE, "Use");
                     if (!worn(o)) ACT(C_WEAR, "Wear");
                     if (o->o_type == RELIC && o != cur_weapon) ACT(C_WIELD, "Wield");
                     break;
    }
    ACT(C_DROP, "Drop");
    ACT('c', "Call (name) it");
    return n;
#undef ACT
}

int
inv_menu()
{
    struct linked_list *l, *it[MAXPACK + 30];
    char *items[MAXPACK + 30], keys[MAXPACK + 30], text[MAXPACK + 30][LINELEN];
    char ak[16], *an[16], at[16][LINELEN], *ai[16];
    int n = 0, i, j, na, ch = 'a';

    for (l = pack; l && n < MAXPACK + 30; l = next(l), n++, ch = ch == 'z' ? 'A' : ch + 1) {
        sprintf(text[n], "%c) %s", ch, inv_name(OBJPTR(l), FALSE));
        items[n] = text[n]; keys[n] = ch; it[n] = l;
    }
    if (!n) {
        msg("You aren't carrying anything.");
        return ESC;
    }
    for (;;) {
        if ((i = menu("Inventory: letter/+ use, - drop, Enter actions, Esc close",
                      items, keys, n)) < 0) break;
        na = item_actions(OBJPTR(it[i]), ak, an);
        if (menu_key == '-') j = na - 2;                /* Drop */
        else if (menu_key != '\r') j = 0;               /* main action */
        else {
            for (j = 0; j < na; j++) {
                sprintf(at[j], " %-3s %s", unctrl(ak[j]), an[j]);
                ai[j] = at[j];
            }
            if ((j = menu(items[i], ai, ak, na)) < 0) continue;
        }
        inv_pick = it[i];
        inv_again = TRUE;
        touchwin(cw);
        return ak[j];
    }
    touchwin(cw);
    return ESC;
}

/* no message window: messages are on row 0 of cw */
WINDOW *msgw;
