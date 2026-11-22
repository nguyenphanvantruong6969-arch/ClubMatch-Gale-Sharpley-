# MT2 protocol (size L: lead + coder + checker)

> Work source: `docs/phien/claude__mt2-chia-clb-theo-loai.md`. Team size, lots, token budget:
> `docs/phien/_GIAO_THUC_GON.md` (L: checker every lot). Mechanics (message formats, quiet test command, silence):
> `docs/phien/XP1_GIAO_THUC.md` §3–§4, §6 with "XP1" = "MT2", "L1–L5" = "L1–L4". Where they differ, THIS file wins.

## 0. Decisions already made (do not ask Truong again)
- Truong (2026-11-22): the type switch must combine with Điểm quyết tâm AND preference-order ranking; can be turned
  OFF; lives in Quản lý → "Danh sách CLB"; new item MT2, new branch. No new library (anything else → "Needs Truong").
- Exactly 3 sessions (lead, coder, checker), no Agent tool. Lead = Sonnet is fine (Opus only if the Design section
  of the branch file needs a real design change). Lead edits the branch file only; never product code.

## 1. Lots
L1 config+switch → L2 pipeline → L3 UI → L4 docs (optional). Each lot's spec = its block in the branch file.
Before each lot: `git fetch origin claude/mt1-bang-loai-clb && git merge --no-edit FETCH_HEAD` if not merged to main.
New i18n keys `mt2_`; audit labels `nkhd_<function>`; after `i18n_errors.py`: `python tao_i18n_js.py`.

## 2. Checker focus (every lot)
Invariants 1 (byte-identical default + legacy `fa_daa`, 3 datasets × 20 seeds), 2 (no rank/outcome in any key),
3 (STB lottery), 4 (`run_history` appends), 5 (pipeline order, one transaction), 6, 7 (CSV/Sổ nhập columns
unchanged), 8 (substitutability evidence for modes chi_xep+types and chia_100+types); teacher role blocked from
the new write paths; OFF → ON → OFF keeps `clubs.loai`; workspace with a session lacking a TU_DO club gets a
clear blocking error, not a crash.

## 3. Prompts
**Lead** (first session; Truong pastes it):
```
You are LEAD for MT2 on branch claude/mt2-chia-clb-theo-loai. Read CLAUDE.md, docs/phien/_GIAO_THUC_GON.md,
docs/phien/MT2_GIAO_THUC.md and docs/phien/claude__mt2-chia-clb-theo-loai.md and follow them. Add Status,
Sessions and "Needs Truong" to the branch file, push, then create CODER and CHECKER sessions (Sonnet,
permission_mode auto, same repo, source_revision claude/mt2-chia-clb-theo-loai) and run L1 to L4. Never write
product code; never ask Truong; blocked items go under "Needs Truong".
```
**Coder:**
```
You are CODER for MT2 on branch claude/mt2-chia-clb-theo-loai. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/MT2_GIAO_THUC.md and the branch file. Set up the venv, then wait for "GO L<n>" / "FIX". Test first,
minimal code, related tests only, kiem_nhanh.py 7/7, soat-ma, CHANGELOG + TIEN_DO row MT2-L<n>, commit, push,
report "CODER DONE L<n> | base <sha> head <sha>".
```
**Checker:**
```
You are CHECKER for MT2 on branch claude/mt2-chia-clb-theo-loai. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/MT2_GIAO_THUC.md and the branch file. Wait for "REVIEW L<n> <base>..<head>", review per §2, write the
verdict to docs/phien/claude__mt2-chia-clb-theo-loai__checker.md only. Never edit product code or tests.
```
