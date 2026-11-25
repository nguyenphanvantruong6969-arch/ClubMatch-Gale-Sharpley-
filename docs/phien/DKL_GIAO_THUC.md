# DKL protocol — gap lot from the D1–D45 audit (size M)

> Template: `docs/phien/_GIAO_THUC_GON.md`. Audit: `docs/phien/DK_DANH_GIA_TINH_NANG.md`. English.
> Branch: `claude/dk4-noi-thang-bo-xep` (Truong 2026-11-25: work on this branch, no new branch). Registration-portal
> UI only: no algorithm, schema, CSV-contract change. Invariants 1–8 untouched (2: medal override is registration layer).

## 0. Team (size M)
coder (Sonnet) + checker (Sonnet), no lead. Coder runs the CI gate. Checker starts when coder writes
`MILESTONE <k> READY` in the branch file (Truong pastes the checker prompt).

## 1. Lots (4 max; L1–L3 must-ship, L4 optional)
| Lot | Audit | Change | Files (by function) | Failing test first |
|---|---|---|---|---|
| L1 | D34 | Student can swap medal placement: path A swap UI (tap two cards in a session to exchange Vàng/Bạc/Đồng); defaults stay 60/30/10 split. Send as `huy_chuong` in `dk_hs_luu` (already accepted). | `js/dang_ky_gv_hs.js` (ranking step), `style.css` | `tests/test_giao_dien_dkl_huy_chuong.py`: swap, submit, `dk_nguyen_vong.huy_chuong` changed; reload shows swap |
| L2 | D8, D13 | Printable PIN slips: admin view "In phiếu PIN" for students (per class, 8 slips/page) and teachers. PIN shown only right after create/reset (stored hashed), so print from that result list. `@media print` layout, no token/password in DOM. | `js/dang_ky_quan_tri.js`, `style.css` | `tests/test_giao_dien_dkl_phieu_pin.py`: after load list, print view has N slips; none after reload; no hash in HTML |
| L3 | D25, D1, D27 | (a) student auto-logout after 60 s idle (reset on any input); (b) admin buttons "Đóng ngay", "Gia hạn +30 phút" via `dk_dat_han`/`dk_chuyen_giai_doan`; (c) "Chốt điểm" confirm button when `dk_diem_thieu` is empty. First grep whether they exist under other labels; skip any already present. | `js/dang_ky_nen.js`, `js/dang_ky_gv_hs.js`, `js/dang_ky_quan_tri.js` | `tests/test_giao_dien_dkl_nho.py` (fake clock via page.clock) |
| L4 (optional) | D31 | "Chưa đăng ký" fold list + 30 s refresh in the progress view. | `api_dang_ky.py` `dk_tien_do`, `js/dang_ky_quan_tri.js` | extend L3 test file |

Out of scope (after DK5): D3 export version, D14 teacher/session conflict, D4 edit sessions, D12, D24.

## 2. Per lot (coder)
Failing test → minimal code → lot test + ≤ 3 related (`-q --tb=line 2>&1 | tail -15`) → `ruff check .` →
`.claude/skills/soat-ma/scripts/kiem_nhanh.py | tail -10` → i18n: new user strings via `i18n_errors.py` only if they are
error codes; UI text per existing `dang_ky_*.js` pattern, run `python tao_i18n_js.py` if `i18n_errors.py` changed →
CHANGELOG `DKL-L<k>` + TIEN_DO row → commit `DKL-L<k>: …` → push. Never rebase/force-push, no PR.
Milestones: M1 after L1+L2 (checker round), M2 after L3 (+L4). Then: registry row, test-file count in
`CLAUDE_CHI_TIET.md`, CI green on Linux AND Windows (`failed_only` logs ≤ 60 lines), write `READY | head <sha>`.

## 3. Rules to respect
- Push only after CLAUDE.md rule 8 (`soat-ma`). Test data is SIMULATED; label it.
- Do not edit files DK4-UI (Truong's other session) is changing without a fresh `git fetch` + merge first; commit small.
- Max 2 FIX rounds per milestone, then "Needs Truong" and `git revert` that lot.

## 4. Prompts
### Coder (paste as one session)
```
Read CLAUDE.md, docs/phien/claude__dk4-noi-thang-bo-xep.md, docs/phien/DKL_GIAO_THUC.md, docs/phien/_GIAO_THUC_GON.md and the audit docs/phien/DK_DANH_GIA_TINH_NANG.md. Reply to Truong in Vietnamese. You are the DKL coder (Sonnet) on branch claude/dk4-noi-thang-bo-xep (no new branch; `git fetch` and merge before each push, DK4-UI is being built in parallel by another session). Build lots L1→L3 (L4 if budget allows) from section 1, per section 2, failing test first. Respect invariants 1–8 and section 3. After L1+L2 write `MILESTONE 1 READY | head <sha>` in the branch file and continue to L3 only after the checker's PASS/FIX; after L3(+L4) write `MILESTONE 2 READY`, then registry row, test count, CI green on Linux and Windows, and `READY | head <sha>`. No subagents, no PR. Stop and update "Current state" if the usage limit is near.
```
### Checker (Truong pastes at each MILESTONE)
```
Read CLAUDE.md, docs/phien/DKL_GIAO_THUC.md and the milestone's commits (git log, git diff by file). Reply to Truong in Vietnamese. You are the DKL checker (Sonnet): report only, never fix. Verify per lot: the test fails without the change and passes with it; invariant 2 (every student can override medal placement, priority key still reads stored medals, never rank); PIN never stored or rendered in clear after reload, no hash/token in the print DOM; idle logout resets on input; no change to CSV contract, schema or algorithm; CHANGELOG and TIEN_DO rows exist; `ruff check .` and `kiem_nhanh.py` pass; CI for the head is green on Linux AND Windows (never PASS with CI pending). Write `PASS` or `FIX <≤10 lines>` in docs/phien/DKL_GIAO_THUC__checker.md, push, and tell Truong in one line.
```
