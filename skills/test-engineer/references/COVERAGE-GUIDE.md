# Coverage Guide

## Cách đo coverage thật

```bash
python3 -m pytest --cov=src --cov-report=term-missing --cov-branch
```

Không tin coverage ước lượng bằng mắt. Report `term-missing` cho biết CHÍNH XÁC dòng nào chưa chạy — dùng nó làm input cho bước generate tests.

## Viết test cho uncovered path — priority order

1. Error paths (raise/except) chưa có test
2. Branch chưa chạy (missing lines trong report)
3. Boundary values (0, -1, max, empty collection)
4. Happy path chính

## Anti-patterns

- Test chỉ cover dòng mà không assert gì hữu ích → coverage xanh, chất lượng đỏ
- Mock quá nhiều → test không catch bug integration
- Test phụ thuộc thứ tự chạy → flaky

