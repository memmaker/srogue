# Super-Rogue — RVIP port

Upstream: Super-Rogue 9.0 (Robert D. Kindelberger, 1984), release 9.0-1 from the
Roguelike Restoration Project: https://github.com/RoguelikeRestorationProject/srogue/tree/c693810

**Our changes:** https://github.com/memmaker/srogue/compare/c693810...master
(commit 1 is the untouched upstream; everything after it is ours).

- `port:` builds on macOS/arm64 and WebAssembly, curses shim (`port/`) with
  an X11 frontend, NetHack tiles (`port/mktiles.py`), DawnLike as a second
  set (`port/mkdawn.py`; DragonDePlatino, palette DawnBringer, CC BY 4.0;
  web: *Tiles* button, desktop: `TILESET=dawn ./play.sh`); fixes crashes from
  undeclared functions (variadic `msg`, pointer-returning `charge_str`/`ring_num`,
  void `srand48`/`free`), a save that lost its buffered tail and 4-byte longs
  read into 8-byte ones.
- `RVIP:` auto-explore (`x`), `<`/`>` walk to known stairs, Enter command
  menu, inventory with a cursor, sound events (`rvip.c` + small hooks).
- `web:` browser build (`web/build.sh`), played at https://ruzzoli.de/roguelikes/srogue/

Build: `make srogue-x11` (XQuartz), `./play.sh`; web: `sh web/build.sh`, `web/deploy.sh`.
Notes for the next person: `HANDOVER.md`. Process: `~/Games/RVIP.md`, `~/Games/rogue2wasm.md`.
