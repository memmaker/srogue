#!/usr/bin/env python3
"""NetHack tiles -> tiles.png (16x16, 32 per row, background transparent)
and tilemap.h (XRogue monster/item/terrain -> tile index).
RVIP step 4: Rogue variants fall back to the NetHack tileset."""
import re, sys, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
NH = os.path.join(HERE, 'nethack')
SRC = os.path.dirname(HERE)
PER_ROW = 32

names, tiles = [], []          # names[i] = list of names for tile i
for f in ('monsters', 'objects', 'other'):
    txt = open(os.path.join(NH, f + '.txt')).read().split('\n')
    pal, i = {}, 0
    while i < len(txt):
        m = re.match(r"^(\S) = \((\d+), *(\d+), *(\d+)\)", txt[i])
        if m:
            pal[m[1]] = tuple(map(int, m.group(2, 3, 4)))
        m = re.match(r"^# tile \d+ \((.*)\)$", txt[i])
        if m:
            n = m[1]
            rows = []
            i += 1
            while txt[i].strip() != "{": i += 1
            i += 1
            while not txt[i].startswith('}'):
                rows.append(txt[i].strip()); i += 1
            if f == 'monsters' and n.endswith(',female'):
                i += 1; continue
            n = re.sub(r', ?(male|nogender)$', '', n)
            key = [n] + [p.strip() for p in n.split(' / ')]
            names.append([k if f != 'other' else 'T:' + k for k in key])
            tiles.append([[pal[c] for c in r] for r in rows])
        i += 1

idx = {}
for i, ks in enumerate(names):
    for k in ks:
        idx.setdefault(k, i)

def T(n):
    if n not in idx:
        sys.exit('no NetHack tile: ' + n)
    return idx[n]

def rng(first, last):
    return T(first), T(last) - T(first) + 1

# --- monsters, in mons_def.c order -------------------------------------
MON = {
 'unknown': 'invisible monster', 'halfling': 'hobbit', 'xvart': 'goblin',
 'rot grub': 'baby long worm', 'urchin': 'acid blob',
 'fire beetle': 'giant beetle', 'ear seeker': 'centipede',
 'stirge': 'vampire bat', 'troglodyte': 'neanderthal',
 'zombie': 'human zombie', 'giant tick': 'cave spider',
 'zoo spore': 'shocking sphere', 'lonchu': 'gremlin',
 'junk monster': 'lurker above', 'jacaranda': 'green mold',
 'gnoll': 'large kobold', 'fire toad': 'salamander',
 'moon dog': 'large dog', 'violet fungi': 'violet fungus',
 'centaur': 'forest centaur', 'nymph': 'wood nymph',
 'blindheim': 'iguana', 'blink dog': 'dog', 'ghast': 'dwarf zombie',
 'shadow': 'shade', 'very young dragon': 'baby red dragon',
 'ice weasel': 'winter wolf cub', 'mimic': 'small mimic',
 'otyugh': 'quivering blob', 'su-monster': 'ape', 'leucrotta': 'leocrotta',
 'wight': 'barrow wight', 'phibian': 'crocodile',
 'fireworm': 'baby purple worm', 'flumph': 'jellyfish',
 'treant': 'wood golem', 'lava child': 'fire elemental',
 'erinyes': 'erinys', 'ulodyte': 'water demon', 'jackalwere': 'werejackal',
 'basilisk': 'pyrolisk', 'glabrezu': 'nalfeshnee',
 'wyvern': 'baby green dragon', 'specter': 'Nazgul',
 'mummy': 'human mummy', 'chimera': 'hell hound',
 'neo-otyugh': 'brown pudding', 'adult dragon': 'green dragon',
 'rhinosphynx': 'titanothere', 'lamia': 'red naga',
 'intellect devourer': 'mind flayer', 'will-o-wisp': 'yellow light',
 'invisible stalker': 'stalker', 'hellmaid': 'amorous demon',
 'shadow dragon': 'black dragon', 'xenolith': 'stone golem',
 'shambling mound': 'straw golem', 'morkoth': 'kraken',
 'white pudding': 'ochre jelly',
 'ancient black dragon': 'black dragon', 'ancient blue dragon': 'blue dragon',
 'ancient red dragon': 'red dragon', 'ancient brass dragon': 'yellow dragon',
 'ancient green dragon': 'green dragon', 'ancient white dragon': 'white dragon',
 'ancient bronze dragon': 'orange dragon',
 'ancient copper dragon': 'shimmering dragon',
 'ancient amethyst dragon': 'gray dragon',
 'ancient silver dragon': 'silver dragon',
 'ancient saphire dragon': 'blue dragon', 'ancient gold dragon': 'gold dragon',
 'nemesis': 'Minion of Huhetotl',
 'lesser god (Hruggek)': 'ogre tyrant', 'lesser god (Surtur)': 'Lord Surtur',
 'demon prince (Yeenoghu)': 'Yeenoghu', 'demon prince (Orcus)': 'Orcus',
 'arch devil (Geryon)': 'Geryon', 'arch devil (Asmodeus)': 'Asmodeus',
 'poet (Brian)': 'Norn', 'witch (Emori)': 'Neferet the Green',
 'hero (aklad)': 'King Arthur', 'cleric of thoth (Heil)': 'Arch Priest',
 'magician/thief (Nagrom)': 'Master of Thieves',
 'magician (Tsoming Zen)': 'Grand Master',
 'dwarven thief (Musty Doit)': 'dwarf ruler',
 'ruler of titans (Yendor)': 'Wizard of Yendor',
 'maker of rock (Stonebones)': 'Cyclops',
 'creator of liches (Vecna)': 'arch-lich', 'lesser god (Thrym)': 'giant',
 'lesser god (Kurtulmak)': 'kobold leader', 'lesser god (Antar)': 'Master Kaen',
 'demon prince (Jubilex)': 'Juiblex', 'demon prince (Bone)': 'Nalzok',
 "demon prince (Graz'zt)": 'Dark One',
 'demon prince (Demogorgon)': 'Demogorgon', 'arch devil (Mammon)': 'Croesus',
 'arch devil (Baalzebul)': 'Baalzebub', 'arch devil (Moloch)': 'balrog',
 'arch devil (Dispater)': 'Dispater',
 'platinum dragon (Bahamut)': 'shimmering dragon',
 'diablero (Prithivi)': 'earth elemental', 'diablero (Apas)': 'water elemental',
 'chromatic dragon (Tiamat)': 'Chromatic Dragon',
 'diablero (Vayu)': 'air elemental', 'diablero (Tejas)': 'fire elemental',
 'etheric dragon (Ishtar)': 'gray dragon', 'diablero (Akasa)': 'energy vortex',
 'greater god (Maglubiyet)': 'Goblin King', 'greater god (Gruumsh)': 'orc-captain',
 'semi-demon (Cambion)': 'imp', 'minor demon (Dretch)': 'lemure',
 'major demon (Nabassu)': 'vrock', 'demon lord (Baphomet)': 'minotaur',
 'prince of hell (Hutijin)': 'pit fiend',
 'princess of hell (Glasya)': 'amorous demon',
 'prince of hell (Titivilus)': 'imp', 'lesser daemon (Pisco)': 'sandestin',
 'lesser daemon (Dergho)': 'hezrou', 'greater daemon (Ultro)': 'nalfeshnee',
 'lesser daemon (Hydro)': 'water demon', 'lesser daemon (Yagno)': 'bone devil',
 'greater daemon (Arcana)': 'djinni', 'oino daemon (Anthraxus)': 'Pestilence',
 'ipsissimus (Alteran)': 'Wizard of Yendor', 'boatman (Charon)': 'Charon',
 'anole': 'lizard', 'creodont': 'wolf', 'gorgosaur': 'crocodile',
 'giant cicada': 'killer bee', 'elasmosaurus': 'giant eel',
 'trilobite': 'scorpion', 'mammoth': 'mumak', 'ichthyosaur': 'shark',
 'grig': 'soldier ant', 'saber-tooth': 'tiger', 'merychippus': 'pony',
 'nematode': 'long worm', 'tussah': 'queen bee', 'theropod': 'baby crocodile',
 'sloth': 'sasquatch', 'pterodactyl': 'raven',
 'brontosaurus': 'baluchitherium', 'sauropod': 'titanothere',
 'wooly mammoth': 'mumak', 'brontops': 'titanothere', 'tricerotops': 'wumpus',
 'sinanthropus': 'neanderthal', 'stegosaurus': 'baluchitherium',
 'plesiosaurus': 'kraken', 'tyranosaurus rex': 'jabberwock',
 'anaconda': 'python', 'imperial mammoth': 'mumak',
 'zinjanthropus': 'carnivorous ape', 'positron': 'shocking sphere',
 'quartermaster': 'shopkeeper',
}
import glob
# ---- per game: monster table name, extra name aliases, class tiles (C_* order) ----
MON_TABLE = 'monsters'
EXTRA = {
 'aquator': 'rust monster', 'emu': 'raven', 'griffin': 'winged gargoyle', 'ice monster': 'ice vortex',
 'kestrel': 'raven', 'phantom': 'ghost', 'quagga': 'pony', 'rattlesnake': 'snake', 'venus flytrap': 'violet fungus',
 'xeroc': 'giant mimic',
 'Amulet of Stonebones': 'amulet of life saving', 'Ankh of Heil': 'amulet of reflection',
 'Axe of Aklad': 'axe', 'Cloak of Emori': 'cloak of magic resistance',
 'Daggers of Musty Doit': 'athame', 'Eye of Vecna': 'lenses',
 'Flail of Yeenoghu': 'flail', 'Horn of Geryon': 'frost horn',
 'Mandolin of Brian': 'magic harp', 'Morning Star of Hruggek': 'morning star',
 'Quill of Nagrom': 'magic marker', 'Ring of Surtur': 'ring / generic ring',
 'Rod of Asmodeus': 'spiked', 'Staff of Ming': 'quarterstaff', 'Wand of Orcus': 'jeweled',
 'alchemy jug': 'clear / water', 'beaker of potions': 'murky / oil', 'bastard sword': 'broadsword',
 'book of skills': 'parchment / dig', 'book of spells': 'vellum / magic missile',
 'boots of dancing': 'fumble boots', 'boots of elvenkind': 'elven boots',
 'bracers of defense': 'leather gloves', 'drums of panic': 'drum of earthquake',
 'dust of choking': 'can of grease', 'dust of disappearance': 'can of grease',
 'gauntlets of ogre power': 'gauntlets of power', 'jewel of attacks': 'red / ruby',
 'keoghtoms ointment': 'can of grease', 'necklace of adaptation': 'amulet of magical breathing',
 'necklace of strangulation': 'amulet of strangulation', 'robe of powerlessness': 'robe',
 'pike': 'spetum', 'doppleganger': 'doppelganger',
 'padded armor': 'leather jacket', 'plate armor': 'crystal plate mail',
 'cleric of Thoth (Heil)': 'Arch Priest', 'hero (Aklad)': 'King Arthur',
 'demigod (Vaprak "The Destroyer")': 'ogre tyrant', 'lesser god (Skoraeus Stonebones)': 'Cyclops',
 'ruler of greater titans (Yendor)': 'Wizard of Yendor', 'the creator of liches (Vecna)': 'arch-lich',
}
for f in ('blueberry candleberry caprifig dewberry elderberry gooseberry guanabana hagberry '
          'jaboticaba peach pitanga rambutan sapodilla soursop strawberry sweetsop whortleberry').split():
    EXTRA[f] = 'slime mold'
CLASS = ['rogue']
CSRC = ''.join(open(f, encoding='latin-1').read() for f in sorted(glob.glob(os.path.join(SRC, '*.c'))))

def table(name):
    """Names of the entries of a C table `name[...] = { {"x", ...}, ... };`."""
    m = re.search(r'\b%s\s*\[[^]]*\]\s*=\s*\{' % name, CSRC)
    if not m:
        return []
    body = CSRC[m.end():CSRC.index('};', m.end())]
    body = re.sub(r'/\*.*?\*/', '', body, flags=re.S)
    return [x.replace('\\"', '"') for x in re.findall(r'\{\s*"((?:[^"\\]|\\.)*)"', body)]


# keyword rules for names no alias covers (first match wins; UltraRogue has ~400 monsters)
RULES = [
 (r'witch-king|ringwraith|nazgul', 'Nazgul'), (r'balrog', 'balrog'), (r'sauron|melkor|lucifer', 'Dark One'),
 (r'^valar', 'Angel'), (r'^maiar', 'Aleax'), (r'goddess', 'Angel'), (r'demi-god|hero-mage|arch-mage|^hero ', 'Aleax'),
 (r'god ', 'Archon'), (r'succubus|wuccubi', 'amorous demon'), (r'demodand|demon|zemure|larva', 'hezrou'),
 (r'devil', 'barbed devil'), (r'yeenoghu', 'Yeenoghu'), (r'young dragon|pseudo|psuedo|dragonne', 'baby red dragon'),
 (r'dragon|wyverg', 'red dragon'), (r'ceratops|cerotops|styraco|monoclon|ankylo|paleoscincus', 'titanothere'),
 (r'saurus|odon|diplodocus|brachio|camarasaurus|allosaurus|tyranno', 'crocodile'),
 (r'elephant|mastadon|loxodant|heffalump|mammoth', 'mumak'), (r'rhino|buffalo|bull|lammasu|shedu|catoblepas|gorgon', 'titanothere'),
 (r'boar|warthog', 'rothe'), (r'camel|pegasus|hipogriff|nightmare', 'horse'), (r'unicorn', 'white unicorn'),
 (r'lion|leopard|pertuska', 'jaguar'), (r'bear', 'owlbear'), (r'baboon|octorilla', 'ape'), (r'badger|hyena|hound', 'jackal'),
 (r'roc$|phoenix|peryton|hawk|falcon|aarakocra|airfang|griffon|harpy', 'raven'),
 (r'beetle|tick|anhkheg|carrion|bulette|remorhaz', 'giant beetle'), (r'frog', 'giant eel'),
 (r'elemental|sylph|slyph|undine|genii|efreeti|aerial|air squid', 'air elemental'),
 (r'ent$|entwife|huorn|triffid|archer bush|dryad|phycomid', 'wood golem'),
 (r'pixie|brownie|pech|satyr|homonc|quellit', 'homunculus'), (r'hag|sorcere|banshee|spectre|mind maggot', 'ghost'),
 (r'naga', 'golden naga'), (r'medusa', 'Medusa'), (r'iguana', 'iguana'), (r'cyclops', 'Cyclops'), (r'manticore|rakshasa|sphinx|rhynosphinx', 'leocrotta'),
 (r'basilisk', 'cockatrice'), (r'piercer|roper', 'lurker above'), (r'horror|neotyugh', 'blue jelly'),
 (r'koppleganger|vilstrak|xonoclon|slithering|tracker|achaierai', 'doppelganger'), (r'player', 'human'),
 # weapons, armour, artifacts
 (r'claymore|two handed', 'two-handed sword'), (r'broad sword', 'broadsword'), (r'cutlass|machete', 'scimitar'),
 (r'sabre|rapier', 'silver saber'), (r'hatchet|tomahawk', 'axe'), (r'hammer|maul', 'war hammer'), (r'pick', 'pick-axe'),
 (r'scythe|sickle', 'bardiche'), (r'pitchfork', 'trident'), (r'singlestick', 'quarterstaff'), (r'leuku', 'knife'),
 (r'footbow bolt', 'crossbow bolt'), (r'footbow', 'crossbow'), (r'grenade', 'rock'), (r'batarang', 'boomerang'),
 (r'brigandine', 'splint mail'), (r'cuirboilli|soft leather', 'leather armor'), (r'superior chain', 'chain mail'),
 (r'mithril', 'elven mithril-coat'), (r'crown', 'helm of brilliance'), (r'palantir', 'crystal ball'),
 (r'phial', 'oil lamp'), (r'sceptre', 'mace'), (r'silmaril', 'red / ruby'), (r'purse', 'bag of holding'),
 (r'time elemental|wood elemental', 'energy vortex'),
]

def strings(name):
    """Entries of a plain C string array `name[...] = { "a", "b", ... };`."""
    m = re.search(r'\b%s\s*\[[^]]*\]\s*=\s*\{' % name, CSRC)
    if not m:
        return []
    body = re.sub(r'/\*.*?\*/', '', CSRC[m.end():CSRC.index('};', m.end())], flags=re.S)
    return re.findall(r'"((?:[^"\\]|\\.)*)"', body)

def fuzzy(n, fallback):
    """NetHack tile for a game name: exact, alias, last word(s), else fallback."""
    base = re.sub(r'\s*\(.*\)', '', n).strip()      # "succubus (Servant of X)"
    for c in (ALIAS.get(n), n, n.lower(), ALIAS.get(base), base, base.lower()):
        if c and c in idx:
            return idx[c]
    w = base.lower().replace('-', ' ').split()
    for k in range(1, len(w)):                          # "giant tick" -> "tick"
        if ' '.join(w[k:]) in idx:
            return idx[' '.join(w[k:])]
    for k in range(len(w) - 1, 0, -1):                  # "wild boar" -> "wild"? first words
        if ' '.join(w[:k]) in idx:
            return idx[' '.join(w[:k])]
    for pat, tile in RULES:
        if re.search(pat, n.lower()) and tile in idx:
            return idx[tile]
    missing.append(n)
    return T(fallback)

missing = []
ALIAS = dict(MON, **EXTRA)
def unique(ts):
    """Own slot per entry (a copy of the shared tile), so a second tile set
    (mkdawn.py) can draw each monster/item differently."""
    out = []
    for t in ts:
        if t in used:
            tiles.append(tiles[t]); t = len(tiles) - 1
        used.add(t); out.append(t)
    return out

used = set()
mon_tiles = unique([fuzzy(n, 'invisible monster') for n in table(MON_TABLE)])
mons = table(MON_TABLE)
WEAP = table('w_magic') or table('weaps') or table('weap_info') or strings('w_names'); ARMOR = table('a_magic') or table('armors') or table('arm_info') or strings('a_names'); MMAG = table('m_magic')
RELIC = table('rel_magic') or table('arts'); FOOD = table('foods')
TERRAIN = {  # char -> tile; walls/doors are chosen in tiles.c
 '.': 'floor of a room', '#': 'corridor', '%': 'staircase down',
 '^': 'magic trap', '>': 'trap door', '{': 'arrow trap', '$': 'sleeping gas trap',
 '}': 'bear trap', '~': 'teleportation trap', '`': 'dart trap',
 '<': 'magic portal', '"': 'pool', "'": 'level teleporter', '\\': 'tree',
 '&': 'horizontal closed door',
}
GENERIC = {  # item class char -> tile when the object isn't known
 '!': 'potion / generic potion', '?': 'scroll / generic scroll',
 ':': 'food ration', ')': 'weapon / generic weapon', ']': 'armor / generic armor',
 ';': 'tool / generic tool', ',': 'amulet / generic amulet',
 '=': 'ring / generic ring', '/': 'wand / generic wand', '*': 'gold piece',
}

def arr(name, vals):
    return 'static const short %s[] = {%s};\n' % (name, ','.join(map(str, vals)))

out = ['/* generated by port/mktiles.py from the NetHack tiles - do not edit */\n',
       '#define TILES_PER_ROW %d\n' % PER_ROW,
       arr('mon_tile', mon_tiles), arr('class_tile', [T(c) for c in CLASS]),
       arr('weap_tile', unique([fuzzy(n, 'weapon / generic weapon') for n in WEAP]) or [-1]),
       arr('armor_tile', unique([fuzzy(n, 'armor / generic armor') for n in ARMOR]) or [-1]),
       arr('mm_tile', [fuzzy(n, 'tool / generic tool') for n in MMAG] or [-1]),
       arr('relic_tile', [fuzzy(n, 'amulet / generic amulet') for n in RELIC] or [-1]),
       arr('food_tile', [fuzzy(n, 'food ration') for n in FOOD] or [-1]),
       'static const short terrain_tile[128] = {%s};\n' % ','.join(
           str(T('T:' + TERRAIN[chr(c)])) if chr(c) in TERRAIN else '-1' for c in range(128)),
       'static const short generic_tile[128] = {%s};\n' % ','.join(
           str(T(GENERIC[chr(c)])) if chr(c) in GENERIC else '-1' for c in range(128))]
for nm, a, b in (('POTION', 'ruby / gain ability', 'murky / oil'),
                 ('SCROLL', 'ZELGO MER / enchant armor', 'STRC PRST SKRZ KRK'),
                 ('RING', 'wooden / adornment', 'shiny / protection from shape changers'),
                 ('WAND', 'glass / light', 'jeweled')):
    s, n = rng(a, b)
    out.append('#define %s_TILES %d\n#define %s_NTILES %d\n' % (nm, s, nm, n))
for k, v in (('HWALL', 'main walls horizontal'), ('VWALL', 'main walls vertical'),
             ('TL', 'main walls tlcorn'), ('TR', 'main walls trcorn'),
             ('BL', 'main walls blcorn'), ('BR', 'main walls brcorn'),
             ('HDOOR', 'horizontal open door'), ('VDOOR', 'vertical open door'),
             ('FLOOR', 'floor of a room'), ('CORR', 'corridor')):
    out.append('#define T_%s %d\n' % (k, T('T:' + v)))
img = Image.new('RGBA', (PER_ROW * 16, (len(tiles) + PER_ROW - 1) // PER_ROW * 16))
for t, rows in enumerate(tiles):
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            a = 0 if c == (71, 108, 108) else 255
            img.putpixel(((t % PER_ROW) * 16 + x, (t // PER_ROW) * 16 + y), c + (a,))
img.save(os.path.join(HERE, 'tiles.png'))

open(os.path.join(HERE, 'tilemap.h'), 'w').write(''.join(out))
print(len(tiles), 'tiles,', len(mons), 'monsters; no tile (fallback):', sorted(set(missing)))
# raw RGBA copy for the X11 frontend (no PNG decoder needed in C)
open(os.path.join(HERE, 'tiles.rgba'), 'wb').write(
    img.size[0].to_bytes(4, 'little') + img.size[1].to_bytes(4, 'little') + img.tobytes())
