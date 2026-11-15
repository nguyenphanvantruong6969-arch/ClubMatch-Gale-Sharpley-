# Branch handoff: claude/fa-sc-sua

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/FA_SC_GIAO_THUC.md` (lead + writer + checker). Checker verdicts: `claude__fa-sc-sua__tester.md`.

## Feature / goal
FA-SC Phase 1 (approved by Truong 2026-11-14, D-SC1): converter-only fixes from `docs/fable/07_FA_SC_FIX_PLAN.md` §2
(evidence `docs/fable/06_CRISIS_MEMO.md`, drills `du_lieu_test/su_co/`). Code lives under `mau_forms_thi_clb/`
(entry `chuyen_fa_daa` in `chuyen_forms_sang_phan_mem.py`, CLI `main`). Kiosk untouched. Every new option defaults
OFF; without it the converter output is byte-identical (invariant 1). New sheets/files are reports only (invariant 2).

## Plan (written by Opus; ticked by lead after CHECKER NO BUGS)
- [x] L0 baseline: converter on `du_lieu_test/demo_t4m.py` fake data (`--day-du` and plain) into scratch; keep outputs
- [x] L1 FA-SC-6 roster input (P1-1) — cc2d9a4, checker NO BUGS 76b2c45
- [x] L2 FA-SC-4 sheet "Cần xử lý" (P1-2) — bca5941, checker NO BUGS b1d956b
- [x] L3 FA-SC-4b per-club dropped-response report (P1-4) — 7c3d3b3, checker NO BUGS 35e4938
- [x] L4 FA-SC-2 per-class confirmation sheet (P1-3) — db28790, checker NO BUGS 0c81390
- [x] L5 FA-SC-10 per-day lottery lock (P2-1; approved 2026-11-15) — 98b8b09, checker NO BUGS 91f3da8

### Lot L1 — roster input (FA-SC-6)
- New optional arg on `chuyen_fa_daa` + CLI flag (e.g. `danh_sach_truong=None` / `--danh-sach-truong CSV`): the roster
  format `danh_sach_chua_dang_ky.py` already reads (`student_id`, `class_id`, optional `email`). Reuse its reader if
  possible; no new library.
- With roster: (a) typed ID not on roster → one warning line naming ID + email; (b) one ID used by two emails → one
  line with both emails, listed BEFORE the workbook is written (non-blocking unless today's code already blocks; d03a
  must no longer be refused: if roster has `email`, replace typed ID by roster ID and report the difference);
  (c) `class_id` from roster fills the existing class column; (d) sheet "Chưa đăng ký" grouped by class, plus
  "missing day" rows per student (registered some days, not all).
- `kiem_nhan` test (new file, e.g. `tests/test_fa_sc_l1_danh_sach.py`): fake roster + export with one collision, one
  unknown ID, one unregistered, one missing day → exactly one line each; clean data → none; no roster → byte-identical.
- Drills must flip: d03a, d03b, d14 (0/120 without class), d01, d02 (student named in a report). Drills may need a
  roster arg passed through `du_lieu_test/su_co/chung.py`; add it with default OFF so old drill numbers reproduce.
- Sổ nhập columns unchanged (invariant 7).

### Lot L2 — sheet "Cần xử lý" in BANG_DIEM.xlsx (FA-SC-4)
- Only when a new option is on (default OFF → workbook byte-identical). One row per student per issue, built ONLY from
  warnings that already exist: wrong-test pair (test without rank + NOT_ATTEMPTED → one merged row), response dropped
  for unknown email, choices changed after test time, FREE club ranked above a tested SELECTIVE club, unused
  reservation (addressed to club teacher). Columns: student, issue (plain Vietnamese), who acts, what to do.
- Typed-name ≠ roster-name check (S37/d05): only if the data already exists without a form change; else skip →
  Needs Truong.
- Also (from L1 review): roster email listed on two IDs → one warning line (today it silently takes the first ID).
- Existing "Cảnh báo" sheet unchanged. Test: each injected case gives one row. Drills flip: d06, d04, d07 (d05 only
  if no form change).

### Lot L3 — per-club dropped-response report (FA-SC-4b)
- From L2 data, behind the same or a sibling option: one small file per club (folder in output dir): emails whose
  response for that club was dropped, and students who ranked that club but have no test. Only that club's rows; no
  scores, no lottery numbers, no other club's data. Test: one file per club, injected cases listed, nothing else.

### Lot L4 — per-class confirmation sheet (FA-SC-2)
- Behind an option; needs the L1 roster for the class. One file per class; one block per student: per day the stored
  choices, the three medals, tests received and whether each counts; dropped/not-counted tests shown "không tính + lý
  do". No other student's data in a class file, no scores of other students, no lottery numbers (STB). Own score:
  include only if the plan says so as report-only; otherwise omit and put "show own score?" on Needs Truong.
- Test: one block per student; dropped test shows reason; privacy assertions (no other class's IDs, no STB column).

### Lot L5 — per-day lottery lock (FA-SC-10 = P2-1; approved by Truong 2026-11-15 incl. new table `stb_buoi`)
- Goal: at the first run store each day's order; later runs keep earlier students' relative order on EVERY day and insert
  newcomers uniformly per day (`chen_stb_cho_hoc_sinh_moi`, seed `_seed_cua_buoi(seed, buoi)`). Spec: plan §2 P2-1;
  prototype `du_lieu_test/su_co/thu_p1_khoa_so_theo_ngay.py`. Schema change allowed ONLY for the new table (rule 7).
- First run must call today's `sinh_stb_theo_buoi` unchanged → invariant 1 (`kiem_nhanh.py --co-so origin/main
  --so-seed 20` → 7/7, 60/60). New parameter (e.g. stored orders = None) defaults to old behaviour.
- All three readers use the stored order: the run (`run_rbda_nhieu_buoi` via `_run_pipeline_da_khoa`),
  `get_so_boc_tham_theo_buoi` (`api_bao_cao.py`), round 2 (`_du_lieu_vong_2`, `api_sau_xep.py`).
- Table `stb_buoi(buoi, student_id, so)` created via `di_tru_schema` (idempotent, backup first, invariant 7). Write it in
  the SAME transaction as the run (invariant 5); `run_history` untouched (4). `force_redraw_stb` clears it and leaves a
  trace (run_history/steps_log entry). Student deleted → others' order unchanged (no renumbering by gaps).
- Old workspaces (lock exists, no stored order): DECISION — the first run after migration uses the legacy computation
  exactly as old code would (so nothing moves silently), then stores that order; a visible step detail says so.
  Never "rebuild" or reshuffle silently. Single-day / non-`stb_ngay` modes: untouched, store nothing.
- Fingerprint (FA-9): covers per-day orders, or states plainly that it does not (writer picks; document it).
- 7 kiem_nhan (plan): (1) 3 datasets × 20 seeds first run byte-identical; (2) property: after +k students earlier
  students' relative order unchanged on every day; (3) newcomer per-day position uniform (chi-square over seeds);
  (4) deletion keeps others' order; (5) redraw clears + trace; (6) migration idempotent with backup; (7) fingerprint.
- Drills: d12 and d16 must flip (earlier students moved: d12 20/51 → ~1/1, d16 18/38 → 0/0; run via
  `du_lieu_test/su_co/d12_*.py`, `d16_*.py`, plain, not the in-process prototype).
- Related tests: new `tests/test_fa_sc_l5_*.py` + every tests/ file grepping stb/seed/lottery identifiers touched
  (at least test_khoa_hat_giong, test_boc_tham, test_chen_stb_cong_bang, test_nhieu_buoi, test_api, test_data_durability,
  test_a14_lop_backend, test_export_ket_qua, test_xuat_hoc_sinh, test_wharton_pipeline, test_a13_13_kiem_nhan,
  test_tham_khao_verify_nhanh). Update the `tests/` row in `CLAUDE_CHI_TIET.md`.
- CHANGELOG must say: reruns with a changed student list now differ from old reruns (intended). Invariant 3 wording
  extended to per-day order: record in "Needs Truong" for confirmation.
- Unclear → "Needs Truong" in this file, never wait. Interaction with G1/G3 → note only.

## Current state (overwrite each handoff)
- Done so far: setup; L1-L4 all ticked (checker NO BUGS each). Phase 1 automatic scope COMPLETE.
- In progress: nothing.
- Tests: per lot, see protocol §2.
- Open problems: none.

## Sessions
| Role | Session id | Model | Status |
|---|---|---|---|
| lead | session_01YVAytzZ86RjYnNn3aTHjZY | Sonnet medium | active (all Sonnet medium, Truong 2026-11-14) |
| writer L4 | session_01YVAyu1Gjsgbsp1AtoyQ8mu | Sonnet medium | archived |
| checker L4 | session_01YVAytziarxgVP2ttMTk2LY | Sonnet medium | archived |
| lead L5 | session_01YVAyu2GQZcAWLnBkzjQFwa | Sonnet medium | active |
| writer L5 | session_01YVAytzPQwmCph4tHz5hnUR | Sonnet medium | active |
| checker L5 | session_01YVAyu1NyBNoy8DMPNpoLfb | Sonnet medium | archived |

## Needs Truong (never built automatically)
- Phase 0 (P0-1…P0-7): wording, checklists, decisions D-SC2…D-SC7 (plan §4 has a recommendation for each).
- P2-1 per-day lottery lock (schema change), P2-2 attendance, P2-3 capacity warning, P2-4, P2-5.
- S37 typed-name check that needs a "class and full name" question in the test form (form generator change).
- L2: "choices changed after test time" (registration rows carry no submit time; needs a form change) and S37/d05 name check (needs a name question in the test form).
- Roster with path A (CSV List): today a clear error; supporting it needs a decision on how List rows map to the roster.
- L4: "show own score on the confirmation sheet?" (omitted: undecided, plan says nothing); a test re-submitted inside the SAME quiz file is dropped silently by the converter (first kept, no warning), so the class sheet cannot name it (needs a warning + decision); dropped responses from unknown emails cannot be tied to a student, so they stay on the IT sheet / club reports only.
- L5: confirm that invariant 3 (STB lottery lock) now also covers the PER-DAY order (table `stb_buoi`); the FA-9 fingerprint deliberately does NOT cover per-day orders (same reason as base lottery numbers; documented in `dau_van_tay_du_lieu`) — confirm or ask for it to be included. Old workspaces: first run after migration reproduces the legacy order, then stores it (visible step warning).
- Wiring the new converter options into the kiosk "Chuẩn bị đợt" tab.

## Decisions and gotchas
- Undecided policy inside a lot: take the plan's "recommended" option only if report-only; else Needs Truong.
- No user-facing internal codes (FA-SC, P1-1, S30) in teacher-facing text.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-14 | Opus (lead) | branch setup, lot specs | |
| 2026-11-14 | Sonnet (writer/checker) | L1 roster input | NO BUGS |
| 2026-11-14 | Sonnet (lead) | L2-L4 run, final summary | all NO BUGS |

## Tổng kết cuối (§7, tiếng Việt)
**Đã làm (bộ chuyển đổi `mau_forms_thi_clb/`, kiosk không đổi, mọi tuỳ chọn mặc định TẮT → đầu ra giống hệt cũ):**
- L1 danh sách học sinh của trường làm đầu vào (`danh_sach_truong`, `--danh-sach-truong`): báo ID lạ, ID trùng hai email, điền lớp, "Chưa đăng ký" theo lớp. Drill d03a, d03b, d14, d01, d02 đổi trạng thái.
- L2 sheet "Cần xử lý" (`can_xu_ly`, `--can-xu-ly`) trong BANG_DIEM.xlsx: mỗi học sinh/vấn đề một dòng. Drill d06, d04, d07 đổi trạng thái; d05 chưa.
- L3 báo cáo theo CLB (`bao_cao_clb`, `--bao-cao-clb`): thư mục BAO_CAO_CLB/, mỗi CLB một tệp, chỉ dữ liệu CLB đó.
- L4 phiếu xác nhận theo lớp (`phieu_lop`, `--phieu-lop`): PHIEU_XAC_NHAN_LOP/, mỗi lớp một tệp, mỗi học sinh một khối; không điểm, không số bốc thăm, không email.
- Test mới: tests/test_fa_sc_l1…l4 (L2: 9, L3: 6, L4: 9, L1 theo tệp riêng); kiem_nhanh 7/7, 60/60 giống hệt ở mọi lô.

**Cần Truong quyết (xem danh sách "Needs Truong" ở trên):** Phase 0 (D-SC2…D-SC7, khuyến nghị ở plan §4); P2-1…P2-5; kiểm tên S37/d05 và "lựa chọn đổi sau giờ thi" (cần sửa form); roster với đường A (CSV List); "có hiện điểm của chính em trên phiếu xác nhận không?"; bài nộp lại trong cùng tệp quiz bị bỏ im lặng; nối các tuỳ chọn vào tab "Chuẩn bị đợt".

**Nên thử trên Forms thật (TH):** chạy converter với danh sách trường thật cùng ba tuỳ chọn mới; kiểm một phiếu lớp và một báo cáo CLB bằng mắt; xác nhận không lộ dữ liệu bạn khác.

**Ghi chú nhật ký AI (3–5 dòng):** Lead + writer + checker đều là Claude Sonnet (effort medium), mỗi lô một cặp mới. Kiểm thử độc lập từng lô (test liên quan, drill, so sánh byte-identical, kiểm riêng tư). Mọi số liệu là dữ liệu giả lập. Không có kết luận báo cáo nào do AI viết.

## Truong decisions (2026-11-15)
- D-SC2: retake only before lock, club teacher approves, different variant, only if no response for the intended club.
- D-SC3: post-result claims = data errors only, proven by a system record.
- D-SC7: (a) no rerun with a changed student list after announcing; then (b) build P2-1 per-day lottery lock.
- Confirmation sheet: do NOT show the student's own score.
- Still open: D-SC4, D-SC5, D-SC6, P2-2, P2-3, form changes (S37, change-after-test), path A roster, kiosk tab wiring.

## Tổng kết L5 (2026-11-15, tiếng Việt)
**Đã làm:** khoá thứ tự bốc thăm THEO NGÀY (bảng mới `stb_buoi`, tạo bằng `di_tru_schema`: idempotent, sao lưu trước). Lần chạy đầu dùng đúng hàm cũ → kết quả giống hệt (`kiem_nhanh` 7/7, 60/60). Lần sau: em cũ giữ thứ tự tương đối ở mọi ngày, em mới được chèn đều ngẫu nhiên. Ba nơi đọc (chạy, `get_so_boc_tham_theo_buoi`, vòng 2) đều dùng thứ tự đã lưu; ghi cùng một giao dịch với kết quả (checker đã thử ép lỗi commit: không đổi gì). `force_redraw_stb` xoá bảng và để lại cảnh báo.
**Số đo (mô phỏng):** d12 em cũ đổi CLB 20 → 1; d16 18 → 0.
**Workspace cũ:** lần chạy đầu sau khi nâng cấp dùng cách tính cũ rồi mới lưu, kèm một cảnh báo; không có gì đổi âm thầm. CHANGELOG ghi: chạy lại sau khi đổi danh sách học sinh nay KHÁC các lần chạy lại cũ (chủ ý).
**Cần Truong:** (1) xác nhận cách diễn đạt bất biến 3 mở rộng sang thứ tự theo ngày; (2) dấu vân tay FA-9 KHÔNG gồm thứ tự theo ngày (đã ghi và có test) — chấp nhận hay muốn gồm?; (3) `tests/test_a13_13_kiem_nhan.py::test_F1` đã lỗi sẵn từ trước L5 (`du_lieu_test/su_co/chung.py` thiếu `"wharton": False`), không do L5 — cần một lô riêng.
**Nhật ký AI:** lead + 2 writer (writer đầu bàn giao ở 200k token) + 1 checker, đều Claude Sonnet medium; checker kiểm độc lập (test, drill, so sánh giống hệt, thử rollback). Số liệu là mô phỏng; không có kết luận báo cáo nào do AI viết.
- 2026-11-15 (Truong "ok"): invariant 3 now also covers the per-day order (`stb_buoi`); FA-9 fingerprint keeps
  excluding per-day orders (as built). PR claude/fa-sc-sua -> main approved.
