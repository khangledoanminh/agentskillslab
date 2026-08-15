---
name: codebase-architect
description: "Analyze a repository's architecture and produce an evidence-based architecture report: module map, dependency graph, coupling metrics, circular dependencies, and hotspot identification, with Mermaid diagrams generated from real import relationships. Use when onboarding to a new codebase, planning major changes, or documenting system structure."
---

# Codebase Architect

Phân tích kiến trúc repo bằng dữ liệu THẬT từ import/dependency relationships, không bằng cảm nhận. Đầu ra: báo cáo kiến trúc + diagram Mermaid tự sinh.

## Quy trình (5 bước)

1. **Map modules**: liệt kê packages/modules, kích thước (dòng code), trách nhiệm suy ra từ tên + docstring.
2. **Build dependency graph**: chạy `scripts/graph_deps.py <repo>` phân tích import statements → adjacency list thật.
3. **Tính metrics**:
   - Coupling: số dependency in/out mỗi module (Ca/Ce).
   - Circular dependencies: DFS tìm cycle trong import graph.
   - Hotspots: module có fan-in cao (nhiều nơi phụ thuộc) + thay đổi gần đây (git log).
4. **Vẽ diagram**: sinh Mermaid flowchart từ graph thật; KHÔNG vẽ tay diagram không khớp code.
5. **Báo cáo**: module map + metrics table + cycle list + hotspot ranking + khuyến nghị tách module nếu coupling quá cao.

## Nguyên tắc

- Mọi con số từ script; diagram phải khớp graph thật (test: parse lại diagram phải bằng graph).
- Không phán kiến trúc "tốt/xấu" chung chung — chỉ ra metric cụ thể và ngưỡng.
- Report ngắn gọn: table + diagram + 5 khuyến nghị tối đa.

## Scripts

- `scripts/graph_deps.py <repo> [--language python|js|ts] [--output graph.json]`
- `scripts/metrics.py graph.json` — tính Ca/Ce, cycles, hotspots → JSON.

## References

- [METRICS-DEFINITIONS.md](references/METRICS-DEFINITIONS.md)
- [DIAGRAM-RULES.md](references/DIAGRAM-RULES.md)
