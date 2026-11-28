"""Mo phong (DU LIEU MO PHONG) danh gia cac chinh sach goi y chi tieu CLB. Khong ghi CSDL."""
import os, sys, random, math, statistics as st
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import rbda_priority_pipeline as loi

def thi_truong_tong_hop(n=800, m=20, L=6, so_thi=5, hat=1, khoa=0, troi=0.0):
    """Thi truong gia: do noi tieng CLB lech (lognormal), chi tieu nha truong dat ~deu (chua biet cau)."""
    r = random.Random(hat)
    cids = ["c%02d" % i for i in range(m)]
    w = {c: math.exp(r.gauss(0, 0.8)) for c in cids}
    # khoa != 0: KHOA HOC SINH MOI (nam sau) cung do noi tieng CLB, troi = do troi so thich giua hai nam
    r = random.Random(hat * 1000 + khoa)
    if troi: w = {c: v * math.exp(r.gauss(0, troi)) for c, v in w.items()}
    students = {"s%03d" % i: {"stb": None, "reserve_group": None} for i in range(n)}
    prefs = {}
    for s in students:
        # Plackett-Luce voi nhieu ca nhan
        ww = {c: w[c] * math.exp(r.gauss(0, 0.6)) for c in cids}
        ds = []
        for _ in range(L):
            tong = sum(v for c, v in ww.items() if c not in ds)
            x = r.random() * tong
            for c, v in ww.items():
                if c in ds: continue
                x -= v
                if x <= 0: ds.append(c); break
        prefs[s] = ds
    T = int(n * 1.05)
    base = T // m
    clubs = {c: {"capacity": base + (1 if i < T - base * m else 0), "reserve_capacity": 0,
                 "reserve_group": None, "buoi": "__mac_dinh__"} for i, c in enumerate(cids)}
    tested = cids[:so_thi]
    scores = {c: {} for c in tested}; app = {c: [] for c in tested}
    for s, ds in prefs.items():
        for c in ds:
            if c in tested:
                scores[c][s] = round(min(10, max(0, r.gauss(6.5, 1.5))), 1); app[c].append(s)
    return students, clubs, scores, app, prefs

def chay(du, clubs, seed):
    students, _c, scores, app, prefs = du
    stb = loi.generate_stb_lottery(sorted(students), seed)
    elig = loi.default_reserve_eligible_fn(students, clubs)
    return dict(loi.run_rbda(students, clubs, scores, app, prefs, stb, elig).assignment)

def hang(prefs, gan):
    """rank cua tung em; khong co cho = L+1."""
    ra = {}
    for s, ds in prefs.items():
        c = gan.get(s)
        ra[s] = ds.index(c) + 1 if c in ds else len(ds) + 1
    return ra

def phuc_loi(du, clubs, seeds):
    prefs = du[4]; out = []
    for sd in seeds:
        h = hang(prefs, chay(du, clubs, sd))
        v = list(h.values()); max(len(x) for x in prefs.values())
        out.append((st.mean(v), sum(x == 1 for x in v) / len(v), sum(x <= 3 for x in v) / len(v),
                    sum(x > len(prefs[s]) for s, x in h.items())))
    return tuple(st.mean(o[i] for o in out) for i in range(4))

def chi_so_clb(du, clubs, seeds):
    """Chi so moi CLB tu ket qua that (khong mo phong them): nv1, ap luc, lap day, co cau, cau chua dap ung."""
    prefs = du[4]; cids = sorted(clubs); res = {c: {"nv1": 0, "quan_tam": 0.0} for c in cids}
    for s, ds in prefs.items():
        res[ds[0]]["nv1"] += 1
        for k, c in enumerate(ds): res[c]["quan_tam"] += 1 / (k + 1)
    acc = {c: {"lap": [], "tv_nv13": [], "chua_dap": []} for c in cids}
    for sd in seeds:
        gan = chay(du, clubs, sd); h = hang(prefs, gan)
        for c in cids:
            tv = [s for s, x in gan.items() if x == c]
            acc[c]["lap"].append(len(tv) / clubs[c]["capacity"])
            acc[c]["tv_nv13"].append(sum(h[s] <= 3 for s in tv) / len(tv) if tv else 0)
        for c in cids:
            # em xep c cao hon cho duoc nhan (gom ca em khong co cho)
            acc[c]["chua_dap"].append(sum(1 for s, ds in prefs.items() if c in ds and gan.get(s) != c and ds.index(c) + 1 < h[s]))
    for c in cids:
        res[c].update({k: st.mean(v) for k, v in acc[c].items()})
        res[c]["cap"] = clubs[c]["capacity"]; res[c]["ap_luc"] = res[c]["nv1"] / clubs[c]["capacity"]
    return res

def gia_tri_bien(du, clubs, seeds, c, d):
    prefs = du[4]; tot = []
    for sd in seeds:
        h0 = hang(prefs, chay(du, clubs, sd))
        cl = {k: dict(v) for k, v in clubs.items()}; cl[c]["capacity"] += d
        h1 = hang(prefs, chay(du, cl, sd))
        tot.append(sum(1 for s in prefs if h1[s] < h0[s]) - sum(1 for s in prefs if h1[s] > h0[s]))
    return st.mean(tot)

def spearman(a, b):
    def rk(x):
        o = sorted(range(len(x)), key=lambda i: x[i]); r = [0] * len(x)
        for j, i in enumerate(o): r[i] = j
        return r
    ra, rb = rk(a), rk(b); n = len(a)
    return 1 - 6 * sum((x - y) ** 2 for x, y in zip(ra, rb)) / (n * (n * n - 1))
