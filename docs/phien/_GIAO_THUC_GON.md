# Lean protocol template (Truong, 2026-11-21) — use for every NEW item

> Why: UX2 (11 small UI changes) ran 3 sessions × 9 lots × per-lot review = 17 checker reports, ~38 fix commits,
> and hit the usage limit. Cost grows with (sessions × lots × review rounds × context size). Cut all four.
> Planning Opus writes `docs/phien/<ITEM>_GIAO_THUC.md` from THIS file (short; refer here, do not copy it).

## 1. Size the team to the item (planner picks one, writes it in the protocol)
| Size | Example | Sessions | Review |
|---|---|---|---|
| S | ≤ 3 UI/doc changes, no backend | 1 Sonnet coder | self-check + Truong tries it |
| M | UI/UX item, export, report (UX2, XP1) | coder (Sonnet) + checker (Sonnet), NO lead: coder runs the CI gate | checker at 2 milestones |
| L | touches algorithm, pipeline, schema, invariants 1–5 | lead + coder + checker (lead may be Sonnet; Opus only if design decisions remain) | checker every lot |
- For M, Truong starts the checker by pasting its prompt when the coder writes `MILESTONE <k> READY`.

## 2. Lots
- At most **4 lots** per item; group by shared helper / file area, not by feature number.
- Mark which lots are must-ship and which are optional; optional lots may be dropped without asking.
- Max **2** FIX rounds per review, then "Needs Truong" + `git revert` of that lot, move on.

## 3. Token budget rules (every session)
- Read by function name: `grep -n` then `sed -n a,b` ≤ 80 lines. Never print whole `style.css`, `i18n.js`,
  `index.html`, `CHANGELOG.md` (`head -20` only), registry, or `TIEN_DO.md` (`tail -5`).
- Tests: the lot's own file + ≤ 3 related, `-q --tb=line 2>&1 | tail -15`. Never the full suite locally (CI runs it).
- `kiem_nhanh.py`: once per lot, `| tail -10`. CI logs: `failed_only`, ≤ 60 lines.
- Screenshots: only in the final review, ≤ 3, `deviceScaleFactor: 1`.
- One Chromium test file per lot with one shared page fixture.
- Messages between sessions: one line; details in the `__<vai>.md` file.
- Stop points: after each commit, if the usage limit is near, update "Current state" and stop; resume next day
  from the branch file (rule 9). Do not rely on automatic summaries to run all night.

## 4. Planner (Opus) budget
- ≤ 15 tool calls: read CLAUDE.md, this file, the previous item's protocol `## 0` only, and the functions the item
  names. Branch file ≤ 100 lines, protocol ≤ 60 lines. No product code (rule 12).
