#!/bin/sh
OUT=$(python3 scripts/work.py asl)
[ "$OUT" = "work output asl" ] && echo PASS || { echo FAIL; exit 1; }
