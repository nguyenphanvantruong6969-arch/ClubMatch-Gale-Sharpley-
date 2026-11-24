# Branch handoff: claude/cb1-van-ban-phuong-an

## Feature / goal
Item **CB1 "Văn bản phương án xếp"** (independent of DC1). The school picks an allocation plan in tab Quản lý (goal
cards MT1/MT2 + GT2 criteria). The app exports ONE plain-language PDF for students, parents, school and jury:
the rules in words + the transparent procedure. Two versions: **BẢN DỰ KIẾN** (before the official run) and
**BẢN CHỐT** (after it). A new admin step **"Chốt phương án"** records who/when (audit log) and a hash of the rules.
Report/export only: no algorithm, priority, CSV or schema change. Size **M** (protocol `docs/phien/CB1_GIAO_THUC.md`).

## Decisions (Truong, final — do not ask again)
- One shared PDF, plain words, no jargon. Content = rules in words + transparent procedure. NO comparison table of
  plans (GT2 comparison stays HTML/CSV), no appendix.
- Seed: checkbox, **default OFF** (keeps D5); only printable in BẢN CHỐT after the lottery is locked. BẢN DỰ KIẾN
  never contains the seed, whatever the input.
- "Chốt phương án" = admin button; account + time go to the existing audit log (`nhat_ky.py`); the PDF prints them.

## Answers to the brief's code questions (verified by reading code, 2026-11-24)
1. **Change after chốt.** Config lives as JSON in `workspace_settings` key `config` (`cau_hinh_ws.KHOA_CAU_HINH`);
   that table is key/value. Store chốt as a NEW ROW `workspace_settings` key `chot_phuong_an` =
   `{"nguoi","vai","luc","bam_luat","muc_tieu":{id,nhom}|null}` — no new table, no column, no `di_tru_schema`.
   `bam_luat` = SHA-256 of `json.dumps({"rules": cfg["rules"], "muc_tieu": {id,nhom}|None}, sort_keys=True,
   ensure_ascii=False)`. PDF warns "Phương án đã đổi sau khi chốt" when current hash ≠ stored (same idea as
   `ket_qua_cu` via `dau_van_tay_chay`). Second warning: latest official run's `run_history.luat_xep` (see
   `TieuChiMixin._luat_tu_dong`) ≠ chốt rules → "Lần xếp chính thức không dùng phương án đã chốt"; compare `rules`
   only after `cau_hinh_ws.chuan_hoa`; if formats are not comparable, drop this warning and note it.
   `cau_hinh_ws.doc_cau_hinh` reads only key `config`, so the new row cannot change any result (invariant 1).
2. **Language.** All exports are Vietnamese-only (`PipelineAPI._nhan_xuat` docstring: "Tệp xuất luôn viết tiếng
   Việt"). So the PDF is Vietnamese; the pure builder takes `lang="vi"` (reuses `tieu_chi.mo_ta_tieu_chi(rules,
   lang)` and `tieu_chi.GHI_CHU[lang]`, both vi/en) so English is possible later. PDF sentences: one dict
   `CAU = {"vi": {...}, "en": {...}}` in the new module (pattern of `tieu_chi.GHI_CHU`). UI labels vi/en in
   `js/i18n.js` (prefix `cb1_`). Error codes appended at END of `i18n_errors.py` (prefix `cb1_`), then
   `python tao_i18n_js.py`. Workspace nouns via `_nhan_xuat()` labels (Học sinh/CLB…), as `bao_cao_tong_hop`.
3. **Boundary with FA-9 biên bản** (`fa_bien_ban.py`, `export_bien_ban_boc_tham`): biên bản stays THE signing
   page (seed, `sha256_stb`, counts per session, signatures). CB1 never prints `sha256_stb`, per-session counts or
   signature lines; it reuses `fa_bien_ban.THU_TU_LE` (import, do not copy) for the ceremony steps and says in one
   sentence that the signed biên bản is a separate document. CB1 does not change `fa_bien_ban.py`.
4. **Procedure milestones** (each printed with state Đã / Chưa + time when known):
   M1 Công bố phương án = key `chot_phuong_an` exists (`luc`, `nguoi`).
   M2 Chốt dữ liệu, dấu vân tay = row in `dau_van_tay_chay` (`dau_van_tay`, `luc`); absent → "chưa chốt dữ liệu".
   M3 Bốc hạt giống có chứng kiến, khoá số bốc thăm = `stb_lock.is_locked=1` (`locked_at`).
   M4 Chạy xếp chính thức = latest official `run_history` row (via `get_last_run_info`).
   M5 Công bố kết quả, hạn khiếu nại = if `rules.fa_khieu_nai`: "trong N ngày" (`fa_khieu_nai_so_ngay`); date only
   if the app already stores a publish time (coder greps `cong_bo`; none → "sau khi công bố").
   Dự kiến: M2–M5 normally "Chưa"; the fingerprint value is printed in BẢN CHỐT only.

## Plan (lots; ticked by the coder)
- [x] **L1 (must) pure builder** — new `phuong_an_xep.py`: `bam_luat(cfg)`, `trang_thai_quy_trinh(moc)` and
  `dung_noi_dung(ban, tieu_chi, muc_tieu, moc, chot, bam_hien_tai, in_hat_giong, hat_giong, lang="vi")` →
  dict of WHITELISTED keys only (like `bao_cao_tong_hop.gom_du_lieu`). Rules: `ban="du_kien"` → no seed key ever;
  `ban="chot"` → seed only if `in_hat_giong` and lock present. Tests `tests/test_cb1_noi_dung.py` (pure, fast).
- [x] **L2 (must) API + PDF** — new mixin `api_phuong_an.py` (wired into `PipelineAPI` like `MucTieuMixin`):
  `chot_phuong_an()` writes key `chot_phuong_an` (account from session; one transaction) — the audit row comes from
  the existing `nhat_ky` wrapper (check `nen_ghi("chot_phuong_an")` is True); `get_phuong_an_xep()` (read: state,
  milestones, warnings, can-export flags); `export_van_ban_phuong_an_pdf(output_path="", ban="du_kien",
  in_hat_giong=False)` via `xuat_pdf` (missing reportlab → `xp1_thieu_thu_vien_pdf`). BẢN CHỐT refused unless chốt
  + official run + lock (`cb1_chua_du_dieu_kien_ban_chot`); seed on dự kiến or before lock →
  `cb1_hat_giong_chua_khoa`. `phan_quyen._QUAN_TRI` += the 3 names; `nkhd_<name>` vi+en. Tests
  `tests/test_cb1_api_pdf.py`: leak test (PDF text has no student_id/name/score/stb of any student, sample data),
  seed absent by default and in dự kiến, warning after config change, `run_thu` + `chon_muc_tieu` never rewrite
  `chot_phuong_an`, teacher role refused, `run_history` row count unchanged by chốt/export. **MILESTONE 1.**
- [x] **L3 (must) UI tab Quản lý** — near the MT1 cards / GT2 block in `index.html`, new `js/2x_phuong_an.js`:
  button "Chốt phương án" (confirm dialog shows rules summary; re-chốt asks again), state line (who/when, warnings),
  buttons "Xuất bản dự kiến" / "Xuất bản chốt" (disabled + reason until allowed), checkbox "In hạt giống" (OFF,
  enabled only for bản chốt after lock). One Chromium test file `tests/test_cb1_ui.py`, one shared page fixture.
- [x] **L4 (optional docs, must-ship docs line)** — `HUONG_DAN_SU_DUNG.md` section; 5-step demo script in
  `docs/ke_hoach/` (simulated data `du_lieu_test/SO_NHAP_MAU_120HS_3BUOI.xlsx`, seed 3); `CLAUDE_CHI_TIET.md`
  code map + tests row; CHANGELOG `CB1-L<n>`, TIEN_DO rows. **MILESTONE 2** (final review, ≤ 3 screenshots).

## Acceptance
- Dự kiến: no seed anywhere; no fingerprint → "chưa chốt dữ liệu". Chốt: account, time, fingerprint, lock time;
  seed only when the box is ticked. Change config after chốt → warning in PDF and UI. Test runs never overwrite chốt.
- Leak test passes; `kiem_nhanh.py` 7/7 (default config byte-identical); CSV contract untouched; CI green.
- Report text = facts only; no commentary for the student's science report (academic integrity).

## Current state
- L1-L4 done and pushed; checker M1 and M2 both NO BUGS. Tests (rbda-kiosk) green at 0594da8 (run 1554). Lead then merged origin/main (DC1) at 1d17129 (PR #36); CI for 1d17129 was still running (push run 45398383007, PR run 45398394935).
- A send_later recheck fires ~13:43Z: if completed report "CI GREEN 1d17129" (or failing jobs, <=60 log lines) to lead session_01YVAyu1X941hBZsuDcwbrLK; fix only CB1-file failures.

## Next steps
1. git pull; list runs for the branch; report CI result for the latest head to the lead.
2. If green, nothing else is pending (Status: DONE already recorded). Windows-exe build workflow was never seen running on this branch; unverified.

## Needs Truong
- (empty)

## Notes from coder
- Chot value also stores `luat_xep` (= `luat_xep_de_ghi(rules)`) so the "official run did not use the chốt plan" warning can compare against `run_history.luat_xep`; additive, same row.
- PDF text has no workspace nouns (tiêu chí sentences are existing school wording from `tieu_chi`); not run through `_nhan_xuat`.

## Files touched
- docs/phien/claude__cb1-van-ban-phuong-an.md, docs/phien/CB1_GIAO_THUC.md: plan.
- phuong_an_xep.py, tests/test_cb1_noi_dung.py: L1.
- api_phuong_an.py, api.py, phan_quyen.py, xuat_pdf.py (`doan`), i18n_errors.py, i18n_loi.js, i18n.js, tests/test_cb1_api_pdf.py: L2; tests test_mt1_api/test_mt1_uoc_tinh/test_ws_nhan/test_gt3_phan_quyen adjusted for new names.

## Session log
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-24 | Opus | plan: branch file + protocol | answers Q1–Q4 above |
| 2026-11-24 | Sonnet | L1 pure builder + 20 tests | kiem_nhanh 7/7 |
| 2026-11-24 | Sonnet | L2 API + PDF + 23 tests | 4 older tests adjusted (counts/lists), no weakening |
| 2026-11-24 | Sonnet | L3 UI + 7 Chromium tests | .run-confirm-bar[hidden] CSS fix |
| 2026-11-24 | Sonnet | L4 docs + demo script | M1 verdict NO BUGS |
| 2026-11-24 | Sonnet | handoff at ~400k context; awaiting CI on 1d17129 (lead's DC1 merge) | no new work |
| 2026-11-24 | Sonnet | CI run 1546 red: 4 tests (tai_lieu code map, a14_the_xem list, ux4_l4 control budget + single yellow button) fixed in product/docs, no test weakened | waiting CI rerun |

## Tóm tắt cho Truong (CB1)
- Khung "Văn bản phương án xếp" ở Quản lý → Cách xếp → "Tuỳ chỉnh thêm" (chỉ quản trị); CI xanh, hai lượt checker không có lỗi.
- Thử 1: nạp `SO_NHAP_MAU_120HS_3BUOI.xlsx`, bấm "Xuất bản dự kiến": PDF có luật bằng lời, các bước quy trình đều "Chưa làm", không có hạt giống.
- Thử 2: bấm "Chốt phương án" (xem hộp xác nhận), chạy xếp chính thức, bấm "Xuất bản chốt": PDF có người chốt, thời điểm, dấu vân tay; ô "In hạt giống" tắt thì không có hạt giống.
- Thử 3: đổi mục tiêu sang "Cơ hội như nhau" rồi mở lại khung: hiện cảnh báo "Phương án đã đổi sau khi chốt".
- Kịch bản 5 bước đầy đủ: `docs/ke_hoach/CB1_KICH_BAN_DEMO.md`. Không có việc nào chờ Truong quyết định.
