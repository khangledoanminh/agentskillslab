# Smell Catalog + Thresholds

| Smell | Detection | Threshold mặc định | Severity |
|-------|-----------|--------------------|----------|
| God class | class > 500 dòng HOẶC > 15 methods HOẶC > 10 public attributes | vượt 1 trong 3 | HIGH |
| Long function | > 50 dòng HOẶC nested > 4 levels | vượt 1 trong 2 | MEDIUM |
| Duplication | clone detection (normalized hash) đoạn ≥ 6 dòng trùng | ≥ 2 occurrences | MEDIUM |
| Circular dependency | cycle trong import graph (DFS) | ≥ 1 cycle | HIGH |
| Deep inheritance | hierarchy depth > 4 | depth > 4 | MEDIUM |
| Shotgun surgery | 1 change cần sửa > 5 files | pattern trong git history | HIGH |
| Feature envy | method dùng attributes class khác nhiều hơn class mình | heuristic count | LOW |

Ngưỡng có thể override qua `--thresholds FILE` (JSON). Threshold chỉ là signal — AI quyết định cuối dựa context.

