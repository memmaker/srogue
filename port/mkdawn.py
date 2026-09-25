#!/usr/bin/env python3
"""Second tile set: DawnLike (DragonDePlatino, palette DawnBringer, CC BY 4.0),
sprites picked by name from rvip-tools/tilesets/dawnlike_names.tsv
(names: Tommy Ettinger's DawnLikeAtlas).

Writes tiles-dawn.png/.rgba with the same slot layout as tiles.png (mktiles.py).
Every slot the game uses gets a DawnLike sprite, nothing is left NetHack:
tile sets are never mixed. Stand-ins for monsters DawnLike lacks are in MON."""
import os, re, sys, glob
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.expanduser('~/Games/rvip-tools/tilesets')
sys.path.insert(0, TS)
from dawnlike_preview import pos, sprite

h = open(os.path.join(HERE, 'tilemap.h')).read()
arr = lambda n: [int(v) for v in re.search(r'%s\[[^]]*\] = \{([^}]*)\}' % n, h).group(1).split(',')]
dfn = lambda n: int(re.search(r'#define %s (\d+)' % n, h).group(1))
PER = dfn('TILES_PER_ROW')
CSRC = ''.join(open(f, encoding='latin-1').read() for f in sorted(glob.glob(os.path.join(HERE, '..', '*.c'))))

def table(name, plain=False):
    m = re.search(r'\b%s\s*\[[^]]*\]\s*=\s*\{' % name, CSRC)
    body = re.sub(r'/\*.*?\*/', '', CSRC[m.end():CSRC.index('};', m.end())], flags=re.S)
    return re.findall(r'"([^"]*)"' if plain else r'\{\s*"([^"]*)"', body)

MON = {  # game name -> DawnLike name, where they differ
 'bat': 'giant bat', 'centaur': 'forest centaur', 'red dragon': 'firedrake',
 'violet fungi': 'violet fungus', 'invisible stalker': 'stalker', 'mimic': 'large mimic',
 'nymph': 'wood nymph', 'zombie': 'human zombie', 'anhkheg': 'killer beetle',
 'elasmosaurus': 'serpent', 'killer frog': 'frog', 'green dragon': 'glendrake',
 'jaguar': 'panther', 'koppleganger': 'giant mimic', 'lonchu': 'gremlin',
 'neotyugh': 'huge meat blob', 'pseudo dragon': 'baby firedrake', 'quellit': 'homunculus',
 'rhynosphinx': 'sphinx', 'shadow': 'shade', 'ulodyte': 'water demon',
 'wuccubi': 'succubus', 'xonoclon': 'stone golem', 'zemure': 'lemure',
 'devil Asmodeus': 'asmodeus',
}
WEAP = {'short bow': 'shortbow', 'two-handed sword': 'two handed sword', 'spetum': 'pronged polearm',
        'bardiche': 'single edged polearm', 'pike': 'vulgar polearm', 'bastard sword': 'broadsword',
        'halberd': 'beaked polearm'}
ARMOR = {'leather armor': 'bronze armor', 'ring mail': 'hotrock mail',
         'studded leather armor': 'lacquered armor', 'scale mail': 'scale armor',
         'padded armor': 'peasant robes', 'chain mail': 'grandmaster mail',
         'splint mail': 'iron armor', 'plate mail': 'full plate', 'plate armor': 'mirror plate'}
TERRAIN = {'%': 'small stairs down', '^': 'stone portal', '\\': 'magic trap tile',
           '>': 'trap door tile', '{': 'arrow trap tile', '$': 'sleeping gas trap tile',
           '}': 'bear trap tile', '~': 'teleportation trap tile', '`': 'dart trap tile',
           '"': 'blue pool', '.': 'day tile floor nswe', '#': 'night stone floor c',
           '&': 'lit brick wall left right'}
GENERIC = {'!': 'clear potion', '?': 'blank scroll', ':': 'food ration', ')': 'long sword',
           ']': 'iron armor', ',': 'amulet of yendor', '=': 'gold ring', '/': 'oak wand',
           '*': 'pile of gold coins'}
WALL = 'lit brick wall '
FIXED = {'HWALL': WALL + 'left right', 'VWALL': WALL + 'up down', 'TL': WALL + 'right down',
         'TR': WALL + 'left down', 'BL': WALL + 'right up', 'BR': WALL + 'left up',
         'HDOOR': 'day tile floor nswe', 'VDOOR': 'day tile floor nswe',   # doors are gaps
         'FLOOR': 'day tile floor nswe', 'CORR': 'night stone floor c'}

img = Image.open(os.path.join(HERE, 'tiles.png')).convert('RGBA')
img = Image.new('RGBA', img.size, (0, 0, 0, 0))
filled = {}
def put(slot, name):
    if slot < 0: return
    if name not in pos: sys.exit('no DawnLike sprite: ' + name)
    filled[slot] = name
    img.paste(sprite(name), ((slot % PER) * 16, (slot // PER) * 16))

for n, slot in zip(table('monsters'), arr('mon_tile')):
    put(slot, MON.get(n, n))
put(arr('class_tile')[0], 'fighter')
for n, slot in zip(table('w_magic'), arr('weap_tile')): put(slot, WEAP.get(n, n))
for n, slot in zip(table('a_magic'), arr('armor_tile')): put(slot, ARMOR.get(n, n))
terr, gen = arr('terrain_tile'), arr('generic_tile')
for ch, n in TERRAIN.items(): put(terr[ord(ch)], n)
for ch, n in GENERIC.items(): put(gen[ord(ch)], n)
for k, n in FIXED.items(): put(dfn('T_' + k), n)

# random looks: tiles.c hashes the look's name into a slot range; give each slot
# the sprite named after a look that lands there, else the next unused one
def hslot(s, first, n):
    v = 5381
    for c in s.encode('latin-1'): v = (v * 33 + c) & 0xffffffff
    return first + v % n
for cls, looks, suffix in (('POTION', table('rainbow', True), ' potion'),
                           ('RING', table('stones', True), ' ring'),
                           ('WAND', table('wood', True) + table('metal', True), ' wand'),
                           ('SCROLL', [], ' scroll')):
    first, n = dfn(cls + '_TILES'), dfn(cls + '_NTILES')
    for l in looks:
        nm = l.lower() + suffix
        if nm in pos and hslot(l, first, n) not in filled: put(hslot(l, first, n), nm)
    spare = iter(sorted(k for k in pos if k.endswith(suffix) and k not in filled.values()))
    for s in range(first, first + n):
        if s not in filled: put(s, next(spare))

img.save(os.path.join(HERE, 'tiles-dawn.png'))
open(os.path.join(HERE, 'tiles-dawn.rgba'), 'wb').write(
    img.size[0].to_bytes(4, 'little') + img.size[1].to_bytes(4, 'little') + img.tobytes())
print(len(filled), 'slots, all DawnLike;', len(MON) + len(WEAP) + len(ARMOR), 'stand-ins by hand')
