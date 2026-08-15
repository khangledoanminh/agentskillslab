---
name: release-engineer
description: "Prepare and validate a release: check changelog completeness, version bump consistency, build artifacts, license compliance, and release checklist items, producing a validated release manifest. Use when cutting a new version, preparing packages for distribution, or auditing release readiness."
---

# Release Engineer

Release readiness được CHỨNG MINH bằng checklist chạy thật, không khai báo. Pipeline: **read state → check items thật → build artifact → verify artifact → manifest**.

## Quy trình (5 bước)

1. **Đọc trạng thái**: current version (từ package metadata), git tag gần nhất, CHANGELOG entries chưa release.
2. **Check items thật** (script): CHANGELOG entry tồn tại cho version mới? version bump nhất quán (metadata == tag == changelog)? tests pass? build artifact tạo được? license file tồn tại? binary không lọt vào artifact source dist?
3. **Build artifact**: chạy build command thật của repo (python build, npm pack, cargo build).
4. **Verify artifact**: artifact tồn tại, size hợp lý, chứa đủ file cần (entry point, LICENSE), không chứa file nhạy cảm (secret scan nhanh).
5. **Manifest**: output JSON release manifest — mọi item pass/fail với evidence.

## Nguyên tắc

- Không tag/publish tự động — skill chỉ chuẩn bị + verify, publish là decision của người.
- Mọi check có evidence (file path, hash, command output).
- Version scheme tuân thủ semver; giải thích major/minor/patch choice.

## Scripts

- `scripts/release_check.py <repo> [--version NEXT]` — chạy mọi check, output manifest JSON.

## References

- [CHECKLIST-REFERENCE.md](references/CHECKLIST-REFERENCE.md)
- [SEMVER-GUIDE.md](references/SEMVER-GUIDE.md)
