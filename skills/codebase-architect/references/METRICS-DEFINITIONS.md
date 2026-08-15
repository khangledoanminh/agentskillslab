# Architecture Metrics Definitions

## Ca (Afferent Coupling)

Số module KHÁC import module X. Ca cao = module được nhiều nơi phụ thuộc = hotspot, thay đổi rủi ro cao.

## Ce (Efferent Coupling)

Số module X import. Ce cao = module phụ thuộc nhiều thứ = dễ break khi dependency đổi.

## I (Instability) = Ce / (Ca + Ce)

I ≈ 0: stable (khó thay đổi), I ≈ 1: unstable (dễ thay đổi). Module abstract nên stable; module concrete chi tiết nên unstable.

## Hotspot score

hotspot = Ca cao + recently changed (git log 90 ngày). Module vừa hot vừa stable-heavy là priority refactor candidate.

## Cycle

Cycle trong import graph = coupling vòng tròn; phá vòng bằng dependency inversion (interface ở module common).

