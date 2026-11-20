# Branch handoff: claude/mt1-bo-muc-tieu

> Read CLAUDE.md, then this file, then `docs/phien/MT1_GIAO_THUC.md`. English. Cap 150 lines.
> Evidence: `docs/fable/08_MT0_MEMO.md` (simulated). UI baseline: UX1A-L2b in `CHANGELOG.md` (Settings =
> one question, cards, save instantly, Undo) — component `ux1aTaoThe` in `js/18_cai_dat.js`.

## Feature / goal
New item **MT** (outside the registry; Truong approved 2026-11-20; parents C3/A1). Lot **MT1 = goal cards**.
The school answers ONE new question in Settings, "Khi một CLB đông người, trường ưu tiên điều gì?", by clicking
one of 3 cards. The software sets the existing rules (and, for card 3, suggested reserved seats), shows the
effect, and after a run shows one result line: goal met or not, how many helped, how many gave way. Mostly an
easier way to drive settings that already exist; new parts = seat suggestion + estimate + result line. The core
algorithm does not change. Later lots (not here): MT2 publish goal before registration, MT3 "why not met", MT5
parent report.

## Status
Status: PLANNED 2026-11-20 (Opus, revision 2: UI-first, 3 cards). Base: `origin/claude/trusting-bohr-wg0l4n`.

## The 3 goal cards (fixed; wording may be polished)
| id | Card title (vi) | One sentence on the card (≤ 90 chars) | Rules set | Club data |
|---|---|---|---|---|
| `nang_luc` (default) | Theo năng lực | CLB có thi chọn theo điểm; CLB không thi bốc thăm công bằng. | default rules (`priority=score, tier_mode=reserve, score_scope=per_slot, tiers=[]`) | unchanged (seats from the imported data stay) |
| `co_hoi` | Cơ hội như nhau | Mọi em có cơ hội như nhau: bốc thăm, không xét điểm thi. | `priority=tier, tiers=[]` (engine: strict ⇒ lottery only, reserves skipped) | unchanged |
| `danh_cho` | Dành chỗ cho một nhóm | Giữ một số chỗ ở mỗi CLB cho một nhóm (vd. khối 10, hoàn cảnh khó khăn). | `priority=score, tier_mode=reserve` | per club `reserve_group = group`, `reserve_capacity = ceil(group share × capacity)` |

- Cards never touch `wharton` / `fa_daa`: those belong to the existing first question (Chỉ xếp thứ tự / Chia 100
  điểm / Huy chương). Conflicts: with "Huy chương", `co_hoi` is disabled with one line of reason (medal mode needs
  scores). With "Chia 100 điểm", `co_hoi` shows one line: "Điểm chia không được dùng với mục tiêu này."
- `danh_cho` group: the student list's group labels. One label ⇒ chosen automatically (0 extra clicks). Several ⇒
  inline pills under the card (1 click). None ⇒ card disabled: "Sổ nhập chưa có cột nhóm."
- Rules edited by hand in "Nâng cao" ⇒ no card highlighted, one grey line "Đang dùng cài đặt riêng · Về mục tiêu
  mẫu" (link re-applies the last card). No 4th card.
- Why 3 not 6 (decision, rev. 2): "năng khiếu" = `nang_luc` (which clubs test is data, not rules); "đam mê" = the
  existing "Huy chương" answer; "hoà nhập" and "khối đầu cấp" = same mechanism with a different group.

## UI contract (MUST; checker tests each line)
1. **Place:** inside the existing Settings panel `#ux1aCaiDat`, directly under the first question, built with the
   SAME component `ux1aTaoThe` (same card look, same spacing, same toast, same error-under-card). It replaces the
   current "Cách xét khi đông" line; "Thay đổi…" (opens Nâng cao) moves under the new question. The workspace
   wizard step 3 shows the same question with the same component. No new page, tab, dialog or modal.
2. **Clicks:** open Settings → goal applied = **1 click** (`nang_luc`, `co_hoi`, `danh_cho` with one group),
   **2 clicks** (`danh_cho`, several groups). Saved instantly + toast "Đã chuyển sang … · Hoàn tác" 10 s (Undo
   restores rules AND club seats exactly). No "Save", no "Are you sure", no "Preview" button.
3. **Effect shown without clicking:** after a card is chosen, ONE line under the cards:
   - before any official run: what will happen in words (from `tieu_chi.mo_ta_tieu_chi`);
   - after an official run: estimate on current data, e.g. "Ước tính so với lần xếp gần nhất: 23 em được chỗ tốt hơn,
     26 em xuống nguyện vọng sau." (in-memory, same locked lottery, writes NOTHING);
   - `danh_cho`: plus "Giữ 6/40 chỗ ở Robotics, … · Xem từng CLB" (collapsed `<details>`, no extra page).
   - Warnings, max ONE line each, amber like GT4-L7: token seats (any club 1–2 seats), no gap found, medal mode
     estimate unavailable.
4. **Result line:** Results tab, existing "Chi tiết" card, ONE line + `<details>`: "Mục tiêu: Dành chỗ cho khối 10 —
   đạt ở 5/5 CLB được chọn nhiều nhất · 23 em được giúp · 26 em nhường chỗ." Counts 1–4 shown as "dưới 5".
   0 clicks to see it.
5. **Words:** plain Vietnamese (+ English); no internal ids, no "dự trữ", "STB", "Wharton", "tier"; passes `chu_cam`.
   Same vocabulary everywhere ("giữ chỗ", "bốc thăm", "nhường chỗ").
6. **Look:** only existing CSS tokens and classes (`.gt-ui`, card classes of `ux1aTaoThe`); text ≥ 14 px, targets
   ≥ 36 px, contrast ≥ 4.5:1, focus ring 3 px; works at 1280 and 1024 px; keyboard: Tab to card, Enter selects.
7. **Roles:** teacher never sees the question; backend refuses teacher calls.

## Plan (lead ticks after checker NO BUGS)
- [ ] **L1 Catalogue (pure)** — new `muc_tieu.py`: `BO_MUC_TIEU` (3 entries: id, vi/en title, sentence, rules
  patch, club action), `rules_cua_muc_tieu(id, rules)`, `nhan_dien_muc_tieu(rules, clubs)` → id or `tuy_chinh`,
  `de_xuat_cho_giu(students, clubs, nhom)` → per club seats `ceil(share × capacity)` capped at capacity, plus
  warnings (`it_qua` if any 1–2). Tests `tests/test_mt1_muc_tieu.py`: patches pass `cau_hinh_ws._chuan_hoa`; only
  `LUAT_XEP_MAC_DINH` keys, never `wharton`/`fa_daa`; default config ⇒ `nang_luc`; `nang_luc` patch == default rules;
  `co_hoi` assignment == pure lottery order on simulated data (if false → STOP, "Needs Truong"); seat formula on a
  hand-checked 10-student case; share read from students only (invariant 2).
- [ ] **L2 API** — `api_muc_tieu.py` mixin: `get_muc_tieu()` (cards, current id, groups found, disabled reasons),
  `chon_muc_tieu(id, nhom=None)` (rules via the `update_workspace_config` path + club seats, ONE transaction,
  backup first; stores top-level config `muc_tieu = {id, nhom}` — not in `rules`, so never in `run_history.luat_xep`
  or fingerprints; returns `hoan_tac` = previous rules + seats), `hoan_tac_muc_tieu(hoan_tac)`. Admin only
  (`phan_quyen.QUYEN`, `nkhd_` labels). Codes `mt_*` at end of `i18n_errors.py` → `python tao_i18n_js.py`.
  Tests `tests/test_mt1_api.py`: roles, unknown id, group missing, medal conflict, Undo exact (rules + every club),
  re-apply idempotent, manual edit ⇒ `tuy_chinh`, config without `muc_tieu` exactly as today.
- [ ] **L3 Estimate + result (read-only)** — `uoc_tinh_muc_tieu(id, nhom)` (in-memory solve with the locked
  lottery vs the last official run; none ⇒ words only; medal mode ⇒ `mt_uoc_tinh_fa`) and
  `bao_cao_muc_tieu(run_id)` (met/not in the 5 most-chosen clubs, helped, gave way, guardrails: first choice %,
  unmatched; counts 1–4 ⇒ "dưới 5"). Tests `tests/test_mt1_uoc_tinh.py`: hand-checked case, zero DB writes (compare
  table checksums before/after), suppression, multi-session, trial runs.
- [ ] **L4 UI** — per UI contract 1–7: `js/19_muc_tieu.js` (new, reuses `ux1aTaoThe`), hooks in `js/18_cai_dat.js`
  and `js/03_ket_qua.js`, `index.html`, keys `mt1_*` in `i18n.js`. Tests `tests/test_giao_dien_mt1.py` (Chromium):
  click count per card (1/2), Undo restores, estimate line appears without click, warnings, result line, teacher
  hidden, 1280/1024 px, keyboard, contrast/size. Screenshots before/after in `docs/phien/anh_mt1/`.
- [ ] **L5 Docs + final review** — `HUONG_DAN_SU_DUNG.md` section "Chọn mục tiêu" (≤ 1 screen, plain words),
  `CLAUDE_CHI_TIET.md` code map, `CHANGELOG.md`, `TIEN_DO.md`; protocol §5 review.

## Acceptance (whole lot)
- Invariant 1: no `muc_tieu` key, and `nang_luc` applied, ⇒ `kiem_nhanh.py --so-seed 20` 7/7 incl. `trung_khit`.
- Invariants 2, 4, 5, 6, 7, 8 untouched; no new library; no new table/column (config JSON key only).
- UI contract 1–7 each covered by a test.

## Decisions and gotchas
- Presets live in code (`muc_tieu.py`), same for every school, versioned with the app.
- Seat formula = MT0 F1/F2 (formula 20/20 vs fixed number 13–14/20, simulated). Token-seat warning = MT0 F4.
- Estimate must never write `run_history` (do NOT call `run_thu` on each click: it appends a row).
- All numbers in tests/docs are SIMULATED. No report commentary for the student's science report.

## Current state
- Done: plan rev. 2 + protocol. Nothing coded.
- Next: lead runs protocol §3 from L1.

## Needs Truong
- (empty)

## Sessions
| Role | Session id | Started |
|---|---|---|

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-20 | Opus | MT0 research, 6 presets, plan + protocol | on `claude/trusting-bohr-wg0l4n` |
| 2026-11-20 | Opus | Plan rev. 2: UI-first, 3 cards, click budget, UI contract | Truong: "đồng bộ, không phức tạp, tối giản thao tác" |
