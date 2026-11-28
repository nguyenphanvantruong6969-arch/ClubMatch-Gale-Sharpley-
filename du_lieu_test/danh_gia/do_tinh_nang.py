# -*- coding: utf-8 -*-
"""DG1 nhóm G — bằng chứng cho từng TÍNH NĂNG: suất dự trữ, điểm quyết tâm (`wharton`), huy chương (`fa_daa`).

    ./.venv/bin/python du_lieu_test/danh_gia/do_tinh_nang.py --nhanh      # ket_qua_nhanh/
    ./.venv/bin/python du_lieu_test/danh_gia/do_tinh_nang.py --day-du     # ket_qua/tinh_nang.json

TOÀN BỘ số trên DỮ LIỆU MÔ PHỎNG. Chỉ in số; không có câu nhận định.

G1 + G2 (mô hình trường α/ρ/κ của `_sinh.py`, một buổi, κ = 1,1, ρ = 0,7): lưới 2×2 «suất dự trữ» {tắt, bật} × «điểm quyết tâm» {tắt, bật}
trên CÙNG dữ liệu và CÙNG seed bốc thăm. Điểm quyết tâm: mỗi em, mỗi quỹ không rỗng, chia đúng 100 điểm (`kiem_ho_so_wharton` phải
báo 0 lỗi) theo một trong ba kiểu — dồn (100 vào CLB đầu quỹ), đều, giảm dần — bốc theo seed dữ liệu; quỹ 1 cho CLB có tick thi, quỹ 2
cho CLB không thi; điểm hiệu lực qua `diem_wharton_hieu_luc` rồi vào `run_rbda(diem_wharton=…)`. Điểm KHÔNG đọc thứ hạng nguyện vọng ở phía
phần mềm (chỉ phía em chia điểm — mô phỏng hành vi — mới dựa vào thứ tự danh sách).

G3 (huy chương): dùng NGUYÊN mô hình trường của `mo_phong_fa_daa.py` (CLB Tự do / Giới hạn / Tuyển chọn, 2 buổi; hành vi lười / thật thà /
chiến lược) vì mô hình α/ρ/κ không có loại CLB. «Tắt» = chế độ cũ (điểm thi + hai quỹ điểm quyết tâm), «bật» = FA-DAA
(huy chương một quỹ); cùng dữ liệu và cùng seed bốc thăm. Huy chương mặc định = hạng trong danh sách em khai (đúng ngoại lệ 2026-11-08 của CLAUDE.md).
"""

import argparse
import os
import random
import sys
import time
import zlib

THU_MUC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC)
sys.path.insert(0, os.path.dirname(THU_MUC))

import do_danh_gia as dg  # noqa: E402
import _chi_so as cs  # noqa: E402
import _sinh as sinh  # noqa: E402
import rbda_priority_pipeline as loi  # noqa: E402

KIEU_CHIA = ("don", "deu", "giam")
KHOA_CHI_SO_G = [
    "a.pct_nv1_tat_ca", "a.pct_top3_tat_ca", "a.hang_tb", "a.cap_chan", "b.n_chua_xep", "b.pct_chua_xep", "c.ty_le_lap_day",
    "c.du_tru_cung_cap", "c.du_tru_da_dung", "c.du_tru_dien_qua_du_tru", "c.du_tru_dien_qua_thuong", "pct_dat_clb_diem_cao",
]
NHOM_DU_TRU = ("chinh_sach", "khoi_10", "khong")


# ---------------------------------------------------------------------------
# Điểm quyết tâm (hai quỹ × 100 điểm mỗi buổi)
# ---------------------------------------------------------------------------

def _chia(ds, kieu):
    """Chia đúng 100 điểm nguyên cho các CLB trong `ds` (đã sắp), theo kiểu `kieu`."""
    n = len(ds)
    if n == 1 or kieu == "don":
        return {ds[0]: 100, **{c: 0 for c in ds[1:]}}
    if kieu == "deu":
        base, du = divmod(100, n)
        return {c: base + (1 if i < du else 0) for i, c in enumerate(ds)}
    w = list(range(n, 0, -1))
    tong = sum(w)
    ra = [100 * x // tong for x in w]
    ra[0] += 100 - sum(ra)
    return dict(zip(ds, ra))


def sinh_diem_quyet_tam(truong, seed):
    """(w1, w2): {sid: {cid: điểm}} theo quỹ; kiểu chia của mỗi em bốc theo `crc32(seed|sid)` — tách khỏi seed bốc thăm."""
    w1, w2, kieu = {}, {}, {}
    for s in sorted(truong["students"]):
        rng = random.Random(zlib.crc32(("dqt|%s|%s" % (seed, s)).encode()))
        k = rng.choice(KIEU_CHIA)
        kieu[s] = k
        ds = truong["preferences"][s]
        for b in truong["ds_buoi"]:
            trong = [c for c in ds if truong["clubs"][c]["buoi"] == b]
            t1 = [c for c in trong if s in truong["tested_scores"].get(c, {})]
            t2 = [c for c in trong if c not in t1]
            if t1:
                w1.setdefault(s, {}).update(_chia(t1, k))
            if t2:
                w2.setdefault(s, {}).update(_chia(t2, k))
    return w1, w2, kieu


def diem_hieu_luc(truong, kb, w1, w2):
    hieu_luc, tb = loi.diem_wharton_hieu_luc(kb["prefs"], w1, w2, kb["scores"])
    return hieu_luc, tb


# ---------------------------------------------------------------------------
# Chạy một ô của lưới 2×2
# ---------------------------------------------------------------------------

def chay_o(truong, kb, seed_bt, du_tru, wharton, w1, w2):
    clubs = kb["clubs"] if du_tru else {c: dict(v, reserve_capacity=0) for c, v in kb["clubs"].items()}
    st, sc, app, prefs = kb["students"], kb["scores"], kb["app"], kb["prefs"]
    stb = loi.generate_stb_lottery(sorted(st), seed_bt)
    elig = loi.default_reserve_eligible_fn(st, clubs)
    dw = diem_hieu_luc(truong, kb, w1, w2)[0] if wharton else None
    kq = loi.run_rbda(st, clubs, sc, app, prefs, stb, elig, diem_wharton=dw)
    cap_chan = len(loi.verify_stability(kq, clubs, prefs, elig))
    ci = cs.tinh_chi_so(st, clubs, prefs, app, sc, kq.assignment, kq.matched_tier, elig, nhom=dg._nhom(truong), cap_chan=cap_chan)
    ph = dg.lam_phang(ci)
    # Em được xếp đúng CLB mình đặt NHIỀU điểm nhất (cả hai quỹ; hoà → CLB đứng trước trong danh sách).
    dat = tot = 0
    for s, c in kq.assignment.items():
        if c is None:
            continue
        diem = {**(w1.get(s) or {}), **(w2.get(s) or {})}
        top = max(prefs[s], key=lambda x: (diem.get(x, 0), -prefs[s].index(x)))
        tot += 1
        dat += top == c
    ph["pct_dat_clb_diem_cao"] = round(100.0 * dat / tot, 3) if tot else 0.0
    # hạng trung bình theo nhóm dự trữ (mẫu số: em được xếp của nhóm)
    for g in NHOM_DU_TRU:
        hs = [s for s in st if (st[s]["reserve_group"] or "khong") == g]
        hang = [prefs[s].index(kq.assignment[s]) + 1 for s in hs if kq.assignment.get(s) in prefs[s]]
        ph["nhom.%s.hang_tb" % g] = round(sum(hang) / len(hang), 3) if hang else None
    return ph, dict(kq.assignment), prefs


def dich_chuyen(a, b, prefs, st):
    """So kết quả `b` với `a` theo NHÓM dự trữ: số em tốt hơn / xấu hơn (như `dg.churn`)."""
    ra = {}
    for g in NHOM_DU_TRU:
        hs = {s for s in a if (st[s]["reserve_group"] or "khong") == g}
        c = dg.churn({s: a[s] for s in hs}, {s: b[s] for s in hs}, prefs)
        ra.update({"%s.%s" % (g, k): v for k, v in c.items()})
    return ra


CAC_O = {"goc": (False, False), "du_tru": (True, False), "wharton": (False, True), "du_tru_wharton": (True, True)}
CAP_SO_SANH = [("du_tru", "goc"), ("du_tru_wharton", "wharton"), ("wharton", "goc"), ("du_tru_wharton", "du_tru")]


def do_luoi_2x2(tham_so, seeds_dl, seeds_bt):
    theo_truong = []
    kiem = {"loi_ho_so": 0, "thong_bao_hieu_luc": 0}
    for sdl in seeds_dl:
        truong = sinh.sinh_truong(seed=sdl, **tham_so)
        kb = dg.dung_kich_ban(truong)
        w1, w2, _kieu = sinh_diem_quyet_tam(truong, sdl)
        thi = {s: {c for c in truong["preferences"][s] if s in truong["tested_scores"].get(c, {})} for s in truong["preferences"]}
        w1_gop, w2_gop = w1, w2
        kiem["loi_ho_so"] += len(loi.kiem_ho_so_wharton(kb["prefs"], thi, w1_gop, w2_gop, kb["clubs"]))
        kiem["thong_bao_hieu_luc"] += len(diem_hieu_luc(truong, kb, w1, w2)[1])
        theo_o = {o: [] for o in CAC_O}
        doi = {p: [] for p in CAP_SO_SANH}
        for sbt in seeds_bt:
            run = {o: chay_o(truong, kb, sbt, *CAC_O[o], w1, w2) for o in CAC_O}
            for o in CAC_O:
                theo_o[o].append(run[o][0])
            for (b, a) in CAP_SO_SANH:
                doi[(b, a)].append(dich_chuyen(run[a][1], run[b][1], kb["prefs"], truong["students"]))
        row = {"o": {o: {k: _tb([p.get(k) for p in ps]) for k in ps[0]} for o, ps in theo_o.items()},
               "doi": {"%s_vs_%s" % pair: {k: _tb([x[k] for x in ds]) for k in ds[0]} for pair, ds in doi.items()}}
        theo_truong.append(row)
    ra = {"tham_so": dict(tham_so), "seed_du_lieu": list(seeds_dl), "seed_boc_tham": list(seeds_bt), "kiem_ho_so": kiem,
          "o": {}, "doi_so_voi": {}}
    for o in CAC_O:
        ra["o"][o] = {k: dg.tong_hop([t["o"][o][k] for t in theo_truong]) for k in theo_truong[0]["o"][o]}
    for ten in theo_truong[0]["doi"]:
        ra["doi_so_voi"][ten] = {k: dg.tong_hop([t["doi"][ten][k] for t in theo_truong]) for k in theo_truong[0]["doi"][ten]}
    # Hiệu CÓ CẶP theo trường: bật − tắt của từng chỉ số lõi.
    ra["hieu_co_cap"] = {}
    for (b, a) in CAP_SO_SANH:
        ra["hieu_co_cap"]["%s_tru_%s" % (b, a)] = {
            k: dg.tong_hop([(t["o"][b][k] - t["o"][a][k]) if (t["o"][b][k] is not None and t["o"][a][k] is not None) else None
                            for t in theo_truong]) for k in theo_truong[0]["o"][b] if k in set(KHOA_CHI_SO_G) | {"nhom.%s.hang_tb" % g for g in NHOM_DU_TRU}
                                                                                       | {"a.theo_nhom.du_tru.%s.pct_nv1" % g for g in NHOM_DU_TRU}
                                                                                       | {"a.theo_nhom.du_tru.%s.pct_da_xep" % g for g in NHOM_DU_TRU}}
    return ra


def _tb(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


# ---------------------------------------------------------------------------
# G3 — huy chương (mô hình `mo_phong_fa_daa`)
# ---------------------------------------------------------------------------

HANH_VI = ("luoi", "that_tha", "chien_luoc")


def _chi_so_that(fa, dl, assignment, huy):
    """Theo hành vi: số em-buổi, NV1 thật, top 2 thật, không có CLB, đặt đúng CLB vàng."""
    ra = {h: {"tong": 0, "nv1": 0, "top2": 0, "khong": 0, "vang": 0, "co_clb": 0} for h in HANH_VI}
    for s, theo in assignment.items():
        h = dl["hs"][s]["hanh_vi"]
        for b in dl["ds_buoi"]:
            c = theo.get(b)
            ds = fa._vi_tri(dl, s, b)
            x = ra[h]
            x["tong"] += 1
            if c is None:
                x["khong"] += 1
            else:
                x["co_clb"] += 1
                x["nv1"] += c == ds[0]
                x["top2"] += c in ds[:2]
                x["vang"] += (huy.get(s) or {}).get(c) == 60
    return ra


def do_huy_chuong(n, seeds_dl, seeds_bt):
    import mo_phong_fa_daa as fa
    theo_truong = []
    for sdl in seeds_dl:
        dl = fa.sinh_du_lieu(n=n, seed=sdl)
        prefs, huy, ticks, diem = fa.dang_ky(dl)
        cu_t = {h: {"tong": 0, "nv1": 0, "top2": 0, "khong": 0, "vang": 0, "co_clb": 0} for h in HANH_VI}
        fa_t = {h: {"tong": 0, "nv1": 0, "top2": 0, "khong": 0, "vang": 0, "co_clb": 0} for h in HANH_VI}
        ly = {}
        doi = {h: {"doi_clb": 0, "tot_hon": 0, "xau_hon": 0} for h in HANH_VI}
        thua = {h: 0 for h in HANH_VI}
        for sbt in seeds_bt:
            a_cu = fa.chay_cu(dl, prefs, ticks, diem, sbt)
            a_fa, ly_do = fa.chay_fa(dl, prefs, huy, ticks, diem, sbt)
            for src, dst in ((_chi_so_that(fa, dl, a_cu, huy), cu_t), (_chi_so_that(fa, dl, a_fa, huy), fa_t)):
                for h in HANH_VI:
                    for k in dst[h]:
                        dst[h][k] += src[h][k]
            for r in ly_do:
                k = "%s|%s" % (r["outcome"], r["reason"])
                ly[k] = ly.get(k, 0) + 1
            bi_thua = {r["student_id"] for r in ly_do if r["reason"] == "LOTTERY" and r["outcome"] == "REJECTED"}
            for s in dl["sids"]:
                h = dl["hs"][s]["hanh_vi"]
                thua[h] += s in bi_thua
                for b in dl["ds_buoi"]:
                    x, y = a_cu[s].get(b), a_fa[s].get(b)
                    if x != y:
                        ds = fa._vi_tri(dl, s, b)
                        hx = ds.index(x) if x in ds else (None if x is None else 99)
                        hy = ds.index(y) if y in ds else (None if y is None else 99)
                        doi[h]["doi_clb"] += 1
                        if hx is None or (hy is not None and hy < hx):
                            doi[h]["tot_hon"] += 1
                        elif hy is None or hy > hx:
                            doi[h]["xau_hon"] += 1
        n_hv = {h: sum(1 for s in dl["sids"] if dl["hs"][s]["hanh_vi"] == h) for h in HANH_VI}
        nl = len(seeds_bt)
        tong_ly = sum(ly.values())
        row = {"n_hv": n_hv, "cu": cu_t, "fa": fa_t, "ly_do_pt": {k: 100.0 * v / tong_ly for k, v in ly.items()},
               "thua_boc_tham_pt": {h: 100.0 * thua[h] / (n_hv[h] * nl) if n_hv[h] else None for h in HANH_VI},
               "doi_tb": {h: {k: v / nl for k, v in doi[h].items()} for h in HANH_VI}}
        theo_truong.append(row)

    def pt(a, b):
        return 100.0 * a / b if b else None

    out = {"n_hs": n, "seed_du_lieu": list(seeds_dl), "seed_boc_tham": list(seeds_bt), "theo_hanh_vi": {}}
    for h in HANH_VI:
        out["theo_hanh_vi"][h] = {"n_hs_tb": dg.tong_hop([r["n_hv"][h] for r in theo_truong])}
        for ten, khoa in (("cu", "cu"), ("fa", "fa")):
            d = {}
            for m, mau in (("pt_nv1_that", "tong"), ("pt_top2_that", "tong"), ("pt_khong_clb", "tong"), ("pt_dat_clb_vang_tren_co_clb", "co_clb")):
                tu = {"pt_nv1_that": "nv1", "pt_top2_that": "top2", "pt_khong_clb": "khong", "pt_dat_clb_vang_tren_co_clb": "vang"}[m]
                d[m] = dg.tong_hop([pt(r[khoa][h][tu], r[khoa][h][mau]) for r in theo_truong])
            out["theo_hanh_vi"][h][ten] = d
        out["theo_hanh_vi"][h]["thua_boc_tham_fa_pt"] = dg.tong_hop([r["thua_boc_tham_pt"][h] for r in theo_truong])
        out["theo_hanh_vi"][h]["doi_clb_cu_sang_fa"] = {k: dg.tong_hop([r["doi_tb"][h][k] for r in theo_truong]) for k in ("doi_clb", "tot_hon", "xau_hon")}
    tong = {"cu": {}, "fa": {}}
    for ten in ("cu", "fa"):
        for m, tu in (("pt_nv1_that", "nv1"), ("pt_top2_that", "top2"), ("pt_khong_clb", "khong")):
            tong[ten][m] = dg.tong_hop([pt(sum(r[ten][h][tu] for h in HANH_VI), sum(r[ten][h]["tong"] for h in HANH_VI)) for r in theo_truong])
    out["tong"] = tong
    khoa_ly = sorted({k for r in theo_truong for k in r["ly_do_pt"]})
    out["ly_do_fa_pt_dong"] = {k: dg.tong_hop([r["ly_do_pt"].get(k, 0.0) for r in theo_truong]) for k in khoa_ly}
    return out


# ---------------------------------------------------------------------------
# Điều phối
# ---------------------------------------------------------------------------

def phan_tinh_nang(cfg):
    ra = {"du_tru_wharton": [], "huy_chuong": []}
    for (n, m) in cfg["quy_mo_g"]:
        for a in cfg["alpha_g"]:
            t0 = time.time()
            ts = {"n_hs": n, "n_clb": m, "alpha": a, "rho": 0.7, "kappa": 1.1}
            ra["du_tru_wharton"].append(do_luoi_2x2(ts, cfg["seed_dl"], cfg["seed_bt"]))
            print("  2x2 %dx%d a=%.2f  %.1fs" % (n, m, a, time.time() - t0), flush=True)
    for (n, _m) in cfg["quy_mo_g"]:
        t0 = time.time()
        ra["huy_chuong"].append(do_huy_chuong(n, cfg["seed_dl"], cfg["seed_bt"]))
        print("  huy_chuong n=%d  %.1fs" % (n, time.time() - t0), flush=True)
    ra["ghi_chu"] = ("du_tru_wharton: mô hình α/ρ/κ, một buổi, κ=1,1, ρ=0,7; 4 ô = suất dự trữ {tắt,bật} × điểm quyết tâm {tắt,bật}, cùng dữ liệu, cùng seed. "
                     "huy_chuong: mô hình `mo_phong_fa_daa` (loại CLB, hành vi), chế độ cũ vs FA-DAA, cùng dữ liệu, cùng seed. "
                     "«doi_so_voi»: số em đổi CLB / tốt hơn / xấu hơn khi bật tính năng, tách theo nhóm dự trữ.")
    return ra


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--nhanh", action="store_true")
    g.add_argument("--day-du", action="store_true")
    g.add_argument("--giam", action="store_true")
    ap.add_argument("--ra")
    a = ap.parse_args(argv)
    che = "nhanh" if a.nhanh else ("giam" if a.giam else "day_du")
    cfg = dict(dg.cau_hinh_chay(che))
    cfg["quy_mo_g"] = [(120, 10), (300, 10)] if che == "nhanh" else dg.QUY_MO
    cfg["alpha_g"] = [0.0, 0.9] if che == "nhanh" else [0.0, 0.5, 0.9]
    ra = a.ra or os.path.join(THU_MUC, "ket_qua_nhanh" if a.nhanh else "ket_qua")
    lenh = "python du_lieu_test/danh_gia/do_tinh_nang.py " + " ".join(argv if argv is not None else sys.argv[1:])
    t0 = time.time()
    print("DG1-G — chế độ %s → %s" % (che, ra), flush=True)
    kq = phan_tinh_nang(cfg)
    dg.ghi_json(os.path.join(ra, "tinh_nang.json"), kq, cfg, lenh, t0)
    print("XONG %.1f giây" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
