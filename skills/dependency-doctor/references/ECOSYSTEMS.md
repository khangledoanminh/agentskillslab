# Ecosystem Specifics

## pip (requirements.txt / pyproject.toml)

Manifest: `requirements.txt`, `setup.py`, `pyproject.toml`. Lockfile: `requirements-lock.txt` (không bắt buộc). Cài `uv pip compile` để có lockfile. Check outdated: parse version specifiers so registry khi online; offline dùng heuristic pattern (year-old versions).

## npm (package.json)

Manifest: `package.json` + `package-lock.json`. Lockfile BẮT BUỘC có để audit đúng version. Check: `npm outdated` (online) hoặc parse lockfile trực tiếp. Workspace: đọc `workspaces` field.

## cargo (Rust)

Manifest: `Cargo.toml` + `Cargo.lock`. Check: parse `Cargo.lock`精确 version, so embedded CVE list. `cargo tree -d` tìm duplicate.

## go (go.mod)

Manifest: `go.mod` + `go.sum`. Check: parse `go.mod` require blocks. `go mod tidy` check consistency.

## Nguyên tắc chung

Lockfile là source of truth về version install thật; manifest chỉ là intent.

