#!/bin/sh
# Super-Rogue, X11 frontend (curses shim, port/): tiled map on top,
# Messages + Status below left, Inventory right (layout in port/be_x11.c;
# override with XROGUE_MAP/_MSG/_STATUS/_INV="x,y"). Saves and scores in save/.
cd "$(dirname "$0")" || exit 1
mkdir -p save
# tile set: TILESET=dawn ./play.sh (DawnLike, port/mkdawn.py) or put "dawn" into save/tileset
[ -z "$TILESET" ] && [ -f save/tileset ] && TILESET=$(cat save/tileset)
[ -n "$TILESET" ] && [ -f "port/tiles-$TILESET.rgba" ] && export XROGUE_TILES="$PWD/port/tiles-$TILESET.rgba"
export HOME="$PWD/save" ROGUEHOME="$PWD/save"
if [ -f save/srogue.sav ]; then exec ./srogue-x11 save/srogue.sav "$@"; fi
exec ./srogue-x11 "$@"
