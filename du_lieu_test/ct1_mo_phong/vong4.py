"""Vong 4: luat lai v3 = muc tieu theo ti le NV1, chi TANG khi co cau chua dap ung, can tong, tran +-X%."""
import os, sys, statistics as st, mo_phong as m, vong2 as v
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from do_toi_uu_on_dinh import nap_ba_bo
def lam(f, x):
    def g(du, cl0, cs):
        old = v.MAX_DOI; v.MAX_DOI = x
        try: return f(du, cl0, cs)
        finally: v.MAX_DOI = old
    return g
def p_v3(du, cl0, cs):
    T = sum(x["capacity"] for x in cl0.values()); N = len(du[0]); caps = {}
    for c in cl0:
        cap = cl0[c]["capacity"]; muc = round(T * cs[c]["nv1"] / N)
        caps[c] = muc if muc < cap or cs[c]["chua_dap"] >= 1 else cap
    return v.can_tong(cl0, caps, {c: cs[c]["chua_dap"] / cl0[c]["capacity"] for c in cl0})
CS = [("hien_tai", lambda du, cl0, cs: {c: x["capacity"] for c, x in cl0.items()}),
      ("nv1(30%)", lam(v.p_nv1, .3)), ("nv1(20%)", lam(v.p_nv1, .2)), ("v1(30%)", lam(v.p_luat_v1, .3)),
      ("v3(30%)", lam(p_v3, .3)), ("v3(20%)", lam(p_v3, .2))]
FIT, EVAL = list(range(10)), list(range(100, 120))
kq = {t: [] for t, _ in CS}; chuyen = {t: [] for t, _ in CS}
for hat in (1, 2, 3, 4, 5, 6):
    n1 = m.thi_truong_tong_hop(hat=hat); cl0 = n1[1]; cs = m.chi_so_clb(n1, cl0, FIT)
    caps = {t: f(n1, cl0, cs) for t, f in CS}
    for troi in (0.0, 0.3, 0.6):
        n2 = m.thi_truong_tong_hop(hat=hat, khoa=1, troi=troi)
        for t, _ in CS:
            kq[t].append(m.phuc_loi(n2, v.voi_cap(cl0, caps[t]), EVAL))
    for t, _ in CS: chuyen[t].append(sum(max(0, caps[t][c] - cl0[c]["capacity"]) for c in cl0))
print("NAM SAU, 6 thi truong 800x20 x 3 muc troi (18 kich ban), TB:")
print("   %-10s %6s %6s %6s %8s %7s %s" % ("cs", "hangTB", "%NV1", "%top3", "khongCho", "chuyen", "so kich ban thang hien_tai(hangTB)"))
for t, _ in CS:
    a = kq[t]; b = kq["hien_tai"]
    print("   %-10s %6.3f %5.1f%% %5.1f%% %8.1f %7.0f %d/18" % (t, st.mean(x[0] for x in a), 100 * st.mean(x[1] for x in a),
          100 * st.mean(x[2] for x in a), st.mean(x[3] for x in a), st.mean(chuyen[t]), sum(x[0] < y[0] for x, y in zip(a, b))))
for ten, du in [(t.split()[0], d) for t, d in nap_ba_bo()[1:]]:
    cl0 = du[1]; cs = m.chi_so_clb(du, cl0, FIT)
    print("\n== %s (cung khoa, seed moi)" % ten)
    for t, f in CS:
        caps = f(du, cl0, cs); r = m.phuc_loi(du, v.voi_cap(cl0, caps), EVAL)
        print("   %-10s %6.3f %5.1f%% %5.1f%% %8.1f chuyen=%d" % (t, r[0], 100 * r[1], 100 * r[2], r[3], sum(max(0, caps[c] - cl0[c]["capacity"]) for c in cl0)))
