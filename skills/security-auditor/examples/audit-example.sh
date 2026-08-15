#!/bin/sh
# Ví dụ: audit một repo mẫu
python3 scripts/audit.py ../../fixtures/repos/vulnerable-sample --output findings.json
echo "---"
cat findings.json | head -30
