---
name: dependency-doctor
description: "Diagnose dependency health across package managers (npm/pip/cargo/go): outdated packages, known vulnerabilities, unused dependencies, version conflicts, and license compliance issues, then produce a prioritized remediation plan. Use when managing, upgrading, or auditing project dependencies."
---

# Dependency Doctor

Chẩn đoán sức khỏe dependencies bằng dữ liệu THẬT từ package manager, không đoán. Đầu ra: bảng vấn đề + plan fix ưu tiên + lệnh chạy được.

## Quy trình (5 bước)

1. **Detect ecosystem**: tìm lockfile/manifest (package-lock.json, requirements.txt, Cargo.toml, go.sum, pyproject.toml). Báo ecosystem phát hiện.
2. **Quét vấn đề** (chạy script thật):
   - `scripts/doctor.py <repo>` chạy các check: outdated (so lockfile vs registry khi có network, hoặc heuristic version pattern khi không), vulnerable (so version với CVE database embedded `references/cves.json`), unused (import analysis), conflicts, license.
3. **Phân loại severity**: CRITICAL (CVE exploited), HIGH (CVE có fix), MEDIUM (outdated major), LOW (license info/unused).
4. **Remediation plan**: thứ tự fix, lệnh upgrade cụ thể, cảnh báo breaking change, backup trước khi upgrade.
5. **Verify sau fix**: chạy lại doctor, xác nhận vấn đề giảm; chạy test suite repo nếu có.

## Nguyên tắc

- Mọi con số (số package, version, CVE) phải từ output của script thật, không ước lượng.
- Không tự động chạy `upgrade` không hỏi — luôn đưa plan trước, đợi xác nhận.
- Lockfile là source of truth; không sửa file thủ công.
- Nếu không có network: chạy chế độ offline (check syntax, lockfile consistency, embedded CVE list), ghi rõ giới hạn.

## Scripts

- `scripts/doctor.py <repo> [--ecosystem pip|npm|cargo|go] [--offline] [--output report.json]`

## References

- [ECOSYSTEMS.md](references/ECOSYSTEMS.md) — đặc thù từng package manager
- [CVE-LIMITATIONS.md](references/CVE-LIMITATIONS.md) — giới hạn database embedded
