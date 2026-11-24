# Branch handoff: claude/dc1-kiem-doc-lap

> Planner: Opus, 2026-11-24. Size **S** (one Sonnet coder). Protocol: `docs/phien/DC1_GIAO_THUC.md`.
> Truong chose option **B** (conservation checks only). Option C (two-pool stability check) is parked; open it
> only if the judges ask for an independent priority check.

Status: DONE 385b80a CI pending (FIX2 after checker report) 2026-11-24

**Tóm tắt (tiếng Việt):** Đã làm L1–L4: script `du_lieu_test/kiem_doc_lap/kiem_doc_lap.py` (chỉ thư viện chuẩn + openpyxl) đối chiếu Sổ nhập với bộ CSV xuất, in bảng K0–K7 và ghi `dau_vao_ket_qua.csv`;
19 test (đột biến từng phép kiểm, cô lập import, ba bộ hợp lệ đều PASS); README và hai mục tài liệu giải trình. Không đổi mã sản phẩm, không đổi hợp đồng CSV.
Không làm: kiểm luật ưu tiên / ổn định, nhiều buổi (thoát mã 2), sổ huy chương.
Truong thử: (1) nạp `SO_NHAP_TEST.xlsx` ở không gian mặc định (tắt điểm quyết tâm), chạy xếp, xuất bộ CSV; (2) chạy lệnh ở `HUONG_DAN_CHAY.md` mục 10;
(3) đọc bảng K0–K7 và mở `dau_vao_ket_qua.csv`, đối chiếu HS001–HS003 với `CA_MAU.md`.

## Feature / goal
DC1: an INDEPENDENT verification script for judges and the school. It reads only the Sổ nhập (.xlsx) and the
default export set (`export_csv`: `ket_qua_phan_bo.csv`, `<goc>_theo_club/`, `<goc>_tong_hop.csv`), imports only
the Python standard library and openpyxl (no repo module), prints a PASS/FAIL table and writes
`dau_vao_ket_qua.csv` (one row per student: preferences, scores, result, rank received). It answers the
feedback "đối chiếu được đầu vào với kết quả". It does NOT check priority rules / stability (see Decisions).

## Findings from code (planner verified, 2026-11-24)
- `_du_lieu_xuat` (api_xuat.py) main file columns, BY POSITION (headers are workspace labels, e.g. `{person_l}`):
  one session = 8 cols `id, ho_ten, lop, club_id, ten_club, nguyen_vong_thu, dien, nhom_du_tru`;
  several sessions = 9 cols (`buoi` inserted after `lop`), one row per student × session.
  Unplaced: `club_id` empty, `ten_club` = "(chưa được xếp)". `dien` = "Thường" / "Dự trữ" (`_nhan_dien`).
- `_ghi_bo_csv`: per-club files in `<goc>_theo_club/` (6 cols: id, ho_ten, lop, nv_thu, dien, nhom) + `_chua_duoc_xep.csv`;
  file names are sanitised (`_ten_file_an_toan`, `_ten_chua_dung`) so match files to clubs BY CONTENT, not name.
- Export has NO preferences, NO scores, NO capacity. Capacity/reserve only in the sectioned `_tong_hop.csv`
  (section "TỪNG …": cols "Đã xếp", "Sức chứa", "Trong đó diện dự trữ", "Chỉ tiêu dự trữ").
- Sổ nhập (`so_nhap.py`): sheet "1. <slot>" cols `Tên CLB, Buổi, Chỉ tiêu, Suất ưu tiên, Nhóm ưu tiên, Mã CLB`;
  sheet "2. <person>" `Mã HS, Họ tên, Nhóm ưu tiên` + preferences in TWO layouts: one header row
  (`NV1, Điểm 1, …`, e.g. `SO_NHAP_TEST.xlsx`) or two header rows (A13.4: group "Nguyện vọng k" over
  `CLB, Điểm thi, Điểm quyết tâm`, data from row 3, e.g. `SO_NHAP_DQT_120HS_HOP_LE.xlsx`). Score cell may be a
  number, "8,5" (comma decimal, rule `doc_diem`) or the word "thi" (tested, no score).
- Only `du_lieu_test/SO_NHAP_TEST.xlsx` (10 clubs, 120 students, reserves) is one-session. All other sample books
  are multi-session; FA (medal) books are out of scope.

## Decisions (do not ask Truong again)
- D1 Open Q1: default export is NOT enough alone → the script reads the Sổ nhập for preferences, scores,
  capacity, reserve capacity and groups. Open Q2: NO change to the export or to the CSV contract (invariant 7);
  no product code changes at all. Open Q3: scores are only PRINTED in `dau_vao_ket_qua.csv` (the export has none),
  so no comparison and no epsilon; parse with the `doc_diem` rule (copied, ≤ 15 lines), use "Điểm thi"/"Điểm k",
  ignore "Điểm quyết tâm".
- D2 Location: `du_lieu_test/kiem_doc_lap/kiem_doc_lap.py` (+ `README.md`). Outside coverage (`omit du_lieu_test/*`).
  CLI: `python kiem_doc_lap.py --so-nhap X.xlsx --ket-qua ket_qua_phan_bo.csv [--ra dau_vao_ket_qua.csv]`;
  `main(argv) -> int` so tests import it. Exit 0 = all PASS, 1 = any FAIL, 2 = unsupported/unreadable input
  (multi-session 9-column file → exit 2 with "nhiều buổi: chưa hỗ trợ, xem DC1 giới hạn").
- D3 Club matching: Sổ nhập `Mã CLB` when filled; blank → match the export's `ten_club` by NFC + casefold +
  collapsed spaces; no match or ambiguous → check K0 FAIL "không đối chiếu được", never a silent guess.
- D4 Checks (codes printed in the table; each FAIL lists count + ≤ 5 student/club ids):
  K0 inputs readable, one session, every exported club maps to a Sổ nhập club;
  K1 every student exactly once (missing / unknown extra / duplicate rows);
  K2 per club placed ≤ `Chỉ tiêu` (blank or 0 capacity → skipped, noted);
  K3 per club "Dự trữ" count ≤ `Suất ưu tiên`; each "Dự trữ" student's group = the club's `Nhóm ưu tiên`;
     exported `nhom_du_tru` = Sổ nhập group of that student;
  K4 placed club is in the student's preference list;
  K5 `nguyen_vong_thu` = position of that club in the student's list (see Gotcha G2);
  K6 per-club files ⇔ main file (same student set per club, `_chua_duoc_xep.csv` = unplaced set, counts equal);
  K7 (optional lot) `_tong_hop.csv` "Đã xếp" and "Trong đó diện dự trữ" equal the counts from the main file.
- D5 Fixed footer text, facts only: "Phạm vi B: chỉ kiểm bảo toàn. KHÔNG kiểm đúng luật ưu tiên / ổn định: CLB có
  hai quỹ chỗ (dự trữ rồi chung), phép thử 'CLB đầy và người nhận cuối kém hơn tôi' sẽ báo sai cho em nhận bằng
  quỹ dự trữ." No commentary, no judgement words beyond PASS/FAIL (academic integrity).
- D6 False-positive datasets (3, one session, built in `tmp_path`, never committed): `SO_NHAP_TEST.xlsx` as is;
  plus two derived from `SO_NHAP_DQT_120HS_HOP_LE.xlsx` (two-header layout) and `SO_NHAP_MAU_120HS_3BUOI.xlsx`
  by keeping only the clubs of "Thứ 2", blanking `Buổi`, and dropping preferences to removed clubs. If a derived
  book does not import cleanly, replace it with `SO_NHAP_TEST.xlsx` at another seed and note it in Current state.

## Gotchas
- G1 CSV is UTF-8 with BOM (`utf-8-sig`); `_an_toan_cho_excel` may prefix cells that start with `= + - @`: read
  its rule and undo exactly that, nothing more.
- G2 Before fixing K1/K5 rules, check on the 3 datasets how import treats a student with no valid preference
  (is there a `match_results` row?) and whether rank counts invalid/duplicate preferences (`import_preferences_csv`).
  Copy the observed rule into the script with a one-line comment. If K5 cannot be made exact → make K5 INFO (not
  FAIL) and add a line under Needs Truong.
- G3 DC1 is NOT in the registry (`SO_DANG_KY_33_MUC.md`, `ke_hoach_thay_doi.json`) — do not edit the registry;
  log only in CHANGELOG + TIEN_DO, and keep the "Needs Truong" line below.

## Plan (lots; ticked by the coder)
- [x] **L1 (must)** Readers + checks K0–K6. Test file `tests/test_dc1_kiem_doc_lap.py` FIRST: mutation tests on a
  valid `SO_NHAP_TEST` export (drop a row → K1; duplicate a row → K1; move one student into a full club → K2;
  set a non-reserve student to "Dự trữ" over quota → K3; club outside preferences → K4; delete a row from one
  per-club file → K6), each asserts THAT check is FAIL; isolation test (ast: imports ⊂ `sys.stdlib_module_names`
  ∪ {openpyxl}, no relative import, no `sys.path` edits); multi-session file → exit 2.
- [x] **L2 (must)** PASS/FAIL table + footer (D5) + `dau_vao_ket_qua.csv` (cols: `student_id, ho_ten, nhom,
  nv_1..nv_k, diem_1..diem_k, club_id_nhan, ten_clb_nhan, dien, hang_nhan`; k = max over students; utf-8-sig).
  Tests: false-positive on the 3 datasets of D6 (all PASS, exit 0); CSV has one row per Sổ nhập student and
  `club_id_nhan` equals the export.
- [x] **L3 (must)** Docs: `du_lieu_test/kiem_doc_lap/README.md` (how to run, what each K means, scope B limits:
  one session, default mode, no FA, no stability); `docs/giai_trinh/HUONG_DAN_CHAY.md` new short section;
  `docs/giai_trinh/KICH_BAN_DEMO.md` one optional step (default workspace, `SO_NHAP_TEST.xlsx`, Xuất CSV, run the
  script, show the table) with "Dữ liệu mô phỏng" and a pointer to `CA_MAU.md` §3–§5 for the cases. Vietnamese.
- [x] **L4 (optional)** K7 `_tong_hop.csv` cross-check + one mutation test. Drop if L1–L3 used the budget.

## Acceptance
Mutation tests FAIL the right check; 3 valid datasets PASS fully; ast isolation test passes;
`kiem_nhanh.py` 7/7; `ruff check .` clean; no file outside `du_lieu_test/kiem_doc_lap/`, `tests/test_dc1_*`,
`docs/`, `CHANGELOG.md` changed.

## Needs Truong
- DC1 is not in the 33-item registry: approve adding it (planner recommends: yes, as a verification item, no sector).
- New default workspaces have điểm quyết tâm ON, which blocks `SO_NHAP_TEST.xlsx` (`wharton_ho_so_chua_hop_le`). Docs (HUONG_DAN_CHAY §10) say to turn it off (`rules.wharton = false`); the UI click path was not verified here.
- Windows commands and the UI export of the CSV set (button) were not run; the CSV set is produced via the `export_csv` API in tests.

## Current state
- L1–L4 done (L4 = K7). L1+L2 were one commit (script + table + CSV were written together). 18 tests green; kiem_nhanh 7/7; ruff clean.
- G2 observed: a student with no valid preference still has a (unplaced) row; unknown/duplicate clubs in a row make import reject the whole book, so rank = position in the list. K5 is exact (FAIL, not INFO).
- soat-ma: tiers 1–3 not applicable (no product code); tier 4 = tests + docs only.

### Self-check (SO_NHAP_TEST, seed 3, final script)
```
Học sinh: 120 | CLB: 10 | dòng kết quả: 120 | đã xếp: 109 | chưa xếp: 11
K0 PASS … K7 PASS  (K0 files/one session/clubs · K1 each student once · K2 capacity · K3 reserve/group/dien
  · K4 club in prefs · K5 rank = position · K6 per-club files · K7 _tong_hop counts)
Tổng: 8 PASS, 0 FAIL
```
`dau_vao_ket_qua.csv` HS001–HS003 checked by eye against the Sổ nhập: HS001 prefs Tin học 7.9 / Mỹ thuật 7, unplaced;
HS002 (chinh_sach) 4th pref Âm nhạc, Thường, rank 4; HS003 (chinh_sach) Tin học, Dự trữ, rank 1. All match.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-24 | Opus (planner) | Read export/Sổ nhập code, wrote this file + DC1_GIAO_THUC.md | no product code |
| 2026-11-24 | Sonnet (coder) | L1–L4: script K0–K7, tests (19), README, docs, CHANGELOG/TIEN_DO | soat-ma: tiers 1–3 n/a (no product code) |

## Checker report (2026-11-24, Sonnet checker, head 9d4cf1a)

Chỉ soát, không sửa mã/test/sổ đăng ký. Dữ liệu dùng là dữ liệu MÔ PHỎNG (`SO_NHAP_TEST.xlsx`, seed 3).

**Kết quả chạy:** `pytest` 3 tệp = 50 passed; `ruff check .` sạch; `kiem_nhanh.py` 7/7; `git diff --stat origin/main...HEAD` chỉ gồm
`CHANGELOG.md`, `docs/**`, `du_lieu_test/kiem_doc_lap/*`, `tests/test_dc1_kiem_doc_lap.py` (đúng phạm vi Acceptance). Script chỉ import thư viện chuẩn + openpyxl.

**Kết luận: không có blocker.** Có 3 mục "nên sửa" và 4 nit.

### Nên sửa (should fix)
1. **K0 không đối chiếu `club_id` với tên CLB (D3 dương tính giả/âm tính giả ngược: lọt lỗi thật).** `_ghep` tra `theo_ma` rồi *rơi sang tra theo tên* dù Mã CLB của Sổ nhập đã điền.
   Repro (bộ hợp lệ seed 3, sửa tệp chính `ket_qua_phan_bo.csv`):
   (a) đổi `club_id` của một dòng đã xếp thành `XXX_BOGUS`, giữ nguyên `ten_clb` → mã thoát 0, "8 PASS, 0 FAIL";
   (b) giữ đúng `club_id`, đổi `ten_clb` thành tên CLB khác → mã thoát 0, "8 PASS, 0 FAIL".
   `dau_vao_ket_qua.csv` còn in `club_id_nhan` sai. README ghi "theo Mã CLB, nếu trống thì theo tên" — không đúng với mã (rơi sang tên cả khi mã không khớp). Đề nghị: khi Mã CLB của Sổ nhập đã điền, `club_id` xuất phải thuộc tập mã đó (nếu không → K0 FAIL "không đối chiếu được"), và `ten_clb` xuất phải khớp tên của CLB có mã đó; chỉ rơi sang tên khi Mã CLB của Sổ nhập trống. Thêm test đột biến (a) và (b).
2. **`test_k3_vuot_suat_du_tru` đỏ do nguyên nhân phụ.** K3 có ba phép con (quỹ dự trữ ≤ suất; nhóm em dự trữ = nhóm CLB; nhóm xuất = nhóm Sổ nhập). Test đổi vài em "Thường"→"Dự trữ" nên vừa vượt suất vừa lệch nhóm. Tôi vô hiệu hoá riêng phép kiểm suất (`if dem.get(...) > c["du_tru"]`) rồi riêng phép kiểm nhóm: cả hai lần test vẫn passed (1 passed). Tức không test nào khoá từng phép con. Đề nghị thêm hai test: (i) chọn em đã đúng nhóm CLB để chỉ vượt suất; (ii) đổi cột `nhom_du_tru`/diện của một em dự trữ mà không vượt suất. (Ghi chú: các đột biến phía Sổ nhập của tôi — đổi nhóm em HS003, đổi Nhóm ưu tiên CLB Tin học, hạ Suất ưu tiên về 0, hạ Chỉ tiêu 12→11 — đều bị FAIL đúng phép K3/K2, nên script đúng; chỉ test yếu.)
3. **K6/K7 FAIL khi thiếu tệp đi kèm, trong khi D4 ghi K7 là "optional lot".** Chỉ đưa tệp chính (không có `*_theo_club/` hoặc `*_tong_hop.csv`) → K6 FAIL "không thấy thư mục", K7 FAIL, mã thoát 1, không phân biệt được với vi phạm thật. README nói tệp phải nằm cạnh nhau nhưng không nói điều gì xảy ra khi thiếu; HUONG_DAN_CHAY mục 10 cũng chưa nói. Đề nghị chọn một: ghi rõ trong README/HUONG_DAN ("thiếu tệp đi kèm → K6/K7 báo FAIL, mã 1"), hoặc đổi thành "BỎ QUA" (không tính FAIL). Quyết định thuộc Truong/Opus; hiện hành vi là FAIL.

### Nit
- N1. K2 bỏ qua CLB có Chỉ tiêu trống/0/không đọc được số (vd. "12 chỗ"); đúng D4 và có ghi "bỏ qua N CLB", nhưng CLB Chỉ tiêu 0 có người xếp vẫn ra PASS. Repro: đặt Chỉ tiêu CLB Bóng đá = 0 → 8 PASS.
- N2. Mã học sinh được `strip()` nên "HS001␠" vẫn khớp (PASS); mã khác hoa/thường thì FAIL K1 (đúng). Không phải lỗi, chỉ ghi nhận.
- N3. `main` in thông báo lỗi đầu vào hai lần (stderr và stdout); `ghi_dau_vao` không bắt `OSError` (đường `--ra` không ghi được → traceback thay vì mã 2).
- N4. KICH_BAN_DEMO 13b chỉ `CA_MAU.md` mục 1–2 đối chiếu HS001–HS003 (đúng với mục "Ca 1/4/5"), nhưng `CA_MAU.md` dùng hạt giống 42 còn tự kiểm dùng seed 3; kết quả ba em khớp ở cả hai, nhưng tài liệu không nói hạt giống nào cần dùng.

### Đối chiếu từng mục được giao
- **K0–K7 so với D4:** đúng, ngoài mục 1 ở trên. K1 (thiếu/lạ/lặp), K2 (Chỉ tiêu), K4, K5, K6 (khớp theo nội dung, không theo tên tệp), K7 chạy đúng trên các đột biến của tôi.
- **D2 mã thoát:** 0/1/2 đúng (tệp 9 cột, Sổ nhập nhiều buổi, thiếu tệp → 2). **D5:** `CHU_THICH` trùng nguyên văn D5. **Không import mô-đun của repo:** có test ast.
- **Đột biến của tôi (tất cả trên bộ hợp lệ seed 3):** em chưa xếp được thêm vào tệp theo CLB → K6 FAIL ✔; em dự trữ đổi `nhom_du_tru` → K3 FAIL ✔; hoán đổi CLB của hai em (giữ bảo toàn) → K3/K4/K5/K6/K7 FAIL ✔; Thường→Dự trữ → K3 FAIL ✔; em đã xếp bị xoá CLB chỉ ở tệp chính → K6, K7 FAIL ✔; dòng thừa HS999 → K1 FAIL ✔; chỉ có tiêu đề → K1 FAIL ✔; xoá Mã CLB cả cột Sổ nhập (khớp theo tên) → PASS ✔; tên CLB IN HOA + NBSP, Mã CLB trống → PASS ✔ (D3 đúng); đổi nhóm HS003 → K3 FAIL ✔; bỏ nguyện vọng 1 của em đã nhận → K4, K5 FAIL ✔. Lọt lỗi: chỉ mục 1 (và N1 theo thiết kế).
- **Tài liệu:** README, HUONG_DAN_CHAY mục 10, KICH_BAN_DEMO 13b bằng tiếng Việt, chỉ nêu dữ kiện, có ghi "Dữ liệu mô phỏng", không có nhận xét/kết luận. Sai lệch duy nhất với script: câu về Mã CLB ở README (mục 1) và thiếu nói về hành vi khi thiếu tệp (mục 3).

| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-24 | Sonnet (checker) | Soát DC1: không blocker; 3 should-fix, 4 nit | chỉ docs, không sửa mã |
