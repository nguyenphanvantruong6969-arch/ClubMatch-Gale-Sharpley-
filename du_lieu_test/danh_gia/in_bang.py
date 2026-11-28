# -*- coding: utf-8 -*-
"""In bảng Markdown tóm tắt từ các JSON của `do_danh_gia.py`. KHÔNG có câu diễn giải — chỉ số, định nghĩa cột, nguồn.

    python du_lieu_test/danh_gia/in_bang.py [THƯ_MỤC_JSON] [--phan mac_dinh co_che ...]

Số kiểu Việt Nam (dấu phẩy thập phân). «tb [KTC 95 %]» = trung bình qua các trường mô phỏng và khoảng tin cậy t;
«sd bốc» = độ lệch chuẩn giữa các lần bốc thăm trong cùng một trường (trung bình qua các trường).
"""

import json
import os
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
MAC_DINH = os.path.join(THU_MUC, "ket_qua")


def doc(thu_muc, ten):
    p = os.path.join(thu_muc, ten)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def so(x, n=1):
    if x is None:
        return "—"
    return ("{:,.%df}" % n).format(x).replace(",", "§").replace(".", ",").replace("§", ".")


def ktc(c, n=1):
    """«tb [lo; hi]» từ một ô chỉ số {tb, ktc95}."""
    if c is None or c.get("tb") is None:
        return "—"
    if not c.get("ktc95"):
        return so(c["tb"], n)
    return "%s [%s; %s]" % (so(c["tb"], n), so(c["ktc95"][0], n), so(c["ktc95"][1], n))


def bang(tieu_de, dong):
    ra = ["| " + " | ".join(tieu_de) + " |", "|" + "|".join("---" for _ in tieu_de) + "|"]
    ra += ["| " + " | ".join(str(x) for x in d) + " |" for d in dong]
    return "\n".join(ra)


def goc(d):
    l = d.get("lan_chay", {})
    n = d.get("dinh_nghia", {})
    return ("*Nguồn: commit `%s`, lệnh `%s`, %s giây, %d trường × %d lần bốc thăm. Dữ liệu MÔ PHỎNG.*"
            % ((l.get("commit") or "?")[:10], l.get("lenh"), l.get("thoi_gian_giay"),
               n.get("so_truong", 0), n.get("so_lan_boc_tham_moi_truong", 0)))


HANG_CHINH = [
    ("a.pct_nv1_tat_ca", "% được NV1 (mẫu số: mọi học sinh)", 1), ("a.pct_top2_tat_ca", "% trong top 2 (mọi HS)", 1),
    ("a.pct_top3_tat_ca", "% trong top 3 (mọi HS)", 1), ("a.pct_nv1_da_xep", "% NV1 (mẫu số: em được xếp)", 1),
    ("a.hang_tb", "Hạng nguyện vọng trung bình (em được xếp)", 2), ("a.ngoai_danh_sach", "Xếp ngoài danh sách (số em)", 1),
    ("a.cap_chan", "Cặp phá vỡ", 1), ("b.n_chua_xep", "Số em chưa được xếp", 1), ("b.pct_chua_xep", "% chưa được xếp (mọi HS)", 1),
    ("b.can_tren_ghep_cuc_dai", "Cận trên: ghép cực đại", 1), ("b.khong_the_tranh", "Không thể tránh (N − cận trên)", 1),
    ("b.gia_uu_tien_on_dinh", "Giá của ưu tiên + ổn định (cận − được xếp)", 1), ("b.lech_cho", "Lệch chỗ (số em)", 1),
    ("b.nguyen_nhan.danh_sach_rong", "Chưa xếp: danh sách rỗng", 1), ("b.nguyen_nhan.khong_diem", "Chưa xếp: không điểm ở CLB tuyển chọn", 1),
    ("b.nguyen_nhan.het_cho_uu_tien_cao_hon", "Chưa xếp: hết chỗ (người ưu tiên cao hơn)", 1),
    ("c.ty_le_lap_day", "% lấp đầy (đã xếp / Σ chỉ tiêu)", 1), ("c.phan_vi_lap_day.min", "Lấp đầy CLB: min", 2),
    ("c.phan_vi_lap_day.median", "Lấp đầy CLB: trung vị", 2), ("c.n_clb_day", "Số CLB đầy", 1), ("c.n_clb_duoi_50", "Số CLB lấp đầy < 50 %", 1),
    ("c.du_tru_cung_cap", "Suất dự trữ cung cấp", 1), ("c.du_tru_da_dung", "Suất dự trữ đã dùng", 1),
    ("c.du_tru_dien_qua_du_tru", "Em diện dự trữ vào qua suất dự trữ", 1), ("c.du_tru_dien_qua_thuong", "Em diện dự trữ vào qua suất thường", 1),
    ("vong", "Số vòng thuật toán", 1),
]


def in_mac_dinh(d):
    cs = d["chi_so"]
    ts = d["tham_so"]
    ra = ["### Cấu hình mặc định: %d HS × %d CLB, α = %s, ρ = %s, κ = %s (κ thực = %s)" % (
        ts["n_hs"], ts["n_clb"], so(ts["alpha"], 2), so(ts["rho"], 1), so(ts["kappa"], 2), so(d.get("kappa_thuc"), 3)), ""]
    ra.append(bang(["Chỉ số", "tb [KTC 95 %]", "sd bốc"], [(t, ktc(cs.get(k), n), so((cs.get(k) or {}).get("sd_boc_tham"), 2))
                                                           for k, t, n in HANG_CHINH if k in cs]))
    ra += ["", "**Đường cong tích luỹ** (% HS được xếp ở nguyện vọng ≤ k, mẫu số: mọi HS)", ""]
    ra.append(bang(["k"] + [str(k) for k in range(1, 7)],
                   [["tb [KTC 95 %]"] + [ktc(cs.get("a.duong_cong_don.%d" % k)) for k in range(1, 7)]]))
    ra += ["", "**Nhóm** (% NV1, mẫu số: HS của nhóm; tb qua các trường)", ""]
    nh = [(k, v) for k, v in cs.items() if k.startswith("a.theo_nhom.") and k.endswith(".pct_nv1")]
    ra.append(bang(["Nhóm", "% NV1", "% chưa xếp = 100 − % được xếp"],
                   [(k[len("a.theo_nhom."):-len(".pct_nv1")], ktc(v), so(None if (cs.get(k.replace(".pct_nv1", ".pct_da_xep")) or {}).get("tb") is None
                                                                       else 100 - cs[k.replace(".pct_nv1", ".pct_da_xep")]["tb"])) for k, v in nh]))
    ra += ["", "**Độ ổn định giữa các lần bốc thăm**: HS có lúc được xếp, có lúc không = %s %% ; HS đổi CLB = %s %%" % (
        ktc(d.get("lat_co_cho_pct")), ktc(d.get("lat_clb_pct"))), ""]
    if d.get("theo_truong") and d["theo_truong"][0].get("theo_clb"):
        n = len(d["theo_truong"])
        ra += ["**Theo CLB (trường mô phỏng đầu tiên, seed dữ liệu %s)**" % d["seed_du_lieu"][0], "",
               bang(["CLB", "Chỉ tiêu", "NV1", "Tỉ lệ cầu", "Đã xếp tb", "Lấp đầy"],
                    [(x["club_id"], x["capacity"], x["nv1"], so(x["ti_le_cau"], 2), so(x["da_xep_tb"], 1), so(x["lap_day_tb"], 3))
                     for x in d["theo_truong"][0]["theo_clb"]]), "", "(%d trường; bảng theo CLB chỉ in trường đầu)" % n, ""]
    ra.append(goc(d))
    return "\n".join(ra)


def in_co_che(d):
    nhan = {"rbda": "RB-DA", "boston": "Boston", "thu_tu_boc_tham": "Thứ tự bốc thăm (RSD)", "ttc": "TTC", "da_clb_de_xuat": "DA do CLB đề xuất"}
    cot = [("a.pct_nv1_tat_ca", "% NV1", 1), ("a.pct_top3_tat_ca", "% top 3", 1), ("a.hang_tb", "Hạng TB", 2),
           ("b.n_chua_xep", "Chưa xếp", 1), ("b.gia_uu_tien_on_dinh", "Cận − xếp", 1), ("c.ty_le_lap_day", "% lấp đầy", 1),
           ("a.cap_chan", "Cặp phá vỡ", 1)]
    ra = ["### So sánh cơ chế (cấu hình mặc định: %s)" % ", ".join("%s=%s" % (k, v) for k, v in d["tham_so"].items()), ""]
    ra.append(bang(["Cơ chế"] + [t for _k, t, _n in cot], [[nhan[m]] + [ktc(d["co_che"][m].get(k), n) for k, _t, n in cot] for m in nhan if m in d["co_che"]]))
    ra += ["", "*" + d["ghi_chu"] + "*", "", goc(d)]
    return "\n".join(ra)


def in_bien_the(d):
    ra = ["### Đổi một tiêu chí (cùng dữ liệu, cùng seed bốc thăm; Δ = biến thể − mặc định)", ""]
    g = d["cac_bien_the"][0]["chi_so"]
    hang = []
    for b in d["cac_bien_the"][1:]:
        c = b["chi_so"]
        ch = b.get("churn", {})
        hang.append((b["bien_the"]["ten"], b["bien_the"]["mo_ta"],
                     so(c["a.pct_nv1_tat_ca"]["tb"] - g["a.pct_nv1_tat_ca"]["tb"], 2), so(c["a.pct_top3_tat_ca"]["tb"] - g["a.pct_top3_tat_ca"]["tb"], 2),
                     so(c["b.n_chua_xep"]["tb"] - g["b.n_chua_xep"]["tb"], 1), so(c["c.ty_le_lap_day"]["tb"] - g["c.ty_le_lap_day"]["tb"], 2),
                     so(ch.get("doi_clb", {}).get("tb"), 1), so(ch.get("tot_hon", {}).get("tb"), 1), so(ch.get("xau_hon", {}).get("tb"), 1),
                     so(c["a.cap_chan"]["tb"], 0)))
    ra.append(bang(["Biến thể", "Thay đổi", "Δ %NV1", "Δ %top3", "Δ chưa xếp (số em)", "Δ %lấp đầy", "Đổi CLB", "Tốt hơn", "Xấu hơn", "Cặp phá vỡ"], hang))
    ra += ["", "Mặc định: %%NV1 = %s, %%top3 = %s, chưa xếp = %s, %%lấp đầy = %s." % (
        ktc(g["a.pct_nv1_tat_ca"]), ktc(g["a.pct_top3_tat_ca"]), ktc(g["b.n_chua_xep"]), ktc(g["c.ty_le_lap_day"])), "",
        "Kiểm: max_choices=10 trùng mặc định = %s; số em đổi CLB khớp `tieu_chi.so_sanh_lan_chay` (mẫu 1 cặp seed): %s" % (
            d["max_choices_10_trung_mac_dinh"], all(x["so_doi_tieu_chi"] == x["doi_clb_do_dg1"] for x in d["doi_chieu_so_sanh_lan_chay"])), "", goc(d)]
    return "\n".join(ra)


def in_quet(d):
    ra = ["### Quét quy mô × α × κ × ρ (tb [KTC 95 %] theo trường)", ""]
    nhom = {}
    for c in d["cac_cau_hinh"]:
        t = c["tham_so"]
        nhom.setdefault((t["n_hs"], t["n_clb"], t["rho"]), []).append(c)
    for (n, m, r), ds in sorted(nhom.items()):
        ra += ["**%d HS × %d CLB, ρ = %s**" % (n, m, so(r, 1)), ""]
        ra.append(bang(["α", "κ", "% NV1", "% top 3", "% chưa xếp", "Cận − xếp", "% lấp đầy", "CLB < 50 %", "Cặp phá vỡ"],
                       [(so(c["tham_so"]["alpha"], 2), so(c["tham_so"]["kappa"], 1), ktc(c["chi_so"].get("a.pct_nv1_tat_ca")),
                         ktc(c["chi_so"].get("a.pct_top3_tat_ca")), ktc(c["chi_so"].get("b.pct_chua_xep")), ktc(c["chi_so"].get("b.gia_uu_tien_on_dinh")),
                         ktc(c["chi_so"].get("c.ty_le_lap_day")), ktc(c["chi_so"].get("c.n_clb_duoi_50")), so(c["chi_so"]["a.cap_chan"]["tb"], 0))
                        for c in sorted(ds, key=lambda x: (x["tham_so"]["alpha"], x["tham_so"]["kappa"]))]))
        ra.append("")
    ra.append(goc(d))
    return "\n".join(ra)


def in_thoi_gian(d):
    ra = ["### Thời gian chạy (median của 3 lần)", ""]
    ra.append(bang(["HS × CLB", "run_rbda (s)", "Số vòng", "Ghi sổ nhập (s)", "Nạp sổ nhập (s)", "run_pipeline 5 bước (s)"],
                   [("%d × %d" % (x["n_hs"], x["n_clb"]), so(x["run_rbda_giay"]["trung_vi"], 4), x["vong"], so(x.get("ghi_so_nhap_giay"), 2),
                     so(x.get("nap_so_nhap_giay"), 2), so((x.get("run_pipeline_giay") or {}).get("trung_vi"), 2)) for x in d["cac_quy_mo"]]))
    ra += ["", goc(d)]
    return "\n".join(ra)


def in_nhieu_buoi(d):
    ra = ["### 800 HS × 20 CLB × 3 buổi (mặc định)", ""]
    cot = [("a.pct_nv1_tat_ca", "% NV1", 1), ("a.pct_top3_tat_ca", "% top 3", 1), ("b.pct_chua_xep", "% chưa xếp", 1),
           ("c.ty_le_lap_day", "% lấp đầy", 1), ("a.cap_chan", "Cặp phá vỡ", 1)]
    ra.append(bang(["Buổi"] + [t for _k, t, _n in cot], [[b] + [ktc(v.get(k), n) for k, _t, n in cot] for b, v in sorted(d["theo_buoi"].items())]))
    ra += ["", "**Theo học sinh (mọi buổi)**", "", bang(["Chỉ số", "tb [KTC 95 %]"], [(k, ktc(v, 2)) for k, v in d["theo_hoc_sinh"].items()]), "", goc(d)]
    return "\n".join(ra)


def in_co_san(d):
    ra = ["### Bộ dữ liệu có sẵn (chạy nguyên trạng; tb ± sd qua các lần bốc thăm)", ""]
    mot = [b for b in d["cac_bo"] if "chi_so" in b]
    nhieu = [b for b in d["cac_bo"] if "theo_buoi" in b]
    ra.append(bang(["Bộ (một buổi)", "HS", "CLB", "% NV1", "% top 3", "Chưa xếp", "Cận − xếp", "% lấp đầy", "Cặp phá vỡ"],
                   [(b["ten"], b["n_hs"], b["n_clb"]) + tuple("%s ± %s" % (so(b["chi_so"][k]["tb"], n), so(b["chi_so"][k]["sd_boc_tham"], 2))
                                                         for k, n in (("a.pct_nv1_tat_ca", 1), ("a.pct_top3_tat_ca", 1), ("b.n_chua_xep", 1),
                                                                      ("b.gia_uu_tien_on_dinh", 1), ("c.ty_le_lap_day", 1), ("a.cap_chan", 0)))
                    for b in mot]))
    if nhieu:
        ra += ["", "**Bộ nhiều buổi** (chạy qua `run_rbda_nhieu_buoi`; mỗi dòng một buổi, mẫu số: mọi học sinh)", ""]
        hang = []
        for b in nhieu:
            for buoi, v in sorted(b["theo_buoi"].items()):
                hang.append((b["ten"], buoi, b["n_hs"]) + tuple("%s ± %s" % (so(v[k]["tb"], n), so(v[k]["sd_boc_tham"], 2))
                                                                for k, n in (("a.pct_nv1_tat_ca", 1), ("a.pct_top3_tat_ca", 1), ("b.n_chua_xep", 1),
                                                                             ("b.gia_uu_tien_on_dinh", 1), ("c.ty_le_lap_day", 1), ("a.cap_chan", 0))))
        ra.append(bang(["Bộ", "Buổi", "HS", "% NV1", "% top 3", "Chưa xếp", "Cận − xếp", "% lấp đầy", "Cặp phá vỡ"], hang))
        ra += ["", bang(["Bộ", "Số buổi", "Số buổi có chỗ / em (tb)", "% em đủ chỗ ở mọi buổi đã khai", "% em không có chỗ buổi nào"],
                        [(b["ten"], b["so_buoi"], so(b["theo_hoc_sinh"]["so_buoi_co_cho_tb"]["tb"], 2), so(b["theo_hoc_sinh"]["pct_du_moi_buoi_da_khai"]["tb"], 1),
                          so(b["theo_hoc_sinh"]["pct_khong_co_cho_nao"]["tb"], 1)) for b in nhieu])]
    ra += ["", goc(d)]
    return "\n".join(ra)


def in_doi_chieu(d):
    ra = ["### Đối chiếu `SO_LIEU_DA_KIEM_CHUNG.md` §2 (bộ TEST, seed 42)", ""]
    ra.append(bang(["Đại lượng", "Đo", "Mong đợi"],
                   [("Được xếp (run_pipeline)", d["pipeline"]["duoc_xep"], "%d / %d" % (d["mong_doi"]["duoc_xep"], d["mong_doi"]["tong"])),
                    ("Nguyện vọng 1 (run_pipeline)", d["pipeline"]["nv1"], d["mong_doi"]["nv1"]),
                    ("Được xếp / NV1 (lõi trong bộ nhớ)", "%d / %d" % (d["loi_trong_bo_nho"]["duoc_xep"], d["loi_trong_bo_nho"]["nv1"]), "108 / 64"),
                    ("Khớp từng dòng match_results", d["khop_tung_dong_match_results"], True), ("Cặp phá vỡ", d["cap_chan"], 0)]))
    ra += ["", goc(d)]
    return "\n".join(ra)



def in_tinh_nang(d):
    ra = ["### Tính năng: suất dự trữ × điểm quyết tâm (lưới 2×2, cùng dữ liệu, cùng seed bốc thăm)", ""]
    cot = [("a.pct_nv1_tat_ca", "% NV1", 1), ("a.pct_top3_tat_ca", "% top 3", 1), ("a.hang_tb", "Hạng TB", 2), ("b.n_chua_xep", "Chưa xếp", 1),
           ("c.du_tru_da_dung", "Dự trữ dùng", 1), ("pct_dat_clb_diem_cao", "% vào CLB điểm cao nhất", 1), ("a.cap_chan", "Cặp phá vỡ", 1)]
    tn = {"goc": "tắt / tắt", "du_tru": "dự trữ bật", "wharton": "điểm quyết tâm bật", "du_tru_wharton": "cả hai bật"}
    for c in d["du_tru_wharton"]:
        t = c["tham_so"]
        ra += ["**%d HS × %d CLB, α = %s** (hồ sơ điểm: %d lỗi)" % (t["n_hs"], t["n_clb"], so(t["alpha"], 2), c["kiem_ho_so"]["loi_ho_so"]), ""]
        ra.append(bang(["Ô"] + [x for _k, x, _n in cot], [[tn[o]] + [ktc(c["o"][o].get(k), n) for k, _x, n in cot] for o in tn]))
        nh = ["chinh_sach", "khoi_10", "khong"]
        ra += ["", "Theo nhóm dự trữ, bật − tắt dự trữ (có cặp theo trường): Δ %NV1 / Δ hạng TB / Δ % được xếp (mẫu số: HS của nhóm)", ""]
        h = c["hieu_co_cap"]["du_tru_tru_goc"]
        ra.append(bang(["Nhóm", "Δ %NV1", "Δ hạng TB", "Δ % được xếp"],
                       [(g, ktc(h.get("a.theo_nhom.du_tru.%s.pct_nv1" % g), 2), ktc(h.get("nhom.%s.hang_tb" % g), 3), ktc(h.get("a.theo_nhom.du_tru.%s.pct_da_xep" % g), 2)) for g in nh]))
        dd = c["doi_so_voi"]["du_tru_vs_goc"]
        ra += ["", "Số em đổi CLB khi bật dự trữ (tb mỗi lần chạy): " + "; ".join(
            "%s: đổi %s, tốt hơn %s, xấu hơn %s" % (g, so(dd["%s.doi_clb" % g]["tb"], 2), so(dd["%s.tot_hon" % g]["tb"], 2), so(dd["%s.xau_hon" % g]["tb"], 2)) for g in nh), ""]
    ra += ["### Tính năng: huy chương (FA-DAA) so với chế độ cũ (mô hình `mo_phong_fa_daa`)", ""]
    for c in d["huy_chuong"]:
        ra += ["**%d học sinh** (mẫu số: em × buổi; «thật» = theo độ thích thật, không theo cách em khai)" % c["n_hs"], ""]
        hang = []
        for h, v in c["theo_hanh_vi"].items():
            hang.append((h, ktc(v["cu"]["pt_nv1_that"]), ktc(v["fa"]["pt_nv1_that"]), ktc(v["cu"]["pt_khong_clb"]), ktc(v["fa"]["pt_khong_clb"]),
                         ktc(v["fa"]["pt_dat_clb_vang_tren_co_clb"]), ktc(v["thua_boc_tham_fa_pt"]),
                         "%s / %s / %s" % tuple(so(v["doi_clb_cu_sang_fa"][k]["tb"], 1) for k in ("doi_clb", "tot_hon", "xau_hon"))))
        ra.append(bang(["Hành vi", "% NV1 thật (cũ)", "% NV1 thật (FA)", "% không CLB (cũ)", "% không CLB (FA)", "% vào CLB vàng (FA, trên có CLB)",
                        "% thua bốc thăm (FA)", "Đổi / tốt hơn / xấu hơn (em×buổi mỗi lần chạy)"], hang))
        ra += ["", "Lý do quyết định (% dòng): " + "; ".join("%s = %s" % (k, so(v["tb"], 1)) for k, v in c["ly_do_fa_pt_dong"].items()), ""]
    ra += [goc(d)]
    return "\n".join(ra)


PHAN = [("doi_chieu_so_lieu.json", in_doi_chieu, "doi_chieu"), ("mac_dinh.json", in_mac_dinh, "mac_dinh"),
        ("co_che_doi_chung.json", in_co_che, "co_che"), ("bien_the_tieu_chi.json", in_bien_the, "bien_the"),
        ("quet_quy_mo.json", in_quet, "quet"), ("thoi_gian.json", in_thoi_gian, "thoi_gian"),
        ("nhieu_buoi.json", in_nhieu_buoi, "nhieu_buoi"), ("bo_co_san.json", in_co_san, "co_san"),
        ("tinh_nang.json", in_tinh_nang, "tinh_nang")]


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    chon = None
    if "--phan" in a:
        i = a.index("--phan")
        chon, a = a[i + 1:], a[:i]
    thu_muc = a[0] if a else MAC_DINH
    ra = []
    for ten, ham, ma in PHAN:
        if chon and ma not in chon:
            continue
        d = doc(thu_muc, ten)
        if d is not None:
            ra.append(ham(d))
    if not ra:
        print("Không thấy JSON nào trong %s" % thu_muc, file=sys.stderr)
        return 1
    print("\n\n".join(ra))
    return 0


if __name__ == "__main__":
    sys.exit(main())
