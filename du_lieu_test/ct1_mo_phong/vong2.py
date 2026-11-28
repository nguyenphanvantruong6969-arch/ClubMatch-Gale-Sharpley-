"""Vong 2: so sanh chinh sach doi chi tieu GIU NGUYEN tong cho. Fit seeds 0-9, danh gia seeds 100-129."""
import os, sys, mo_phong as m
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from do_toi_uu_on_dinh import nap_ba_bo
FIT, EVAL = list(range(10)), list(range(100, 130))
MAX_DOI = 0.30   # doi toi da +-30%/ky

def gioi(cl0, c):
    cap = cl0[c]["capacity"]; return max(8, round(cap * (1 - MAX_DOI))), round(cap * (1 + MAX_DOI))

def voi_cap(cl0, caps):
    return {c: {**v, "capacity": caps[c], "reserve_capacity": min(v["reserve_capacity"], caps[c])} for c, v in cl0.items()}

def can_tong(cl0, caps, uu):
    """dua tong ve dung T bang cach +-1 theo thu tu uu tien (diem cao duoc them truoc, thap bi bot truoc), ton trong gioi han."""
    T = sum(v["capacity"] for v in cl0.values())
    caps = {c: min(max(caps[c], gioi(cl0, c)[0]), gioi(cl0, c)[1]) for c in caps}
    thu_tu = sorted(caps, key=lambda c: -uu[c])
    while sum(caps.values()) != T:
        if sum(caps.values()) < T:
            c = next((c for c in thu_tu if caps[c] < gioi(cl0, c)[1]), None)
            if c is None: break
            caps[c] += 1
        else:
            c = next((c for c in reversed(thu_tu) if caps[c] > gioi(cl0, c)[0]), None)
            if c is None: break
            caps[c] -= 1
    return caps

def p_nv1(du, cl0, cs):
    T = sum(v["capacity"] for v in cl0.values()); N = len(du[0])
    caps = {c: round(T * cs[c]["nv1"] / N) for c in cl0}
    return can_tong(cl0, caps, {c: cs[c]["ap_luc"] for c in cl0})

def p_goi_y_hien_tai(du, cl0, cs):   # fa_daa.goi_y_chi_tieu: min(nv1, gioi_han); gioi_han = cap*1.3; KHONG can tong
    return {c: max(1, min(cs[c]["nv1"], gioi(cl0, c)[1])) for c in cl0}

def p_luat_v1(du, cl0, cs):  # ban nhap buoi brainstorm 1
    caps = {}
    for c in cl0:
        cap = cl0[c]["capacity"]
        if cs[c]["ap_luc"] >= 1.5: caps[c] = cap + round(cs[c]["chua_dap"])
        elif cs[c]["lap"] < 0.7 or (cs[c]["ap_luc"] < 0.5 and cs[c]["tv_nv13"] < 0.5): caps[c] = round(cap * cs[c]["lap"])
        else: caps[c] = cap
    return can_tong(cl0, caps, {c: cs[c]["ap_luc"] for c in cl0})

def p_luat_v2(du, cl0, cs):
    """Bot = cho trong thuc (tru dem 1); them theo 'cau chua dap ung' tren moi cho; can tong."""
    caps = {}
    for c in cl0:
        cap = cl0[c]["capacity"]; trong = cap * (1 - cs[c]["lap"])
        caps[c] = cap - max(0, round(trong) - 1)
    uu = {c: cs[c]["chua_dap"] / cl0[c]["capacity"] for c in cl0}
    return can_tong(cl0, caps, uu)

def p_tham_lam(du, cl0, cs, buoc=80):
    """Chuan tren: chuyen tung cho bang mo phong that (gia tri bien). Fit tren FIT[:5]."""
    caps = {c: v["capacity"] for c, v in cl0.items()}; sd = FIT[:5]
    def loi(caps): return -m.phuc_loi(du, voi_cap(cl0, caps), sd)[0]
    goc = loi(caps)
    for _ in range(buoc):
        # rut gon: chon a co loi +1 lon nhat, b co thiet -1 nho nhat
        def thu(c, d):
            cc = dict(caps); cc[c] += d; return loi(cc) - goc
        A = [(thu(a, 1), a) for a in caps if caps[a] < gioi(cl0, a)[1]]
        B = [(thu(b, -1), b) for b in caps if caps[b] > gioi(cl0, b)[0]]
        if not A or not B: break
        ga, a = max(A); gb, b = max(B)
        if a == b: break
        cc = dict(caps); cc[a] += 1; cc[b] -= 1; moi = loi(cc)
        if moi <= goc + 1e-9: break
        caps, goc = cc, moi
    return caps

CS = [("hien_tai", lambda du, cl0, cs: {c: v["capacity"] for c, v in cl0.items()}),
      ("nv1_ti_le", p_nv1), ("goi_y_hien_tai", p_goi_y_hien_tai),
      ("luat_v1", p_luat_v1), ("luat_v2", p_luat_v2), ("tham_lam_mo_phong", p_tham_lam)]
if __name__ == "__main__":
    bo = [("tong_hop_h%d" % h, m.thi_truong_tong_hop(hat=h)) for h in (1, 2, 3)]
    bo += [(t.split()[0], d) for t, d in nap_ba_bo()[1:]]
    for ten, du in bo:
        cl0 = du[1]; cs = m.chi_so_clb(du, cl0, FIT)
        print("\n== %s  N=%d  tong cho=%d" % (ten, len(du[0]), sum(v['capacity'] for v in cl0.values())))
        print("   %-18s %6s %6s %6s %7s %6s %6s" % ("chinh_sach", "hangTB", "%NV1", "%top3", "khongCho", "tong", "chuyen"))
        for tcs, f in CS:
            caps = f(du, cl0, cs)
            hb, nv1, t3, kc = m.phuc_loi(du, voi_cap(cl0, caps), EVAL)
            chuyen = sum(max(0, caps[c] - cl0[c]["capacity"]) for c in cl0)
            print("   %-18s %6.3f %5.1f%% %5.1f%% %7.1f %6d %6d" % (tcs, hb, nv1 * 100, t3 * 100, kc, sum(caps.values()), chuyen))
