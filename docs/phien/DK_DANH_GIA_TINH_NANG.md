# DK feature audit D1–D45 (read-only, static)

> Branch `claude/dk4-noi-thang-bo-xep`, head `42b93af`. English. Method: code search (grep by function name) of
> `api_dang_ky.py`, `dang_ky_schema.py`, `dang_ky_sang_xep.py`, `js/dang_ky_*.js`. **Nothing was run in a browser**;
> "partial/missing" = no matching code found, so confirm by hand before building. Decisions: `claude__gracious-johnson-pnqvrg.md`.

## Result by item
| Item | Status | Evidence |
|---|---|---|
| D1 deadline per phase, auto-close by clock | done (backend) | `dk_dat_han`, phase check reads `han_chot` (docstring: expired phase closes itself) |
| D1 "Đóng ngay", "Gia hạn" buttons | **not found** in UI | no string match in `js/dang_ky_quan_tri.js`; `dk_dat_han` can do it, check UI |
| D2 open-to-students conditions | done | `_dk_kiem_dieu_kien_mo_hs` (docstring D2) |
| D3 step back, logged | done | `dk_chuyen_giai_doan`, "Lùi về giai đoạn" button |
| D3 each export gets a version | **missing** | `dk_xuat_so_nhap` has no version/counter |
| D4 sessions and grades editable | partial | `dk_khoi_tao(buoi, khoi)` sets at setup; no later edit function found |
| D5 rooms (unique, >0, in-use not deletable) | done | `dk_phong_luu/xoa`, `dk_phong_dang_dung` |
| D6 add vs replace student list | done | `dk_hs_nap_danh_sach(che_do)` |
| D7 grade from class name | done | `_dk_buoi_khoi`, `dk_hs_nap_danh_sach` |
| D8 student PIN auto + **printable slips** | partial | PIN shown once on create/reset; only a generic `@media print` in `style.css`, no slip layout |
| D9 unlisted student refused | likely done | `dk_dang_nhap` (confirm with a test) |
| D10 admin lock after idle | done | `GIAY_NGHI_QUAN_TRI = 120` |
| D11 backup/restore JSON | done (allocator side) | `dk_chot_va_xep` backs up first; no portal-level restore screen found |
| D12 mock switch Demo/Cả trường | **not found** | by design? (prototype-only); confirm |
| D13 teachers: self sign-up + admin-created, slips | partial | `dk_gv_tu_dang_ky`, `dk_gv_tao_hang_loat`, `dk_gv_dat_lai_pin`; slips = same gap as D8 |
| D14 teacher never two clubs same session | **not confirmed** | no matching rule in `dk_clb_luu` search |
| D15/D16 club fields, 2×/week = 2 clubs | done | `dk_clb_luu`, `LOAI_CLB` |
| D17 teacher edits only while GV open and "chờ duyệt" | done | `dk_clb_luu` docstring |
| D18/D19 approve/reject, raise quota after open | done | `dk_clb_duyet`, `dk_clb_sua_sau_mo` |
| D20/D21 student login, own grade, ≤10 per session | done | `dk_hs_clb_hop_le`, `TOI_DA_NV_BUOI`, now settable via `dk_dat_gioi_han` |
| D22 tap add / ↑↓ / ✕ | done (UI) | `dang_ky_gv_hs.js`; not run |
| D23/D35/D44 tests, ≤5 per session, below floor | done | `TOI_DA_THI_BUOI`; `dk_hs_luu`; "Dưới sàn" chip text **not found** in UI |
| D24 receipt with Forms links | **dropped** by D41 | Forms link is stored per club (`link_forms`), receipt page not built |
| D25 edit until deadline; auto-logout 30 s after submit, 60 s idle | partial | 30 s after submit exists; **60 s idle not found** |
| D26 students never see demand | likely done | demand only in admin `dk_tien_do` |
| D27 scores paste + table + missing list | done | `dk_diem_dat`, `dk_diem_dan`, `dk_diem_thieu`; "Chốt điểm" button **not found** |
| D28/D29 defaults | n/a | allocator rules, covered by DK2/DK4 tests |
| D30 export preview | partial | `dk_xuat_ban_mau`, `dk_xuat_so_nhap` exist; preview screen not checked |
| D31 live admin views | partial | `dk_tien_do` (by class, demand per club) used at `dang_ky_quan_tri.js:64`; "not-registered fold" not found; no auto refresh |
| D32/D33 | not in this audit | not listed in handoff text |
| D34 medal mode: default 60/30/10, student can override | partial | `HUY_CHUONG`, `huy_chuong` stored and sent; **swap UI not found** (invariant 2 exception requires it) |
| D36 admin IA "Việc bây giờ" | done (3 tabs) | spec said 4 tabs; code has 3 ("Việc bây giờ · Danh sách · Thêm") — confirm intent |
| D37 design laws | not audited | needs a visual review |
| D38 "← Về trang chọn vai trò" | done | `DK.veTrangDau` |
| D39 per-day student flow | done (UI) | `dang_ky_gv_hs.js` per-buổi steps; not run |
| D40 chip overflow, D41 receipt code dropped, D43–D45 | done | per DK2/DK3 notes and tests |

## Gaps ranked (value for a real school day, then cost)
1. **D34 medal swap UI** — only gap that touches an invariant (2, exception D2: every student must be able to override).
2. **D8/D13 PIN slips print** — hard blocker for the real day (800 PINs on paper).
3. **D25 60 s idle logout** — shared kiosks, privacy.
4. **D1 "Đóng ngay"/"Gia hạn"** and **D27 "Chốt điểm"** buttons — small, check first whether they exist under other labels.
5. **D31** not-registered fold + refresh; **D3** export version; **D14** teacher conflict rule; **D4** edit sessions.

Proposed lot (size M): items 1–4. Items 5 after DK5. D12 / D24 stay out unless Truong wants them.
