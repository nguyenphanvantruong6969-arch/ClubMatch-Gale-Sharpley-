# Branch handoff: claude/determined-allen-kig6ud

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Answer the jury feedback on the pre-repo version (technical evidence + role of AI; per-student explanation, bounded
criteria config with trials and comparison, school review). This branch holds ONLY the plan (item GT-KH, outside the
registry; parents C3, A1, E1, E2). Implementation runs on 3 team branches + 1 integration branch, see
`docs/phien/GT_GIAO_THUC.md`. Each GT team branch is created from this branch.

## Plan (written by Opus)
- [x] Gap analysis feedback ↔ repo (`docs/ke_hoach/GT_KE_HOACH.md` §1)
- [x] Decisions with Truong (D-GT1…D-GT9 in the protocol §0)
- [x] Protocol for 3 teams × (Opus lead, Sonnet writer, Sonnet checker): `docs/phien/GT_GIAO_THUC.md`
- [x] Task files: `docs/ke_hoach/gt/GT1_GIAI_TRINH.md`, `GT2_TIEU_CHI.md`, `GT3_QUYEN_TAI_LIEU.md`
- [ ] Truong's collaborators start the 3 leads with the protocol §11 lead prompt (K = 1, 2, 3)

## Current state (overwrite each handoff)
- Done so far: plan docs, CHANGELOG + TIEN_DO row GT-KH. No code changed.
- In progress: none.
- Tests: none run (docs only).
- Open problems: none.

## Decisions and gotchas (keep short)
- Weights: bounded lexicographic only (existing `rules` keys), no weighted sum (D-GT1).
- Trial runs are labelled rows in `run_history` (`loai_chay='thu'`) + `ket_qua_thu`; every "latest run" reader must
  skip them (GT2 L2 risk).
- Default RB-DA mode has NO reasons today (only FA mode) — GT1 L1 builds them.
- Accounts OFF until the first admin exists, so invariant 1 and existing tests hold.
- Schema changes approved by Truong 2026-11-15 (D-GT8); CSV contract unchanged.
- Deadline ~1 week; lots ordered so the jury-visible parts land first (D-GT9).

## Next steps (ordered)
1. Collaborators run the three lead prompts (protocol §11). Nothing else on this branch.
2. GT3 lead integrates on `claude/gt-tich-hop` (protocol §9); Truong merges to main.

## Files touched
- docs/ke_hoach/GT_KE_HOACH.md: gap table, structure, risks
- docs/ke_hoach/gt/GT1_GIAI_TRINH.md, GT2_TIEU_CHI.md, GT3_QUYEN_TAI_LIEU.md: lot specs with "Done when"
- docs/phien/GT_GIAO_THUC.md: run protocol, prompts, CI gate, integration
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: GT-KH entry

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-15 | Opus | Gap analysis, Q&A with Truong, plan + protocol + 3 task files | docs only |
