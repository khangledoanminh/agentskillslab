# AgentSkillsLab — Threat Model

**Version:** 1.0 · **Date:** August 15, 2026 · **Classification:** Public

---

## 1. Scope & Assumptions

AgentSkillsLab gồm hai bề mặt tấn công chính: **(A)** CLI/library consume và thực thi Skills bên thứ ba, và **(B)** chính Skills flagship của repo. Threat model này giả định skill content **có thể độc hại** và thiết kế defense theo nguyên tắc "zero trust đối với Skill":

> Assume Skill content can be malicious. Never blindly execute untrusted Skill code.

Asset cần bảo vệ: (1) credential trên máy host (env vars, keychains, git credentials); (2) dữ liệu ngoài phạm vi task; (3) tính toàn vẹn của hệ thống (không arbitrary code execution, không data exfiltration); (4) uy tín của developer khi dùng findings của skill (không hallucinated scan results).

## 2. Threat Inventory

| ID | Threat | Vector | Likelihood | Impact | Mitigation |
|----|--------|--------|------------|--------|------------|
| T1 | Malicious script execution | scripts/ chứa payload khi `agent-skills test` chạy | HIGH | CRITICAL | Runner với permission envelope, timeout, denylist; user phê duyệt trước khi chạy |
| T2 | Prompt injection qua SKILL.md | instructions chèn lệnh vượt tầm task | MEDIUM | HIGH | SKILL.md đọc dưới dạng dữ liệu; runner không thực thi nội dung markdown; user reviews output |
| T3 | Credential theft | script đọc env vars / ~/.ssh / ~/.git-credentials | HIGH | CRITICAL | Runner chặn path traversal khỏi workdir; cảnh báo khi script truy cập file ngoài phạm vi; skill.yaml khai báo permissions |
| T4 | Data exfiltration qua network | script POST dữ liệu ra ngoài | MEDIUM | HIGH | `permissions.network` khai báo + heuristic phát hiện outbound (documented limitation: không block tuyệt đối ở envelope mode) |
| T5 | Typosquatting | skill tên gần skill nổi tiếng | MEDIUM | MEDIUM | validator reject tên chứa reserved words; docs cảnh báo install từ trusted source |
| T6 | Obfuscated code | base64/exec/eval trong scripts | MEDIUM | HIGH | detector phát hiện obfuscation markers; validator FAIL với finding OBF-001 |
| T7 | Dangerous downloads | script tải và thực thi file ngoài | MEDIUM | HIGH | detector URL + exec patterns; permissions.download phải khai báo |
| T8 | Resource exhaustion | manifest/scripts khổng lồ, fork bomb, zip bomb | LOW | MEDIUM | Size limits trong spec (manifest ≤100KB), timeout runner,拒绝 symlink traversal |
| T9 | Symlink / path traversal | links ngoài workdir | MEDIUM | MEDIUM | resolve paths rồi verify prefix; reject symlinks ra ngoài skill dir |
| T10 | Supply-chain dependency attack | dependency-doctor cài tool mới | LOW | MEDIUM | runner không cài packages khi test; install luôn dry-run mặc định |
| T11 | Malformed metadata crash | YAML bomb, unicode abuse | LOW | LOW | safe YAML loader, size limits, exception boundaries quanh parser |
| T12 | Credential leak từ findings | findings.json chứa secret thật | MEDIUM | MEDIUM | findings chứa line-number evidence nhưng SNIP giá trị secret; SECURITY.md hướng dẫn |
| T13 | Command injection qua CLI args | file paths chứa metacharacters | MEDIUM | HIGH | Không dùng shell=True trong Python subprocess; args list hóa |
| T14 | Race condition khi concurrent ops | nhiều process validate cùng skill | LOW | LOW | CLI read-only đối với skill dir; install viết qua atomic rename |

## 3. Defense-in-Depth Layers

**Layer 1 — Spec (ngăn chặn cấu trúc):** schema validation từ chối skill không đạt chuẩn (D1). **Layer 2 — Validator (phát hiện):** scan patterns độc hại trước khi bất kỳ script nào chạy (D2). **Layer 3 — Runner (giới hạn thực thi):** envelope với timeout, workdir lock, denylist (D3). **Layer 4 — Human approval (quyết định cuối):** lệnh có side-effect (`test` chạy scripts của skill, `install`) luôn in summary và yêu cầu confirm hoặc flag `--yes`; findings của skills security-auditor mang tính hỗ trợ quyết định, không auto-fix.

## 4. Permission Model

```yaml
# skill.yaml
permissions:
  filesystem: local          # local | read-only | none
  network: none              # none | outbound-only
  downloads: false
  install_packages: false
  subprocess: safe           # safe | none
  max_runtime_seconds: 300
```

Mặc định cho skill không khai báo: `filesystem: local, network: none, downloads: false, install_packages: false, subprocess: safe`. Runner enforce ở mức heuristic + denylist; giới hạn này **documented chứ không ảo tưởng absolute isolation** (xem Unverified U1).

## 5. Known Limitations & Unverified Items

| ID | Item | Trạng thái |
|----|------|-----------|
| U1 | Envelope không phải sandbox OS-level (không seccomp/rootfs) | WARNING — đủ cho threat local; khuyên dùng VM cho skill hoàn toàn không tin cậy |
| U2 | Phát hiện network exfiltration là heuristic (không MITM host) | WARNING |
| U3 | Prompt injection qua SKILL.md chỉ giảm thiểu bằng quy trình review, không chặn kỹ thuật tuyệt đối | WARNING |

## 6. Incident Response (nếu phát hiện skill độc hại trong ecosystem)

Báo cáo qua SECURITY.md (email + issue template), repo sẽ: revoke trong docs compatibility list, publish advisory với mã finding, cập nhật denylist/detector.

## 7. Security Testing Plan

Kiểm thử adversarial có trong `tests/`: malicious fixtures (T1, T5, T6, T7, T8, T9, T11, T13) được validate bởi chính CLI để chứng minh fail-safe, và các cuộc thử nghiệm "escape" permission envelope (xem AUDIT_SUMMARY).
