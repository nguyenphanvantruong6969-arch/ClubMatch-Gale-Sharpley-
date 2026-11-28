# -*- coding: utf-8 -*-
"""DG1 — bộ đo định lượng: nguyện vọng, chưa được xếp, chỉ tiêu, đổi tiêu chí, so cơ chế, quy mô.

    ./.venv/bin/python du_lieu_test/danh_gia/do_danh_gia.py --nhanh                # < 2 phút, ra ket_qua_nhanh/ (không commit)
    ./.venv/bin/python du_lieu_test/danh_gia/do_danh_gia.py --day-du               # bộ đầy đủ, ra ket_qua/
    ./.venv/bin/python du_lieu_test/danh_gia/do_danh_gia.py --so-nhap PATH.xlsx    # dữ liệu thật: ra ket_qua_that/ (KHÔNG commit)
    ./.venv/bin/python du_lieu_test/danh_gia/in_bang.py ket_qua/                   # in bảng Markdown từ JSON

TOÀN BỘ số trong JSON do dữ liệu MÔ PHỎNG sinh ra (trừ khi chạy `--so-nhap`). Không con số nào gõ tay.

Hai nguồn ngẫu nhiên TÁCH BIỆT, không bao giờ trộn:
  * seed DỮ LIỆU  — một trường mô phỏng khác (5 giá trị: SEED_DU_LIEU);
  * seed BỐC THĂM — cùng một trường, lần bốc số STB khác (10 giá trị: SEED_BOC_THAM).
Mỗi cấu hình: trung bình và KTC 95 % (t, bậc tự do = số seed dữ liệu − 1) tính trên TRUNG BÌNH THEO TRƯỜNG; độ lệch
chuẩn giữa các lần bốc thăm trong cùng một trường được báo riêng (`sd_boc_tham`).

Đường chạy: lõi `rbda_priority_pipeline.run_rbda` gọi TRỰC TIẾP trên dữ liệu trong bộ nhớ (cùng hàm `run_pipeline` gọi — đã kiểm
khớp từng dòng `match_results` bằng test và bằng phép đối chiếu bộ TEST seed 42, xem `doi_chieu_so_lieu.json`). Đi qua
`PipelineAPI` + Sổ nhập thật chỉ ở phép đối chiếu và ở phép đo thời gian (`thoi_gian.json`).
"""

import argparse
import json
import math
import os
import statistics
import subprocess
import sys
import tempfile
import time

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
sys.path.insert(0, GOC)
sys.path.insert(0, THU_MUC)
sys.path.insert(0, os.path.dirname(THU_MUC))

import rbda_priority_pipeline as loi  # noqa: E402
import _chi_so as cs  # noqa: E402
import _sinh as sinh  # noqa: E402
import co_che_doi_chung as cc  # noqa: E402

SEED_DU_LIEU = [101, 102, 103, 104, 105]
SEED_BOC_THAM = list(range(1, 11))
ALPHA = [0.0, 0.25, 0.5, 0.75, 0.9]
KAPPA = [0.9, 1.1, 1.3]
RHO = [0.0, 0.7]
QUY_MO = [(120, 10), (300, 10), (800, 20)]
MAC_DINH = {"n_hs": 800, "n_clb": 20, "alpha": 0.5, "rho": 0.7, "kappa": 1.1}
T_975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262,
         10: 2.228, 15: 2.131, 20: 2.086, 30: 2.042}
DO_DAI_CONG = 10

# Chỉ số giữ lại khi quét nhiều cấu hình (bản đầy đủ chỉ ở mac_dinh.json / bien_the / co_che).
CHI_SO_QUET = [
    "a.pct_nv1_tat_ca", "a.pct_top2_tat_ca", "a.pct_top3_tat_ca", "a.pct_nv1_da_xep", "a.hang_tb", "a.ngoai_danh_sach",
    "a.cap_chan", "b.pct_chua_xep", "b.n_chua_xep", "b.can_tren_ghep_cuc_dai", "b.khong_the_tranh", "b.gia_uu_tien_on_dinh",
    "b.lech_cho", "b.nguyen_nhan.danh_sach_rong", "b.nguyen_nhan.khong_diem", "b.nguyen_nhan.het_cho_uu_tien_cao_hon",
    "c.ty_le_lap_day", "c.n_clb_day", "c.n_clb_duoi_50", "c.phan_vi_lap_day.min", "c.phan_vi_lap_day.median",
    "c.du_tru_da_dung", "c.du_tru_cung_cap", "c.du_tru_dien_qua_du_tru", "c.du_tru_dien_qua_thuong", "vong",
] + ["a.duong_cong_don.%d" % k for k in range(1, 7)]


# ---------------------------------------------------------------------------
# Thống kê nhỏ
# ---------------------------------------------------------------------------

def _t975(df):
    if df in T_975:
        return T_975[df]
    for k in sorted(T_975):
        if df <= k:
            return T_975[k]
    return 1.96


def tong_hop(gia_tri):
    """Trung bình + KTC 95 % t của một dãy số (mỗi phần tử = trung bình MỘT trường)."""
    xs = [x for x in gia_tri if x is not None]
    if not xs:
        return {"tb": None, "ktc95": None, "n": 0}
    tb = sum(xs) / len(xs)
    if len(xs) < 2:
        return {"tb": round(tb, 4), "ktc95": None, "n": len(xs)}
    sd = statistics.stdev(xs)
    h = _t975(len(xs) - 1) * sd / math.sqrt(len(xs))
    return {"tb": round(tb, 4), "ktc95": [round(tb - h, 4), round(tb + h, 4)], "n": len(xs)}


def lam_phang(d, tien_to=""):
    ra = {}
    for k, v in d.items():
        ten = tien_to + k
        if k == "theo_clb":
            continue
        if isinstance(v, dict):
            ra.update(lam_phang(v, ten + "."))
        elif isinstance(v, list):
            if k == "duong_cong_don":
                v = list(v) + [v[-1] if v else None] * (DO_DAI_CONG - len(v))
            for i, x in enumerate(v):
                if isinstance(x, (int, float)) and not isinstance(x, bool):
                    ra["%s.%d" % (ten, i + 1)] = x
        elif isinstance(v, bool):
            ra[ten] = 1 if v else 0
        elif isinstance(v, (int, float)):
            ra[ten] = v
    return ra


# ---------------------------------------------------------------------------
# Dựng kịch bản (một biến thể = MỘT thay đổi so với mặc định)
# ---------------------------------------------------------------------------

def dung_kich_ban(truong, bien_the=None):
    """Trả về dict đủ cho `run_rbda`. `bien_the` = {"ten", ...} với một (và chỉ một) khoá thay đổi."""
    bt = bien_the or {}
    students = truong["students"]
    clubs = {c: dict(v) for c, v in truong["clubs"].items()}
    prefs = {s: list(ds) for s, ds in truong["preferences"].items()}
    scores = {c: dict(d) for c, d in truong["tested_scores"].items()}
    dky = {c: list(v) for c, v in truong["dang_ky_thi"].items()}

    f = bt.get("he_so_chi_tieu")
    if f:
        for v in clubs.values():
            v["capacity"] = max(1, round(v["capacity"] * f))
            v["reserve_capacity"] = min(v["capacity"], round(v["reserve_capacity"] * f))
    if bt.get("du_tru_tat"):
        for v in clubs.values():
            v["reserve_capacity"] = 0
    k = bt.get("max_choices")
    if k:
        # Biểu mẫu giới hạn số nguyện vọng: cắt danh sách MỖI BUỔI (ở đây gồm một buổi hoặc theo thứ tự buổi), bỏ tick ngoài danh sách.
        theo_buoi = loi.nhom_theo_buoi(clubs)
        cua_buoi = {c: b for b, ds in theo_buoi.items() for c in ds}
        moi = {}
        for s, ds in prefs.items():
            dem = {}
            ra = []
            for c in ds:
                b = cua_buoi[c]
                if dem.get(b, 0) < k:
                    dem[b] = dem.get(b, 0) + 1
                    ra.append(c)
            moi[s] = ra
        prefs = moi
        giu = {(s, c) for s, ds in prefs.items() for c in ds}
        dky = {c: [s for s in ds if (s, c) in giu] for c, ds in dky.items()}
        scores = {c: {s: v for s, v in d.items() if (s, c) in giu} for c, d in scores.items()}
    app = loi.hop_ung_vien(dky, prefs)

    luat = bt.get("luat") or {}
    thamso = loi.tham_so_luat(luat, students)
    ll = loi.luat_xep_cua(luat)
    if ll["priority"] == "tier":
        scores = {c: {} for c in scores}
    elif ll["score_scope"] == "per_person":
        theo_nguoi = {}
        for d in scores.values():
            for s, v in d.items():
                theo_nguoi.setdefault(s, []).append(v)
        diem_ng = {s: round(sum(v) / len(v), 1) for s, v in theo_nguoi.items()}
        scores = {c: {s: diem_ng[s] for s in app[c] if s in diem_ng} for c in clubs}
    return {"students": students, "clubs": clubs, "scores": scores, "app": app, "prefs": prefs,
            "tier_rank": thamso["tier_rank"], "bo_qua": thamso["bo_qua_du_tru"], "bt": bt}


def _nhom(truong):
    return {"du_tru": {s: (v["reserve_group"] or "khong") for s, v in truong["students"].items()}, "khoi": truong["khoi"]}


def chay_mot(kb, seed_bt, truong):
    """Một lần RB-DA + chỉ số. Trả (chỉ số, MatchResult, thời gian giây)."""
    stb = loi.generate_stb_lottery(sorted(kb["students"]), seed_bt)
    elig = loi.default_reserve_eligible_fn(kb["students"], kb["clubs"])
    t0 = time.perf_counter()
    kq = loi.run_rbda(kb["students"], kb["clubs"], kb["scores"], kb["app"], kb["prefs"], stb, elig,
                      tier_rank=kb["tier_rank"], bo_qua_du_tru=kb["bo_qua"])
    dt = time.perf_counter() - t0
    cap_chan = len(loi.verify_stability(kq, kb["clubs"], kb["prefs"], elig, bo_qua_du_tru=kb["bo_qua"]))
    ci = cs.tinh_chi_so(kb["students"], kb["clubs"], kb["prefs"], kb["app"], kb["scores"], kq.assignment,
                        kq.matched_tier, elig, nhom=_nhom(truong), cap_chan=cap_chan)
    ci["vong"] = kq.rounds_run
    return ci, kq, dt


# ---------------------------------------------------------------------------
# Một cấu hình × lưới seed
# ---------------------------------------------------------------------------

def do_cau_hinh(tham_so, seeds_dl, seeds_bt, bien_the=None, chi_so_giu=None, luu_theo_clb=False, doi_chieu=None):
    """Chạy `len(seeds_dl) × len(seeds_bt)` lần. `doi_chieu` = {seed_dl: {seed_bt: assignment}} của bản mặc định (tính churn)."""
    theo_truong = []
    ra_assign = {}
    thoi_gian = []
    for sdl in seeds_dl:
        truong = sinh.sinh_truong(seed=sdl, **tham_so)
        kb = dung_kich_ban(truong, bien_the)
        phang_lan, chiu = [], {}
        theo_clb_tong = {}
        co_cho = {}
        clb_cua = {}
        ra_assign[sdl] = {}
        for sbt in seeds_bt:
            ci, kq, dt = chay_mot(kb, sbt, truong)
            thoi_gian.append(dt)
            ra_assign[sdl][sbt] = dict(kq.assignment)
            ph = lam_phang(ci)
            phang_lan.append(ph)
            for s, c in kq.assignment.items():
                co_cho.setdefault(s, set()).add(c is not None)
                clb_cua.setdefault(s, set()).add(c)
            if luu_theo_clb:
                for x in ci["c"]["theo_clb"]:
                    d = theo_clb_tong.setdefault(x["club_id"], {"capacity": x["capacity"], "nv1": x["nv1"], "da_xep": []})
                    d["da_xep"].append(x["da_xep"])
            if doi_chieu is not None:
                chiu.setdefault("lan", []).append(churn(doi_chieu[sdl][sbt], kq.assignment, kb["prefs"]))
        khoa = [k for k in phang_lan[0] if chi_so_giu is None or k in chi_so_giu]
        tb = {k: sum(p[k] for p in phang_lan if k in p) / len(phang_lan) for k in khoa}
        sd = {k: (statistics.stdev([p[k] for p in phang_lan]) if len(phang_lan) > 1 else 0.0) for k in khoa}
        n = len(truong["students"])
        row = {"seed_du_lieu": sdl, "tb": tb, "sd_boc_tham": sd,
               "lat_co_cho": sum(1 for v in co_cho.values() if len(v) > 1),
               "lat_clb": sum(1 for v in clb_cua.values() if len(v) > 1), "n_hs": n,
               "tham_so_thuc": truong["tham_so"]}
        if luu_theo_clb:
            row["theo_clb"] = [{"club_id": c, "capacity": d["capacity"], "nv1": d["nv1"],
                                "da_xep_tb": round(sum(d["da_xep"]) / len(d["da_xep"]), 3),
                                "lap_day_tb": round(sum(d["da_xep"]) / len(d["da_xep"]) / d["capacity"], 4),
                                "ti_le_cau": round(d["nv1"] / d["capacity"], 4)} for c, d in sorted(theo_clb_tong.items())]
        if chiu:
            row["churn"] = {k: sum(x[k] for x in chiu["lan"]) / len(chiu["lan"]) for k in chiu["lan"][0]}
        theo_truong.append(row)
    khoa = list(theo_truong[0]["tb"])
    chi_so = {k: dict(tong_hop([r["tb"][k] for r in theo_truong]),
                      sd_boc_tham=round(sum(r["sd_boc_tham"][k] for r in theo_truong) / len(theo_truong), 4),
                      theo_bo=[round(r["tb"][k], 4) for r in theo_truong]) for k in khoa}
    ra = {
        "tham_so": dict(tham_so), "bien_the": bien_the, "seed_du_lieu": list(seeds_dl), "seed_boc_tham": list(seeds_bt),
        "chi_so": chi_so,
        "lat_co_cho_pct": tong_hop([100.0 * r["lat_co_cho"] / r["n_hs"] for r in theo_truong]),
        "lat_clb_pct": tong_hop([100.0 * r["lat_clb"] / r["n_hs"] for r in theo_truong]),
        "thoi_gian_run_rbda_giay": {"trung_vi": round(statistics.median(thoi_gian), 5), "max": round(max(thoi_gian), 5)},
        "theo_truong": [{k: v for k, v in r.items() if k not in ("tb", "sd_boc_tham")} for r in theo_truong],
        "kappa_thuc": tong_hop([r["tham_so_thuc"]["kappa_thuc"] for r in theo_truong])["tb"],
    }
    if any("churn" in r for r in theo_truong):
        ra["churn"] = {k: tong_hop([r["churn"][k] for r in theo_truong]) for k in theo_truong[0]["churn"]}
    ra["_assign"] = ra_assign
    return ra


def churn(a, b, prefs):
    """So hai kết quả CÙNG danh sách em: bao nhiêu em đổi CLB; tốt hơn / xấu hơn / đổi mà cùng hạng.

    tốt hơn = chưa có chỗ → có chỗ, hoặc hạng nhỏ hơn (thích hơn); xấu hơn = ngược lại.
    """
    def hang(sid, c):
        if c is None:
            return None
        ds = prefs.get(sid, [])
        return ds.index(c) + 1 if c in ds else 99
    tot = xau = cung = 0
    for s in a:
        if a[s] == b.get(s):
            continue
        ha, hb = hang(s, a[s]), hang(s, b.get(s))
        if ha is None:
            tot += 1
        elif hb is None or hb > ha:
            xau += 1
        elif hb < ha:
            tot += 1
        else:
            cung += 1
    return {"doi_clb": tot + xau + cung, "tot_hon": tot, "xau_hon": xau, "doi_cung_hang": cung}


def _bo_assign(d):
    d = dict(d)
    d.pop("_assign", None)
    return d


# ---------------------------------------------------------------------------
# Các phần của bộ đo
# ---------------------------------------------------------------------------

def phan_quet(cfg):
    ra = []
    for (n, m) in cfg["quy_mo"]:
        for a in cfg["alpha"]:
            for k in cfg["kappa"]:
                for r in cfg["rho"]:
                    t = time.time()
                    d = do_cau_hinh({"n_hs": n, "n_clb": m, "alpha": a, "rho": r, "kappa": k},
                                    cfg["seed_dl"], cfg["seed_bt"], chi_so_giu=set(CHI_SO_QUET))
                    d = _bo_assign(d)
                    d.pop("theo_truong", None)
                    ra.append(d)
                    print("  quet %dx%d a=%.2f k=%.1f rho=%.1f  %.1fs" % (n, m, a, k, r, time.time() - t), flush=True)
    return {"cac_cau_hinh": ra}


def tham_so_mac_dinh(cfg):
    return dict(cfg["mac_dinh"])


def phan_mac_dinh(cfg):
    d = do_cau_hinh(tham_so_mac_dinh(cfg), cfg["seed_dl"], cfg["seed_bt"], luu_theo_clb=True)
    return _bo_assign(d)


BIEN_THE = [
    {"ten": "mac_dinh", "mo_ta": "Mặc định (điểm theo CLB, suất dự trữ mềm, nhóm không xếp cứng)"},
    {"ten": "du_tru_tat", "mo_ta": "Tắt toàn bộ suất dự trữ (reserve_capacity = 0)", "du_tru_tat": True},
    {"ten": "nhom_cung", "mo_ta": "tier_mode = strict, tiers = [chinh_sach, khoi_10] (hạng nhóm trước điểm, bỏ suất dự trữ)",
     "luat": {"tier_mode": "strict", "tiers": ["chinh_sach", "khoi_10"]}},
    {"ten": "chi_nhom", "mo_ta": "priority = tier, tiers = [chinh_sach, khoi_10] (bỏ điểm, nhóm rồi bốc thăm)",
     "luat": {"priority": "tier", "tiers": ["chinh_sach", "khoi_10"]}},
    {"ten": "diem_theo_nguoi", "mo_ta": "score_scope = per_person (điểm của em = trung bình điểm các bài em đã thi)",
     "luat": {"score_scope": "per_person"}},
    {"ten": "toi_da_3_nv", "mo_ta": "max_choices = 3", "max_choices": 3},
    {"ten": "toi_da_5_nv", "mo_ta": "max_choices = 5", "max_choices": 5},
    {"ten": "toi_da_10_nv", "mo_ta": "max_choices = 10 (danh sách mô phỏng ≤ 6 → phải GIỐNG HỆT mặc định)", "max_choices": 10},
    {"ten": "chi_tieu_-20", "mo_ta": "Chỉ tiêu mọi CLB × 0,8", "he_so_chi_tieu": 0.8},
    {"ten": "chi_tieu_+20", "mo_ta": "Chỉ tiêu mọi CLB × 1,2", "he_so_chi_tieu": 1.2},
]


def phan_bien_the(cfg):
    ts = tham_so_mac_dinh(cfg)
    goc = do_cau_hinh(ts, cfg["seed_dl"], cfg["seed_bt"])
    doi_chieu = goc["_assign"]
    ra = [_bo_assign(dict(goc, bien_the=BIEN_THE[0]))]
    for bt in BIEN_THE[1:]:
        t = time.time()
        d = do_cau_hinh(ts, cfg["seed_dl"], cfg["seed_bt"], bien_the=bt, doi_chieu=doi_chieu)
        ra.append(_bo_assign(d))
        print("  bien_the %-16s %.1fs" % (bt["ten"], time.time() - t), flush=True)
    # Kiểm tự nhất quán: max_choices = 10 phải trùng khít mặc định.
    r10 = next(x for x in ra if (x["bien_the"] or {}).get("ten") == "toi_da_10_nv")
    giong = r10["churn"]["doi_clb"]["tb"] == 0 and r10["churn"]["doi_clb"]["ktc95"] in (None, [0.0, 0.0])
    # Đối chiếu churn với `tieu_chi.so_sanh_lan_chay` (hàm thuần của phần mềm) trên MỘT cặp (seed dữ liệu đầu, seed bốc thăm đầu).
    import tieu_chi
    truong = sinh.sinh_truong(seed=cfg["seed_dl"][0], **ts)
    a = doi_chieu[cfg["seed_dl"][0]][cfg["seed_bt"][0]]
    kiem = []
    for bt in BIEN_THE[1:]:
        kb = dung_kich_ban(truong, bt)
        ci, kq, _ = chay_mot(kb, cfg["seed_bt"][0], truong)
        rows_a = [(s, "b", c, None) for s, c in a.items()]
        rows_b = [(s, "b", c, None) for s, c in kq.assignment.items()]
        so = tieu_chi.so_sanh_lan_chay({"nhan": "thu", "run_id": 1, "luat": {}, "rows": rows_a},
                                       {"nhan": "thu", "run_id": 2, "luat": bt.get("luat") or {}, "rows": rows_b},
                                       {"students": {}, "clubs": {}, "diem": {}, "tiers": []})
        kiem.append({"bien_the": bt["ten"], "so_doi_tieu_chi": so["so_doi"],
                     "doi_clb_do_dg1": churn(a, kq.assignment, kb["prefs"])["doi_clb"]})
    return {"cac_bien_the": ra, "max_choices_10_trung_mac_dinh": giong, "doi_chieu_so_sanh_lan_chay": kiem,
            "ghi_chu": "churn: trung bình trên lưới seed, so cùng seed dữ liệu + cùng seed bốc thăm với 'mac_dinh'."}


def dem_cap_chan(xep, clubs, prefs, base_rank, chon):
    """Số cặp phá vỡ của ma trận `xep` bất kỳ, bằng ĐÚNG `club_choice_function` (qua `cc._ham_chon`) — cùng vòng lặp với `cc.thong_ke`."""
    bang = cc.bang_thu_hang_nguyen_vong(prefs)
    giu = {c: [] for c in clubs}
    for s, c in xep.items():
        if c is not None:
            giu[c].append(s)
    n = 0
    for s, ps in prefs.items():
        ht = xep.get(s)
        gh = bang[s].get(ht, len(ps)) if ht else len(ps)
        for c in ps[:gh]:
            if c not in clubs or s not in base_rank.get(c, {}):
                continue
            nhan, _ = chon(c, giu[c] + [s])
            if s in nhan:
                n += 1
    return n


CO_CHE = ["rbda", "boston", "thu_tu_boc_tham", "ttc", "da_clb_de_xuat"]


def phan_co_che(cfg):
    ts = tham_so_mac_dinh(cfg)
    gom = {m: [] for m in CO_CHE}
    for sdl in cfg["seed_dl"]:
        truong = sinh.sinh_truong(seed=sdl, **ts)
        kb = dung_kich_ban(truong)
        st, clubs, sc, app, prefs = kb["students"], kb["clubs"], kb["scores"], kb["app"], kb["prefs"]
        elig = loi.default_reserve_eligible_fn(st, clubs)
        theo_m = {m: [] for m in CO_CHE}
        for sbt in cfg["seed_bt"]:
            stb = loi.generate_stb_lottery(sorted(st), sbt)
            base_rank = cc.tinh_base_rank(clubs, sc, app, stb)
            chon = cc._ham_chon(clubs, base_rank, elig)
            kq = loi.run_rbda(st, clubs, sc, app, prefs, stb, elig)
            ket = {"rbda": (dict(kq.assignment), dict(kq.matched_tier))}
            for m, ham in (("boston", cc.co_che_boston), ("thu_tu_boc_tham", cc.co_che_thu_tu_boc_tham),
                           ("ttc", cc.co_che_ttc), ("da_clb_de_xuat", cc.da_clb_de_xuat)):
                ket[m] = (ham(st, clubs, sc, app, prefs, stb, elig), {})
            for m in CO_CHE:
                xep, tang = ket[m]
                cap_chan = len(loi.verify_stability(kq, clubs, prefs, elig)) if m == "rbda" else dem_cap_chan(xep, clubs, prefs, base_rank, chon)
                ci = cs.tinh_chi_so(st, clubs, prefs, app, sc, xep, tang, elig, nhom=_nhom(truong), cap_chan=cap_chan)
                theo_m[m].append(lam_phang(ci))
        for m in CO_CHE:
            ph = theo_m[m]
            gom[m].append({k: sum(p[k] for p in ph) / len(ph) for k in ph[0]})
        print("  co_che seed_dl=%d xong" % sdl, flush=True)
    ra = {}
    for m in CO_CHE:
        ra[m] = {k: tong_hop([r[k] for r in gom[m]]) for k in gom[m][0]}
    return {"tham_so": ts, "seed_du_lieu": cfg["seed_dl"], "seed_boc_tham": cfg["seed_bt"], "co_che": ra,
            "ghi_chu": "Suất dự trữ dùng (tang) chỉ có ở RB-DA; các cơ chế đối chứng đều gọi `club_choice_function` thật nhưng không ghi tầng. "
                       "Cặp phá vỡ: RB-DA qua `verify_stability`; cơ chế khác qua cùng vòng lặp với `cc.thong_ke`."}


def phan_thoi_gian(cfg):
    import statistics as st
    ra = []
    for (n, m) in cfg["thoi_gian"]:
        ts = {"n_hs": n, "n_clb": m, "alpha": 0.5, "rho": 0.7, "kappa": 1.1}
        truong = sinh.sinh_truong(seed=cfg["seed_dl"][0], **ts)
        kb = dung_kich_ban(truong)
        ts_run, vong = [], []
        for _ in range(3):
            ci, kq, dt = chay_mot(kb, 1, truong)
            ts_run.append(dt)
            vong.append(kq.rounds_run)
        hang = {"n_hs": n, "n_clb": m, "run_rbda_giay": {"trung_vi": round(st.median(ts_run), 5), "cac_lan": [round(x, 5) for x in ts_run]},
                "vong": vong[0]}
        if cfg.get("pipeline_that", True):
            from api import PipelineAPI
            import cau_hinh_ws
            with tempfile.TemporaryDirectory() as tmp:
                x = os.path.join(tmp, "so.xlsx")
                t0 = time.perf_counter()
                sinh.sinh_so_nhap(truong, x)
                t_ghi = time.perf_counter() - t0
                import base64
                api = PipelineAPI(os.path.join(tmp, "app.db"))
                cau_hinh_ws.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
                with open(x, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                t0 = time.perf_counter()
                kq = api.import_so_nhap(b64)
                t_nap = time.perf_counter() - t0
                if not kq["ok"]:
                    raise RuntimeError("nạp sổ nhập: %r" % kq["errors"])
                ts_pl = []
                for lan in range(3):
                    t0 = time.perf_counter()
                    r = api.run_pipeline(seed=1 + lan)
                    ts_pl.append(time.perf_counter() - t0)
                    if not r["ok"]:
                        raise RuntimeError("run_pipeline: %r" % r["errors"])
                hang["ghi_so_nhap_giay"] = round(t_ghi, 3)
                hang["nap_so_nhap_giay"] = round(t_nap, 3)
                hang["run_pipeline_giay"] = {"trung_vi": round(st.median(ts_pl), 3), "cac_lan": [round(x, 3) for x in ts_pl],
                                             "ghi_chu": "5 bước: sao lưu, kiểm, khoá STB, giải, ghi một giao dịch, xuất tệp"}
        ra.append(hang)
        print("  thoi_gian %dx%d: rbda %.3fs" % (n, m, hang["run_rbda_giay"]["trung_vi"]), flush=True)
    return {"cac_quy_mo": ra, "ghi_chu": "Thời gian CPU tường (perf_counter), máy ghi ở lan_chay.may; median của 3 lần."}


def phan_nhieu_buoi(cfg):
    ts = {"n_hs": cfg["mac_dinh"]["n_hs"], "n_clb": cfg["mac_dinh"]["n_clb"], "alpha": 0.5, "rho": 0.7, "kappa": 1.1}
    theo_truong = []
    for sdl in cfg["seed_dl"]:
        truong = sinh.sinh_truong(seed=sdl, so_buoi=3, **ts)
        st, clubs = truong["students"], truong["clubs"]
        sc, app, prefs = truong["tested_scores"], truong["applicants"], truong["preferences"]
        elig = loi.default_reserve_eligible_fn(st, clubs)
        lan = []
        for sbt in cfg["seed_bt"]:
            stb = loi.generate_stb_lottery(sorted(st), sbt)
            kt = loi.run_rbda_nhieu_buoi(st, clubs, sc, app, prefs, stb, elig, seed=sbt)
            pha_vo = loi.verify_stability_tuan(kt, clubs, prefs, elig)
            theo_b = {}
            xep_b, nv_b = {}, {}
            for b in kt.ds_buoi:
                cb, sb, ab, pb = loi.cat_du_lieu_theo_buoi(b, loi.nhom_theo_buoi(clubs)[b], clubs, sc, app, prefs)
                kq = kt.per_buoi[b]
                ci = cs.tinh_chi_so(st, cb, pb, ab, sb, kq.assignment, kq.matched_tier, elig,
                                    nhom=_nhom(truong), cap_chan=len(pha_vo[b]))
                theo_b[b] = lam_phang(ci)
                xep_b[b] = dict(kq.assignment)
                nv_b[b] = pb
            tong = cs.tong_hop_theo_hoc_sinh(xep_b, nv_b)
            lan.append({"theo_buoi": theo_b, "theo_hoc_sinh": tong})
        buoi = sorted(lan[0]["theo_buoi"])
        row = {"seed_du_lieu": sdl,
               "theo_buoi": {b: {k: sum(x["theo_buoi"][b][k] for x in lan) / len(lan) for k in lan[0]["theo_buoi"][b]} for b in buoi},
               "theo_hoc_sinh": {k: sum(x["theo_hoc_sinh"][k] for x in lan) / len(lan) for k in lan[0]["theo_hoc_sinh"]}}
        theo_truong.append(row)
        print("  nhieu_buoi seed_dl=%d xong" % sdl, flush=True)
    buoi = sorted(theo_truong[0]["theo_buoi"])
    return {"tham_so": dict(ts, so_buoi=3), "seed_du_lieu": cfg["seed_dl"], "seed_boc_tham": cfg["seed_bt"],
            "theo_buoi": {b: {k: tong_hop([r["theo_buoi"][b][k] for r in theo_truong]) for k in theo_truong[0]["theo_buoi"][b]
                              if k in set(CHI_SO_QUET) | {"a.cap_chan"}} for b in buoi},
            "theo_hoc_sinh": {k: tong_hop([r["theo_hoc_sinh"][k] for r in theo_truong]) for k in theo_truong[0]["theo_hoc_sinh"]},
            "ghi_chu": "Mỗi buổi: chỉ số A–C trên riêng buổi đó (mẫu số = mọi học sinh). theo_hoc_sinh: xem định nghĩa `tong_hop_theo_hoc_sinh`."}


# Bộ dữ liệu có sẵn (chạy nguyên trạng).
CO_SAN = [
    ("bo_sach", "csv", ["bo_sach/SACH_01_danh_sach_CLB.csv", "bo_sach/SACH_02_chon_CLB_muon_thi.csv", "bo_sach/SACH_03_xep_hang_nguyen_vong.csv"]),
    ("bo_can_bang", "csv", ["bo_can_bang/CANBANG_01_danh_sach_CLB.csv", "bo_can_bang/CANBANG_02_chon_CLB_muon_thi.csv", "bo_can_bang/CANBANG_03_xep_hang_nguyen_vong.csv"]),
    ("bo_kich_tran", "csv", ["bo_kich_tran/KICHTRAN_01_danh_sach_CLB.csv", "bo_kich_tran/KICHTRAN_02_chon_CLB_muon_thi.csv", "bo_kich_tran/KICHTRAN_03_xep_hang_nguyen_vong.csv"]),
    ("TEST_0x", "csv", ["TEST_01_danh_sach_CLB.xlsx", "TEST_02_chon_CLB_muon_thi.xlsx", "TEST_03_xep_hang_nguyen_vong.xlsx"]),
    ("SO_NHAP_DQT_800HS_HOP_LE", "so_nhap", ["SO_NHAP_DQT_800HS_HOP_LE.xlsx"]),
]


def nap_co_san(loai, files):
    from do_anh_huong_seed import nap_bo
    tmp = tempfile.mkdtemp()
    try:
        if loai == "csv":
            db = nap_bo(tmp, files)
            return loi.load_from_sqlite(db)
        _db, du = sinh.doc_qua_phan_mem(os.path.join(os.path.dirname(THU_MUC), files[0]), tmp)
        return du
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def chay_du_lieu_co_san(ten, du_lieu, seeds_bt):
    students, clubs, sc, app, prefs, _stb = du_lieu
    elig = loi.default_reserve_eligible_fn(students, clubs)
    khoi = {s: "?" for s in students}
    nhom = {"du_tru": {s: (v["reserve_group"] or "khong") for s, v in students.items()}, "khoi": khoi}
    lan = []
    for sbt in seeds_bt:
        stb = loi.generate_stb_lottery(sorted(students), sbt)
        kq = loi.run_rbda(students, clubs, sc, app, prefs, stb, elig)
        cap = len(loi.verify_stability(kq, clubs, prefs, elig))
        ci = cs.tinh_chi_so(students, clubs, prefs, app, sc, kq.assignment, kq.matched_tier, elig, nhom=nhom, cap_chan=cap)
        ci["vong"] = kq.rounds_run
        lan.append((sbt, ci))
    phang = [lam_phang(ci) for _s, ci in lan]
    return {"ten": ten, "n_hs": len(students), "n_clb": len(clubs), "seed_boc_tham": list(seeds_bt),
            "chi_so": {k: {"tb": round(sum(p[k] for p in phang) / len(phang), 4),
                           "sd_boc_tham": round(statistics.stdev([p[k] for p in phang]), 4) if len(phang) > 1 else 0.0}
                       for k in phang[0]},
            "theo_clb_lan_dau": lan[0][1]["c"]["theo_clb"], "ghi_chu": "Một bộ dữ liệu cố định: chỉ có phương sai do bốc thăm (không có KTC giữa các trường)."}


def phan_co_san(cfg):
    ra = []
    for ten, loai, files in CO_SAN:
        du = nap_co_san(loai, files)
        ra.append(chay_du_lieu_co_san(ten, du, cfg["seed_bt"]))
        print("  co_san %s xong" % ten, flush=True)
    return {"cac_bo": ra}


def phan_doi_chieu():
    """Cổng bắt buộc: bộ TEST, seed 42, ĐI QUA `run_pipeline` thật = 108/120, NV1 = 64 (SO_LIEU_DA_KIEM_CHUNG.md §2)
    và đường lõi trong bộ nhớ cho ĐÚNG kết quả đó, 0 cặp phá vỡ."""
    import sqlite3
    from api import PipelineAPI
    from do_anh_huong_seed import BO_DU_LIEU, nap_bo
    ten, files = BO_DU_LIEU[2]
    tmp = tempfile.mkdtemp()
    try:
        db = nap_bo(tmp, files)
        r = PipelineAPI(db).run_pipeline(seed=42)
        if not r["ok"]:
            raise RuntimeError("run_pipeline: %r" % r["errors"])
        c = sqlite3.connect(db)
        dong = c.execute("SELECT student_id, club_id, rank_in_student_pref FROM match_results").fetchall()
        c.close()
        pl = {s: cid for s, cid, _h in dong}
        du = loi.load_from_sqlite(db)
        students, clubs, sc, app, prefs, _ = du
        stb = loi.generate_stb_lottery(sorted(students), 42)
        elig = loi.default_reserve_eligible_fn(students, clubs)
        kq = loi.run_rbda(students, clubs, sc, app, prefs, stb, elig)
        cap = len(loi.verify_stability(kq, clubs, prefs, elig))
        ket = {
            "bo": ten.strip(), "seed": 42, "n_hs": len(students),
            "pipeline": {"duoc_xep": sum(1 for v in pl.values() if v), "nv1": sum(1 for _s, c_, h in dong if h == 1)},
            "loi_trong_bo_nho": {"duoc_xep": sum(1 for v in kq.assignment.values() if v),
                                 "nv1": sum(1 for h in kq.rank_in_student_pref.values() if h == 1), "vong": kq.rounds_run},
            "khop_tung_dong_match_results": pl == dict(kq.assignment), "cap_chan": cap,
            "mong_doi": {"duoc_xep": 108, "nv1": 64, "tong": 120, "nguon": "du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md §2"},
        }
        ket["dat"] = (ket["pipeline"] == {"duoc_xep": 108, "nv1": 64} and ket["n_hs"] == 120 and ket["khop_tung_dong_match_results"]
                      and ket["loi_trong_bo_nho"]["duoc_xep"] == 108 and ket["loi_trong_bo_nho"]["nv1"] == 64 and cap == 0)
        return ket
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# Điều phối
# ---------------------------------------------------------------------------

def cau_hinh_chay(che_do):
    if che_do == "nhanh":
        return {"che_do": "nhanh", "quy_mo": [(120, 10), (300, 10)], "alpha": [0.0, 0.5, 0.9], "kappa": [1.1], "rho": [0.7],
                "seed_dl": SEED_DU_LIEU[:2], "seed_bt": SEED_BOC_THAM[:3], "mac_dinh": {"n_hs": 300, "n_clb": 10, "alpha": 0.5, "rho": 0.7, "kappa": 1.1},
                "thoi_gian": [(120, 10), (300, 10)], "pipeline_that": False}
    if che_do == "giam":
        return {"che_do": "giam", "quy_mo": QUY_MO, "alpha": ALPHA, "kappa": KAPPA, "rho": RHO, "seed_dl": SEED_DU_LIEU[:3],
                "seed_bt": SEED_BOC_THAM[:5], "mac_dinh": dict(MAC_DINH), "thoi_gian": QUY_MO + [(2000, 50)]}
    return {"che_do": "day_du", "quy_mo": QUY_MO, "alpha": ALPHA, "kappa": KAPPA, "rho": RHO, "seed_dl": SEED_DU_LIEU,
            "seed_bt": SEED_BOC_THAM, "mac_dinh": dict(MAC_DINH), "thoi_gian": QUY_MO + [(2000, 50)]}


def dinh_nghia(cfg):
    return {
        "luu_y": "TOÀN BỘ số đo trên DỮ LIỆU MÔ PHỎNG, không phải khảo sát học sinh thật.",
        "chi_so": cs.DINH_NGHIA,
        "tham_so_sinh": sinh.tham_so_sinh(),
        "seed_du_lieu": cfg["seed_dl"], "seed_boc_tham": cfg["seed_bt"],
        "so_truong": len(cfg["seed_dl"]), "so_lan_boc_tham_moi_truong": len(cfg["seed_bt"]),
        "cach_tinh_ktc": "KTC 95 % kiểu t trên trung bình theo TRƯỜNG (n = số seed dữ liệu, bậc tự do n−1, t_{0,975} = "
                         + str(T_975.get(len(cfg["seed_dl"]) - 1)) + "); sd_boc_tham = trung bình độ lệch chuẩn giữa các lần bốc thăm trong cùng một trường.",
        "lat_co_cho_pct": "% học sinh có lúc được xếp, có lúc không, giữa các lần bốc thăm của cùng một trường",
        "lat_clb_pct": "% học sinh có CLB (hoặc 'không xếp') thay đổi giữa các lần bốc thăm của cùng một trường",
        "cau_hinh_chay": {k: v for k, v in cfg.items()},
    }


def thong_tin_lan_chay(lenh, t_bat_dau):
    try:
        ma = subprocess.check_output(["git", "-C", GOC, "rev-parse", "HEAD"], text=True).strip()
        sach = subprocess.check_output(["git", "-C", GOC, "status", "--porcelain", "--", ":!du_lieu_test/danh_gia/ket_qua"], text=True).strip() == ""
    except Exception:
        ma, sach = "khong_ro", None
    import platform
    return {"lenh": lenh, "commit": ma, "cay_lam_viec_sach": sach, "python": sys.version.split()[0], "may": platform.platform(),
            "bat_dau": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t_bat_dau)), "thoi_gian_giay": round(time.time() - t_bat_dau, 1)}


def ghi_json(duong, noi_dung, cfg, lenh, t0):
    noi_dung = dict(noi_dung)
    noi_dung["dinh_nghia"] = dinh_nghia(cfg)
    noi_dung["lan_chay"] = thong_tin_lan_chay(lenh, t0)
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w", encoding="utf-8") as f:
        json.dump(noi_dung, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    print("  ghi %s (%.0f KB)" % (os.path.relpath(duong, GOC), os.path.getsize(duong) / 1024), flush=True)


PHAN = ["doi_chieu", "mac_dinh", "co_che", "bien_the", "quet", "thoi_gian", "nhieu_buoi", "co_san"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--nhanh", action="store_true", help="120 & 300, α ∈ {0,0.5,0.9}, 2 trường × 3 lần bốc thăm → ket_qua_nhanh/")
    g.add_argument("--day-du", action="store_true", help="bộ đầy đủ → ket_qua/ (mặc định nếu không có cờ nào)")
    g.add_argument("--giam", action="store_true", help="lưới giảm: 3 trường × 5 lần bốc thăm → ket_qua/")
    g.add_argument("--so-nhap", metavar="PATH", help="Sổ nhập THẬT: chỉ chạy mặc định + so cơ chế, ra ket_qua_that/ (KHÔNG commit)")
    ap.add_argument("--phan", nargs="*", choices=PHAN, help="chỉ chạy các phần này")
    ap.add_argument("--ra", help="thư mục ra (mặc định theo chế độ)")
    a = ap.parse_args(argv)
    che_do = "nhanh" if a.nhanh else ("giam" if a.giam else "day_du")
    cfg = cau_hinh_chay(che_do)
    ra = a.ra or os.path.join(THU_MUC, "ket_qua_nhanh" if a.nhanh else ("ket_qua_that" if a.so_nhap else "ket_qua"))
    lenh = "python du_lieu_test/danh_gia/do_danh_gia.py " + " ".join(argv if argv is not None else sys.argv[1:])
    t0 = time.time()

    if a.so_nhap:
        return chay_that(a.so_nhap, cfg, ra, lenh, t0)

    phan = a.phan or PHAN
    print("DG1 — chế độ %s, %d trường × %d lần bốc thăm → %s" % (che_do, len(cfg["seed_dl"]), len(cfg["seed_bt"]), ra), flush=True)
    dc = phan_doi_chieu()
    if not dc["dat"]:
        ghi_json(os.path.join(ra, "doi_chieu_so_lieu.json"), dc, cfg, lenh, t0)
        print("!! ĐỐI CHIẾU SỐ LIỆU LỆCH: %r — dừng." % dc, file=sys.stderr)
        return 2
    ghi_json(os.path.join(ra, "doi_chieu_so_lieu.json"), dc, cfg, lenh, t0)
    cac = {"mac_dinh": ("mac_dinh.json", phan_mac_dinh), "co_che": ("co_che_doi_chung.json", phan_co_che),
           "bien_the": ("bien_the_tieu_chi.json", phan_bien_the), "quet": ("quet_quy_mo.json", phan_quet),
           "thoi_gian": ("thoi_gian.json", phan_thoi_gian), "nhieu_buoi": ("nhieu_buoi.json", phan_nhieu_buoi),
           "co_san": ("bo_co_san.json", phan_co_san)}
    for p in PHAN:
        if p in phan and p in cac:
            ten, ham = cac[p]
            t1 = time.time()
            print("[%s]" % p, flush=True)
            kq = ham(cfg)
            ghi_json(os.path.join(ra, ten), kq, cfg, lenh, t0)
            print("[%s] %.1fs" % (p, time.time() - t1), flush=True)
    print("XONG %.1f giây" % (time.time() - t0))
    return 0


def chay_that(duong, cfg, ra, lenh, t0):
    """Dữ liệu thật: mặc định + so cơ chế trên đúng Sổ nhập đó, gắn nhãn không commit. Không in tên học sinh."""
    tmp = tempfile.mkdtemp()
    try:
        _db, du = sinh.doc_qua_phan_mem(duong, tmp)
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    kq = chay_du_lieu_co_san("so_nhap_that", du, cfg["seed_bt"])
    kq["nhan"] = "dữ liệu thật — không commit"
    kq.pop("theo_clb_lan_dau", None)
    ghi_json(os.path.join(ra, "so_nhap_that.json"), kq, cfg, lenh, t0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
