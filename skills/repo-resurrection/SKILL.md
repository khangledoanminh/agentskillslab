---
name: repo-resurrection
description: "Revive an abandoned repository: audit its state, restore the build environment, fix broken dependencies and tests, modernize code and tooling, generate documentation, and produce a migration plan to bring the project back to life. Use when inheriting a dead or broken project that needs to become buildable, testable, and maintainable again."
---

# Repo Resurrection

Hồi sinh repo chết theo thứ tự: **audit → environment → dependencies → tests → code → docs → migration plan**. Mỗi bước có exit criterion rõ.

## Quy trình (7 bước)

1. **Audit**: đọc README/docs cũ, last commit, CI config, lockfile. Chạy `scripts/audit_state.py <repo>` → trạng thái: build broken? tests? dependency age? docs dead links?
2. **Restore environment**: dựng env chạy được (venv/container). Ghi lại chính xác steps + phiên bản tool — đây là deliverable quan trọng nhất.
3. **Fix dependencies**: cập nhật package tới version build được + không vulnerable. Giữ lockfile mới.
4. **Repair tests**: làm test suite chạy lại. Nếu test quá cũ không sửa được: viết characterization test mới covering core behavior.
5. **Modernize code**: chỉ các thay đổi cần để build/test pass + security fixes. KHÔNG rewrite theo ý thích — giữ behavior.
6. **Generate docs**: README mới (setup, run, test, architecture ngắn), docstring thiếu, changelog từ git history.
7. **Migration plan**: roadmap từng giai đoạn (1: build/test xanh; 2: dependency current; 3: feature parity; 4: CI tự động) + risk từng giai đoạn.

## Exit criteria

| Bước | Criterion |
|------|-----------|
| 2 | `make build`/equivalent pass trong env mới |
| 3 | Không dependency vulnerable đã biết (embedded CVE check) |
| 4 | ≥1 test suite chạy xanh |
| 5 | Behavior test không đổi |
| 6 | README mới tồn tại + setup chạy được từ README |
| 7 | Migration plan written + review-ready |

## Nguyên tắc

- Behavior preservation tuyệt đối — project sống lại, không biến thành project khác.
- Document mọi decision: vì sao upgrade version X mà không phải Y.
- Nếu repo quá lớn: resurrect core module trước, module còn lại trong migration plan.

## Scripts

- `scripts/audit_state.py <repo>` — báo cáo trạng thái repo cũ (last commit age, CI, deps, tests, docs).

## References

- [AUDIT-CHECKLIST.md](references/AUDIT-CHECKLIST.md)
- [MODERNIZATION-GUIDE.md](references/MODERNIZATION-GUIDE.md)
