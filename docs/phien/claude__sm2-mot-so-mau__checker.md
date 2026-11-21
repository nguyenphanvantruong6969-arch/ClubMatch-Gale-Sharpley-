# SM2 checker verdict — `origin/claude/ux2-phan-hoi-nut..origin/claude/sm2-mot-so-mau` (head cd00b62)

**Verdict (round 1, ff08a62): 1 BUG (moderate, vocabulary). Round 2 recheck of 3a7c44f: see bottom → NO BUGS.**

## Bugs
1. **Column dictionary hard-codes school vocabulary → wrong in workspaces with custom labels.**
   `so_nhap._ghi_tu_dien_cot` / `TU_DIEN_COT` write literal "1. CLB", "2. Học sinh", "Tên CLB", "Mã CLB", "Mã HS",
   "học sinh", "CLB Tự do…" into the Hướng dẫn sheet, ignoring `cfg` labels. Repro:
   `so_nhap.ghi_so_nhap(p, [], [], cfg=chuan_hoa(<company labels: slot=Dự án, person=Nhân viên>), luon_co_cot_w=True, co_lop=True, day_du=True)`
   → sheets are `1. Dự án / 2. Nhân viên / Hướng dẫn / Giữ chỗ`, but the new dictionary's "Trang" column says
   `1. CLB` / `2. Học sinh` (sheets that do not exist in that file) and the rows describe "Tên CLB", "Mã HS", "học sinh".
   Before SM2 the company sample had no dictionary, so this is new, and `tao_so_nhap_mau` now sends it to every vocabulary.
   (The older Hướng dẫn text already leaks "CLB"/"Mã HS" in a few lines — pre-existing, not counted; no test covers it.)
   Fix options: build the "Trang"/"Cột" cells from `cfg` labels (sheet names + header names the file really has),
   or, minimal: emit the dictionary only when the sheet names are the default school ones, else skip it (and test both).
   Add a test with a custom-label workspace (e.g. CONG_TY in `tests/test_ws_so_nhap.py`) asserting no "1. CLB"/"2. Học sinh" in the dictionary.

## Passed (evidence)
- Plan boxes all ticked and match the diff. Related tests run by me: 203 passed (`test_sm2_*`, `test_so_nhap`, `test_so_mau_day_du`,
  `test_a13_8_so_mau`, `test_so_mau_co_cot_quyet_tam`, `test_fg2_xem_truoc_fa`, `test_ux1_l5_backend`, `test_i18n_sync`,
  `test_van_phong_tu_nhien`, `test_a13_12_tai_lieu`, `test_ws_so_nhap`). Chromium UI file not re-run locally (CI).
- Invariants 1/6/7: no algorithm, CSV, schema or API return-shape change. `ghi_so_nhap` with default args is byte-identical to base
  (sha256 of all zip parts except docProps equal: c530d737…2619 on both commits). `tao_so_nhap_mau` signature unchanged;
  `kieu="huy_chuong"` still forces the medal label (test `test_kieu_huy_chuong_van_ep_nhan_huy_chuong`).
- L1: FA import of `SO_NHAP_MAU_DAY_DU.xlsx` and `SO_NHAP_FA_MAU_120HS.xlsx` → no `wharton_chua_dung_het`; non-FA still warns (regression test).
  Medal errors still reported: preview (`xem_truoc_so_nhap`) on a workbook with three 60s gives `fa_huy_chuong_trung_gia_tri` and `fa_huy_chuong_clb_tu_do`.
  The import itself on that workbook now returns no warnings; on base it returned `wharton_chua_dung_het` + `wharton_vuot_ngan_sach`
  (a quỹ budget check that is meaningless for 60/30/10 medals) — dropping both in FA is justified; medal validity is the preview's job.
- Non-FA workspace with empty FA/Giờ/Giữ chỗ cells imports with only the two pre-existing warnings (`test_so_mau_dien_tay_…`).
- vi + en: `import_hint` updated in both; `test_i18n_sync` green. Wrong-mode prompt (`ux1bSsTaiSoMau`) still uses `ux1a_btn_so_mau_huy_chuong`.
- One-buổi school: header/`Buổi` handling untouched by `day_du` (only FA/Giờ columns + Giữ chỗ + dictionary added); no new warning path.

## Coder deviations — judged
| Deviation | Verdict |
|---|---|
| Kept i18n key `ux1a_btn_so_mau_huy_chuong` | Justified: `js/18_cai_dat.js` still uses it for the kept wrong-mode prompt; removing it would break that prompt. |
| Regenerated `mau_csv/SO_NHAP_CLB.xlsx` (+`day_du=True` in `tao_mau_trong`) | Justified: T1a requires the main sample equal the app sample; test green. |
| "em" → "học sinh" in the dictionary (4 cells in `SO_NHAP_MAU_DAY_DU.xlsx`) | Justified: the Hướng dẫn-sheet wording rule (T1a/G3) bans "em"; text-only change. (Same dictionary still hard-codes "học sinh" → see Bug 1.) |
| `BAM_SO_MAU_MAC_DINH` hash updated | Justified, not weakened: the sample structure changed on purpose and the comment says why. Limitation: a hash only proves "changed as now", so default-ness is guarded by `test_ghi_so_nhap_mac_dinh_khong_doi` + my sha256 check above. |
| `test_fg2…::test_so_mau_fa_huong_dan…` reads Hướng dẫn by name | Justified, stronger (was "last sheet", now Giữ chỗ is last). |
| `test_ws_so_nhap.py` (2), `test_ws_so_nhap_giao_dien.py` (2), `test_so_nhap.py` | Justified: expected sheet/column lists now include Giữ chỗ / FA / Giờ columns; assertions still exact. |
| `test_giao_dien_ux1_nhap_so.py` "hai nút" → "một nút" | Justified: replaces a test of a removed feature with a stricter one (one call, ✓, Giữ chỗ, dictionary). |

## Nits (no action required)
- `taiSoNhapMau("huy_chuong")` from the wrong-mode prompt now shows the ✓ (`nutDaXong`) on `#btnTaiSoMau` and disables it while the prompt button was clicked; harmless.
- FA import no longer says anything about invalid medals itself; the preview does (unchanged from base for medals).

## Needs Truong
- None blocking. Decide whether Bug 1 is fixed now (coder `FIX`) or accepted (dictionary is school-vocabulary only).

## Recheck of FIX1 (commit 3a7c44f) — NO BUGS
- Bug 1 fixed with the minimal option: `ghi_so_nhap` writes `_ghi_tu_dien_cot` only when sheet names, club headers, student head and "Lớp" label equal the default school ones. Company labels → full structure + Giữ chỗ, no dictionary, no "1. CLB"/"2. Học sinh" (new test `test_tu_dien_khong_chi_toi_sheet_khong_co_o_workspace_nhan_rieng`).
- Default school sample unchanged (`test_tu_dien_van_co_o_truong_hoc_mac_dinh`, fg2 hash, T1a). `du_lieu_test` script calls `_ghi_tu_dien_cot` directly, unaffected.
- Ran: 148 passed (`test_sm2_*`, `test_so_mau_day_du`, `test_fg2_xem_truoc_fa`, `test_so_nhap`, `test_ws_so_nhap`, `test_van_phong_tu_nhien`).
- Nit (no action): the guard does not look at the score label, so a workspace that renames only "Điểm" (not slot/person/group) still gets the dictionary with "Điểm k". Harmless wording mismatch.
