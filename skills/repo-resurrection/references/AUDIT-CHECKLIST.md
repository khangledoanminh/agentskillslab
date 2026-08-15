# Repo State Audit Checklist

| # | Item | Check command | Pass criteria |
|---|------|---------------|---------------|
| 1 | Last commit age | `git log -1 --format=%ci` | ghi nhận, > 1 năm = legacy flag |
| 2 | Build broken? | chạy build command trong docs/CI | exit 0 |
| 3 | Tests status | chạy test suite | ≥ 1 suite chạy được |
| 4 | Dependency freshness | so manifest version vs registry | ghi tuổi từng dep |
| 5 | Docs dead links | scan README/docs links | internal links tồn tại |
| 6 | CI config hiện hữu? | `.github/`, `.travis.yml`, `ci/` | ghi nhận |
| 7 | Runtime version | toolchain version yêu cầu vs hiện tại | tương thích |
| 8 | Secret scan nhanh | scan pattern secrets trong repo | 0 secret thật |

