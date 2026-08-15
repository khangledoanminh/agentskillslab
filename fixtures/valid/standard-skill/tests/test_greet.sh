#!/bin/bash
# test: greet.py output format
set -u
OUT=$(python3 scripts/greet.py --name fixture-test)
if [ "$OUT" != "Hello, fixture-test!" ]; then
  echo "FAIL: expected 'Hello, fixture-test!', got '$OUT'"
  exit 1
fi
echo "PASS: greet output format correct"
