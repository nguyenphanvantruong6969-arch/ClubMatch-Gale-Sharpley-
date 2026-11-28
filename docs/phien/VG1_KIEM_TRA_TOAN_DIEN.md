# VG1 — Comprehensive role-play test (Sonnet, 2026-11-27)

> Method: acted as admin / teacher / student against `dk_*` API (87 + 13 scripted checks) and in Chromium (admin, teacher, student at 375 px).
> All data SIMULATED. No product code changed. Scripts are throw-away (scratchpad); every finding below was reproduced by hand.
> "Planned" = already covered by VG1 L1–L4. "NEW" = not covered yet → candidate lot **L5** (or item VG2).

## Held up (no bug found)
Input validation of clubs (16 bad inputs), room clash, 2 clubs/teacher/session, teacher/student cannot call admin functions, no-token calls,
student sees only own-grade approved clubs, wishes validation (duplicates, wrong grade, exam on non-selective, non-dict items), score range/NaN/inf,
score pasting with bad lines, exit gate «thiếu điểm», export xlsx works, same error for unknown user vs wrong PIN, 375 px layout: no overflow, taps ≥ 40 px, no JS errors.

## Findings
| # | Sev | Finding (how to reproduce) | Status |
|---|---|---|---|
| 1 | High | **Anyone can lock out the admin.** 5 wrong admin passwords from the public gate → real admin gets `dk_tam_khoa` for 5 min; `dk_mo_khoa` needs an admin session, so only `QUEN_MAT_KHAU.bat` helps. Repeatable every 5 min. Same for any student/teacher id (5 wrong PINs). | NEW (L1 only fixes malformed PINs) |
| 2 | High | **PIN reset does not end old sessions.** `dk_gv_dat_lai_pin` / `dk_hs_dat_lai_pin`: the old token still works (idle timer refreshes on use). A leaked/shared login stays valid after the reset. Will matter for the new bulk PIN export (L2): old sessions must die on reset. | NEW → add to L2 |
| 3 | Med | **Removed student's old token can still save wishes** (`dk_hs_nap_danh_sach(..., "thay")` after going back, reopen, old token `dk_hs_luu`) → rows in `dk_nguyen_vong` for a student who no longer exists. More likely once L3 allows multi-step back. | NEW → add to L3 |
| 4 | Med | **Deleting a room used only by rejected clubs succeeds** and leaves `phong_id` dangling; re-approving that club then fails with `dk_phong_la`. (`dk_phong_xoa` ignores rejected clubs.) | NEW |
| 5 | Med | **Case-only duplicates accepted**: room `p1` next to `P1`, club `a1` next to `A1`, teacher `cô an` next to `Cô An` (same root cause as bug 1: no normalisation). Students see two near-identical clubs. | NEW → extend L1 normalisation to rooms, clubs, teacher self-register |
| 6 | Med | **No way to delete a teacher** (no `dk_gv_xoa`), and teacher self-registration has no rate limit: 30 junk accounts created with only the school code. | NEW |
| 7 | Med | **Weak PINs**: teacher can self-register PIN `0000`/`1234`; generated PINs are 4 digits (10⁴ space). With #1 this is brute-forceable between locks. | NEW (policy: reject trivial PINs) |
| 8 | Med | **UI «Danh sách»: «Giáo viên (N)» and «Học sinh (N)» are collapsed by default** (`<details>` closed) → after Excel import the tab shows only a heading with a count and looks empty. Very likely Truong's defect 7 ("Đặng Văn Nam 4"). Screenshot reproduced; needs Truong to confirm. | NEW (open them by default when N ≤ ~50) |
| 9 | Med | **UI landing card says «N giáo viên đã đăng ký tài khoản»** but counts admin-created accounts (2 shown, nobody registered). | Defect 7 earlier (needs definition) |
| 10 | Med | **«Đóng ngay» (teacher stage) closes with one click, no confirmation**, even with no Tự do club (UI confirmation of defects 4–5). | L4 + add confirm dialog |
| 11 | Low | Init accepts a 1-char school code and admin password `1234`, while `dk_cai_dat_doi` rejects a school code < 4 chars (inconsistent). | NEW |
| 12 | Low | A student who un-ticks then re-ticks an exam club after the admin entered the score loses the score silently (stage `hs_dang_ky` only). | NEW (warn or keep) |
| 13 | Low | `nguyen_vong` that is not a list → generic `dk_loi_chung` (logged) instead of a validation error. API-only. | NEW |
| 14 | Low | Idle timeout: UI text says 60 s for students, backend allows 300 s (`GIAY_NGHI_KHAC * 5`) — harmless (client logs out first). The «Thao tác hoàn tất.» text is a 1×1 screen-reader live region, NOT a visible bug (retracted in round 2). | Dropped |

## Suggested L5 (size S, backend + 2 UI tweaks) — if Truong approves
Fixes 1 (lock keyed by IP-less identity: unlock by admin without session is impossible → proposal: never lock `quan_tri`; instead slow down: exponential delay, or lock only the offending attempt rate), 2, 4, 5, 6 (`dk_gv_xoa` + sign-up cap per stage), 7, 8, 10.
Needs Truong's decision first on #1 (accept slowdown instead of lock-out for the admin account).

## Round 2 — UI and user flows in Chromium (2026-11-27, on the branch tip incl. VG1-L1..L3)
Walked every admin stage × 2 widths (1100 / 375 px) × 4 tabs, a teacher creating a club, a student ranking → medals → exam → review → send, score entry, reload.
No JS/console error anywhere. Held up: HTML in club names is escaped; double-clicking «Gửi duyệt» / «Gửi nguyện vọng» saves once; reload returns to the landing page (no stale
session); the exam step warns «CLB Tuyển chọn em xếp nhưng chưa tick sẽ không được xét: Robot»; scores `8,5` save correctly; student 390 px layout fine.
| # | Sev | Finding | Status |
|---|---|---|---|
| 15 | Med | **Admin tables overflow at 375 px** (whole page scrolls sideways): «Duyệt CLB» table 684 px wide (overflow 344 px), «Nhập điểm» 43 px, «Xuất» 182 px. `.dk-bang` has no scroll wrapper. | NEW → L3 |
| 16 | Med | **Stale error stays after success**: score box shows «Điểm phải là số từ 0 đến 10…» while the next valid score `8,5` is already saved (DB 8.5); invalid text also stays in the box. | NEW → L3 |
| 17 | Med | **Teacher «Xoá» (own pending club) deletes at once, no confirmation.** (Admin «Đóng ngay» is finding 10.) | NEW → L3 |
| 18 | Low | **Accessibility:** every row has the same «Đặt lại PIN» button with no person in its accessible name (screen-reader users cannot tell them apart); admin screens have no `<h1>`; «← Mở phần mềm xếp CLB» and the switch `on` are < 36 px tap targets. | NEW → L3 |
| 19 | Low | Club-name input has no `maxlength` (80): the «Tên đang để trống hoặc quá dài.» error appears only at «Gửi duyệt», three steps later; message mixes "blank" and "too long". | NEW → L3 |
| 20 | Info | Duyệt screen's «Chưa đi tiếp được» list does not mention the missing Tự do club (VG1-L4 scope). | VG1-L4 |

## Round 3 — stress test and "is it simple and clear?" (2026-11-27, branch tip incl. VG1-L1..L3)
### Stress (API level, 800 students × 20 clubs × 5 sessions, 40 parallel threads; the portal server is `127.0.0.1` + secret token, so real load is lower)
| Test | Result |
|---|---|
| Import 800 students | 1.3 s (1.7 ms each) |
| Reset 800 PINs one by one | 3.5 s (≈ 4 ms each; PBKDF2 10 000 rounds) |
| 800 logins in parallel | 3.0 s, 0 errors |
| 800 students save 5 sessions × 3 clubs in parallel | 2.4 s, **0 errors**, 800 submitted, 12 000 wish rows consistent |
| Admin lists (students/progress/clubs/scores/preview) | ≤ 0.03 s each, also under 30 reading threads (0.14 s) |
**Held up:** no "database is locked", no lost or duplicated rows, no slowdown. Capacity is NOT a concern for 800 students.
| # | Sev | Finding | Status |
|---|---|---|---|
| 21 | Low | **Lock table grows without bound:** every wrong login for an id that does not exist writes a row in `dk_cai_dat` (2 000 attempts → 2 000 rows, 5 ms each, never purged). A stranger can bloat the DB and the backup. | NEW → VG2-L1 (cap/purge: keep only ids that exist + one shared counter for unknown ids; drop rows older than the lock window) |
| 22 | Low | **Session tokens are never purged** unless the user comes back (1 021 tokens after the run). Harmless at this size, but also keeps a stale token alive until reuse. | NEW → VG2-L1 (purge expired on each login) |
### Simplicity and clarity (walked as a first-time admin, a teacher, a student)
| # | Sev | Finding | Status |
|---|---|---|---|
| 23 | **High** | **Student needs 16 screens / 20 clicks** with 5 sessions even when choosing 1 club in 1 session: every session has 3 screens (rank → medals → exam), also for sessions the student leaves EMPTY («Buổi T3 · Đặt huy chương» with nothing to place). Roughly 3× more taps than necessary on a shared kiosk with 800 students. | NEW → VG2-L4 |
| 24 | Med | **Internal code shown to users:** a teacher registering outside the open stage sees `Việc này chỉ làm được ở giai đoạn "gv_dang_ky".` (`dk_sai_giai_doan`, same for `duyet`, `chuan_bi`, `hs_dang_ky`, `nhap_diem`). Must show the stage's name («Giáo viên đăng ký»). | NEW → VG2-L4 |
| 25 | Med | **Jargon for school staff:** «Xếp lại (cùng hạt giống)», «lần chạy 1, hạt giống 7», «chế độ giữ chỗ và huy chương». Replace with plain words («Xếp lại và giữ nguyên kết quả bốc thăm»; hide the number behind «Chi tiết kỹ thuật»). Students see «NV1/NV2» without a legend. | NEW → VG2-L4 |
| 26 | Low | **First-run screen has no help:** no hint that the password needs ≥ 4 characters, what «Mã trường» is for, what a «Khối» is, nor that the password cannot be recovered in the app (only `QUEN_MAT_KHAU.bat`). | NEW → VG2-L4 |
| 27 | Low | **Wrong/odd status text:** Chuẩn bị with 0 students says «0 học sinh · 0 lớp · đã có PIN»; the student login form is fully shown while the stage is «Chưa mở». | NEW → VG2-L4 |
Good already: error messages are short plain Vietnamese (75 `dk_*` codes, only 1 over 28 words); the 6-step progress bar; «Chưa đi tiếp được: …» explains what blocks the admin; the medal screen explains Vàng/Bạc/Đồng in 3 sentences; teacher form has 3 clear steps.
