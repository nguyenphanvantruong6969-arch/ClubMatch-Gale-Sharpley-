# GT — Giải trình & bằng chứng (plan answering the jury feedback)

> Opus plan, 2026-11-15, branch `claude/determined-allen-kig6ud`. Decisions D-GT1…D-GT9 and the run protocol:
> `docs/phien/GT_GIAO_THUC.md`. Lot specs: `docs/ke_hoach/gt/GT1_*.md`, `GT2_*.md`, `GT3_*.md`. English (cheap).

## 1. Feedback → current state (checked against the repo at `35609f7`)
| Jury asks for | State | Where it is / what is missing | Team |
|---|---|---|---|
| Source code, history | done | 637 commits, `CHANGELOG.md`, `TIEN_DO.md` | — |
| How to run | partly | `README.md`, `HUONG_DAN_CAI_DAT.md`; no single short "run + demo" page | GT3 L4 |
| Anonymous test data | done | `du_lieu_test/SO_NHAP_*` (simulated) | — |
| Input data, constraints, matching algorithm, full clubs | mostly | `docs/CO_CHE_THUAT_TOAN.md`, waitlist `fa_sau_xep.hang_cho` | GT3 L4 |
| Flow diagram | missing | pipeline order only in text (invariant 5) | GT3 L4 |
| Which part uses AI | missing | software has **no AI/ML** (deterministic DA + STB); AI only assisted coding (`docs/nhat_ky_ai/`) | GT3 L4 |
| Member roles | missing | 2 members (code / research) — template only, students fill it | GT3 L4 |
| Why each student got / did not get a club | partly | FA mode only: `fa_daa.ly_do_ket_qua` → `fa_ly_do.cau_ly_do`, column "Lý do" + `ket_qua_ly_do.csv`. Default RB-DA mode: **no reason at all**. No per-student screen, slip or self-lookup | GT1 |
| Authorised admin configures criteria within transparent limits | partly | workspace `rules` already bounded (`LUAT_XEP_MAC_DINH`, validated in `cau_hinh_ws._chuan_hoa`); no plain "order of criteria" view, no roles | GT2 L1, GT3 |
| Try different configurations, see the change | missing | no trial run, no comparison | GT2 L2–L4 |
| Avoid sensitive personal data | done by design | invariant 2; make it a test + a sentence in the docs | GT2 L1, GT3 L4 |
| School keeps the right to review | done | appeals / adjustments (`fa_sau_xep`, `tests/test_fa_gap3_khieu_nai.py`); `run_history` never deleted | GT3 L4 (document) |
| Cases with explanations, weight table + changed results, missing data, conflicting criteria | missing | needs GT1 + GT2 output | Integration I4 |

## 2. Structure (new pieces only)
```
                     ┌───────────────────────── GT3: tai_khoan.py (accounts, pbkdf2) ──────────────┐
UI (index.html, js/) │  login → role → permission map (PipelineAPI gate) → nhat_ky_thao_tac (audit)│
                     └──────────────────────────────────────────────────────────────────────────────┘
 js/14_giai_trinh.js ── get_giai_trinh_hoc_sinh ── giai_trinh.py (pure) ── reads match_results, run_history,
   lookup / slip /      export_phieu_giai_trinh                              fa_ly_do (FA) or recomputed
   student mode         tra_cuu_hoc_sinh (code)  ── ma_tra_cuu table         priority (RB-DA); sentences in
                                                                               fa_ly_do.py (one source)
 js/15_tieu_chi.js  ── mo_ta_tieu_chi / run_thu / so_sanh_lan_chay ── tieu_chi.py (pure) ── run_history.loai_chay,
   criteria / trial /                                                              ket_qua_thu (never match_results)
   compare
 docs/giai_trinh/   ── VAI_TRO_AI, SO_DO_LUONG(.svg), HUONG_DAN_CHAY, DU_LIEU_DAU_VAO, PHAN_CONG (template),
                       KICH_BAN_VIDEO, KICH_BAN_DEMO, CA_MAU (generated), GOI_MINH_CHUNG.docx/.pdf (generated)
```

## 3. Order and dependencies
- GT1, GT2, GT3 run in parallel on separate branches (namespaces in the protocol §1 avoid collisions).
- Cross-team wiring is deferred to integration (`claude/gt-tich-hop`, GT3 lead): I1 permissions for GT1/GT2 APIs,
  I2 student-mode exit behind admin login, I3 audit of trial runs / code generation, I4 case + evidence pack.
- If time runs out, the lowest-priority lots are: GT1 L4 (self-lookup; slips cover it), GT2 L4 (apply button),
  GT3 L3 viewer UI (log table still written).

## 4. Risks
| Risk | Guard |
|---|---|
| Trial rows confuse "latest run" readers (`api.py`, `api_xuat.py`, `fa_sau_xep.py`, `api_sau_xep.py`, `rbda_priority_pipeline.py`) | GT2 L2 filters `loai_chay IS NULL` at every reader; snapshot test of all `get_*` before/after a trial |
| RB-DA reasons wrong or inconsistent with the result | GT1 L1 property test against `verify_stability` on 3 datasets × seeds |
| Leaking other students' data in explanations | privacy test: response JSON / slip contains no other student_id or name |
| Login locks the school out | accounts OFF by default; last admin cannot be deleted; reset via `recovery.py` with backup |
| Breaking byte-identity | everything defaults OFF; `kiem_nhanh.py` every lot |
| Academic integrity | docs are operational; no conclusions; every number labelled SIMULATED; role table filled by students |
