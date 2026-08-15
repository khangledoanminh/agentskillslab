# Statistical Notes

## Vì sao median thay vì mean

Mean nhạy outlier: 1 lần GC pause 200ms giữa 5 lần đo 10ms → mean 52ms, median 10ms. Median phản ánh "trường hợp điển hình" tốt hơn cho performance.

## Outlier handling

Loại bỏ iteration đầu (warmup effect). Không loại thêm iteration khác trừ khi có lý do ghi lại (VD: background process spike — phải ghi evidence).

## Significance threshold

Speedup ≥ 20% mới coi đáng kể (dưới ngưỡng này nằm trong noise đo lường thông thường). Luôn verify correctness sau patch: output before == output after.

