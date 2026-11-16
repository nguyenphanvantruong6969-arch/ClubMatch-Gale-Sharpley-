"""GT1-L3: phiếu giải trình in (`export_phieu_giai_trinh` + `phieu_giai_trinh.py`). Dữ liệu MÔ PHỎNG.

Một trang một học sinh; mỗi trang chỉ có mã / tên của chính em; lớp rỗng -> `gt1_khong_co_hoc_sinh`; dấu tiếng Việt
nguyên vẹn; HTML tự đủ (không địa chỉ ngoài), mọi giá trị được thoát; cảnh báo "dữ liệu đã đổi" ở MỌI trang;
số ngày khiếu nại chỉ khi bật; không ghi vào CSDL; chạy lại một lần (không gọi API mỗi em).
"""

import re

import cau_hinh_ws as ch
import phieu_giai_trinh
from _fa import bat_fa, dung_fa_clb, ma
from _wharton import tat_wharton

HS = {"s1": ("Nguyễn Văn Ánh", "10A1"), "s2": ("Trần Thị Bé", "10A2"), "s3": ("Lê Đức <b>X</b>", "10A1")}


def _dung(api, fa=False):
    if fa:
        bat_fa(api)
        dung_fa_clb(api, A=(1, "GIOI_HAN", None, None, None, "thu_2"), T=(9, "TU_DO", None, None, None, "thu_2"))
        nv = ["A", "T"]
    else:
        tat_wharton(api)
        dung_fa_clb(api, A=(1, None, None, None, None, "thu_2"), B=(5, None, None, None, None, "thu_2"))
        nv = ["A", "B"]
    for sid, (ten, lop) in HS.items():
        assert api.create_student_if_missing(sid, ten)["ok"]
        assert api.submit_preferences(sid, nv)["ok"]
    with api._ket_noi_ghi() as cur:
        for sid, (_, lop) in HS.items():
            cur.execute("UPDATE students SET class_id = ? WHERE student_id = ?", (lop, sid))
    assert api.run_pipeline(seed=3)["ok"]


def _trang(html):
    return re.findall(r'<section class="trang">(.*?)</section>', html, flags=re.S)


def _xuat(api, tmp_path, **kw):
    r = api.export_phieu_giai_trinh(str(tmp_path / "phieu.html"), **kw)
    assert r["ok"], r
    with open(r["data"]["path"], encoding="utf-8") as f:
        return r["data"], f.read()


def test_mot_trang_mot_hoc_sinh_va_chi_co_du_lieu_cua_em_do(api, tmp_path):
    _dung(api)
    d, html = _xuat(api, tmp_path)
    trang = _trang(html)
    assert d["n_trang"] == len(trang) == 3
    for t in trang:
        co = [sid for sid in HS if re.search(r"<b>Mã:</b> %s " % sid, t)]
        assert len(co) == 1
        for sid, (ten, _) in HS.items():
            from html import escape
            assert (escape(ten) in t) == (sid == co[0]), (sid, co)
    assert "Nguyễn Văn Ánh" in html and "Trần Thị Bé" in html          # dấu nguyên vẹn
    assert "<b>X</b>" not in html and "&lt;b&gt;X&lt;/b&gt;" in html    # thoát HTML


def test_chon_theo_ma_theo_lop_va_lop_rong_bao_loi(api, tmp_path):
    _dung(api)
    d, html = _xuat(api, tmp_path, student_ids=["s2"])
    assert d["n_trang"] == 1 and "Trần Thị Bé" in html and "Nguyễn Văn Ánh" not in html
    d, html = _xuat(api, tmp_path, lop="10a1")
    assert d["n_trang"] == 2 and "Trần Thị Bé" not in html
    for kw in ({"lop": "99Z"}, {"student_ids": []}, {"student_ids": ["khong_co"]}):
        assert ma(api.export_phieu_giai_trinh(str(tmp_path / "x.html"), **kw)["errors"]) == ["gt1_khong_co_hoc_sinh"]


def test_chua_chay_bao_loi(api, tmp_path):
    assert ma(api.export_phieu_giai_trinh(str(tmp_path / "x.html"))["errors"]) == ["gt1_chua_chay"]


def test_html_tu_du_khong_dia_chi_ngoai_va_khong_ma_noi_bo(api, tmp_path):
    _dung(api)
    _, html = _xuat(api, tmp_path)
    assert not re.search(r"(?:src|href)\s*=|https?://|url\(|@import|<script|<link", html)
    assert "page-break-after" in html and "@media print" in html
    for noi_bo in ("NO_CHOICES", "FULL_", "HIGHER_CHOICE", "UNASSIGNED", "Wharton", "GT1", "stb", "None"):
        assert noi_bo not in html, noi_bo


def test_canh_bao_da_doi_o_moi_trang(api, tmp_path):
    _dung(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE clubs SET capacity = capacity + 1 WHERE club_id = 'A'")
    _, html = _xuat(api, tmp_path)
    assert html.count(phieu_giai_trinh.CANH_BAO_DA_DOI) == 3
    assert all("canh-bao" in t for t in _trang(html))


def test_so_ngay_khieu_nai_chi_khi_bat(api, tmp_path, api_factory):
    _dung(api)
    _, html = _xuat(api, tmp_path)
    assert "liên hệ giáo viên phụ trách." in html and "ngày" not in html
    api2 = api_factory()
    _dung(api2, fa=True)
    ch.ghi_cau_hinh(api2.db_path, {"rules": {"fa_daa": True, "fa_diem_danh": True, "fa_khieu_nai": True,
                                             "fa_khieu_nai_so_ngay": 5}})
    _, html = _xuat(api2, tmp_path)
    assert "trong 5 ngày" in html


def test_fa_bat_van_ra_phieu_va_khong_ghi_csdl(api, tmp_path):
    _dung(api, fa=True)

    def chup():
        with api._ket_noi_doc() as cur:
            return [cur.execute("SELECT COUNT(*), COALESCE(SUM(rowid),0) FROM %s" % b).fetchone()[:]
                    for b in ("match_results", "run_history", "stb_lock", "students", "fa_ly_do")]
    truoc = chup()
    d, html = _xuat(api, tmp_path)
    assert d["n_trang"] == 3 and "Kết quả:" in html
    assert chup() == truoc


def test_dung_lai_mot_lan_khong_goi_api_moi_em(api, tmp_path, monkeypatch):
    _dung(api)
    dem = {"n": 0}
    goc = type(api)._giai_trinh_dung_lai

    def dem_goi(self, run_id):
        dem["n"] += 1
        return goc(self, run_id)
    monkeypatch.setattr(type(api), "_giai_trinh_dung_lai", dem_goi)
    _xuat(api, tmp_path)
    assert dem["n"] == 1


def test_phieu_co_cho_trong_cho_ma_tra_cuu(api, tmp_path):
    _dung(api)
    _, html = _xuat(api, tmp_path)
    assert html.count('<div class="ma-tra-cuu"></div>') == 3
