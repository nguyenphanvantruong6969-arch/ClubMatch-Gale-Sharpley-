# Nhật ký AI của dự án (Phụ lục 1: trích dẫn trợ giúp của AI)

- **Mục đích:** ghi lại các lần dùng AI (Claude Code) trong dự án, theo `CLAUDE.md` mục *Academic integrity*.
- **Nguồn: CHỈ dữ liệu có trong repo này** — bảng *Session log* của các tệp bàn giao `docs/phien/claude__*.md`, `CHANGELOG.md`, lịch sử git (nội dung commit và dòng `Claude-Session`), các báo cáo trong `docs/phien/bao_cao_dem/` và `docs/ke_hoach/`. Không đọc lịch sử chat. Repo chứa việc của cả tài khoản Truong và tài khoản bạn cộng tác.
- **Phiên cha** = phiên lập kế hoạch / điều phối / soát (Opus), nơi Truong giao việc và chốt quyết định. **Phiên con** = phiên làm theo kế hoạch (Sonnet), chỉ tóm tắt một dòng, không chép lời nhắn.
- **Nguyên văn:** chỉ những chữ repo lưu đúng lời Truong (mục 1). Mọi chỗ khác là *theo ghi chép trong repo* (chép lại dòng ghi chép, có dẫn tệp), không phải lời nhắn nguyên văn. Không đoán, không viết thay.
- **Phạm vi:** `CHANGELOG.md` từ 08/10/2026; lịch sử git từ 24/10/2026 (1047 commit, 176 phiên có dòng `Claude-Session`). Việc trước đó (08–09/2026) chỉ có trong `BAN_GIAO.md` và `KE_HOACH_SUA_THIET_KE.md` (mục 5).
- Chỉ nêu sự việc; không có bình luận hay kết luận nghiên cứu (phần đó học sinh tự viết). Mọi số liệu kiểm thử là dữ liệu MÔ PHỎNG.
- Dựng lại: `python docs/nhat_ky_ai/dung_nhat_ky_ai.py` (nên `git fetch origin` trước). Không có số liệu nào nhập tay.

## 1. Lời Truong được lưu nguyên văn trong repo

- `docs/ke_hoach/FA_DAA_VISION.md`: bản vision FA-DAA của Truong (08/11/2026), chép nguyên văn vào repo (ghi trong tệp bàn giao `claude__keen-ride-72sa7t.md`, mục *Files touched*). Không chép lại ở đây; xem tệp gốc.
- `BAN_GIAO.md` — Yêu cầu của Truong: “Suggest other name for “nguyen vong may thi duoc suat” and include any info that can be added and display using a pie chart”
- `BAN_GIAO.md` — Nhật ký AI: toàn bộ mã trên do AI (Claude) viết theo yêu cầu của Truong: “use this skill to redesign charts and information in the Result sector to be more friendly and helpful for the adminstrator. Define done as Renovate and help display data better”
- `BAN_GIAO.md` — Triệu chứng học sinh báo (lỗi 24, 01/09): “mới cài, mở lần đầu thì thường bị lỗi backend không kết nối được”
- `BAN_GIAO.md` — Học sinh hỏi (lỗi 19, 01/09): “chạy trên máy khác có ra cùng kết quả không?”
- `CHANGELOG.md` — Theo yêu cầu của Truong (28/10/2026, đợt soát A13): “làm bước cuối”
- `docs/ke_hoach/BAO_CAO_SOAT_MA_A13.md` — Bước cuối — skill soat-ma (28/10/2026): “tiếp”
- `docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md` — Soạn 05/11/2026 theo yêu cầu của Truong: “viết prompt và lên kế hoạch nghiên cứu cụ thể các app để bổ sung cho architecture hiện có”

## 2. Chỉ thị và quyết định của Truong (theo `CHANGELOG.md`)

Các mục `CHANGELOG.md` có tiêu đề ghi Truong yêu cầu / duyệt / chọn / quyết định. Chép nguyên tiêu đề (ghi chép của AI trong repo, không phải lời nhắn nguyên văn).

- 25/10/2026 — A13 Điểm Wharton: pipeline tự điền quỹ một CLB trong bộ nhớ (theo quyết định của Truong, cách A)
- 03/11/2026 — T1a, T1b (nhánh `claude/epic-knuth-801pkw`; Truong duyệt, bỏ qua sổ đăng ký)
- 03/11/2026 — T4-K3 (ngoài sổ, Truong duyệt 03/11/2026): skill `xu-li-raw-forms` đọc thư mục nhiều phần CSV
- 04/11/2026 — T4-K1 (ngoài sổ, Truong duyệt 03/11/2026): cột `lop` tuỳ chọn từ `hoc_sinh` tới cột Lớp của Sổ
- 03/11/2026 — A14-B10 (ngoài sổ, Truong duyệt 03/11/2026): bỏ `DROP COLUMN` ở hai test A14 còn lại
- 03/11/2026 — Z-SOAT-2 (ngoài sổ, Truong duyệt 03/11/2026): `soat-ma` tìm ruff trên PATH
- 04/11/2026 — T3-HT (ngoài sổ, Truong duyệt 04/11/2026): hạ tầng tự động hoá T3 (điều phối + viết mã + soát)
- 04/11/2026 — T3-L0 (ngoài sổ, Truong duyệt 04/11/2026): ba lỗi sản phẩm của nghiên cứu T3 (B1/T3-26, B2/T3-01, B3/T3-42)
- 04/11/2026 — T3-L1 (ngoài sổ, Truong duyệt 04/11/2026): chữ và hiển thị nhỏ (nghiên cứu T3, lô 1)
- 04/11/2026 — CI-HUY (ngoài sổ, Truong yêu cầu 04/11/2026): huỷ lượt CI cũ khi có commit mới
- 04/11/2026 — T3-L2 (ngoài sổ, Truong duyệt 04/11/2026): bớt khối, gom nút (nghiên cứu T3, lô 2)
- 04/11/2026 — T3-L3 (ngoài sổ, Truong duyệt 04/11/2026): tên thẻ, thẻ Kết quả gọn, tải bảng, Điểm chuẩn một nơi, chữ Sổ nhập (nghiên cứu T3, lô 3)
- 04/11/2026 — T3-L4 (ngoài sổ, Truong duyệt 04/11/2026): thứ tự tệp "Tải bảng này", bỏ dòng nhắc chết, Điểm chuẩn gọn
- 05/11/2026 — T3-L5 (ngoài sổ, Truong yêu cầu): Điểm chuẩn cùng nền các thẻ khác, thẻ 05 chỉ ghi "Quản lý"
- 05/11/2026 — T4M-NC (ngoài sổ, Truong yêu cầu 05/11/2026): kế hoạch nghiên cứu hệ sinh thái Microsoft của trường
- 05/11/2026 — Z-CLAUDE-GON (ngoài sổ, Truong yêu cầu 05/11/2026; Truong duyệt bản tiếng Anh)
- 05/11/2026 — T4M-Q1, T4M-Q2, T4M-Q3 (Truong duyệt 05/11/2026): chế độ "chỉ thi" của mẫu Microsoft Forms
- 06/11/2026 — T4M-DEMO (Truong duyệt 06/11/2026): chạy thử trọn chuỗi bằng một lệnh
- 06/11/2026 — T4M-NC: Truong duyệt vòng 2
- 08/11/2026 — FA-KH (quyết định của Truong): ngoại lệ bất biến 2 cho huy chương mặc định, D11 không chặn
- 08/11/2026 — FA-M3 (một phần, Truong duyệt): đặt huy chương trên đường B, đủ 6 cách đặt
- 10/11/2026 — FA-9b: biên bản bốc thăm bản Excel (đêm 5, Truong duyệt)
- 10/11/2026 — FA-CI3: CI Windows cài python-docx (PR #14, Truong chọn)
- 10/11/2026 — AI-LOG: nhật ký AI chỉ từ dữ liệu trong repo (Truong yêu cầu)
- 10/11/2026 — FA-KH: hướng dẫn mới nhất cho 7 lỗi nhỏ trước khi merge PR #14 (Truong yêu cầu)
- 12/11/2026 — DOC-FABLE (ngoài sổ, Truong yêu cầu 12/11/2026): tệp bối cảnh dự án + tệp giao việc cho Fable
- 13/11/2026 — GIAM-MAY-RUI-KH (Truong yêu cầu 13/11/2026): kế hoạch giảm may rủi cho Sonnet (chỉ tài liệu)
- 14/11/2026 — FA-SC (mục mới ngoài sổ, Truong duyệt D-SC1): sự cố do con người, phần nghiên cứu
- 15/11/2026 — FA-SC-L5 (FA-SC-10 / P2-1, Truong duyệt 15/11 kể cả bảng mới `stb_buoi`): khoá thứ tự bốc thăm THEO NGÀY
- 18/11/2026 — UX1a: rà soát thao tác người dùng (mục mới UX1, Truong duyệt)

## 3. Các luồng việc: phiên cha và phiên con

Mỗi luồng là một tệp bàn giao (một nhánh). Dòng của phiên cha chép nguyên ô *What was done* của bảng Session log; phiên con lồng dưới phiên cha gần nhất trước nó, mỗi phiên một dòng tóm tắt.

### 01/11/2026 — `claude/demo-wharton-va-duong-dan`
Nguồn: `docs/phien/claude__demo-wharton-va-duong-dan.md`
Mục tiêu (theo tệp bàn giao): A13.13 (continued), branched from claude/wharton-mac-dinh-bat. Two small jobs from the parent session: 1. Demo DB must show commitment points (Wharton ON by default); `--tat-wharton` rebuilds the old DB. 2. Remove hard-coded `/home/user/truong/...` paths in `du_lieu_test/do_do_dai_nguyen_vong.py`.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 01/11/2026 · Sonnet: Both jobs done, tests and ruff green

### 01/11/2026 — `claude/sleepy-sagan-ly5fx0`
Nguồn: `docs/phien/claude__sleepy-sagan-ly5fx0.md`
Mục tiêu (theo tệp bàn giao): Workflow tooling for Claude sessions on this repo (no algorithm change): session handoff files, token-saving rules in CLAUDE.md.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 01/11/2026 · Sonnet: Built handoff scheme, NO SUBAGENT rule, related-tests-only rule, CLAUDE.md trim
  - Phiên con · 01/11/2026 · Sonnet: Rule 11: Opus session creates the branch file from the template

### 01/11/2026 — `claude/wharton-mac-dinh-bat`
Nguồn: `docs/phien/claude__wharton-mac-dinh-bat.md`
Mục tiêu (theo tệp bàn giao): A13.13: the school workspace default `rules.wharton = True` (commitment points / "Wharton" ON by default). Truong approved breaking invariant 1 for this item (recorded in CHANGELOG + TIEN_DO under A13.13). Invariants 2-8 hold. Out of scope: "template header by vocabulary" (Direction A/B).

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 01/11/2026 · Sonnet: Branch + handoff created
  - Phiên con · 01/11/2026 · Sonnet: Implemented A13.13, fixed tests/scripts, parent acceptance suite
  - Phiên con · 01/11/2026 · Sonnet: Round 3 (group A after CI) + round 4 (group B, direction c, demo-branch merge, skills, NHAP_TAY)
  - Phiên con · 01/11/2026 · Sonnet: Final handoff after round 4: 4 red tests fixed, ruff/soat-ma green, report sent to parent
  - Phiên con · 01/11/2026 · Sonnet: Recorded Truong's approval in CHANGELOG; final handoff
  - Phiên con · 01/11/2026 · Sonnet: Full handoff rewrite requested by parent (rule 9, context ~538k)
  - Phiên con · 01/11/2026 · Sonnet: Handoff re-confirmed (hook fired again); nothing new done
  - Phiên con · 01/11/2026 · Sonnet: Session 2 picked up handoff 74ab5bb

### 02/11/2026 — `claude/a14-giao-dien`
Nguồn: `docs/phien/claude__a14-giao-dien.md`
Mục tiêu (theo tệp bàn giao): A14 part B (export + UI for the student class). Part A (branch claude/a14-lop-hoc-sinh) owns DB column students.class_id, chuan_hoa_lop, `cohort` noun and all class APIs. Part B: Excel sheet "Theo lớp" (always), API export_theo_lop (folder, one .xlsx per class), "Lớp" column after "Họ tên" in several tables, and UI (Manager filter/sort/edit, Results filter/sort/export button, kiosk required class dropdown, workspace…

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 02/11/2026 · Sonnet: export + UI + tests written
  - Phiên con · 02/11/2026 · Sonnet: merged A, fixed name clash + filter bug, soat-ma
  - Phiên con · 02/11/2026 · Sonnet: tabs 06/07, lang re-render, export cleanup, tests, soat-ma
  - Phiên con · 02/11/2026 · Sonnet: cross-review fixes B1-B7 (A merged last)
  - Phiên con · 04/11/2026 · Sonnet: Closed docs after PR #6 merge

### 02/11/2026 — `claude/a14-lop-hoc-sinh`
Nguồn: `docs/phien/claude__a14-lop-hoc-sinh.md`
Mục tiêu (theo tệp bàn giao): A14 "Lớp của học sinh" (part A, backend; part B = branch claude/a14-giao-dien does export + UI). Each student may have a class (e.g. 10H1A) used ONLY for display, sorting, filtering and export for homeroom teachers. The allocation algorithm NEVER reads it. DB: `students.class_id` TEXT, NULL = none. New vocabulary noun `cohort` (vi "Lớp", en "Class"). One shared normaliser `rbda_priority_pipeline.chuan_hoa_lop(raw) -…

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 02/11/2026 · Sonnet: Step 1 base
  - Phiên con · 02/11/2026 · Sonnet: Step 2 import/API/docs, old-test fixes, soat-ma
  - Phiên con · 03/11/2026 · Sonnet: C1 label re-save, C2 sample files with simulated classes
  - Phiên con · 02/11/2026 · Sonnet: Cross-review fixes A1-A6
  - Phiên con · 04/11/2026 · Sonnet: Closed docs after PR #6 merge

### 02/11/2026 — `claude/dieu-phoi-a14`
Nguồn: `docs/phien/claude__dieu-phoi-a14.md` (chỉ có trên nhánh `claude/dieu-phoi-a14`)
Mục tiêu (theo tệp bàn giao): A14 "class per student" (Lớp): each student has `students.class_id` used ONLY for display / sort / filter / export to homeroom teachers (GVCN); the allocation never reads it. Opus coordinated two parallel Sonnet sessions (A = base + import + API, B = export + UI + view tabs 06/07), cross-review, fix rounds and final verification.

- **02/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Coordinated A14: spec Q&A, prompts, parallel sessions A/B, cross-review, fix rounds, full-suite verification, PR #6 merged, PR #7 opened and green *(handoff at ~400k tokens)*
- **04/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: PR #7 check-in 1: still green, clean, no reviews; check-in 2 scheduled *(no new work; open a new session)*
- **04/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: PR #7 merged by Truong (05:52Z); unsubscribed, check-in deleted *(A14 closed)*

### 03/11/2026 — `claude/epic-knuth-801pkw`
Nguồn: `docs/phien/claude__epic-knuth-801pkw.md`
Mục tiêu (theo tệp bàn giao): Follow-up to A14 (student class). Branch starts from `claude/a14-giao-dien` (fast-forwarded, includes A14 part A + B). Truong's task file (2026-11-03), explicitly overriding the registry rule (rule 1): - T1a: static sample `mau_csv/SO_NHAP_CLB.xlsx` has no "Lớp" column (software-generated sample has it). Add it and make that file the main sample. - T1b: an old workspace whose saved config already has two nouns with…

- **03/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: ff to a14-giao-dien, wrote plan for T1/T2 *(coordinator session)*
  - Phiên con · 03/11/2026 · Sonnet: T1a, T1b, T2 implemented, tests green, pushed
  - Phiên con · 03/11/2026 · Sonnet: Fix round 1 (F1-F8) from Opus plan
  - Phiên con · 03/11/2026 · Sonnet: Fix round 2 (G1-G3) from Opus plan
  - Phiên con · 03/11/2026 · Sonnet: Fix round 3 (snapshot of Sổ guide text)
  - Phiên con · 03/11/2026 · Sonnet: Handoff at context limit, round 3 committed
  - Phiên con · 03/11/2026 · Sonnet: Final handoff: rounds 1-3 done and reported
  - Phiên con · 04/11/2026 · Sonnet: CON-4: T4 design doc and 5 diagrams, rounds 1, 2, 3b pushed (ca9e161); handoff at context limit
- **04/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Coordinated T3 (closed), T4 design rounds 1-4, T4-K1 (closed); handoff at context limit *(K2 waits on design round 5 (CON-6))*
- **04/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Merged main, resolved 7 conflicts, opened PR #8 (no K2) *(full suite + CI pending at handoff)*
- **04/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Fixed PR #8 CI failures from T4-K1 (baac5d0) *(CI on baac5d0 pending at handoff)*

### 04/11/2026 — `claude/gallant-mendel-uki8j2`
Nguồn: `docs/phien/claude__gallant-mendel-uki8j2.md`
Mục tiêu (theo tệp bàn giao): Execute the T3 UI debloat study (`docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md`) in four lots, automated by a coordinator + implementer + tester chain (protocol: `docs/phien/T3_GIAO_THUC.md`). Item codes: outside the registry, Truong approved 2026-11-04: `T3-L0`..`T3-L3` (one TIEN_DO row each). Display-only changes except L0 B1/B2 backend guards. Algorithm, `match_results`, `run_history`, STB, CSV column contract: untouc…

- **04/11/2026 · Phiên cha · Opus (coord)** — theo ghi chép trong repo: Asked Truong 16 decisions, wrote protocol + plan, role-aware hook

### 04/11/2026 — `claude/gallant-mendel-uki8j2` (impl)
Nguồn: `docs/phien/claude__gallant-mendel-uki8j2__impl.md`
Mục tiêu (theo tệp bàn giao): Implement T3 lots L0..L3 on this branch (spec = "Lot L<n>" in `docs/phien/claude__gallant-mendel-uki8j2.md`; study rows by id: `grep -n "^| T3-26 " docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md`).

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 04/11/2026 · Sonnet (impl 1): L0 implemented, fix1, fixci1
  - Phiên con · 04/11/2026 · Sonnet (impl 1): L1 implemented (`0fd4981`), handoff written
  - Phiên con · 04/11/2026 · Sonnet (impl 3): L2 finished (T3-23, T3-28, T3-21, docs, soat-ma)
  - Phiên con · 04/11/2026 · Sonnet (impl 3): L2 fix1 (6 tester items, 5 done, T3-32 collapse skipped)
  - Phiên con · 04/11/2026 · Sonnet (impl 4): L3 implemented (T3-11/16/17/18/19/22/27/31 + tab names)

### 04/11/2026 — `claude/gallant-mendel-uki8j2` (tester)
Nguồn: `docs/phien/claude__gallant-mendel-uki8j2__tester.md`
Mục tiêu (theo tệp bàn giao): Review each T3 lot diff (L0..L3), run related tests, take <= 6 screenshots per lot, report to coord. Never edit product code/tests.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 04/11/2026 · Opus (tester): L0 review, invariant 1 re-check, 3 screenshots
  - Phiên con · 04/11/2026 · Opus (tester): L0 fix1 re-check
  - Phiên con · 04/11/2026 · Sonnet (tester): L1 + L0fixci1 review, 6 screenshots
  - Phiên con · 04/11/2026 · Sonnet (tester): L1 fix1 re-check
  - Phiên con · 04/11/2026 · Sonnet (tester): L1 fix1 re-check NO BUGS; L2 review
  - Phiên con · 04/11/2026 · Sonnet (tester): Handoff at 200k
  - Phiên con · 04/11/2026 · Sonnet (tester): L2 fix1 re-check, screenshots 01/04/07
  - Phiên con · 04/11/2026 · Sonnet (tester): L3 review, 6 screenshots

### 05/11/2026 — `claude/upbeat-shannon-g5nnms`
Nguồn: `docs/phien/claude__upbeat-shannon-g5nnms.md`
Mục tiêu (theo tệp bàn giao): T4M-NC (outside the 33-item registry; Truong asked 05/11/2026): fit RB-DA into the school's EXISTING Microsoft ecosystem (Power Apps "ECA Registration HVT", M365 A3/A5, PowerSchool sync, IT runs the kiosk). Truong decided the school adopts RB-DA incl. entrance quizzes (Tầng 1) built by our tooling on Microsoft Forms. Plans: `docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md` (research, NC-01..27, prompts P1..P5), `docs/h…

- **05/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Explained T4; gathered school profile via 28 questions; wrote T4M research plan + prompts P1..P4 *(No code changed)*
- **05/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Slimmed prompts + CLAUDE.md; ran GĐ1 + P4 (web docs read, kiosk import contract) *(Key: DVfT + Developer Plan end 15/11/2026; PowerSchool not an SDS OneRoster provider)*
- **05/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Handoff at ~400k context (Stop hook); no new work *(Next: Truong GĐ2 with IT)*
- **05/11/2026 · Phiên cha · Opus+Sonnet** — theo ghi chép trong repo: GĐ2 interview sheet written (by a subagent: rule 10 breach, Truong flagged it; reviewed by Opus); P3 subagent stopped, partial file deleted; P3 moved to a new Sonnet session *(Never use Agent tool; open sessions)*
  - Phiên con · 05/11/2026 · Sonnet: GĐ3 doc (P3 amended): guide, fake Lists-export generator, test first (7 red -> green)
- **05/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong decided: school adopts RB-DA with entrance quizzes (Tầng 1); added NC-23..26 + prompt P5 *(Sonnet P3 session told)*
- **05/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: P5 research (Forms Quiz, Graph, Quick Import, Power Apps quiz); found mau_forms_thi_clb already covers Forms quiz; results §7; interview sheet +4 Qs *(Proposed T4M-Q1..Q3)*
- **05/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong approved T4M-Q1..Q3; opened Sonnet session for them *(Order Q1 -> Q2 -> Q3)*
  - Phiên con · 05/11/2026 · Sonnet: T4M-Q1..Q3 done: quiz-only converter, quiz-only form generator, teacher note; tests first (27), mutation check found missing 200-boundary case, fixed
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed T4M-Q1..Q3 (58 related tests pass, ruff clean, default output identical except docx/xlsx core.xml timestamp); Truong approved T4M-DEMO, Sonnet session opened
  - Phiên con · 06/11/2026 · Sonnet: T4M-DEMO done: fake quiz-only Forms generator, `demo_t4m.py` one-command chain, README 0b; tests first (11), mutation check found 1 weak test (uppercase emails), fixed
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong approved auto chain (bundle design only, GĐ4 v0, auto-run, simulation tables only); wrote T4M_KE_HOACH_TU_DONG.md *(S2 launched)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: S2 T4M-GOI-TK: bundle design doc (two-phase orchestrator, invariants 1/2/3/4/5/8, week-level counter-example, CSV/schema proposal, A8-GOI-1..3 kiem_nhan, ECA questions) *(Design only; no code; 5 decisions for Truong)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed S0 T4M-DEMO (69 tests pass, demo runs, 3 seeded warnings) and S2 (OK); found Lớp gap -> T4M-Q1b; launched S1, S3, S4, Q1b *(S2 D1-D5 await Truong)*
  - Phiên con · 06/11/2026 · Sonnet: S1 T4M-VH done: one-round operations guide for school IT (8 steps)
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed S1 T4M-VH (OK); added --co-so filter to Q1b scope
  - Phiên con · 06/11/2026 · Sonnet: T4M-Q1b: tests first (1 red), converter carries Lớp from Lists into Sổ nhập, demo workaround removed; one old test's expectation updated (test Lists has class 9A1)
  - Phiên con · 06/11/2026 · Sonnet: S4 T4M-DO: simulation grid script, tables, tests first; mutation check caught condition A dropping applicant lists (results no longer depended on seed)
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: S3 T4M-GD4-V0: draft v0 T4M_MICROSOFT.md (P2 under fallback A; two store branches; matrix filled; item codes T4M-M1..M4; T4-K2 options only) *(Docs only; D1-D5 still pending Truong)*
  - Phiên con · 06/11/2026 · Sonnet: T4M-Q1b-b (orchestrator addition): --co-so filter, tests first (4 red -> green), ops guide steps 4-5
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed Q1b (OK, test expectation change justified), S3 (OK, cites DO sections not numbers); S4 sent back: table 2 says 15 clubs with tests, de_thi.json has 10 *(Waiting S4 fix, Q1b-b)*
  - Phiên con · 06/11/2026 · Sonnet: T4M-DO review fix: table 2 exam-club count 15 -> 10, method wording, test that B is Tier 1 for exactly the clubs with de_thi, grid rerun
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed S4 fix (OK) and Q1b-b (OK); chain finished; cancelled check-in; asked Truong pending decisions
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong decided D1-D5 (principle), M1/M3/M4, K2-b, round 2; wrote plan §6; launched R1-R3
  - Phiên con · 06/11/2026 · Sonnet: T4M-M1 (R1): app-edit spec for Top 3 per day, 14 requirements with pass/fail checks
  - Phiên con · 06/11/2026 · Sonnet: T4M-M4 (R3): flow guide for sending per-homeroom Excel to homeroom teachers; docs only
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed R1 T4M-M1 (OK); added HDT §9 rows 5.5 (bilingual) and 5.6 (restore) for R10/R12
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed R3 T4M-M4 (OK; fixed DLP reference NC-16 -> NC-14) *(Waiting R2)*
  - Phiên con · 06/11/2026 · Sonnet: T4M-M3 (R2): `doi_chieu_lists.py` list-export diff tool, tests first (17), ops guide step 8
  - Phiên con · 06/11/2026 · Sonnet: T4M-M3 review fix: raw NV comparison + unknown-code warning headline, tests first (6 red -> green)
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed R2 fix (raw NV compare, warning headline; my false-negative scenario now caught); round 2 finished; 109 related tests pass, ruff clean, kiem_nhanh 7/7 *(Next needs Truong: GĐ2 interviews)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong asked for a quiz portal loop; designed T4M_CONG_THI.md (app as portal, one Form per club, BaiThi status list via standard flow, score via converter); proposed Q4a-c, M5 *(Awaiting Truong approval)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong approved Q4a-c + M5, score level 5a; wrote plan §7; launched C1, C2
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Handoff at ~400k context: rewrote state/next/decisions; round 3 C1, C2 still running; fallback trigger deleted *(New root must poll C1/C2 (they message the old session))*
  - Phiên con · 06/11/2026 · Sonnet: T4M-M5 (C2): Thi tuyển screen spec (§10, R15..R24) + "Đã làm" flow guide; docs only
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Second handoff note: C2 reported DONE (unreviewed); C1 running *(No new work started)*
  - Phiên con · 06/11/2026 · Sonnet: T4M-Q4a/b/c (C1): `--moi-clb` generator, one-club-per-export converter, `--bai-thi` report; tests first (24)
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Third handoff note: C1 also reported DONE (unreviewed) *(Round 3 needs Opus review only)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed round 3 (C1, C2): 134 tests, kiem_nhanh 7/7, outputs identical; added 1 test (mutation survivor), HDT §13 rows 13.1-13.4 (C2 numbering clash); round 3 ticked *(Next: Truong decides PR to main)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong chose cách B; T4M-DEMO-B: demo --moi-clb (tests first, 4 red -> green, 2 mutations caught), interview sheet B3 IT-15..18 *(Next: PR to main?)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Built simulation artifact (cách B); Truong flagged 10 NV / 5 tests / determination points missing; decided 7 NV, tick max 5, points in app (b); wrote plan §8 round 4 *(Launching D1, D2)*
  - Phiên con · 06/11/2026 · Sonnet: T4M-M6 (D2): app spec Top 7, tick max 5, determination-point screen; R25..R38, HDT rows 14.x + section 14; CONG_THI, MICROSOFT, interview sheet
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Updated simulation artifact v2 (Top 7, tick, two funds); reviewed D2 T4M-M6 (OK; R37 no longer counts legit "vắng thi" warnings) *(Waiting D1)*
  - Phiên con · 06/11/2026 · Sonnet: T4M-Q5a/b/c (D1): converter THIk/WPk, fake Lists/Forms with ticks and funds, demo --day-du; tests first (29 red on first run -> all 34 green), 5 mutations caught
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed D1 T4M-Q5a/b/c: tests green after fixing D2/D1 clash (HDT no longer named `NV3`), demo default and --moi-clb outputs identical to before, --day-du runs; kiosk auto-fills single-club fund (confirmed); round 4 done *(Artifact v3 next)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Artifact v4 (demo --day-du numbers); handoff at ~400k context (Stop hook); no new work *(Next: ask Truong about PR to main)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong asked to recreate the simulation page; asked clarifying questions only (no new work, context full) *(New session: get answers first)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong wants the simulation as a real Microsoft system; proposed build kit T4M-BK + own prototype before 15/11; no work started *(Ask Truong which path)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong pointed out he answered earlier; checked §1 of the research plan: path = build kit for IT; NC-02 stays an IT question *(Plan T4M-BK next session)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Wrote plan §9 round 5 T4M-BK (build kit for IT: K0 research, K1/K2 Sonnet, K3 review); asked Truong to approve it and the PR to main *(No code; no child sessions)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong approved T4M-BK + PR: merged main (CHANGELOG both sides, 157 tests pass), opened PR #13; K0 research -> KQ §8; wrote K1/K2 prompts; root session id updated in plan §3 *(Launching K1)*
  - Phiên con · 06/11/2026 · Sonnet: T4M-BK1/BK2 (K1): bo_dung_t4m column module (ECA 30 cols), site script (46 actions), sample CSVs + KIEM_COT_ECA.md, 4 Power Fx files k=1..7; tests first, static syntax t…
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed K1: sent back 2 blocking fixes (accepted 0e8d0ec, launched K2) (site script nesting, addSPField id), 2 minor; corrected §9 decision 1 (Buoi text differs) *(Waiting K1)*
  - Phiên con · 06/11/2026 · Sonnet: K1 fixes after Opus review: site script subactions + $schema + addSPField id, Nhan named formula, xfail -> normal test; tests first (5 red), 2 mutations caught
  - Phiên con · 06/11/2026 · Sonnet: T4M-BK3/BK4 (K2): flow table + one-command kit (4 folders + zip) + HUONG_DAN_IT.md; tests first (25); 3 mutations caught (1 weak test tightened)
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: K3: reviewed K2 979213b (accepted; rule-2 gap noted); round 5 done *(Next: Truong/IT)*
- **06/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Fixed PR #13 CI red (3 causes reproduced locally first); flaky UI test from main split off

### 08/11/2026 — `claude/keen-ride-72sa7t`
Nguồn: `docs/phien/claude__keen-ride-72sa7t.md`
Mục tiêu (theo tệp bàn giao): Implement Truong's FA-DAA vision (`docs/ke_hoach/FA_DAA_VISION.md`, 2026-11-08) for real use THIS term at a school of 500-1000 students on the Microsoft ecosystem: club types FREE / LIMITED / SELECTIVE, three medals per day (60/30/10, one fund) replacing the two-fund determination points, pass mark for SELECTIVE, reserved seats, minimum members, fallback to FREE clubs, a reason for every result, demand table for tea…

- **08/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Read vision + code (priority, wharton, STB, registry A5/A6/A13/C3, T4M); wrote plan, night-run file, handoff *(No code changed; D1 blocked; D8 waits for GĐ2)*
- **08/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Council review applied: D1 reason, D3, D4, D5->FA-9 record, D9, D11, D12 *(Docs only)*
- **08/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong decisions: D2 invariant-2 exception (CLAUDE.md), path B gold-override question, D11 no-block equating, D1 deferred *(Docs + CLAUDE.md only)*
- **08/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Truong: path B second medal question (swap silver/bronze); built `dat_huy_chuong_duong_b`, tests first (19 red -> green), mutation caught 8/19 *(Converter only; not wired; no kiosk/schema/CSV change)*
  - Phiên con · 09/11/2026 · Sonnet: FA-0: venv OK; baseline TestTrungKhit 7 passed, test_wharton_pipeline 29 passed, ruff clean
  - Phiên con · 09/11/2026 · Sonnet: FA-1: rules.fa_daa, 4 club cols, giu_cho, So nhap/CSV optional cols; tests/test_fa_du_lieu.py (43), related 1673 passed, kiem_nhanh 7/7, mutation caught
  - Phiên con · 09/11/2026 · Sonnet: FA-2: kiem_truoc_fa + hooks (pipeline, health); tests/test_fa_kiem_truoc.py (15); related 1823 passed (+1 expected count test, fixed); mutation caught
  - Phiên con · 09/11/2026 · Sonnet: FA-3: huy chuong one fund + submit_huy_chuong + pipeline validation; tests/test_fa_huy_chuong.py (20); related 1992 passed; mutation caught (after adding invalid-value c…
  - Phiên con · 09/11/2026 · Sonnet: FA-4..FA-8 (one commit, overlapping files): chay_fa_daa, minimum-members loop, fa_ly_do, demand table + so_sanh_suc_chua.py, property tests; related 4077 passed (+2 fixe…
  - Phiên con · 09/11/2026 · Sonnet: Night report 2026-11-09: 9/9 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09.md
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Review night 1: GO. Non-UI tests 4981/1 fail/4 skip; fixed `test_van_phong_tu_nhien` (DAA acronym, f9b9031); invariant 1 3x20x2 identical; mutations 5/5; released night 2 in CHAY_DEM_FA_DAA.md *(report bao_cao_dem/2026-11-09_soat_dem1.md; RUNNING line removed)*
  - Phiên con · 09/11/2026 · Sonnet: FA-M1: chuyen_phieu_clb.py + PHIEU_THIET_LAP_CLB.md; tests/test_fa_m1_phieu_clb.py 17; related 201 passed; mutation caught; kiem_nhanh 7/7
  - Phiên con · 09/11/2026 · Sonnet: FA-M2: bieu_mau.cac_phan_fa + tao_mau_forms --fa-daa; tests/test_fa_m2_forms_dang_ky.py 10 (mutation caught after adding the >3-clubs case); related 263 passed; old mode…
  - Phiên con · 09/11/2026 · Sonnet: FA-M3: chuyen_fa_daa (+doc_lists fa, doc_dang_ky_fa_forms, quy_diem_10, co_nhanh_qua); tests/test_fa_m3_chuyen.py 25; related 266 passed; default-mode cells identical; 3…
  - Phiên con · 09/11/2026 · Sonnet: FA-M4: phan_tich_cau_hoi.py + tao_mau_forms --bien-the + converter gate (D11); tests/test_fa_m4_phan_tich.py 24; related 330 passed; old modes identical; 5 mutations cau…
  - Phiên con · 09/11/2026 · Sonnet: FA-M5: T4M_DAC_TA_SUA_APP §12 (R39-R54) + bo_dung_t4m ECA_FA + tao_bo_dung_t4m --fa-daa; tests/test_fa_m5_bo_dung.py 10; related 208 passed (after scoping old R1..R38 te…
  - Phiên con · 09/11/2026 · Sonnet: FA-M6: docs/he_sinh_thai/FA_SAU_XEP.md (docs only) + tests/test_fa_m6_tai_lieu.py 6; related passed; 2 mutations caught; kiem_nhanh 7/7
  - Phiên con · 09/11/2026 · Sonnet: Night 2 report 2026-11-09: 6/6 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem2.md
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed night 2: GO; 6 new bugs + 4 open night-1 findings + 1 email gap listed as FA-S1..S11 (not fixed, Truong's instruction); wrote plan §6 and night-3 protocol *(Repro: FA-S3, FA-S4; 197 related tests pass)*
  - Phiên con · 09/11/2026 · Opus (night 3, Truong asked): FA-S8: CSV club import keeps the row when FA is off; red first, mutation caught
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S7 export latest run only + FA-S9 rollback test; red first; mutations caught (S9: commit before lock -> red)
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S3: N_NHO when either side small; 1 old expectation changed per spec
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S1 retake rule; red first; 2 mutations caught; converter/T4M tests 252 passed
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S5 wrong-variant warning; red first; mutation caught (2 tests)
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S2 --bo-cau per variant; red first; mutation caught
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S4 unreadable quiz times warning; red first; mutation caught
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S6 generator reads club type; red first; mutation caught; without flag diff -r identical
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S11 email join script + EMAIL_MA_HS.csv; red first; mutation caught; new test file (count 217)
  - Phiên con · 09/11/2026 · Opus (night 3): FA-S10 plan §4 D8 path-B row fixed
  - Phiên con · 09/11/2026 · Opus (night 3): FA-UI-1 FA switch in workspace wizard; red first (5/5); mutation caught; ws/wharton UI tests 341 passed after fixing 'em' wording
  - Phiên con · 09/11/2026 · Opus (night 3): FA-UI-2 club table FA columns; red first; mutation caught; related 2334 passed / 1 skipped
  - Phiên con · 09/11/2026 · Opus (night 3): FA-UI-3 medal step; red first (4/5); swap mutation caught; related 2704 passed / 1 skipped after wording fix
  - Phiên con · 09/11/2026 · Opus (night 3): FA-UI-4 reasons column + 2 export buttons; red first; mutation caught; related 2526 passed / 1 skipped
  - Phiên con · 09/11/2026 · Opus (night 3): FA-UI-5 user guide section 15; doc test red first
  - Phiên con · 09/11/2026 · Opus (night 3): Night 3 report 2026-11-09: 16/16 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem3.md
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Reviewed night 3: GO; repro FA-N1 (partial run drops other days' reasons) and FA-N2 (on-site lazy path saves no medals); kiem_nhanh 7/7; wrote plan §7 and night-4 protocol *(UI tests not rerun (playwright install did not finish))*
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Handoff at ~400k context (Stop hook): rewrote Current state; night 4 released, not started *(Next session: Read CLAUDE.md + this file)*
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Gave Truong a night-4 schedule prompt (23:13/01:13/03:13 VN); no new work (context over limit) *(Report may be named 2026-11-09_dem4.md or 2026-11-10_dem4.md)*
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Night 4 running on collaborator side; wrote chained auto plan (Opus review night 4 -> Sonnet night 5) in Next steps *(No task created by this session)*
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Gave Truong a self-review/self-fix loop prompt (two recurring tasks, stop rules in Next steps 5); no new work *(Context over limit)*
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Answered vision coverage (projected after night 5: P1 ~90 %, P2 ~95 %, P3 ~30-40 %, overall ~75-80 %; gaps: real Microsoft test/D8, full CI + Windows build, P3 features, admin dashboard §11). No night-4 commits on this branch yet at 2026-11-09 ~23:00 *(No new work)*
- **09/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Answered: Forms yes (setup form, quizzes, surveys); Power Apps vs Forms-only registration = D8 open; NOT everything in M365 (kiosk + converters run offline on the IT Windows PC, files moved by Excel/CSV) *(No new work)*
  - Phiên con · 09/11/2026 · Sonnet (night 4): FA-N1: per-day latest run reasons + warning; tests/test_fa_n1_ly_do_mot_phan.py 3 (red first); related 1955 passed/1 skipped; mutation caught; kiem_nhanh 7/7
  - Phiên con · 09/11/2026 · Sonnet (night 4): FA-N2: on-site lazy medals saved + follow re-rank (js hcTheoNguyenVong); tests/test_giao_dien_fa_n2_luu_mac_dinh.py 3 Chromium red first; related UI 63 passed; mutation…
  - Phiên con · 09/11/2026 · Sonnet (night 4): FA-N3: fa_can_diem_quyet_tam error code; tests/test_fa_n3_loi_diem_quyet_tam.py 5 red first; related fa+ws 2423 passed (1 count test fixed); mutation caught; kiem_nhanh…
  - Phiên con · 09/11/2026 · Sonnet (night 4): FA-N4: single-variant club retake warning + guide line; tests/test_fa_n4_mot_de_khong_thi_lai.py 3 red first; converter/forms tests 129 passed; mutation caught; kiem_nha…
  - Phiên con · 09/11/2026 · Sonnet (night 4): FA-9: fa_bien_ban.py + export_bien_ban_boc_tham + button; tests/test_fa_bien_ban.py 9 + 1 Chromium; related 112 passed; 2 mutations caught; kiem_nhanh 7/7; pure module w…
  - Phiên con · 09/11/2026 · Sonnet (night 4): FA-10: du_lieu_test/mo_phong_fa_daa.py tables only; tests/test_mo_phong_fa_daa.py 9; 3 mutations caught after adding 2 tests; module written before tests
  - Phiên con · 09/11/2026 · Sonnet (night 4): Night 4 report 2026-11-09: 6/6 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem4.md
- **10/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Status check; recorded Truong decisions (auto review, PR after night 5, D8 waits, Excel lottery record approved); ticked FA-9/FA-10 in Plan *(Docs only)*
  - Phiên con · 10/11/2026 · Sonnet (review, by hand): Reviewed night 4: GO; repro FA-O1 (reason rows sort `chu_nhat` before `thu_2`); biên bản after partial run OK; related 2276 passed, Chromium 7, kiem_nhanh 7/7; wrote pla…
  - Phiên con · 10/11/2026 · Sonnet (night 5): FA-O1: reasons sorted with khoa_sap_buoi; test in test_fa_n1_ly_do_mot_phan.py red first; related 2135 passed/1 skipped; mutation caught; ruff clean
  - Phiên con · 10/11/2026 · Sonnet (night 5): FA-9b: fa_bien_ban.ghi_xlsx + path_xlsx + button/i18n; 5 tests red first + Chromium check; 3 mutations caught (2 unit/API, 1 UI); related 2195 passed/1 skipped; ruff cle…
  - Phiên con · 10/11/2026 · Sonnet (night 5): Night 5 report 2026-11-10: 2/2 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-10_dem5.md
- **10/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Review night 5 (2 trung FA-P1/P2 fixed test-first, mutations caught; 5 nhỏ listed); soat-ma 4 tiers; PR #14 opened; CI fixes FA-CI1..3 *(3x20 seeds identical; Truong chose python-docx on Windows CI)*
- **10/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Vision coverage brief (~70 % overall, ~85 % P1+P2); Truong chose the 8 small review fixes (7 items, FA-P7=SM-3); wrote LATEST_INSTRUCTION.md for his friend's Sonnet run *(Docs only)*
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: SM-1: ghi_xlsx cleans cells via so_excel.lam_sach; 2 tests red first; related 2035 passed/1 skipped (D1 marker); mutation caught; ruff clean
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: FA-P3: get_ly_do_ket_qua returns thieu_buoi; one notice #lyDoThieuBuoi from fa_ly_do_thieu_buoi; 2 API + 1 UI tests red first (FA-off unchanged guard); 2 mutations caught (API, JS); related 2151 passed/1 skipped, Chromium ran; ruff clean
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: FA-P4: tao_ban_ghi sorts days with khoa_sap_buoi; 1 test red first (HTML + xlsx + hash unchanged); mutation caught; related passed; ruff clean
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: FA-P6: _doc_ly_do_moi_nhat sorts days with khoa_sap_buoi; 1 test red first (canh_bao + thieu_buoi); mutation caught; related passed; ruff clean
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: FA-P5: one base name for html+xlsx via _duong_xuat kem_duoi; repro test red first + empty-folder test; mutation caught; related passed; ruff clean
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: SM-2: condition wait (held call settled + DB poll ≤5 s) instead of 800 ms; 5/5 passed in Chromium; all FA UI tests passed *(test-only)*
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: FA-P7/SM-3: danh_sach_seed(n) deterministic; 3 tests red first; mutation caught; --so-seed 20 -> 60/60 identical, 7/7
- **10/11/2026 · Phiên cha · Opus (SOLO, small fixes)** — theo ghi chép trong repo: Small-fix report: 7/7 done, 0 blocked; --so-seed 20 60/60 identical; report docs/phien/bao_cao_dem/2026-11-10_sua_nho.md *(RUNNING line removed)*

### 10/11/2026 — `claude/fa-gaps`
Nguồn: `docs/phien/claude__fa-gaps.md`
Mục tiêu (theo tệp bàn giao): Fill every remaining FA-DAA vision gap (GAP-0 … GAP-14) per `INSTRUCTION_FILL_GAPS.md`: post-allocation changes (adjustment table + replay, attendance, waitlist invites, appeals, round 2), feedback/surveys, next-term capacity, admin dashboard, two-grader deviation, reminders, Power Apps kit, simulation, improvement cycles (measurement mode), D1 memo. Every behaviour behind a new `rules` key defaulting to False; defa…

- **10/11/2026 · Phiên cha · Opus (SOLO)** — theo ghi chép trong repo: F1 setup: branch claude/fa-gaps from keen-ride 60f75a5 *(phase 1 done 7/7)*
- **10/11/2026 · Phiên cha · Opus (SOLO, son hat)** — theo ghi chép trong repo: GAP-0 done: fa_dieu_chinh + vi_tri_hien_tai; 16 tests red first; related 2456 passed/1 skipped; 2 mutations caught; 60/60
- **10/11/2026 · Phiên cha · Opus (SOLO, son hat)** — theo ghi chép trong repo: GAP-1 done: attendance + release; 13 tests red first (3 Chromium); related 4768 passed/4 skipped (D1 marker, numpy, POSIX user); 2 mutations caught; 60/60
- **10/11/2026 · Phiên cha · Opus (SOLO, son hat)** — theo ghi chép trong repo: GAP-2 done: waitlist invites; 10 tests red first (1 Chromium); related 4636 passed/4 skipped; 3 mutations caught; 60/60
- **10/11/2026 · Phiên cha · Opus (SOLO)** — theo ghi chép trong repo: Phase 1 7/7; wave 1 done + GO; wave 2 coded (suites unconfirmed); wave-3 spec draft *(context limit stop)*
- **10/11/2026 · Phiên cha · Opus (SOLO)** — theo ghi chép trong repo: Wave 2 suites + GO; waves 3–4 coded (GAP-7..14); GAP-13 spec edge rule corrected *(suites running)*
- **10/11/2026 · Phiên cha · Opus (SOLO)** — theo ghi chép trong repo: Waves 3–4 reviewed GO; final report; ALL WAVES DONE; draft PR #15 *(handoff (context limit))*

### 11/11/2026 — `claude/forms-gop`
Nguồn: `docs/phien/claude__forms-gop.md`
Mục tiêu (theo tệp bàn giao): Cut IT work on path B (Microsoft Forms) for the club-allocation kiosk: FA-M2b = ONE registration form for all days (`tao_mau_forms.py --fa-daa --mot-bieu-mau`); FA-M6b = ONE "after results" form (3 feedback questions + appeal branch) with one kiosk import button. Spec: `docs/ke_hoach/FORMS_GOP_KE_HOACH.md` (follow exactly). Built on `origin/claude/fa-gaps`. Push only to `claude/forms-gop`; no PR. All numbers SIMULAT…

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 11/11/2026 · Sonnet (forms-gop): FA-M2b: tests red first (13), `cac_phan_fa_gop`, `sinh_dang_ky(mot_bieu_mau)`, `--mot-bieu-mau`; mutation (drop a day) caught by 5 tests; `diff -r` vs snapshot identical
  - Phiên con · 11/11/2026 · Sonnet (forms-gop): FA-M6b: tests red first (22 + 2 UI), reader, API refactor + `nhap_sau_ket_qua_forms`, generator, UI button; mutations (Forms time -> import time; ignore co_sai) caught
  - Phiên con · 11/11/2026 · Sonnet (forms-gop): Section 4: soat-ma review (no high/medium findings), `diff -r` vs snapshot identical, Vietnamese report
- **11/11/2026 · Phiên cha · Opus (forms-gop)** — theo ghi chép trong repo: War room "giảm việc IT vòng 2": 9 redundancies (R1-R9) found; Truong approved FA-M7..FA-M10; wrote `IT_GIAO_DIEN_KE_HOACH.md` *(docs only)*
- **11/11/2026 · Phiên cha · Opus (forms-gop)** — theo ghi chép trong repo: Split phase 2 into 3 parallel prompts (file ownership, marker blocks, G0 sync, integration by A) *(docs only)*
- **11/11/2026 · Phiên cha · Opus (forms-gop)** — theo ghi chép trong repo: No-human-input runbook TU_DONG.md (SOLO / DIEU_PHOI) + AUTO mode in PROMPT_A/B/C *(docs only)*
- **11/11/2026 · Phiên cha · Opus (forms-gop)** — theo ghi chép trong repo: TU_DONG.md: role CHU_TRI (Opus delegates to Sonnet, reviews) + green loop until full suite, coverage, CI and Windows build pass *(docs only)*
- **11/11/2026 · Phiên cha · Opus (forms-gop)** — theo ghi chép trong repo: PROMPT_A/B/C rebuilt: each pasted into an Opus lead that delegates to Sonnet coders and runs its own green loop; A integrates + final green loop *(docs only)*
  - Phiên con · 11/11/2026 · Sonnet coder: CODER session_01TGThn8TcYiUVHyfRHBD82v INTEGRATE DONE 739736e
  - Phiên con · 11/11/2026 · Sonnet coder: CODER session_01TGThn8TcYiUVHyfRHBD82v INTEGRATE-FIX1 DONE 9ac0998
- **12/11/2026 · Phiên cha · Opus (forms-gop)** — theo ghi chép trong repo: Novice walkthrough + senior review (18 findings, browser mode, SIMULATED data); fix plan FG-1…FG-9 written *(D1–D4 approved (all Recommended))*
- **12/11/2026 · Phiên cha · Opus (forms-gop)** — theo ghi chép trong repo: INTEGRATE-2: merged it-ui-b/c, fold, FIX-1 via Sonnet; full suite + CI + Windows build green -> IT-UI GREEN *(5972 passed, cov 93.52 %, 60/60)*

### 11/11/2026 — `claude/it-ui-a`
Nguồn: `docs/phien/claude__it-ui-a.md`
Mục tiêu (theo tệp bàn giao): Worker A: G0 groundwork (code contract shared by workers B and C: `forms_dot.py`, `api_forms.py` FormsMixin, stubs `api_forms_nap.py`/`api_forms_bo.py`, `kiosk.spec`, tab "Chuẩn bị đợt", marker blocks, error codes), then FA-M7 (one source for clubs and exams), then green loop, then Phase 3 integration of `claude/it-ui-b|c` into `claude/forms-gop`. All numbers SIMULATED; all Forms work TH.

- **11/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: Branch + handoff created, BASE recorded
  - Phiên con · 11/11/2026 · Sonnet coder: CODER session_01TGThn85Pq2YHSsR4JaidNW G0 DONE c7b5d1d
  - Phiên con · 11/11/2026 · Sonnet coder: CODER session_01TGThn8yVQTjim3hxvfMDWv FA-M7 DONE d5a303e
  - Phiên con · 11/11/2026 · Sonnet coder: CODER session_01TGThn8yVQTjim3hxvfMDWv FA-M7-FIX1 DONE 414a94c
  - Phiên con · 11/11/2026 · Sonnet coder: CODER session_01TGThn6pDja9nUgPuhpnPyu FIX-1 DONE db76ea9
- **11/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: Green loop on claude/it-ui-a GREEN (round 2); now WAITING_B/C *(CI 43047307624, build 43035758322)*
- **11/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: Phase 3 wait ended (12 wake-ups, no B/C); B, C BLOCKED; INTEGRATE A alone

### 12/11/2026 — `claude/it-ui-b`
Nguồn: `docs/phien/claude__it-ui-b.md`
Mục tiêu (theo tệp bàn giao): FA-M9 (load Forms/List files in the "Chuẩn bị đợt" tab, step 4) and FA-M10 (buttons after allocation, step 5). All numbers SIMULATED; all Forms work TH (not tried on real Microsoft).

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 12/11/2026 · sonnet-5-5 lead: branch created, handoff written
  - Phiên con · 12/11/2026 · sonnet-5-5 coder: SNAPSHOT (53 files) + FA-M9-THUAN (22 tests) + FA-M10-THUAN (7 tests); mutations red
  - Phiên con · 12/11/2026 · sonnet-5-5 coder: FA-M9: api_forms_nap.py (nhan_dien_tep_forms, chuyen_tep_forms, get_forms_nap, lay_so_nhap_nap) + step 4 UI; 19 API + 4 Chromium tests green; mutation ignore lua_chon ->…
  - Phiên con · 12/11/2026 · sonnet-5-5 coder: FA-M10: xuat_ket_qua_list, ai_chua_dang_ky, doi_chieu_hai_lan + step 5 UI; 8 API + 5 Chromium tests green; 2 mutations red
  - Phiên con · 12/11/2026 · sonnet-5-5 lead: 12 wake-ups (07:00-10:57 UTC) waiting for A; forms-gop/it-ui-a unchanged (254) -> BLOCKED

### 12/11/2026 — `claude/it-ui-c`
Nguồn: `docs/phien/claude__it-ui-c.md`
Mục tiêu (theo tệp bàn giao): FA-M8: "Tạo bộ biểu mẫu" button (step 3 of the kiosk tab "Chuẩn bị đợt"): R3 (no answer key on Forms, `dap_an_tren_forms`), R8 (one zip with every form file for the chosen path), R9 (club setup form `sinh_phieu_clb`). All numbers SIMULATED; all Forms work TH (not tried on real Microsoft).

- **12/11/2026 · Phiên cha · opus lead** — theo ghi chép trong repo: branch created from BASE 5196217, handoff written
  - Phiên con · 12/11/2026 · sonnet coder: FA-M8-THUAN: `bm.TIEU_DE_PHIEU_CLB`/`cac_phan_phieu_clb`; in tao_mau_forms.py `sinh_phieu_clb`, `ghi_cai_dat_phieu_clb`, `dap_an_tren_forms` (default True) on ghi_cai_da…
- **12/11/2026 · Phiên cha · opus lead** — theo ghi chép trong repo: review FA-M8-THUAN c9550fa: PASS *(278 related passed; ruff clean; snapshot 8 modes vs BASE identical (xlsx/docx compared without core.xml); mutation re-done by lead -> R3 test red; kiem_nhanh 7…)*
  - Phiên con · 12/11/2026 · sonnet coder: FA-M8 Phase 2: `api_forms_bo.py` (`get_bo_bieu_mau`, `tao_bo_bieu_mau_api`), `js/13_chuan_bi_bo.js` (bước 3), `cb_bo_*` (i18n.js vi+en, khối C), CSS khối C; tests/test_f…
- **12/11/2026 · Phiên cha · opus lead** — theo ghi chép trong repo: review FA-M8 57f4631..959eca9: PASS *(143 related passed (Chromium ran, 0 skipped); ruff clean; snapshot 8 modes identical; UI mutation (always mot_bieu_mau:true) re-done by lead -> red; kiem_nhanh…)*
- **12/11/2026 · Phiên cha · opus lead** — theo ghi chép trong repo: green loop round 1 started
- **12/11/2026 · Phiên cha · opus lead** — theo ghi chép trong repo: green loop round 1: RED (2 ids, same local/CI Linux/CI Windows) *(FIX-1 delegated)*
  - Phiên con · 12/11/2026 · sonnet coder: FIX-1: (1) CLAUDE_CHI_TIET.md hàng `tests/` 254→257 (lệch quyền sở hữu có chủ đích, ghi ở MANH_C.md); (2) vi `cb_bo_ghi` "tệp zip"→"tệp nén" (i18n.js), đoạn hướng dẫn MA…
- **12/11/2026 · Phiên cha · opus lead** — theo ghi chép trong repo: review FIX-1 b641d89: PASS (coder log line above has wrong session id/hash; real: session_01YVAytyWT5up1scxVFbRakd, b641d89) *(2 ids now pass + test_giao_dien_fa_m8_bo (22 passed); ruff clean; kiem_nhanh 7/7; CLAUDE_CHI_TIET diff = one number only. Green loop round 2 started)*
- **12/11/2026 · Phiên cha · opus lead** — theo ghi chép trong repo: green loop round 2 GREEN on b31ffb4 (local, CI 43164264450, Windows build 43171635413) *(STATUS: GREEN)*

### 13/11/2026 — `claude/giam-may-rui`
Nguồn: `docs/phien/claude__giam-may-rui.md`
Mục tiêu (theo tệp bàn giao): Reduce the role of luck without touching the DA core (Truong 2026-11-13, "implement 1 + 2" of Fable G-H): FA-CT1 split a day's seats by demand (report-only suggestion), FA-CT2 "where to add X seats" + teacher export/UI, FA-D7L optional 0.1-step test scores with the pass/fail set exactly unchanged. Registry: A13 sub-items, goal G-D. Spec: `docs/ke_hoach/GIAM_MAY_RUI_KE_HOACH.md` (follow exactly). Branch from `origin/…

- **13/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Plan FA-CT1, FA-CT2, FA-D7L from Fable G-H; rounding proof checked *(report-only seats; option default off)*

### 13/11/2026 — `claude/sg-sua`
Nguồn: `docs/phien/claude__sg-sua.md`
Mục tiêu (theo tệp bàn giao): Fix the 19 findings of Fable's whole-kiosk UI audit ("Soát giao diện kiosk RB-DA", 2026-11-13), most severe first. Spec: `docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md` (follow exactly; items SG-1 … SG-12). Run by three people in parallel (A `claude/sg-a` + integrator, B `claude/sg-b`, C `claude/sg-c`; each person = one Opus lead + Sonnet coder + Sonnet checker): `docs/ke_hoach/SG_SONG_SONG.md`; per-person state in `docs…

- **13/11/2026 · Phiên cha · Opus (forms-gop session)** — theo ghi chép trong repo: Read Fable report, re-checked C1/C2/C3/H1 in code, wrote spec + this handoff *(plan only)*
- **13/11/2026 · Phiên cha · Opus (forms-gop session)** — theo ghi chép trong repo: Truong approved D1–D3; wrote three-role runbook SG_VONG_LAP.md *(plan only)*
- **13/11/2026 · Phiên cha · Opus (forms-gop session)** — theo ghi chép trong repo: Truong chose a 3-way parallel split; wrote SG_SONG_SONG.md, added marker blocks *(no behaviour change)*
- **13/11/2026 · Phiên cha · Opus (forms-gop session)** — theo ghi chép trong repo: Truong: each person = 1 Opus lead managing a Sonnet coder + a Sonnet checker; SG_SONG_SONG.md rewritten *(plan only)*
- **14/11/2026 · Phiên cha · Opus (lead A)** — theo ghi chép trong repo: Persons A, B, C done; merged sg-c and sg-b into claude/sg-sua; folded MANH_* into CHANGELOG/TIEN_DO; test count 293 *(gate next)*
- **14/11/2026 · Phiên cha · Opus (lead A)** — theo ghi chép trong repo: Gate run: full suite 6220 passed / 93.82 % cov, ruff, kiem_nhanh 7/7, integration checker PASS, walkthroughs, generator diff; found PR 17 (wrong base, other session). Handoff at ~400k context *(next: CI read, docs, PR to main)*

### 14/11/2026 — `claude/dreamy-johnson-cgw652`
Nguồn: `docs/phien/claude__dreamy-johnson-cgw652.md`
Mục tiêu (theo tệp bàn giao): Crisis and human-error scenarios for one real allocation round (students, club teachers, GVCN, IT): find what can go wrong when people slip (e.g. a student takes the wrong club's test), how much harm it does, whether the system detects it, and which fix keeps the 8 invariants. Research by Fable; brief `docs/fable/05_CRISIS_BRIEF.md`. Registry: none yet. New item **FA-SC** (outside the registry), approved by Truong 2…

- **14/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Wrote FA-SC Fable brief and handoff *(docs only)*
- **14/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Brief: student journey S8–S29, solution column required per row, prompt updated *(Truong asked for more student-side cases)*
- **14/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: D-SC1 approved; started Fable session (brief §8 prompt) *(Fable branch claude/fable-fa-sc)*

### 14/11/2026 — `claude/fa-sc-sua`
Nguồn: `docs/phien/claude__fa-sc-sua.md`
Mục tiêu (theo tệp bàn giao): FA-SC Phase 1 (approved by Truong 2026-11-14, D-SC1): converter-only fixes from `docs/fable/07_FA_SC_FIX_PLAN.md` §2 (evidence `docs/fable/06_CRISIS_MEMO.md`, drills `du_lieu_test/su_co/`). Code lives under `mau_forms_thi_clb/` (entry `chuyen_fa_daa` in `chuyen_forms_sang_phan_mem.py`, CLI `main`). Kiosk untouched. Every new option defaults OFF; without it the converter output is byte-identical (invariant 1). New sh…

- **14/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: branch setup, lot specs
  - Phiên con · 14/11/2026 · Sonnet (writer/checker): L1 roster input
  - Phiên con · 14/11/2026 · Sonnet (lead): L2-L4 run, final summary

### 14/11/2026 — `claude/fable-fa-sc`
Nguồn: `docs/phien/claude__fable-fa-sc.md`
Mục tiêu (theo tệp bàn giao): FA-SC (new item, outside the registry, approved D-SC1 2026-11-14): human-error and crisis scenarios for one real allocation round. Research only (Fable). Brief: `docs/fable/05_CRISIS_BRIEF.md`. Parent branch: `claude/dreamy-johnson-cgw652` (its handoff holds the Opus plan).

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 14/11/2026 · Fable: Step 1 catalogue memo, handoff
  - Phiên con · 14/11/2026 · Fable: Drills d01–d15, remedy tables, runbook, CHANGELOG/TIEN_DO
  - Phiên con · 14/11/2026 · Fable: Fix plan proposal + per-day lottery prototype

### 15/11/2026 — `claude/determined-allen-kig6ud`
Nguồn: `docs/phien/claude__determined-allen-kig6ud.md`
Mục tiêu (theo tệp bàn giao): Answer the jury feedback on the pre-repo version (technical evidence + role of AI; per-student explanation, bounded criteria config with trials and comparison, school review). This branch holds ONLY the plan (item GT-KH, outside the registry; parents C3, A1, E1, E2). Implementation runs on 3 team branches + 1 integration branch, see `docs/phien/GT_GIAO_THUC.md`. Each GT team branch is created from this branch.

- **15/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Gap analysis, Q&A with Truong, plan + protocol + 3 task files *(docs only)*

### 15/11/2026 — `claude/fa-sc-sua` (impl)
Nguồn: `docs/phien/claude__fa-sc-sua__impl.md`
Mục tiêu (theo tệp bàn giao): FA-SC-L5 (P2-1): per-day lottery lock. Table `stb_buoi(buoi, student_id, so)`; first run = old `sinh_stb_theo_buoi` (byte-identical), later runs keep old students' order every day and insert newcomers uniformly (`chen_stb_cho_hoc_sinh_moi`).

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 15/11/2026 · Sonnet (writer L5): L5 code+tests+drills+CHANGELOG

### 16/11/2026 — `claude/ecstatic-curie-cw61js`
Nguồn: `docs/phien/claude__ecstatic-curie-cw61js.md` (chỉ có trên nhánh `claude/ecstatic-curie-cw61js`)
Mục tiêu (theo tệp bàn giao): New registry item **PA-HC** (Truong approved "mở mục mới", 2026-11-16): in the Power Apps kit for FA-DAA path A (`mau_forms_thi_clb/tao_bo_dung_t4m.py --fa-daa`), an OPTIONAL medal mode with THREE dropdowns per day: "Huy chương vàng trao cho CLB nào?", then silver, then bronze. Each lists the student's ranked clubs of that day (no FREE club), a club picked above disappears below, bronze is hidden when only 2 eligibl…

- **16/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: War room with Truong: build, Power Apps, medals, exam channel; wrote PA-HC plan *(No code)*

### 16/11/2026 — `claude/gt1-giai-trinh`
Nguồn: `docs/phien/claude__gt1-giai-trinh.md`
Mục tiêu (theo tệp bàn giao): GT1 (parent item C3): per-student explanation for ANY run (default RB-DA and FA-DAA). The school can show each student, in plain words, their preferences, the scores/criteria that mattered, each club's capacity and cut-off, constraints, and why they got (or did not get) each club — on screen (admin/teacher), on a printed slip, and by self-lookup with a code. Reports/controls only: no run code path changes (invariant…

- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: Branch + handoff file created *(base 5926107)*
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: WRITER DONE L1 6fda292; REVIEW L1 sent; writer handoff -> writer 2
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: L1 fix1 2ccfd01 NO BUGS; ticked; GO L2
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: L2 fix1 2d2c947 NO BUGS; ticked; GO L3
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: WRITER DONE L3 35a16d2; REVIEW L3; writer 2 handoff -> writer 3
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: L3 NO BUGS; ticked; GO L4 to writer 3
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: L4 1 bug -> FIX L4 r1; checker handoff -> checker 2
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: L4 fix1 NO BUGS; ticked; start CI gate
- **16/11/2026 · Phiên cha · Opus lead** — theo ghi chép trong repo: CI fix1 a3a9cf9; CI green 499edf1; Status DONE; children archived

### 16/11/2026 — `claude/gt1-giai-trinh` (impl)
Nguồn: `docs/phien/claude__gt1-giai-trinh__impl.md`
Mục tiêu (theo tệp bàn giao): GT1 (parent C3): per-student explanation for any run (RB-DA default and FA-DAA). Lots L1-L4 in `docs/ke_hoach/gt/GT1_GIAI_TRINH.md`. Reports/controls only: no run code path changes.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 16/11/2026 · Sonnet writer: L1 done, pushed, reported; handoff at ~200k context
  - Phiên con · 16/11/2026 · Sonnet writer 2: L1 fix1, L2 (+fix1), L3 done and pushed; handoff at ~200k
  - Phiên con · 16/11/2026 · Sonnet writer 3: L4 (+fix1) done, CI fix1 pushed (a3a9cf9); handoff on hook

### 16/11/2026 — `claude/gt1-giai-trinh` (tester)
Nguồn: `docs/phien/claude__gt1-giai-trinh__tester.md`
Mục tiêu (theo tệp bàn giao): Checker for GT1 (per-student explanation, parent C3). Reviews ONE lot diff per `REVIEW L<n> <base>..<head>` from the lead (session_01TGThn8ujS9oohKhbgDiJgD), runs related tests + `kiem_nhanh.py`, tries own edge cases (temp test files, deleted after), writes the verdict below, commits+pushes only this file, reports with send_message in §7 format.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 16/11/2026 · Sonnet checker: L1-L4 reviews; verdicts below; handoff at ~200k tokens

### 16/11/2026 — `claude/gt3-quyen-tai-lieu`
Nguồn: `docs/phien/claude__gt3-quyen-tai-lieu.md`
Mục tiêu (theo tệp bàn giao): GT3 (parents E1-lite, E2; docs outside the registry): two roles (`quan_tri`, `giao_vien`) with passwords, OFF until the first admin account exists; a central permission gate in `PipelineAPI`; an append-only audit log of every write action; and the evidence pack the jury asked for (role of AI, flow diagram, how to run, input data, member-roles template, demo and video scripts). Then the GT3 lead runs integration of G…

- **16/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: Branch + handoff file created
- **16/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: L1-L4 passed checker; CI green on c66889d *(4 writers, 2 checkers (context handoffs))*
- **16/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: §9 watch 16:26-22:26 UTC, GT2 absent; handoff to lead 2 session_01YVAyu27w5WZmfqRfkjo3Av *(context ~400k)*
- **16/11/2026 · Phiên cha · Opus (lead 2)** — theo ghi chép trong repo: Hourly check scheduled task trig_01W71KuYwPkLHj5cSWusJgME (cron 27 * * * *) bound to session_01YVAyu27w5WZmfqRfkjo3Av; GT2 still absent 22:28 UTC *(—)*
- **17/11/2026 · Phiên cha · Opus (lead 2)** — theo ghi chép trong repo: GT2 lead started 02:40 UTC: session_01YVAyu3PPHv9SNntepRSLwh (branch claude/gt2-tieu-chi, not yet pushed); hourly §9 watch continues *(—)*
- **17/11/2026 · Phiên cha · Opus (lead 2)** — theo ghi chép trong repo: 03:27 UTC: origin/claude/gt2-tieu-chi pushed, Status IN PROGRESS (L3) *(—)*
- **17/11/2026 · Phiên cha · Opus (lead 2)** — theo ghi chép trong repo: 04:27 UTC: GT2 Status IN PROGRESS (CI gate) *(—)*
- **17/11/2026 · Phiên cha · Opus (lead 2)** — theo ghi chép trong repo: 05:28 UTC: GT2 DONE 8965d2b (run 44018417803 verified). §9 step 2 started on claude/gt-tich-hop (state in docs/phien/claude__gt-tich-hop.md); hourly watch disabled *(—)*

### 16/11/2026 — `claude/gt3-quyen-tai-lieu` (impl)
Nguồn: `docs/phien/claude__gt3-quyen-tai-lieu__impl.md`
Mục tiêu (theo tệp bàn giao): GT3 writer: implement lots L1-L4 (accounts+login, permission gate, audit log, evidence docs) one at a time on `GO L<n>` / `FIX` from the lead; report only in the protocol section 7 formats (send_message to the lead id).

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 16/11/2026 · Sonnet (writer): L1 implemented, pushed 53e453a, reported to lead
  - Phiên con · 16/11/2026 · Sonnet (writer 2): L1 fix1 (NFC), L2 + fix1 reported; L3 coded and tested, WRITER DONE L3 not sent
  - Phiên con · 16/11/2026 · Sonnet (writer 3): L3 related run + test_ws_nhan fix, L3 fix1, L4 docs; all reported

### 16/11/2026 — `claude/gt3-quyen-tai-lieu` (tester)
Nguồn: `docs/phien/claude__gt3-quyen-tai-lieu__tester.md`
Mục tiêu (theo tệp bàn giao): Review each GT3 lot diff (`REVIEW L<n> <base>..<head>`), run related tests + own edge cases on fake data, write the verdict below, push, then `send_message` the lead (claude-code-remote tool, session_id = lead) with `CHECKER REPORT L<n>`.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 16/11/2026 · Sonnet (checker): Reviewed L1, L2, L3 incl. fix rounds (6 reviews), all NO BUGS at last head

### 17/11/2026 — `claude/gt-hoan-thien`
Nguồn: `docs/phien/claude__gt-hoan-thien.md`
Mục tiêu (theo tệp bàn giao): GT4: fix the problems found by the review of `claude/gt-tich-hop` (`docs/ke_hoach/gt/GT4_RA_SOAT.md`, R0-R10) without touching the allocation core. Base: `origin/claude/admiring-fermat-yf077m` (= `claude/gt-tich-hop` c9e3830 + plan files). Truong merges to `main` himself. No PR.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 17/11/2026 · Sonnet (reviewer): review of gt-tich-hop; plan + prompts written
  - Phiên con · 17/11/2026 · Sonnet (writer): L0-L7 implemented, tested, pushed; waiting for checker; handoff at ~400k context
  - Phiên con · 18/11/2026 · Sonnet (fix session, branch fix-gt4 from 2d6eecf): B1-B3, OL1, OL2 fixed test-first; CI failures of 0325e70 fixed (test_ws_nhan codes, van_phong i18n wording, 2 flaky Chromium tests); CHANGELOG + TIEN_DO updated

### 17/11/2026 — `claude/gt-tich-hop`
Nguồn: `docs/phien/claude__gt-tich-hop.md`
Mục tiêu (theo tệp bàn giao): Integrate GT1 (giải trình, `claude/gt1-giai-trinh` DONE 499edf1), GT2 (tiêu chí, `claude/gt2-tieu-chi` DONE 8965d2b) and GT3 (quyền + tài liệu, `claude/gt3-quyen-tai-lieu` DONE c66889d) on one branch from `origin/main` (35609f7), then run integration lots I1-I4 (spec: `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md` § "Integration lots") and the §6 CI gate. Truong merges to main himself. No PR.

- **17/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: GT2 DONE verified (run 44018417803 success); branch created, GT1 merged, file written *(—)*
- **17/11/2026 · Phiên cha · Opus (orig. GT3 lead)** — theo ghi chép trong repo: I4 fix + 2 CI fixes, CI green 572685d, Status DONE *(integration sessions had stopped on spend limit)*
- **18/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: UX1 opened; UX1a audit written (screenshots, click counts, plan UX1b/UX1c) *(waiting Truong §5 answers)*

### 17/11/2026 — `claude/gt-tich-hop` (impl)
Nguồn: `docs/phien/claude__gt-tich-hop__impl.md`
Mục tiêu (theo tệp bàn giao): Writer for the GT1+GT2+GT3 integration on `claude/gt-tich-hop` (lots I0-I4, spec: Plan in the lead file and `docs/ke_hoach/gt/GT3_QUYEN_TAI_LIEU.md` § "Integration lots"). Setup done: `.claude/phien_vai.json` (`impl`, coord = lead id), `.venv` built from requirements-dev.txt.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 17/11/2026 · Sonnet (writer): I0 merges, I1 QUYEN, I2 student-mode lock + reload fix, soat-ma on I2
  - Phiên con · 17/11/2026 · Sonnet (writer): I2 fix3, I3 (tests only), I4 (ca mau + goi minh chung); soat-ma; handoff at ~200k

### 17/11/2026 — `claude/gt2-tieu-chi`
Nguồn: `docs/phien/claude__gt2-tieu-chi.md`
Mục tiêu (theo tệp bàn giao): GT2 (parents A1, Z7-lite): an authorised admin sees the allocation criteria as a plain ordered list, changes them only within the approved bounded set (D-GT1: lexicographic, existing `rules` keys/values only, no weights, no sensitive data), runs labelled TRIAL allocations (`run_history.loai_chay='thu'`, rows in `ket_qua_thu`) that never touch official results, compares any two runs side by side (totals, per club, pe…

- **17/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: Branch + handoff file created *(GT3 integration without GT2 starts 2026-11-18T16:25Z)*
- **17/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: L1-L4 passed checker; CI green on 8965d2b; Status DONE *(4 writers, 3 checkers (context handoffs))*

### 17/11/2026 — `claude/gt2-tieu-chi` (impl)
Nguồn: `docs/phien/claude__gt2-tieu-chi__impl.md`
Mục tiêu (theo tệp bàn giao): GT2 writer role: implement lots L1-L4 (criteria in plain words, trial runs, compare, adopt), one lot per `GO L<n>` from the lead.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 17/11/2026 · Sonnet (writer): L1 implemented, tested, pushed, reported
  - Phiên con · 17/11/2026 · Sonnet (writer 2): L1 fix1+fix2 passed; L2 coded and tested (25 new), WIP committed
  - Phiên con · 17/11/2026 · Sonnet (writer 3): L2 related run + fix1 passed; L3 coded, tested, pushed, reported

### 17/11/2026 — `claude/gt2-tieu-chi` (tester)
Nguồn: `docs/phien/claude__gt2-tieu-chi__tester.md`
Mục tiêu (theo tệp bàn giao): CHECKER for GT2 (criteria in plain words, trial runs, compare runs, adopt criteria). Reviews ONE lot diff per "REVIEW L<n> <base>..<head>", runs related tests, own edge cases, writes verdict here, pushes only this file, reports to lead in protocol §7 format (send_message to the lead). Never edits product code or tests.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 17/11/2026 · Sonnet (checker 1): Setup; reviewed L1 (3 rounds -> NO BUGS) and L2 (1 minor bug + 1 note)
  - Phiên con · 17/11/2026 · Sonnet (checker 2): L2 fix1 NO BUGS; L3 NO BUGS; L4 1 minor bug reported
  - Phiên con · 17/11/2026 · Sonnet (checker 3): L4 fix1 NO BUGS

### 18/11/2026 — `claude/ux1-a-giao-dien` (impl)
Nguồn: `docs/phien/claude__ux1-a-giao-dien__impl.md`
Mục tiêu (theo tệp bàn giao): UX1 (direct UI, fewer steps), team A: next-step bar, 4-group navigation, Settings = one question with three cards, results page lookup first + one export menu, warnings/medal book (L5, L5b), docs (L8-A). UI/presentation only: default config stays byte-identical (invariant 1), every element id and data-tab kept.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 18/11/2026 · Sonnet 5.5: L1, L2, L2b, L3 (+fix1) coded, tested, pushed; reports sent to lead
  - Phiên con · 18/11/2026 · Sonnet 5.5: L5 coded, regression-fixed, pushed 764c85c, reported to lead
  - Phiên con · 18/11/2026 · Sonnet 5.5: L5b coded + tests; WIP pushed; regression pending
  - Phiên con · 18/11/2026 · Sonnet 5.5: L5b done, pushed 4cae05b, reported
  - Phiên con · 18/11/2026 · Sonnet 5.5: L8-A done (docs, screenshots, After table), pushed ad569c2, reported
  - Phiên con · 18/11/2026 · Sonnet 5.5: L8-A fix1 (32 unplaced, poster line in lead file) pushed 326dbc6, reported
  - Phiên con · 18/11/2026 · Sonnet 5.5: FIX L2b round 2 coded (readiness honesty, pointless actions hidden, Hoàn tác contrast), WIP pushed

### 18/11/2026 — `claude/xp1-xuat-pdf`
Nguồn: `docs/phien/claude__xp1-xuat-pdf.md`
Mục tiêu (theo tệp bàn giao): New item **XP1 — bulk PDF export** (approved by Truong 2026-11-18; new item like UX1, tracked in `TIEN_DO.md`, not in the 33-item registry). For Truong's workflow PDF is THE way data leaves the app, so the admin must be able to export in bulk: (1) **member lists** as PDF, one file per club OR one file per class; (2) **explanation slips** (`phieu giai trinh`) as PDF in bulk, one file per class (or one chosen class),…

- **18/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Created branch from ux1 @66f9ffb; wrote Goal + Plan *(Decisions: reportlab + TTF, Sonnet codes)*
- **18/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Wrote XP1_GIAO_THUC.md (3-session protocol, prompts) *(Lead prompt in §7)*
- **19/11/2026 · Phiên cha · Opus (lead)** — theo ghi chép trong repo: Ran XP1 L1-L5 with coder+checker, CI gate, final review *(3 sessions)*

### 19/11/2026 — `claude/ux1-b-phieu` (impl)
Nguồn: `docs/phien/claude__ux1-b-phieu__impl.md`
Mục tiêu (theo tệp bàn giao): UX1 team B: slip content, summary report, L5c UX fixes. Lot order: L4-B -> L7 -> L5c -> L8-B -> CI gate -> review. No product-logic change; invariant 1 (byte-identical match_results) must stay 7/7.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 19/11/2026 · Sonnet: L4-B, L7 (+2 fixes), L5c; handoff at ~400k context
  - Phiên con · 19/11/2026 · Sonnet: Hook re-fired; no new work since 903bffa; lead said stay available (no replacement session)
  - Phiên con · 19/11/2026 · Sonnet: L5c fix1 (f3ff065); hook re-fired at >400k; lead says no replacement session
  - Phiên con · 19/11/2026 · Sonnet: L8-B (b960b60); hook re-fired at >400k; staying available per lead
  - Phiên con · 19/11/2026 · Sonnet: CI-1: index.html fallback text of group label synced with i18n.js (test_t3_l1_chu_du_phong green)
  - Phiên con · 19/11/2026 · Sonnet: R1 (lead review): FA cutoff column, single MEDAL sentence, report label/case/unit fixes
  - Phiên con · 19/11/2026 · Sonnet: R1 fix2: FA cutoff from stored REJECTED rows (reserve-safe), 3 tests
  - Phiên con · 19/11/2026 · Sonnet: Final: UX1B DONE (CI green eac69df); impl file finalised

### 19/11/2026 — `claude/ux1-tich-hop` (coder)
Nguồn: `docs/phien/claude__ux1-tich-hop__coder.md`
Mục tiêu (theo tệp bàn giao): Integrate UX1 A (new UI), XP1 (PDF export) and UX1 B (slips, teacher role) into one branch. Done; CI green f8ee571.

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 19/11/2026 · Sonnet: I1, I2, I3 (+fix1), I4 fix1

### 20/11/2026 — `claude/inspiring-cori-2za7na`
Nguồn: `docs/phien/claude__inspiring-cori-2za7na.md` (chỉ có trên nhánh `claude/inspiring-cori-2za7na`)
Mục tiêu (theo tệp bàn giao): **GT5 — close the gaps in the round-2 evidence pack** (`docs/giai_trinh/`), parent A1 / GT family (GT1–GT4 done). Reviewers' round-1 feedback (received 15/11) asked for: (1) code, run guide, data/constraints, matching, what happens when seats run out, team roles, where AI is (not) used, flow diagram, anonymised test data, a demo of changing a rule; (2) per-student explanation, bounded configurable "weights", trial c…

- **20/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Audited pack vs. feedback, wrote GT5 plan + protocol *(gaps 1–6 above)*

### 20/11/2026 — `claude/mt1-bo-muc-tieu`
Nguồn: `docs/phien/claude__mt1-bo-muc-tieu.md`
Mục tiêu (theo tệp bàn giao): New item **MT** (outside the registry; Truong approved 2026-11-20; parents C3/A1). Lot **MT1 = goal cards**. The school answers ONE new question in Settings, "Khi một CLB đông người, trường ưu tiên điều gì?", by clicking one of 3 cards. The software sets the existing rules (and, for card 3, suggested reserved seats), shows the effect, and after a run shows one result line: goal met or not, how many helped, how many…

- **20/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: MT0 research, 6 presets, plan + protocol *(on `claude/trusting-bohr-wg0l4n`)*
- **20/11/2026 · Phiên cha · Opus** — theo ghi chép trong repo: Plan rev. 2: UI-first, 3 cards, click budget, UI contract *(Truong: "đồng bộ, không phức tạp, tối giản thao tác")*

### 20/11/2026 — `claude/mt1-bo-muc-tieu` (impl)
Nguồn: `docs/phien/claude__mt1-bo-muc-tieu__impl.md` (chỉ có trên nhánh `claude/mt1-bo-muc-tieu`)

- *(Tệp này không ghi phiên cha; phiên cha nằm ở luồng điều phối khác)*
  - Phiên con · 20/11/2026 · Sonnet (coder): L1–L3 delivered; L4 code + 22 UI tests written
  - Phiên con · 20/11/2026 · Sonnet (coder): L4 verified (153 UI + 204 backend tests, kiem_nhanh 7/7, screenshots) and reported
  - Phiên con · 20/11/2026 · Sonnet (coder): FIX L4 round 1 (0/0 sentence, wizard note, old toast replaced, clearer amber text)
  - Phiên con · 20/11/2026 · Sonnet (coder): FIX L4 fix1b: amber no-gap sentence set to the lead's wording
  - Phiên con · 20/11/2026 · Sonnet (coder): L5 docs: HUONG_DAN 'Chọn mục tiêu', CHANGELOG, TIEN_DO

## 4. Phiên có commit trong git (dòng `Claude-Session`)

Để đối chiếu: mỗi phiên Claude có commit, mã 8 ký tự cuối, ngày, số commit, mã mục trong tiêu đề commit. Repo không ghi phiên nào là cha hay con.

| Mã phiên | Từ | Đến | Số commit | Mã mục (theo tiêu đề commit) | Commit ví dụ |
|---|---|---|---|---|---|
| C3a1YhqF | 24/10/2026 | 24/10/2026 | 1 | — | e08af78 |
| hz6WMv5u | 24/10/2026 | 25/10/2026 | 8 | — | a8b077d 1011f35 fb35974 |
| mCWfrrwL | 25/10/2026 | 25/10/2026 | 6 | A13.3 | 4c448ae dd4a5f3 17497bd |
| JjS1z2mZ | 25/10/2026 | 27/10/2026 | 8 | A13.4 | d85fe2c d54ba04 aa60ebe |
| V9pSwnP8 | 27/10/2026 | 27/10/2026 | 10 | A13.5 | cb53cc0 6ed3718 eb203a7 |
| xJpKsyKc | 27/10/2026 | 27/10/2026 | 1 | — | 11bd6f6 |
| zafjmyBa | 28/10/2026 | 28/10/2026 | 2 | — | a2d8b4b c27ff32 |
| VBKnzq8m | 28/10/2026 | 28/10/2026 | 7 | A13.11 | daff982 77b1cb9 02c3089 |
| 6bVDyWHg | 28/10/2026 | 28/10/2026 | 6 | A13.10 | 43f3f89 5088334 86f7c65 |
| HdJs6TZX | 28/10/2026 | 28/10/2026 | 18 | A13.12 | b045b42 2f4228d e1f6d56 |
| Lys3VpqX | 29/10/2026 | 29/10/2026 | 4 | A13.14, A13.13 | 578af21 b4ffce3 df3eda1 |
| NsHqeuCE | 01/11/2026 | 01/11/2026 | 5 | CLAUDE.md | cee2940 5fd624b 2367a8c |
| ZS4eiU6U | 01/11/2026 | 01/11/2026 | 13 | A13.13 | 2176ee7 74ab5bb 01ea7cd |
| TfR1eikv | 01/11/2026 | 01/11/2026 | 2 | — | 64e47f5 4fe6f56 |
| nvcVK8a9 | 01/11/2026 | 01/11/2026 | 1 | — | 79c8946 |
| gLEyFJQc | 01/11/2026 | 01/11/2026 | 1 | — | a05fc1e |
| tEybZqXm | 02/11/2026 | 04/11/2026 | 14 | A14 | 804d205 0b0991a c3cd884 |
| e9PkriHi | 02/11/2026 | 04/11/2026 | 22 | A14 | 5ad0f18 45c848b 73d8d05 |
| 8cd64rmp | 03/11/2026 | 04/11/2026 | 7 | — | aa48425 baac5d0 930afcd |
| ngVvTQdq | 03/11/2026 | 03/11/2026 | 10 | — | 8ed0a66 cebfa2c 0e56a1b |
| BydGUj7d | 03/11/2026 | 03/11/2026 | 1 | — | 353d1c4 |
| 9KX6VoZF | 03/11/2026 | 04/11/2026 | 5 | T4 | c50d5c0 ca9e161 10a530e |
| yg3WkppJ | 03/11/2026 | 03/11/2026 | 3 | T3 | 0d28de0 7461c0b bfb340f |
| 5ae6dE88 | 03/11/2026 | 03/11/2026 | 9 | Z-SOAT-2, A14-B10, T4, T4-K3 | 373eaf0 fb72a8b 78cb0e7 |
| 4MDFqofZ | 04/11/2026 | 04/11/2026 | 2 | T4-K1 | 85d22ce fff0f41 |
| b4CTcC1X | 04/11/2026 | 04/11/2026 | 1 | — | 00372e0 |
| rzrTqFD7 | 04/11/2026 | 04/11/2026 | 1 | — | a16bf16 |
| 5pa3nYSD | 04/11/2026 | 04/11/2026 | 7 | T3-L4, T3, T3-L1, T3-L0, fixci1 | b17ac78 4aa7ab4 7d1e130 |
| CeJXaN5S | 04/11/2026 | 04/11/2026 | 12 | T3-L4, T3-L3, T3-L2, fix3, T3, fix2, CI-HUY | b9d4e19 1f5903d 384065a |
| zT6ML4Qx | 04/11/2026 | 04/11/2026 | 4 | T3, T3-L2, T3-L1 | fab9f82 9dd8e14 555847d |
| oGYkwnan | 04/11/2026 | 04/11/2026 | 1 | T3-L3 | ad4f227 |
| gz5yriDb | 04/11/2026 | 04/11/2026 | 2 | T3-L3 | 1d5a384 ca81585 |
| wSnLDQPq | 05/11/2026 | 05/11/2026 | 2 | — | 2324aaa ceeeef8 |
| APhazqHY | 06/11/2026 | 06/11/2026 | 9 | T4M-NC, T4M-M4, T4M-M1 | f341694 3b4ef49 790eb4d |
| wrMDXQXg | 06/11/2026 | 06/11/2026 | 1 | T4M-M1 | d78dcc4 |
| na8W6GrA | 06/11/2026 | 06/11/2026 | 1 | T4M-M4 | d8d47c7 |
| MfgeCCPS | 06/11/2026 | 06/11/2026 | 2 | T4M-M3 | 8711ae1 d9d69fc |
| 2dhwkPzs | 06/11/2026 | 06/11/2026 | 1 | T4M-M5 | c4371e4 |
| ACp7Az4F | 06/11/2026 | 06/11/2026 | 2 | T4M-Q4a/b/c | d887988 0b2bbc8 |
| 3oUwVHfW | 06/11/2026 | 06/11/2026 | 11 | T4M-M6, T4M-DEMO-B | 8d2a278 5fa4cc1 5d6654d |
| 2Prtmm9W | 06/11/2026 | 06/11/2026 | 1 | T4M-M6 | 7e31127 |
| JanVM398 | 06/11/2026 | 06/11/2026 | 2 | T4M-Q5a/b/c | befdb1f 7e274d4 |
| ArvejR4i | 06/11/2026 | 06/11/2026 | 9 | T4M-NC, T4M-BK0 | ee81851 28c83dc fe44472 |
| xgM6Qjmx | 06/11/2026 | 06/11/2026 | 2 | T4M-BK1, BK2 | 0e8d0ec 1fb93d0 |
| 1oBj8zhY | 06/11/2026 | 06/11/2026 | 1 | T4M-BK3, BK4 | 979213b |
| LNw3PrRF | 06/11/2026 | 06/11/2026 | 1 | — | 59503b9 |
| PgyEfvMe | 09/11/2026 | 09/11/2026 | 6 | FA-BC, FA-10, FA-9, FA-N3, FA-N4, FA-N2, FA-N1 | 1198ef5 6c7bf4d cf90452 |
| 7JUvpaoF | 09/11/2026 | 10/11/2026 | 5 | AI-LOG, FA-KH | 20332d0 c43d4d9 4adc3eb |
| B56GWZ8J | 10/11/2026 | 10/11/2026 | 6 | FA-BC, FA-9b, FA-O1, FA-O0, FA-SOAT | b93b3d0 d9482a7 fff8df5 |
| TsLFG9TZ | 10/11/2026 | 10/11/2026 | 9 | FA-KH, FA-CI1, FA-CI3, FA-CI2, FA-SOAT, FA-P2, FA-P1 | 1d2aa20 40947ae c6e5e6a |
| xW9hz2Sq | 10/11/2026 | 10/11/2026 | 2 | AI-LOG | 9644288 e6052ec |
| Ne6xXHXP | 10/11/2026 | 11/11/2026 | 6 | FA-KH, GAP-KH | d12835a 19a8f8e fb5815b |
| bwqiigmr | 10/11/2026 | 10/11/2026 | 23 | GAP-KH, GAP-4, GAP-5, GAP-6, GAP-3, GAP-2, GAP-1, GAP-0 | f85c3e7 9b2d588 db043db |
| 52cE6GqX | 10/11/2026 | 10/11/2026 | 21 | GAP-KH, GAP-BC, GAP-14, GAP-13, GAP-12, GAP-4, GAP-11, GAP-8 | 9264f31 3f4f21f e9dde74 |
| JqJkPihi | 11/11/2026 | 11/11/2026 | 3 | FA-BC, FA-M6b, FA-M2b | a8e8f32 fa7d2e0 56fa911 |
| o75CQETh | 11/11/2026 | 12/11/2026 | 12 | FA-BC, FIX-1, INTEGRATE-2, FA-KH | ac47f39 24f5137 d60d221 |
| CZzBpJCq | 11/11/2026 | 12/11/2026 | 10 | FA-KH | 5196217 bfb0bb3 c4ef825 |
| R4JaidNW | 11/11/2026 | 11/11/2026 | 2 | FA-M7, G0 | d731a3d c7b5d1d |
| hxvfMDWv | 11/11/2026 | 11/11/2026 | 4 | FA-M7-FIX1, FA-M7 | ffb8e83 414a94c 4db0c03 |
| PuhpnPyu | 11/11/2026 | 11/11/2026 | 2 | FA-KH | 5ead67e db76ea9 |
| fRHBD82v | 11/11/2026 | 11/11/2026 | 4 | INTEGRATE-FIX1, INTEGRATE | 1c52030 9ac0998 0d74662 |
| 8oSuiyFi | 12/11/2026 | 12/11/2026 | 6 | FA-KH | 0bbe563 b31ffb4 58e75ee |
| tw7iV7Z7 | 12/11/2026 | 12/11/2026 | 3 | FA-M9-THUAN, FA-M10-THUAN | 69e3d00 194d5de 568bd20 |
| cjoTQrMS | 12/11/2026 | 12/11/2026 | 2 | FA-M8-THUAN | c6058ba c9550fa |
| EqWPy8jf | 12/11/2026 | 12/11/2026 | 2 | FA-M9 | cf38ab5 934d031 |
| ZvebVahw | 12/11/2026 | 12/11/2026 | 3 | FA-M8 | 959eca9 14a4435 57f4631 |
| XNUQbYRG | 12/11/2026 | 12/11/2026 | 1 | FA-M10 | b43953c |
| cn7yNVEo | 12/11/2026 | 12/11/2026 | 2 | FIX-1 | fbbb823 e7c5a1f |
| xVFbRakd | 12/11/2026 | 12/11/2026 | 1 | FIX-1 | b641d89 |
| k6hPPupC | 12/11/2026 | 12/11/2026 | 2 | FG-KH | 7555285 4d5bcfe |
| 1Z4aEFSS | 12/11/2026 | 13/11/2026 | 4 | GIAM-MAY-RUI-KH, DOC-FABLE | c1de264 f5e8a41 87b766f |
| uwv2PB8e | 12/11/2026 | 13/11/2026 | 3 | DOC-FABLE | 145da21 d209686 59a0d83 |
| 5sYejKse | 13/11/2026 | 13/11/2026 | 14 | FG, GREEN | 909f8df d73b479 90b2dbf |
| Mfuncuk2 | 13/11/2026 | 13/11/2026 | 3 | FG-5, FG-4 | 684edcd e90555a 5e38fbc |
| t2fs5iQu | 13/11/2026 | 13/11/2026 | 4 | GIAM-MAY-RUI, FA-D7L, FA-CT2, FA-CT1 | 4e133ef 7254539 e2885eb |
| xiBZ3HP2 | 13/11/2026 | 13/11/2026 | 2 | FG-6 | ebc9869 f91d1af |
| K8kCxfWR | 13/11/2026 | 13/11/2026 | 2 | FG-2 | 0668955 9db3039 |
| nk4CKsg9 | 13/11/2026 | 13/11/2026 | 2 | FG-1 | 32d65ba 13e93f3 |
| z5Lj6S7P | 13/11/2026 | 13/11/2026 | 5 | FG-7 | 49328f0 d754dbd 6131243 |
| TkP7cCJi | 13/11/2026 | 13/11/2026 | 2 | FG-8 | b345d0a cd0b2df |
| zaUQr5XA | 13/11/2026 | 13/11/2026 | 2 | FG-9 | 15ebc55 39eb6a5 |
| TxcxNyFF | 13/11/2026 | 13/11/2026 | 2 | FG, FINISH | fdfc3f7 b7c8380 |
| R46EeJMg | 13/11/2026 | 13/11/2026 | 1 | FIX-1 | eddf198 |
| dh2wyyui | 13/11/2026 | 13/11/2026 | 8 | SG-KH, DOC-FABLE | 798eb2f ba4b207 4bcc617 |
| 89pKN66o | 13/11/2026 | 14/11/2026 | 22 | SG-INT, SG-A | 828614e d46ccc7 7d448de |
| TDfW53iL | 13/11/2026 | 13/11/2026 | 1 | SG-1, 1 | 39de078 |
| A1uMuruk | 13/11/2026 | 13/11/2026 | 2 | SG-3 | 6450508 f2e7702 |
| HTFkb9a4 | 13/11/2026 | 13/11/2026 | 1 | SG-3, 0 | c7ff951 |
| LMhnwS9V | 13/11/2026 | 13/11/2026 | 4 | SG-4, FIX-1 | e761f43 17eaf11 b39d2bb |
| a7GNKWsZ | 13/11/2026 | 13/11/2026 | 1 | SG-4, 0 | 98d47ce |
| K4Ce6A5K | 13/11/2026 | 13/11/2026 | 1 | SG-4, 1 | f660d28 |
| wwt7335U | 13/11/2026 | 14/11/2026 | 14 | SG-C | 38dd60e 0992109 286b56b |
| 878jxQF4 | 13/11/2026 | 13/11/2026 | 1 | SG-6 | d6fd6bd |
| UADLpcQk | 13/11/2026 | 13/11/2026 | 2 | SG-10, FIX-1 | d7f5bac 4dad18a |
| FitcHYj9 | 13/11/2026 | 14/11/2026 | 16 | SG-B | de43b90 2165a9f f66ab1d |
| j5e8xu4E | 13/11/2026 | 13/11/2026 | 5 | SG-C, SG-9, FIX-1 | e5747dc c266cae c838080 |
| zKjBUGzq | 13/11/2026 | 13/11/2026 | 3 | SG-B, SG-6, FIX-1 | a782b14 b83651d 297d653 |
| Hn9DjZpt | 13/11/2026 | 13/11/2026 | 1 | SG-10 | c9e1c15 |
| 7uYC28bX | 13/11/2026 | 13/11/2026 | 1 | SG-C | b36b154 |
| UrEroXCZ | 13/11/2026 | 13/11/2026 | 1 | SG-6, 2 | 144fbe6 |
| fK4pvZA2 | 13/11/2026 | 13/11/2026 | 1 | SG-10, 1 | e676654 |
| naoMzV7d | 13/11/2026 | 13/11/2026 | 1 | SG-9, 2 | f84ad66 |
| WaYP2tTL | 13/11/2026 | 13/11/2026 | 3 | SG-11a | cb4f8d6 debf971 103aef6 |
| k3rANq4G | 13/11/2026 | 13/11/2026 | 4 | SG-B, SG-8, FIX-1 | 10cd320 5e47810 bca7728 |
| Ktu6pP4g | 13/11/2026 | 13/11/2026 | 3 | SG-12 | 1be392a a050c69 51c2d25 |
| VP6Wyrys | 13/11/2026 | 13/11/2026 | 1 | SG-B | 2857546 |
| QKBEWwRo | 13/11/2026 | 13/11/2026 | 1 | SG-11a, 0 | 9663436 |
| 9uHdXZyx | 13/11/2026 | 13/11/2026 | 8 | SG-12, FIX-2, FIX-1 | 748d2a9 488a20b ead60df |
| Taybds6n | 13/11/2026 | 13/11/2026 | 1 | SG-B | 2b9eaee |
| CheckerC | 13/11/2026 | 13/11/2026 | 1 | SG-12 | e389b52 |
| xhiYKg2y | 13/11/2026 | 13/11/2026 | 1 | SG-12 | 6c2fb38 |
| 6orU1Yim | 13/11/2026 | 13/11/2026 | 5 | SG-11b, r2, SG-B, FIX-1 | 7b4458c dff2363 29bfa1e |
| TPMw9NsZ | 13/11/2026 | 13/11/2026 | 1 | SG-11b | 501c24f |
| m7PHf7Jq | 13/11/2026 | 13/11/2026 | 1 | SG-12, r2 | 493b8ff |
| CxTDDP4W | 13/11/2026 | 13/11/2026 | 1 | SG-11b, r2 | 6fc7a43 |
| qWMcwnFN | 13/11/2026 | 13/11/2026 | 1 | SG-C | fbd9740 |
| xHWJZn1G | 13/11/2026 | 13/11/2026 | 1 | SG-2, FIX-2 | 690322f |
| 1aNxajw8 | 14/11/2026 | 14/11/2026 | 1 | SG-2, r3 | 837e560 |
| Lhcpe5Hg | 14/11/2026 | 14/11/2026 | 1 | SG-INT | a790b14 |
| Yngw4vjM | 14/11/2026 | 14/11/2026 | 1 | SG-6 | 413ec36 |
| X8QiFtNh | 14/11/2026 | 15/11/2026 | 10 | FA-SC | 7186043 0b7321c 8fc0137 |
| YtTbwpaU | 14/11/2026 | 14/11/2026 | 3 | FA-SC, 3-5, 1 | 222edb7 41b70ab 84940b8 |
| fiJpThan | 14/11/2026 | 14/11/2026 | 4 | FA-SC | 684b897 76b2c45 b0614a3 |
| JPLLF9Ru | 14/11/2026 | 14/11/2026 | 2 | FA-SC-L2, FA-SC-L1 | bca5941 cc2d9a4 |
| M5WpigYs | 14/11/2026 | 14/11/2026 | 1 | FA-SC-L3 | 7c3d3b3 |
| jw3GVFr6 | 14/11/2026 | 14/11/2026 | 1 | FA-SC-L4 | db28790 |
| ttMTk2LY | 14/11/2026 | 14/11/2026 | 1 | FA-SC | 0c81390 |
| BkzjQFwa | 15/11/2026 | 15/11/2026 | 3 | FA-SC | aee944b 68af423 61eedb1 |
| n3aTHjZY | 15/11/2026 | 15/11/2026 | 1 | FA-SC-L5 | adc42d8 |
| rpUnB73L | 15/11/2026 | 15/11/2026 | 1 | FA-SC-L5 | 98b8b09 |
| MPNpoLfb | 15/11/2026 | 15/11/2026 | 1 | FA-SC | 91f3da8 |
| UdC6esKM | 15/11/2026 | 16/11/2026 | 10 | — | 8968657 6cbde69 59c77b1 |
| py9CtCWd | 15/11/2026 | 15/11/2026 | 1 | GT-KH | 5926107 |
| hbgDiJgD | 16/11/2026 | 16/11/2026 | 10 | GT1 | 0f40c79 5c166ce 22561a3 |
| 1TGThTHP | 16/11/2026 | 16/11/2026 | 1 | GT1-L1 | 6fda292 |
| HBdZiZXv | 16/11/2026 | 16/11/2026 | 5 | GT1, GT1-L3, GT1-L2, fix1, GT1-L1 | 0eedd17 35a16d2 2d2c947 |
| JwzjvqVX | 16/11/2026 | 16/11/2026 | 4 | GT1, CI, fix1, GT1-L4 | 499edf1 a3a9cf9 c5621e7 |
| Do4sWuEa | 16/11/2026 | 16/11/2026 | 1 | PA-HC | 174b9ac |
| zADRDejq | 16/11/2026 | 17/11/2026 | 19 | GT, CI, GT-I4, GT3, GT3-L1 | c9e3830 572685d b30faa2 |
| 5L3EVnKE | 16/11/2026 | 16/11/2026 | 7 | GT3, GT3-L3, GT3-L2, GT3-L1 | e3e3202 96095d0 deee200 |
| tSession | 16/11/2026 | 16/11/2026 | 1 | GT3-L1, fix1 | e62e24a |
| Fdiaw85i | 16/11/2026 | 16/11/2026 | 4 | GT3-L3, GT3-L2, fix1 | 385afc1 5208c6d 22fb361 |
| GiQks7T1 | 16/11/2026 | 16/11/2026 | 4 | GT3, GT3-L4, GT3-L3, fix1 | 86826b4 6674e67 ff12579 |
| DYYbTYZt | 16/11/2026 | 16/11/2026 | 3 | GT3, CI, fix2, fix1, GT3-L4 | 8c033b4 1c79f2f 2474f3d |
| Rfkjo3Av | 16/11/2026 | 17/11/2026 | 6 | GT, GT3 | 250b5c5 6f02b5e 8bf5f5c |
| tepRSLwh | 17/11/2026 | 17/11/2026 | 13 | GT2 | 65d20a7 05f4743 f37097b |
| MTkDDtfN | 17/11/2026 | 17/11/2026 | 2 | GT2, GT2-L1 | e4991a3 ecf2130 |
| 7iiw4hsP | 17/11/2026 | 17/11/2026 | 5 | GT2, GT2-L2, GT2-L1 | b34457c 4df1c97 092ec62 |
| QUfsDamp | 17/11/2026 | 17/11/2026 | 3 | GT2-L1, fix2, fix1 | 3f5957c f4c574e 9b67a95 |
| b8oi1vsW | 17/11/2026 | 17/11/2026 | 4 | GT2, GT2-L3, GT2-L2, fix1 | 9947e41 1cca309 e92d544 |
| Lo8qJeao | 17/11/2026 | 17/11/2026 | 3 | GT2, CI, fix1, GT2-L4 | 8965d2b 98ebaaa 20f396d |
| mWkNvEa3 | 17/11/2026 | 17/11/2026 | 1 | GT2-L4 | 8da5a98 |
| rGPtH4ZW | 17/11/2026 | 18/11/2026 | 11 | GT4, 2, I4, I3, I2, fix3, fix1b, fix1 | 89d5921 f45c9e5 4661b7b |
| VW8d9t8v | 17/11/2026 | 17/11/2026 | 2 | GT4 | eb53631 827eb8f |
| 1Qg2gidq | 17/11/2026 | 17/11/2026 | 1 | — | a7773f1 |
| GsXwVf1g | 17/11/2026 | 17/11/2026 | 8 | GT4-L7, GT4-L6, GT4-L5, GT4-L4, GT4-L3, GT4-L2, GT4-L1, GT4-L0 | cc7aa23 f59862a 6ecf9cb |
| eckcwnRR | 18/11/2026 | 18/11/2026 | 2 | GT4 | 2b97c6f 293864d |
| TUoP1bqB | 18/11/2026 | 18/11/2026 | 8 | UX1, UX1a | 407e62c 228666f 169fbb1 |
| jDeXhcVc | 18/11/2026 | 19/11/2026 | 6 | UX1A | 567e0c5 46a048a 3d421e2 |
| 5L6zfZ57 | 18/11/2026 | 19/11/2026 | 8 | UX1A | 4552a96 63b081e 0bc2026 |
| 4PsyTimd | 18/11/2026 | 19/11/2026 | 9 | UX1F, CLAUDE.md, XP1, UX1B, UX1A-L2b, fix4, fix3 | 7fda9bd dc4cff7 396509b |
| aGiBWkze | 19/11/2026 | 19/11/2026 | 9 | XP1 | f7f1db6 0a62915 2b42e89 |
| 4dXBTk72 | 19/11/2026 | 19/11/2026 | 11 | XP1-L5, fix3, fix2, XP1-L4, XP1-L3, XP1-L2, XP1-L1, fix1 | 81f26e9 c68076a 1c0b48c |
| 1fcHGdde | 19/11/2026 | 19/11/2026 | 23 | UX1B, R1, fix2, CI-1, UX1B-L8-B, UX1B-L5c, fix1, UX1B-L7 | c618629 b510dbf eac69df |
| AYVAYVAJ | 19/11/2026 | 19/11/2026 | 1 | UX1B-L4-B | 0f73c43 |
| YVAstS8t | 19/11/2026 | 19/11/2026 | 9 | UX1B | 385f5f6 cb7ed01 dd521f4 |
| TgfwCCGj | 19/11/2026 | 19/11/2026 | 11 | UX1I-I4, UX1I-I3, UX1I-I2, UX1I, UX1I-I1 | a9266db 147fdbb 6a631ce |
| 178zVkKz | 19/11/2026 | 19/11/2026 | 7 | UX1I, UX1I-I4, fix1, UX1I-I3, UX1I-I2, UX1I-I1 | 4beb03e b0b357c b2f7f8b |
| wtD3Z9GW | 19/11/2026 | 19/11/2026 | 6 | UX1I, UX1I-I4, UX1I-I3, UX1I-I2, UX1I-I1 | 49fe99f f8ee571 0619ab5 |
| CXj6dH9h | 19/11/2026 | 19/11/2026 | 1 | UX1B | 71e2a86 |
| td4gEvz4 | 19/11/2026 | 20/11/2026 | 7 | UX1F, UX1F-L5 | 5c1829a 3306876 eafe684 |
| 5P1azpLB | 19/11/2026 | 20/11/2026 | 6 | UX1F-L4, UX1F-L3, UX1F-L2, UX1F-L1 | 252466e 567ac43 f4be762 |
| 7tBYx1dE | 20/11/2026 | 20/11/2026 | 1 | GT5-KH | beb36b7 |
| wihGK5vS | 20/11/2026 | 20/11/2026 | 4 | MT1, 2, MT0 | 4373a46 4dab8bf d96a248 |
| vuf2JfSJ | 20/11/2026 | 20/11/2026 | 10 | MT1 | 51ba743 6c4950d 298dc0f |
| FwKrtDKm | 20/11/2026 | 20/11/2026 | 18 | MT1, CI-fix1, fix3, MT1-L4, fix2, MT1-L5, fix1, fix1b | 37e4bca b1e1101 dd81704 |

## 5. Trước lịch sử git (trước 24/10/2026, theo `CHANGELOG.md`)

Repo không giữ phiên hay commit của giai đoạn này. Nhật ký AI đã có sẵn từ trước:

- `KE_HOACH_SUA_THIET_KE.md` §11 *AI-log entries for the executed tasks* (27–28/09/2026): bảng việc, tệp AI viết mới, mã học sinh viết bị sửa. Mẫu ghi nhật ký: cùng tệp §7.
- `BAN_GIAO.md` §2 *Trạng thái hiện tại*: các đoạn "Nhật ký AI" theo từng việc (08–09/2026); §6 quy định dùng AI của Sở GD&ĐT.

Tiêu đề mục `CHANGELOG.md` trước lịch sử git:

- 08/10/2026 — Giai đoạn 0 (chỉ đọc và đo)
- 08/10/2026 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)
- 08/10/2026 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 4 (/code-review trên vòng 3: 9 điểm, sửa 8, bác một phần 1)
- 09/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng A (2 lần /code-review trên 2386dd7: 20 điểm ~15 khác nhau)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng B (/code-review trên vòng A: 7 điểm, sửa 5, bác 2)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng C (/code-review trên vòng B: 8 điểm, sửa 7, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng D (/code-review trên vòng C: 6 điểm, sửa 6)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng E (/code-review trên vòng D: 8 điểm, sửa 7, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng F (/code-review trên vòng E: 7 điểm, sửa 6, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng G (/code-review trên vòng F: 8 điểm, sửa 7, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng H (/code-review trên vòng G: 6 điểm, sửa 6)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng I (/code-review trên vòng H: 9 điểm, sửa 8, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng J (/code-review trên vòng I: 9 điểm, sửa 9)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng K (/code-review trên vòng J: 10 điểm, sửa 9, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng L (/code-review trên vòng K: 9 điểm, sửa 8, sửa một phần 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng M (/code-review trên vòng L: 10 điểm, sửa 9, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng N (/code-review trên vòng M: 8 điểm, sửa 5, bác 3)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng O (/code-review trên vòng N: 7 điểm, sửa 5, bác 2)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng P (/code-review trên vòng O: 7 điểm, sửa 7)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng Q (/code-review trên vòng P: 7 điểm, sửa 5, bác 2)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng R (/code-review trên vòng Q: 6 điểm, sửa 5, bác 1)
- 10/10/2026 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng S (/code-review trên vòng R: 6 điểm, không lỗi đúng/sai — vòng sạch)
- 14/10/2026 — Workspace: ghép các nhánh và vòng sửa lỗi sau review (/code-review trên 4 nhánh)
- 14/10/2026 — Workspace: vòng sửa lỗi thứ ba (hai lượt /code-review cuối, trước khi gộp vào main)
- 14/10/2026 — Sửa lỗi CI Windows của PR #1 (24 test đỏ; Linux đạt)
- 15/10/2026 — Skill `tao-workspace-tu-raw` và hai bộ dữ liệu thử (ngoài sổ đăng ký, theo yêu cầu chủ dự án)
- 15/10/2026 — Workspace: Việt hoá sạch màn chọn và sửa bảng (ngoài sổ đăng ký, theo yêu cầu chủ dự án; chồng lấn Z1)

---
Dựng bằng `docs/nhat_ky_ai/dung_nhat_ky_ai.py` (tệp bàn giao, `CHANGELOG.md`, `git log --all`).
