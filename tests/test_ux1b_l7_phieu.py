"""UX1B-L7: nội dung phiếu giải trình — dòng tóm tắt, điểm CLB đã thi (có thanh SVG), "Em nên làm gì tiếp", cột và
chú giải huy chương (chế độ FA), chữ đời thường. KHÔNG có loại CLB (XP1). Dữ liệu MÔ PHỎNG."""

import re

import giai_trinh
import phieu_giai_trinh
from _fa import bat_fa, dung_fa_clb, dung_hs_fa
from _wharton import tat_wharton


def _trang(html):
    return re.findall(r'<section class="trang">(.*?)</section>', html, flags=re.S)


def _phieu(api, tmp_path, sid):
    r = api.export_phieu_giai_trinh(str(tmp_path / ("p_%s.html" % sid)), student_ids=[sid])
    assert r["ok"], r
    with open(r["data"]["path"], encoding="utf-8") as f:
        return f.read()


def _dung_thuong(api):
    tat_wharton(api)
    dung_fa_clb(api, A=(1,), B=(5,))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={"s1": ["A", "B"], "s2": ["A", "B"], "s3": ["A", "B"], "s4": ["A"]})
    for sid in ("s1", "s2"):
        assert api.submit_test_selection(sid, ["A"])["ok"]
    assert api.submit_club_scores("A", [{"student_id": "s1", "score": 9}, {"student_id": "s2", "score": 5}])["ok"]
    assert api.run_pipeline(seed=3)["ok"]


def _dung_fa(api):
    bat_fa(api)
    dung_fa_clb(api, G=(2, "GIOI_HAN"), T=(9, "TU_DO"))
    dung_hs_fa(api, "s1", "s2", "s3", "s4", nv={s: ["G", "T"] for s in ("s1", "s2", "s3", "s4")})
    for sid, m in (("s1", 60), ("s2", 30), ("s3", 10)):
        assert api.submit_huy_chuong(sid, {"G": m})["ok"]
    assert api.run_pipeline(seed=3)["ok"]


# ---------------------------------------------------------------- 1. dòng tóm tắt
def test_dong_tom_tat_mot_buoi(api, tmp_path):
    _dung_thuong(api)
    assert "Em được xếp vào CLB A." in _phieu(api, tmp_path, "s1").split("<h2>")[0] or \
        "Em được xếp vào CLB A." in _phieu(api, tmp_path, "s1")
    p4 = _phieu(api, tmp_path, "s4")
    assert 'class="tom-tat"' in p4 and "Em chưa có CLB nào." in p4


def test_dong_tom_tat_nhieu_buoi_dem_k_tren_n():
    def b(clb, ten, ket):
        return {"clubs": {clb: {"ten": ten, "capacity": 5, "reserve_capacity": 0, "chon_loc": False}},
                "prefs": {"s": [clb]}, "scores": {}, "stb": {"s": 1}, "assign": {"s": ket}, "base_rank": {clb: {"s": 0}}}
    du = {"fa_bat": False, "du_lieu_da_doi": False, "run": {}, "ds_buoi": ["thu_4", "thu_6"],
          "buoi": {"thu_4": b("X", "CLB Làm vườn", "X"), "thu_6": b("Y", "CLB Mỹ thuật", None)}}
    gt = giai_trinh.giai_trinh_mot_hoc_sinh(du, "s")
    assert gt["tom_tat_dong"] == "Em có 1/2 buổi: CLB Làm vườn (Thứ 4)."
    du["buoi"]["thu_6"]["assign"]["s"] = "Y"
    assert giai_trinh.giai_trinh_mot_hoc_sinh(du, "s")["tom_tat_dong"] == \
        "Em có 2/2 buổi: CLB Làm vườn (Thứ 4), CLB Mỹ thuật (Thứ 6)."
    du["buoi"]["thu_4"]["assign"]["s"] = du["buoi"]["thu_6"]["assign"]["s"] = None
    assert giai_trinh.giai_trinh_mot_hoc_sinh(du, "s")["tom_tat_dong"] == "Em chưa có CLB ở buổi nào."


# ---------------------------------------------------------------- 2-3. điểm CLB đã thi + SVG
def test_diem_da_thi_va_svg_chi_voi_clb_em_da_thi(api, tmp_path):
    _dung_thuong(api)
    p1, p3 = _phieu(api, tmp_path, "s1"), _phieu(api, tmp_path, "s3")
    assert "<svg" in p1 and "9" in p1 and "Điểm các CLB em đã thi" in p1
    assert "<svg" not in p3 and "Điểm các CLB em đã thi" not in p3
    assert "<script" not in p1 and "http" not in p1                    # tự đủ


def test_clb_da_thi_ngoai_nguyen_vong_van_co_diem_va_muc_vao_duoc():
    b = {"clubs": {"A": {"ten": "CLB A", "capacity": 1, "reserve_capacity": 0, "chon_loc": True},
                   "C": {"ten": "CLB C", "capacity": 1, "reserve_capacity": 0, "chon_loc": True}},
         "prefs": {"s": ["A"], "u": ["C"]}, "scores": {"A": {"s": 7.0}, "C": {"s": 6.0, "u": 8.0}},
         "stb": {"s": 1, "u": 2}, "assign": {"s": "A", "u": "C"}, "base_rank": {"A": {"s": 0}, "C": {"u": 0, "s": 1}}}
    du = {"fa_bat": False, "du_lieu_da_doi": False, "run": {}, "ds_buoi": ["__mac_dinh__"], "buoi": {"__mac_dinh__": b}}
    gt = giai_trinh.giai_trinh_mot_hoc_sinh(du, "s")
    thi = {x["club_id"]: x for x in gt["buoi"][0]["diem_da_thi"]}
    assert set(thi) == {"A", "C"} and thi["C"]["trong_nv"] is False and thi["C"]["diem_em"] == 6.0
    assert thi["C"]["diem_chuan"] == 8.0 and thi["C"]["diem_chuan_loai"] == "diem"
    html = phieu_giai_trinh.dung_phieu_html([(gt, ("s", "Em S", None), None)])
    assert html.count("<svg") == 2 and "u" not in re.findall(r"<b>Mã:</b> (\w+)", html)


# ---------------------------------------------------------------- 4. "Em nên làm gì tiếp"
def test_buoc_tiep_chi_khi_chua_co_cho_va_chi_ghi_tinh_nang_dang_bat(api, tmp_path):
    _dung_thuong(api)
    p1, p4 = _phieu(api, tmp_path, "s1"), _phieu(api, tmp_path, "s4")
    assert "Em nên làm gì tiếp" not in p1
    assert "Em nên làm gì tiếp" in p4 and "hỏi giáo viên phụ trách" in p4
    assert "vòng 2" not in p4 and "khiếu nại" not in p4.split("Em nên làm gì tiếp")[1].split("</ul>")[0]


def test_buoc_tiep_ghi_vong_2_va_khieu_nai_khi_bat():
    import cau_hinh_ws  # noqa: F401
    b = {"clubs": {"A": {"ten": "CLB A", "capacity": 0, "reserve_capacity": 0, "chon_loc": False}},
         "prefs": {"s": ["A"]}, "scores": {}, "stb": {"s": 1}, "assign": {}, "base_rank": {"A": {}}}
    du = {"fa_bat": False, "du_lieu_da_doi": False, "run": {}, "ds_buoi": ["__mac_dinh__"], "buoi": {"__mac_dinh__": b},
          "tinh_nang": {"vong_2": True, "moi_cho_trong": True, "khieu_nai": True, "so_ngay": 3}}
    gt = giai_trinh.giai_trinh_mot_hoc_sinh(du, "s")
    ghep = " ".join(gt["buoc_tiep"])
    assert "vòng 2" in ghep and "danh sách chờ" in ghep and "3 ngày" in ghep and "giáo viên phụ trách" in ghep


# ---------------------------------------------------------------- 5. huy chương (FA)
def test_fa_moi_dong_co_huy_chuong_dung_va_chu_giai(api, tmp_path):
    _dung_fa(api)
    gt = api.get_giai_trinh_hoc_sinh("s2")["data"]
    dong = {x["club_id"]: x for x in gt["buoi"][0]["cac_lua_chon"]}
    assert dong["G"]["huy_chuong"] == "Bạc" and dong["T"]["huy_chuong"] is None
    p1 = _phieu(api, tmp_path, "s1")
    assert "<th>Huy chương</th>" in p1 and "Vàng" in p1
    assert "Huy chương:" in p1 and "Vàng, rồi Bạc, rồi Đồng" in p1
    assert "<th>Loại CLB</th><th>Huy chương</th>" in p1               # UX1I-I3: cột Loại CLB (XP1) rồi cột Huy chương (B)


def test_fa_dong_ly_do_medal_goi_ten_huy_chuong(api, tmp_path):
    _dung_fa(api)
    p3 = _phieu(api, tmp_path, "s3")
    assert "Em đặt huy chương Đồng; các bạn đặt Bạc ở CLB G được xét trước." in p3
    p4 = _phieu(api, tmp_path, "s4")
    assert "Em chưa đặt huy chương ở CLB G; các bạn đặt Bạc được xét trước." in p4
    assert "Em s1" not in p3 and "Em s2" not in p3                     # không dữ liệu em khác


def test_khong_fa_khong_co_cot_hay_chu_giai_huy_chuong(api, tmp_path):
    _dung_thuong(api)
    p = _phieu(api, tmp_path, "s1")
    assert "Huy chương" not in p and "huy_chuong" not in p


# ---------------------------------------------------------------- 6. chữ đời thường
def test_chu_doi_thuong_khong_so_khoa_va_cot_moi(api, tmp_path):
    _dung_thuong(api)
    p = _phieu(api, tmp_path, "s2")
    assert "<th>Điểm thi</th>" in p and "<th>Chỗ đã nhận / tối đa</th>" in p
    assert "Bốc thăm" not in p and "số khoá" not in p.lower()
    gt = api.get_giai_trinh_hoc_sinh("s2")["data"]
    assert "huy_chuong" not in gt["buoi"][0]["cac_lua_chon"][0]


# ---------------------------------------------------------------- fix1: CLB không có điểm thi không nói "bằng điểm"
def test_fa_clb_khong_thi_ly_do_medal_khong_noi_bang_diem(api, tmp_path):
    _dung_fa(api)                                    # G = Giới hạn, không điểm thi
    for sid in ("s3", "s4"):
        p = _phieu(api, tmp_path, sid)
        assert "bằng điểm" not in p
        assert "các bạn đặt Bạc" in p and "Các bạn đặt huy chương cao hơn" not in p      # MỘT câu, không lặp ý
    gt = api.get_giai_trinh_hoc_sinh("s3")["data"]
    g = next(x for x in gt["buoi"][0]["cac_lua_chon"] if x["club_id"] == "G")
    assert g["cau"] == "Em đặt huy chương Đồng; các bạn đặt Bạc ở CLB G được xét trước."
    assert g["diem_chuan_loai"] == "huy_chuong" and g["diem_chuan"] == "Bạc"      # CLB không thi: mức vào được là huy chương


def test_fa_clb_co_thi_van_noi_bang_diem():
    import fa_ly_do
    assert "bằng điểm" in fa_ly_do.cau_ly_do({"reason": "MEDAL", "diem_em": 7.0, "outcome": "REJECTED"}, "CLB S")
    assert "bằng điểm" not in fa_ly_do.cau_ly_do({"reason": "MEDAL", "diem_em": None, "outcome": "REJECTED"}, "CLB G")


# ---------------------------------------------------------------- fix1: học sinh tự tra cứu không nhận số khoá bốc thăm
def test_phan_hoi_hoc_sinh_khong_co_seed_nhung_nhan_vien_van_co(api):
    _dung_thuong(api)
    assert api.tao_ma_tra_cuu()["ok"]
    with api._ket_noi_doc() as cur:
        ma = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))
    hs = api.tra_cuu_hoc_sinh("s1", ma["s1"])
    assert hs["ok"], hs
    assert "seed" not in hs["data"]["run"]
    assert all("stb_em" not in x for b in hs["data"]["buoi"] for x in b["cac_lua_chon"])
    nv = api.get_giai_trinh_hoc_sinh("s1")["data"]
    assert nv["run"]["seed"] == 3
    assert any("stb_em" in x for b in nv["buoi"] for x in b["cac_lua_chon"])


# ---------------------------------------------------------------- R1: mức vào được ở chế độ FA (sổ mẫu thật)
def test_r1_fa_clb_co_thi_day_hien_muc_vao_duoc_va_thanh_svg_co_vach_do(api, tmp_path):
    import base64
    import os
    bat_fa(api)
    goc = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(goc, "du_lieu_test", "SO_NHAP_FA_MAU_120HS.xlsx"), "rb") as f:
        assert api.import_so_nhap(base64.b64encode(f.read()).decode())["ok"]
    assert api.run_pipeline(42)["ok"], "sổ FA mẫu phải chạy được"
    with api._ket_noi_doc() as cur:
        ds = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
    co_vach = 0
    for sid in ds:
        gt = api.get_giai_trinh_hoc_sinh(sid)["data"]
        for b in gt["buoi"]:
            for x in b["cac_lua_chon"]:
                if x["chon_loc"]:
                    assert x["diem_chuan_loai"] in ("diem", "con_cho"), (sid, x)      # không còn "—" ở CLB có thi
                    co_vach += x["diem_chuan_loai"] == "diem"
                    if x["diem_chuan_loai"] == "diem":
                        assert x["da_nhan"] >= x["suc_chua"]
            for t in b["diem_da_thi"]:
                if t["diem_chuan_loai"] == "diem":
                    assert t["diem_chuan"] is not None
    assert co_vach > 0, "sổ mẫu có CLB Tuyển chọn đã đầy: phải có ít nhất một mức vào được bằng số"
    p = _phieu(api, tmp_path, "FA001")
    assert "<svg" in p and 'stroke="#b91c1c"' in p                                     # có vạch đỏ mức vào được


# ---------------------------------------------------------------- R1 fix2: cột, thanh SVG và câu "Vì sao" cùng một mức
def _clb_thi_co_giu_cho(api, cho, diem, giu):
    from _fa import giu_cho
    bat_fa(api)
    dung_fa_clb(api, T=(cho, "TUYEN_CHON", 0), U=(9, "TU_DO"))
    dung_hs_fa(api, *diem, nv={s: ["T", "U"] for s in diem})
    for sid, d in diem.items():
        assert api.submit_test_selection(sid, ["T"])["ok"]
    assert api.submit_club_scores("T", [{"student_id": s, "score": d} for s, d in diem.items()])["ok"]
    giu_cho(api, *[("T", s) for s in giu])
    assert api.run_pipeline(seed=3)["ok"]


def _dong_t(api, sid):
    gt = api.get_giai_trinh_hoc_sinh(sid)["data"]
    return next(x for x in gt["buoi"][0]["cac_lua_chon"] if x["club_id"] == "T")


def test_r1_fix2_giu_cho_khong_keo_muc_vao_duoc_xuong_thap(api, tmp_path):
    """T Tuyển chọn 2 chỗ: r giữ chỗ (3 điểm), t 8, x 7. x bị từ chối ở mức 8 (không phải 3)."""
    _clb_thi_co_giu_cho(api, 2, {"r": 3, "t": 8, "x": 7}, ["r"])
    for sid in ("x", "t", "r"):
        d = _dong_t(api, sid)
        assert (d["diem_chuan"], d["diem_chuan_loai"]) == (8.0, "diem"), (sid, d)      # MỘT mức cho mọi dòng của CLB
    x = _dong_t(api, "x")
    assert "8" in x["cau"] and x["ma"] == "SCORE"
    p = _phieu(api, tmp_path, "x")
    assert "8 điểm" in p and "3 điểm" not in p
    thi = api.get_giai_trinh_hoc_sinh("x")["data"]["buoi"][0]["diem_da_thi"]
    assert thi[0]["diem_chuan"] == 8.0 and thi[0]["diem_em"] == 7        # thanh SVG: em (7) dưới vạch đỏ (8)


def test_r1_fix2_nguoi_nhan_cuoi_giu_cho_thi_ghi_cho_danh_rieng_khong_ghi_so(api, tmp_path):
    """T chỉ 1 chỗ và người nhận là r (giữ chỗ): không có mức điểm nào ai đã đạt."""
    _clb_thi_co_giu_cho(api, 1, {"r": 3, "x": 7}, ["r"])
    for sid in ("x", "r"):
        d = _dong_t(api, sid)
        assert (d["diem_chuan"], d["diem_chuan_loai"]) == (None, "giu_cho"), (sid, d)
    p = _phieu(api, tmp_path, "x")
    assert "Chỗ dành riêng" in p and "3 điểm" not in p


def test_r1_fix2_chua_ai_bi_tu_choi_thi_con_cho_khong_co_so(api):
    _clb_thi_co_giu_cho(api, 5, {"r": 3, "x": 7}, [])
    for sid in ("x", "r"):
        d = _dong_t(api, sid)
        assert (d["diem_chuan"], d["diem_chuan_loai"]) == (None, "con_cho")
