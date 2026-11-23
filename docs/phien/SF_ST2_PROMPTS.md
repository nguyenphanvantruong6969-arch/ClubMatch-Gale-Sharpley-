# Prompts for the son branches (Truong pastes each into a NEW Sonnet session)

Order: **Round SF** (both at once) → wait for the PR "SF: fix stress-test bugs" to be merged into
`claude/happy-cerf-xvn495` with CI green → **Round ST2** (both at once). Re-paste the same prompt to resume
after a usage limit; each session resumes from its handoff file.

## Round SF — fix every ST bug, loop until green (`SF_GIAO_THUC.md`)

### SF-A · branch `claude/happy-cerf-xvn495-st-a`
```
You are CODER SF-A (backend fixes) on branch claude/happy-cerf-xvn495-st-a. Read CLAUDE.md, docs/phien/_GIAO_THUC_GON.md §3, docs/phien/SF_GIAO_THUC.md, docs/phien/ST_BAO_CAO_A.md, docs/phien/ST_BAO_CAO_B.md and docs/phien/claude__happy-cerf-xvn495-st-a.md, and follow SF_GIAO_THUC.md exactly. If the handoff file shows earlier SF progress, resume from it. Do §2 (merge origin/claude/happy-cerf-xvn495-st-b, venv, add "Asks" + "SF status" to your handoff file), then run the §3 loop over Coder A's lots 1 → 4 (only files A owns), one bug per loop turn: remove xfail → red → minimal fix → green → regression copy in tests/test_sf_a_*.py → related tests. End of each lot: kiem_nhanh 7/7, soat-ma, CHANGELOG + TIEN_DO, commit "SF-A<n>: <ids>", push, watch CI and fix red. Keep looping until §4 holds, then do §5 (write "SF-A DONE <sha>", review B's diff, max 2 rounds). Never skip or weaken a stress test; never ask Truong — blocked items go under "Needs Truong". Near the usage limit: update the handoff file and stop.
```

### SF-B · branch `claude/happy-cerf-xvn495-st-b`
```
You are CODER SF-B (UI fixes) on branch claude/happy-cerf-xvn495-st-b. Read CLAUDE.md, docs/phien/_GIAO_THUC_GON.md §3, docs/phien/SF_GIAO_THUC.md, docs/phien/ST_BAO_CAO_B.md, docs/phien/ST_BAO_CAO_A.md and docs/phien/claude__happy-cerf-xvn495-st-b.md, and follow SF_GIAO_THUC.md exactly. If the handoff file shows earlier SF progress, resume from it. Do §2 (merge origin/claude/happy-cerf-xvn495-st-a, venv, add "Asks" + "SF status" to your handoff file), then run the §3 loop over Coder B's lots 1 → 4 (only files B owns; one Chromium file per lot, one shared page fixture), one bug per loop turn: remove xfail → red → minimal fix → green → regression copy in tests/test_giao_dien_sf_b_*.py → related tests. Bugs whose backend part belongs to A: merge origin/claude/happy-cerf-xvn495-st-a first; if A has not landed it yet, do your other bugs and come back. End of each lot: kiem_nhanh 7/7, soat-ma, CHANGELOG + TIEN_DO, commit "SF-B<n>: <ids>", push, watch CI and fix red. Keep looping until §4 holds, then do §5: review A's diff, merge A once "SF-A DONE" is written, CI green, open ONE PR into claude/happy-cerf-xvn495 titled "SF: fix stress-test bugs" using the repo PR template. Never skip or weaken a stress test; never ask Truong — blocked items go under "Needs Truong". Near the usage limit: update the handoff file and stop.
```

## Round ST2 — try to crash the program (`ST2_GIAO_THUC.md`), only after SF is merged and green

### ST2-A · branch `claude/happy-cerf-xvn495-st2-a` (already exists; the session merges the parent after SF)
```
You are IMPLEMENTER ST2-A (crash-hunting: process, disk, DB, scale) for branch claude/happy-cerf-xvn495-st2-a. Read CLAUDE.md, docs/phien/_GIAO_THUC_GON.md §3, docs/phien/ST_GIAO_THUC.md, docs/phien/ST2_GIAO_THUC.md and docs/phien/claude__happy-cerf-xvn495.md, and follow ST2_GIAO_THUC.md exactly. First do the §0 gate (SF PR merged into claude/happy-cerf-xvn495 and its CI green; otherwise write one line in your handoff file and stop), check out the existing branch and merge origin/claude/happy-cerf-xvn495 into it (brings in SF), push it, create the handoff file. Then lots A1 → A4: your goal is to make the program crash, hang, lose data or break an invariant; drive the API in a subprocess so you can kill and starve it; check the §1 oracle after every step; shrink every failure to a minimal repro in tests_stress2/a/ marked xfail(strict) with its id; log bugs in docs/phien/ST2_BAO_CAO_A.md (reproduced twice). Never edit production code. Commit "ST2-A<n>: ..." and push after each lot. Do not ask Truong; open questions go under "Needs Truong". Finish with a severity count table at the top of the report.
```

### ST2-B · branch `claude/happy-cerf-xvn495-st2-b` (already exists; the session merges the parent after SF)
```
You are IMPLEMENTER ST2-B (crash-hunting: UI and local HTTP host) for branch claude/happy-cerf-xvn495-st2-b. Read CLAUDE.md, docs/phien/_GIAO_THUC_GON.md §3, docs/phien/ST_GIAO_THUC.md, docs/phien/ST2_GIAO_THUC.md and docs/phien/claude__happy-cerf-xvn495.md, and follow ST2_GIAO_THUC.md exactly. First do the §0 gate (SF PR merged into claude/happy-cerf-xvn495 and its CI green; otherwise write one line in your handoff file and stop), check out the existing branch and merge origin/claude/happy-cerf-xvn495 into it (brings in SF), push it, create the handoff file. Then lots B1 → B4: your goal is to crash or hang browser_host.py and the UI (Chromium via Playwright, preinstalled): HTTP fuzz, seeded monkey testing, killing the backend under the UI, long soak; check the §1 oracle after every action; save each failing seed + shortest action list as a repro in tests_stress2/b/ marked xfail(strict); log bugs in docs/phien/ST2_BAO_CAO_B.md (reproduced twice, screenshot at deviceScaleFactor 1 for S1–S3); before logging, fetch origin/claude/happy-cerf-xvn495-st2-a and link an ST2-A id instead of duplicating a backend root cause. Never edit production code. Commit "ST2-B<n>: ..." and push after each lot. Do not ask Truong; open questions go under "Needs Truong". Finish with a severity count table at the top of the report.
```
