"""Ket qua SAU tung buoc chuyen cho (DU LIEU MO PHONG, bo TEST). Moi buoc giu tong cho."""
import os, sys, statistics as st, mo_phong as m, vong2 as v
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from do_toi_uu_on_dinh import nap_ba_bo
du = [d for t, d in nap_ba_bo() if t.startswith("TEST")][0]; prefs = du[4]; cl0 = du[1]
BUOC = [("clb_bongro", "clb_bongda", 4), ("clb_amnhac", "clb_tienganh", 3),
        ("clb_tinhnguyen", "clb_tinhoc", 2), ("clb_vanhoc", "clb_mythuat", 2)]
def do(caps, seeds):
    r = []
    for sd in seeds:
        h = m.hang(prefs, m.chay(du, v.voi_cap(cl0, caps), sd))
        r.append(h)
    return r
def tom(hs, h0s):
    out = []
    for h, h0 in zip(hs, h0s):
        out.append((sum(x == 1 for x in h.values()), sum(x <= 3 for x in h.values()),
                    sum(x > len(prefs[s]) for s, x in h.items()),
                    sum(h[s] < h0[s] for s in prefs), sum(h[s] > h0[s] for s in prefs)))
    return [st.mean(o[i] for o in out) for i in range(5)]
for nhan, seeds in (("SEED KHOA 42", [42]), ("TB 20 SEED", list(range(100, 120)))):
    caps = {c: x["capacity"] for c, x in cl0.items()}
    h0 = do(caps, seeds)
    print("\n==", nhan, "  NV1 | top3 | khongCho | tot hon | te hon (so voi ban dau)")
    print("  ban dau      ", ["%.1f" % x for x in tom(h0, h0)])
    for a, b, k in BUOC:
        prev = do(caps, seeds)
        caps[a] -= k; caps[b] += k
        now = do(caps, seeds)
        print("  %-12s->%-12s %d  cum:" % (a, b, k), ["%.1f" % x for x in tom(now, h0)], " buoc nay:", ["%.1f" % x for x in tom(now, prev)][3:])
