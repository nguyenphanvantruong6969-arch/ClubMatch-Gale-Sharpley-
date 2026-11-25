# DKL protocol — close every gap between the real portal and prototype v8 (size M, 4 lots)

> Template: `docs/phien/_GIAO_THUC_GON.md`. Reference ("the artifact"): `docs/phien/DK1_BAN_MAU_V8.html` (decisions D1–D45 in
> `claude__gracious-johnson-pnqvrg.md`, D43–D45 in `claude__dk2-cau-noi-so-nhap.md`). English. Branch `claude/dk4-noi-thang-bo-xep`
> (Truong 2026-11-25: no new branch). Base head must have CI green: `42b93af` is green (run 45646931916 attempt 2, Linux+Windows);
> later commits are docs only.
> Method of this table: 508 UI strings extracted mechanically from v8, 409 absent from the portal (sample names/club titles
> are noise), then v8's `data-act` list (45 actions) walked per role against `js/dang_ky_*.js` (read in full, 123+121+159 lines).
> **Corrects the earlier audit**: medal swap (D34: per-club `<select>` + "Đặt lại huy chương theo thứ tự xếp") and 60 s idle logout
> (`DK.henGio(60)`) DO exist. `dk_hs_clb_hop_le` already returns `link_forms, mo_ta, yeu_cau, phong`, the UI ignores them.
> **Rule for coder and checker: this table is the scope. A row not ticked with a test is not done.**

## 0. Team, push rule, CI reality
- Coder (Sonnet) + checker (Sonnet), no lead; Truong pastes the checker prompt at each MILESTONE. Full CI ≈ 20–25 min, Linux+Windows.
- **Push rule:** commit locally per lot; push only at a milestone (M1 after L1+L2, M2 after L3+L4) and for the final READY.
  DK4-UI and DKL never push in the same window. Every push cancels the run in flight; never push while a needed run is going.
  Budget: ≤ 4 full CI cycles tonight. Realistic order: L1 → L2 (M1 push) → L3 → L4 (M2 push) → CI → READY.
- Invariants 1–8 untouched. No schema/CSV/algorithm change. New API functions only in `api_dang_ky.py` (+ `i18n_errors.py` codes
  → `python tao_i18n_js.py`; new `dk_*` write functions need `nkhd_<fn>` journal labels vi+en, and PIN/token never logged).

## 1. Ownership split with DK4-UI
The DK4-UI prompt text is not in the repo (given to Truong in chat). Boundary used here, Truong to confirm:
- **DK4-UI owns look:** `style.css` tokens, step bar, 6-phase bar, card layout, spacing, gold-button placement, 1366/390 px.
- **DKL owns behaviour:** new buttons/screens/API calls, data shown, validation, timers, print layout logic.
- Overlap risk: both touch `js/dang_ky_*.js`. DKL coder `git fetch` + merge before starting each lot; keep new DOM in new helper
  functions (`DK.…`) rather than rewriting existing renderers.

## 2. v8 diff table (gap → v8 evidence → lot)
| # | Gap in real portal | v8 evidence | Lot |
|---|---|---|---|
| S1 | After submit, student sees NO Forms test links for ticked Tuyển chọn clubs (D24) | `link_forms` returned by `dk_hs_clb_hop_le`, never rendered; v8 "Làm bài thi" | L1 |
| S2 | No "Dưới sàn" chip / rule text "Không làm bài, hoặc dưới mốc điểm, thì em không được xét vào CLB đó" (D23/35) | strings in v8 | L1 |
| S3 | Club cards show only name/loại/điểm sàn; hide `mo_ta`, `yeu_cau`, `phong`, teacher (D15) | v8 cards, "Yêu cầu:", "Địa điểm" | L1 |
| S4 | No deadline shown to student; expired message lacks "Nguyện vọng em đã gửi vẫn được tính" | v8 "Đã hết hạn đăng ký…" | L1 + L4 (`dk_trang_thai` returns `han_chot` already) |
| S5 | No final review ("Xem lại và gửi") across all days; no empty-submission warning "Em chưa chọn CLB nào…"; no "Tự do = em chắc chắn có chỗ" inline warning | v8 `hsStep review` | L1 |
| S6 | Submit time shown as raw ISO ("2026-11-25 14:03"); D41 wants "Đã gửi lúc hh:mm, thứ …"; no "Xong, thoát" button | v8 | L1 |
| S7 | Rank/medal/test merged on one screen per buổi; v8 steps "Tiếp: đặt huy chương", "Tiếp: bài kiểm tra" | v8 `hsStep` | **DK4-UI** (layout); DKL only if Truong wants separate steps |
| S8 | Teacher cannot edit or delete own club while GV phase open and "chờ duyệt" (D17); no "+ Đăng ký CLB mới" list, no deadline note, no PIN-forgotten hint | v8 `gvEdit gvDelClub` | L3 |
| S9 | Teacher form: no per-step Vietnamese validation messages ("Nhập tên CLB.", "Chỉ tiêu là số nguyên từ 1.", "Chọn khối được tham gia.", link must start `https://`), room list not filtered to rooms free in that buổi | v8 strings | L3 (+ `dk_phong_danh_sach(buoi)` filter in L4) |
| A1 | No "Đóng ngay" / "Gia hạn" (+1 giờ, +1 ngày), no deadline field for HS phase (only GV phase) (D1) | `closeNow`, `extend` | L2 |
| A2 | **No score entry UI at all** in "Nhập điểm": no paste "mã⇥điểm" per club, no typing table, no "Chốt điểm" confirm (D27). Backend exists: `dk_diem_dat`, `dk_diem_dan`, `dk_diem_thieu` | `pasteScores`, `lockScores` | L2 (blocker) |
| A3 | No printable PIN slips (students, teachers); PINs only in an on-screen table shown once (D8/D13) | `slips` "Xem phiếu PIN" | L2 |
| A4 | Student list: only "Thêm vào danh sách"; no "Thay cả danh sách" with confirm; no lock after students started (D6) | v8 `hsMode`, "Học sinh đã bắt đầu…" | L2 (backend flag exists: `che_do`) |
| A5 | Rooms: no delete button / "Phòng không có CLB nào nên xoá được" (backend `dk_phong_xoa` exists) (D5) | `roomDel` | L2 |
| A6 | Admin cannot edit approved/pending club quota/room, or approve with changed quota/room (D18/D19); only Duyệt / Từ chối | v8 "Sửa CLB đã duyệt", `dk_clb_sua_sau_mo`, `dk_clb_duyet(chi_tieu, phong_id)` exist | L2 |
| A7 | D31: "Nhu cầu theo CLB" (demand per club, `dk_tien_do.theo_clb` already returned) and not-registered fold not shown; no refresh | v8 | L2 |
| A8 | Phase-1 checklist "Kiểm tra ba mục dưới đây" / "Chưa đi tiếp được: chưa có phòng, chưa có danh sách học sinh" missing; the gold phase button isn't blocked with reasons (D2 backend error shown only after click) | v8 | L2 |
| A9 | Tabs: v8 = 4 tabs `Việc bây giờ · Danh sách · Cài đặt · Thêm ▾`; portal = 3, **no "Cài đặt"**: school code (Đổi mã trường), buổi (Thêm/Xoá buổi), khối (Lưu khối) not editable after setup (D4/D36, v8 settles it) | v8 settings | L4 |
| A10 | Export: no preview before "Xuất Sổ nhập" (sheets `1. CLB`, `2. Học sinh`) (D30); no export version/counter (D3) | `stuPreview`, `gvPreview` | L4 |
| A11 | Backup/restore in the portal (D11): "Tạo bản sao lưu", "Khôi phục", "Chưa sao lưu trong 60 phút qua". Coder greps the existing app backup function; expose "Sao lưu ngay" (+ restore only if an API already exists), else record in Needs Truong, do not invent a new format | `backup`, `restore` | L4 |
| A12 | Admin lock text "Tự khoá sau 2 phút" / "Đã khoá quản lý vì không thao tác." : server lock exists (`GIAY_NGHI_QUAN_TRI`), no UI message; no admin password change | v8 | L4 |
| — | Prototype-only, OUT OF SCOPE: `reseed`, `fakeApprove/fakeRegs/fakeScores`, "Công cụ thử", "Demo nhỏ/Cả trường" (D12), "MÔ PHỎNG" watermark (DK5 uses simulated data instead) | v8 | — |
| — | Verified present (do not rebuild): D9 (`dk_dang_nhap`), D14 (`dk_gv_hai_clb_mot_buoi`), D21 (`toi_da_nv/thi` settings), D26 (demand only in `dk_tien_do`), D34 swap (`<select>` + reset), D25 60 s idle (`DK.henGio`), D38, D39 per-buổi flow, D2 conditions, D3 step back | code | — |

## 3. Lots (group by file area; all must-ship; each tick = failing test first)
- **L1 student** (`js/dang_ky_gv_hs.js` student half, small `style.css` additions) — S1–S6.
  Test `tests/test_giao_dien_dkl_hoc_sinh.py` (one Chromium page fixture): links shown after submit only for ticked Tuyển chọn;
  "Dưới sàn" text; card shows mo_ta/yeu_cau/phong; review screen lists all buổi; empty-submit warning; time format; no demand counts (D26).
- **L2 admin operations** (`js/dang_ky_quan_tri.js`, helpers in a new `js/dang_ky_quan_tri_2.js` loaded from `dang_ky.html`) — A1–A8.
  Score entry: per-club paste box + table with "Dưới sàn" chip, comma/dot decimals, missing list, "Chốt điểm" confirm.
  PIN slips: `@media print`, 8 per page, only from the just-created/reset result (hash never in DOM), "In" via `window.print()`,
  plus on-screen copy fallback (webview may block print). Test `tests/test_giao_dien_dkl_quan_tri.py`.
- **L3 teacher** (`js/dang_ky_gv_hs.js` teacher half) — S8, S9. Test `tests/test_giao_dien_dkl_giao_vien.py`.
- **L4 settings, export, backend rules** (`api_dang_ky.py`, `js/dang_ky_quan_tri_2.js`) — A9–A12, S4 data, rooms-free filter.
  New: `dk_cai_dat_doi` (school code, buổi, khối; refuse buổi/khối change after GV phase, D4), `dk_xuat_xem_truoc`, export counter
  in `dk_cai_dat`. Tests `tests/test_dkl_cai_dat.py` (API) + extend `test_giao_dien_dkl_quan_tri.py`.

## 4. Per lot, milestones, definition of done
Failing test → minimal code → lot test + ≤ 3 related (`-q --tb=line 2>&1 | tail -15`) → `ruff check .` → `kiem_nhanh.py | tail -10`
→ CHANGELOG `DKL-L<k>` + TIEN_DO row → local commit `DKL-L<k>: …`. After L2: `git fetch` + merge, push, write `MILESTONE 1 READY | head <sha>`.
After L4: same with `MILESTONE 2 READY`, then registry row (`SO_DANG_KY_33_MUC.md`), test-file count in `CLAUDE_CHI_TIET.md`, CI green on
Linux AND Windows (`failed_only` logs ≤ 60 lines), then `READY | head <sha>`. Done = every row of §2 ticked with its test name in the
branch file, or moved to "Needs Truong" with the reason. Max 2 FIX rounds per milestone, then `git revert` that lot. No PR/tag.
Test data labelled SIMULATED.

## 5. Prompts
### Coder (one Sonnet session)
```
Read CLAUDE.md, docs/phien/claude__dk4-noi-thang-bo-xep.md, docs/phien/DKL_GIAO_THUC.md, docs/phien/_GIAO_THUC_GON.md. Reply to Truong in Vietnamese. You are the DKL coder (Sonnet) on branch claude/dk4-noi-thang-bo-xep (no new branch). SCOPE = the v8 diff table in DKL_GIAO_THUC.md §2: every row is a task and anything not ticked with a passing test is not done; first open docs/phien/DK1_BAN_MAU_V8.html for each row you build and match its behaviour (strings, flow, limits), in Vietnamese. Look/tokens belong to the DK4-UI session: do not restyle, add only the CSS your new elements need; `git fetch` + merge before each lot because both sessions touch js/dang_ky_*.js. Build lots L1→L4 in order, failing test first, commit locally per lot, push ONLY at the two milestones (after L2 write `MILESTONE 1 READY | head <sha>`; after L4 `MILESTONE 2 READY`), never push while a CI run you need is in flight, no doc-only pushes. After L4: registry row, test count, CI green on Linux and Windows, then `READY | head <sha>`. Respect invariants 1–8 and §0. No subagents, no PR. If the usage limit is near, update "Current state" in the branch file and stop.
```
### Checker (Truong pastes at each MILESTONE)
```
Read CLAUDE.md, docs/phien/DKL_GIAO_THUC.md and the milestone's commits. Reply to Truong in Vietnamese. You are the DKL checker (Sonnet): report only, never fix. For EVERY row of §2 assigned to the milestone's lots, open the v8 prototype behaviour and the real code and mark PASS/FAIL with the test name; unticked rows = FAIL. Also verify: score entry accepts comma and dot, "Dưới sàn" rule; PIN slips never show hash/token and appear only for just-created/reset PINs; Forms links only for ticked Tuyển chọn clubs; students never see demand (D26); invariant 2 (medal override stays, priority key never reads rank); no schema/CSV/algorithm change; `i18n` regenerated if `i18n_errors.py` changed; new write functions have `nkhd_` labels; CHANGELOG/TIEN_DO rows; `ruff` and `kiem_nhanh.py`; CI for the head green on Linux AND Windows (never PASS with CI pending). Write `PASS` or `FIX <≤10 lines>` in docs/phien/DKL_GIAO_THUC__checker.md, push once, tell Truong in one line.
```
