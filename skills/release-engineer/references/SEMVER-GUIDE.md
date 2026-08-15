# Semver Guide (2.0.0)

Format: MAJOR.MINOR.PATCH.

- **MAJOR** bump: breaking change API/hành vi (user code hiện tại break)
- **MINOR** bump: feature mới backward-compatible
- **PATCH** bump: bugfix backward-compatible

Nguyên tắc release engineer: đọc diff từ tag trước → phân loại breaking/non-breaking → đề xuất bump level + giải thích. Không tự quyết định MAJOR bump một mình — luôn đưa đề xuất kèm rationale cho người quyết định.
Pre-release: `-alpha.1`, `-beta.2` theo semver spec.

