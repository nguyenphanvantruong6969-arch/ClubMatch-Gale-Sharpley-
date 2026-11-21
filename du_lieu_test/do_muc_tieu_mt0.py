"""
do_muc_tieu_mt0.py — MT0 (new item MT, outside the registry; research only).

SỐ LIỆU MÔ PHỎNG. Calls the real `run_rbda` / `verify_stability`; no production code changed.

Questions:
  Q1  Price of a goal: how many students are displaced per student helped, by reserve size?
  Q2  Commitment: fixed seat number (decided from last year) vs formula (recomputed each year
      from this year's group share) — which meets the goal more often, at what price?
  Q3  Smallest uniform reserve that meets the representation goal (distribution over seeds).
  Q4  Goal metric definitions: compute all 6 on every run; check guardrails (blocking pairs = 0).
  Q5  Privacy: how often is a group count in a club below 5 (must be suppressed)?

Run:  python du_lieu_test/do_muc_tieu_mt0.py
"""

import math
import os
import random
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rbda_priority_pipeline import run_rbda, verify_stability  # noqa: E402

N, C, NPREF, NTEST, SEEDS = 800, 20, 10, 5, 20
SCEN = {
    # name: (popularity skew, seats per student, group share, group score gap in SD)
    "S1 can bang": (0.5, 1.05, 0.15, 0.0),
    "S2 CLB hot": (1.2, 1.00, 0.15, -0.5),
    "S3 thieu cho, nhom nho": (1.0, 0.90, 0.08, -0.8),
}


def gen(seed, skew, ratio, share, gap):
    R = random.Random(seed)
    ids = [f"c{j:02d}" for j in range(C)]
    pop = [1.0 / (j + 1) ** skew for j in range(C)]
    cap = max(1, round(N * ratio / C))
    stu = {}
    for i in range(N):
        stu[f"s{i:03d}"] = {"G": R.random() < share, "lop": i // 40, "khoi": 10 + (i // 40) % 3}
    prefs, apps, sc = {}, {c: [] for c in ids}, {}
    for s, d in stu.items():
        w = {c: pop[j] * R.random() for j, c in enumerate(ids)}  # noisy popularity
        order = sorted(ids, key=lambda c: -w[c])[:NPREF]
        prefs[s] = order
        abil = R.gauss(gap if d["G"] else 0.0, 1.0)
        sc[s] = {c: round(max(0.0, 6.5 + 1.5 * (abil + R.gauss(0, 0.6))) * 2) / 2 for c in order[:NTEST]}
        for c in order:
            apps[c].append(s)
    perm = list(stu)
    R.shuffle(perm)
    stb = {s: k + 1 for k, s in enumerate(perm)}
    nv1 = {c: 0 for c in ids}
    for s in stu:
        nv1[prefs[s][0]] += 1
    hot = sorted(ids, key=lambda c: -nv1[c])[:5]
    return dict(stu=stu, ids=ids, cap=cap, prefs=prefs, apps=apps, sc=sc, stb=stb, hot=hot)


def clubs_of(d, r):
    return {c: {"capacity": d["cap"], "reserve_capacity": min(r, d["cap"])} for c in d["ids"]}


def solve(d, r):
    ts = {c: {s: d["sc"][s][c] for s in d["apps"][c] if c in d["sc"][s]} for c in d["ids"]}
    return run_rbda({s: {} for s in d["stu"]}, clubs_of(d, r), ts, d["apps"], d["prefs"], d["stb"],
                    lambda s, c: d["stu"][s]["G"])


def rank(d, m, s):
    c = m.assignment.get(s)
    return d["prefs"][s].index(c) + 1 if c else NPREF + 1


def goals(d, m, base):
    stu = d["stu"]
    G = [s for s in stu if stu[s]["G"]]
    NG = [s for s in stu if not stu[s]["G"]]
    share = len(G) / N
    mem = {c: [s for s in stu if m.assignment.get(s) == c] for c in d["ids"]}
    hot_ok = sum(sum(stu[s]["G"] for s in mem[c]) / max(1, len(mem[c])) >= 0.9 * share for c in d["hot"])
    top3 = lambda grp: sum(rank(d, m, s) <= 3 for s in grp) / max(1, len(grp))  # noqa: E731
    k10 = [s for s in stu if stu[s]["khoi"] == 10]
    small = sum(0 < sum(stu[s]["G"] for s in mem[c]) < 5 for c in d["ids"])
    lop_max = max((max([sum(stu[s]["lop"] == L for s in mem[c]) for L in range(N // 40)]) / max(1, len(mem[c])))
                  for c in d["ids"] if mem[c])
    return {
        "M1 hot dat": hot_ok / 5,                                 # representation in hot clubs
        "M2 top3 G": top3(G), "M2 top3 ngoai": top3(NG),          # top-3 by group
        "M3 CLB < 50%": sum(len(mem[c]) < 0.5 * d["cap"] for c in d["ids"]),  # club viability
        "M4 khong cho": sum(m.assignment.get(s) is None for s in stu),
        "M5 lop max": lop_max,                                    # class spread
        "M6 top3 khoi10": top3(k10),
        "C NV1": sum(rank(d, m, s) == 1 for s in stu) / N,       # guardrails
        "C giup": sum(rank(d, m, s) < rank(d, base, s) for s in G),
        "C nhuong": sum(rank(d, m, s) > rank(d, base, s) for s in NG),
        "Q5 nhom<5": small,
        "share": share,
    }


def mean(xs):
    return st.mean(xs) if xs else float("nan")


def main():
    for name, (skew, ratio, share, gap) in SCEN.items():
        print(f"\n=== {name}: skew={skew}, cho/HS={ratio}, nhom G~{share:.0%}, chenh diem={gap} SD (SO LIEU MO PHONG, {SEEDS} seed)")
        cap = max(1, round(N * ratio / C))
        levels = sorted({0, 1, 2, math.ceil(share * cap), math.ceil(0.2 * cap), math.ceil(0.3 * cap)})
        tab = {r: [] for r in levels}
        min_r, bp_total = [], 0
        q2 = {"so co dinh": [], "cong thuc": []}
        for seed in range(SEEDS):
            d = gen(seed, skew, ratio, share, gap)
            base = solve(d, 0)
            found = None
            for r in range(0, cap + 1):
                m = solve(d, r)
                g = goals(d, m, base)
                if r in tab:
                    tab[r].append(g)
                    if r == math.ceil(share * cap):
                        bp_total += len(verify_stability(m, clubs_of(d, r), d["prefs"],
                                                         lambda s, c: d["stu"][s]["G"]))
                if found is None and g["M1 hot dat"] == 1.0:
                    found = r
                if found is not None and r > max(levels):
                    break
            min_r.append(found if found is not None else cap)
            # Q2: last year = this seed; this year = seed+1000 with a different group share
            R = random.Random(seed + 7)
            share_new = share * R.uniform(0.5, 1.6)
            d_new = gen(seed + 1000, skew, ratio, share_new, gap)
            base_new = solve(d_new, 0)
            share_last = sum(v["G"] for v in d["stu"].values()) / N
            share_now = sum(v["G"] for v in d_new["stu"].values()) / N
            for lab, r in (("so co dinh", math.ceil(share_last * cap)), ("cong thuc", math.ceil(share_now * cap))):
                q2[lab].append(goals(d_new, solve(d_new, r), base_new))
        print(f"cap/CLB={cap}. Cot: suat du tru moi CLB | M1 % CLB hot dat | top3 G | top3 ngoai G | "
              f"NV1 chung | so em G duoc giup | so em khac nhuong | khong cho | CLB<50% | lop max | top3 khoi10 | CLB co nhom<5")
        for r in levels:
            a = tab[r]
            print(f"  r={r:>2} | {mean([g['M1 hot dat'] for g in a]):>5.0%} | {mean([g['M2 top3 G'] for g in a]):>5.1%} | "
                  f"{mean([g['M2 top3 ngoai'] for g in a]):>5.1%} | {mean([g['C NV1'] for g in a]):>5.1%} | "
                  f"{mean([g['C giup'] for g in a]):>5.1f} | {mean([g['C nhuong'] for g in a]):>5.1f} | "
                  f"{mean([g['M4 khong cho'] for g in a]):>5.1f} | {mean([g['M3 CLB < 50%'] for g in a]):>4.1f} | "
                  f"{mean([g['M5 lop max'] for g in a]):>5.1%} | {mean([g['M6 top3 khoi10'] for g in a]):>5.1%} | "
                  f"{mean([g['Q5 nhom<5'] for g in a]):>4.1f}")
        print(f"  Q3 suat nho nhat dat M1 (5/5 CLB hot): trung vi {st.median(min_r)}, min {min(min_r)}, max {max(min_r)}"
              f"  (cong thuc ceil(ti le*cap) = {math.ceil(share * cap)})")
        print(f"  Q4 cap pha vo o muc cong thuc, tong {SEEDS} seed: {bp_total}")
        for lab, a in q2.items():
            print(f"  Q2 nam sau ({lab}): M1 dat TB {mean([g['M1 hot dat'] for g in a]):.0%}, "
                  f"so seed dat 5/5: {sum(g['M1 hot dat'] == 1.0 for g in a)}/{SEEDS}, "
                  f"nhuong TB {mean([g['C nhuong'] for g in a]):.1f}, giup TB {mean([g['C giup'] for g in a]):.1f}")


if __name__ == "__main__":
    main()
