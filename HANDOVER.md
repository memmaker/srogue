# Super-Rogue 9.0 — RVIP handover (2026-09-25)

Ported after Rogue 3.6 (`~/Games/rogue3.6`), which it grew out of: same data
model (`struct linked_list`, `OBJPTR`, `cw`/`mw`/`hw`, real map in `stdscr`).

- `rvip.c` and `port/` = Rogue 3.6's. Differences: pack letters step with
  `npch()`, one character per trap kind (no `TRAP`), `morestr` is an array
  (`-DWC_MORESTR_ARRAY`), two status lines (default `WC_STATUS_ROWS`),
  no `mdport.c` (HOME from `getenv` in `main.c`, save file `srogue.sav`).
- Almost no prototypes upstream. Declared in `rogue.h`: `msg`/`addmsg`
  (variadic: arm64 passes the args on the stack), `charge_str`/`ring_num`
  (pointers), and `stdlib.h`/`unistd.h` (void `srand48`/`free`/`abort`
  trap on wasm). `daemon` is renamed `sr_daemon` (libc clash).
- The game catches SIGSEGV (`game_err`) and hides ASan reports: run ASan
  builds with `ASAN_OPTIONS=allow_user_segv_handler=0`. It also ignores
  SIGTERM after a save attempt: stop test runs with `kill -9 <own pid>`.
- Save/restore: `save_file` closed the fd under a buffered FILE (lost the
  tail) → `fclose`; `rs_read_long`/`ulong` read 4 bytes into a 64-bit long;
  restore's `endwin()` + `fork()` unlink would close the X window → plain
  `unlink` under the shim; inode check and unlink skipped on the web.
- Web: no passwd entry → name "Rodney"; no `setuid`.
- The trading post is reached through a `^` trap; explore never steps on traps.
