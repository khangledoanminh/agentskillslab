# Diagram Generation Rules

1. Diagram Mermaid sinh TỰ ĐỘNG từ graph.json thật — không vẽ tay.
2. Validate roundtrip: parse diagram output phải reconstruct được graph gốc (test bằng `scripts/verify_diagram.py`).
3. Module > 1 file gom thành 1 node; dependency aggregation bằng số import.
4. Edge label = số dependency giữa 2 module.
5. Cycle highlight bằng stroke màu đỏ + ghi chú "CYCLE".
6. Giới hạn diagram ≤ 30 nodes; module nhỏ gom vào "others" cluster.

