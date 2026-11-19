"""XP1-L2 — phiếu giải trình PDF theo lớp, có loại CLB. Dữ liệu MÔ PHỎNG (cùng bộ dựng với test_gt1_phieu)."""
import os
import re

import pytest

pytest.importorskip("reportlab")

from test_gt1_phieu import HS, _dung  # noqa: E402

try:  # chỉ để đọc lại chữ trong PDF; thiếu thì các ca đọc chữ tự bỏ qua
    import pypdf
except ImportError:
    pypdf = None

can_pypdf = pytest.mark.skipif(pypdf is None, reason="cần pypdf để đọc lại chữ trong PDF")


def _trang_pdf(duong):
    return [p.extract_text() for p in pypdf.PdfReader(duong).pages]


def _n_trang(duong):
    with open(duong, "rb") as f:
        return max(int(m) for m in re.findall(rb"/Count (\d+)", f.read()))


def _tep(thu_muc):
    # tmp_path còn app.db, bản sao lưu và CSV của lần chạy; chỉ xét tệp PDF / tệp tạm do xuất PDF để lại
    return sorted(t for t in os.listdir(thu_muc)
                  if os.path.isfile(os.path.join(thu_muc, t)) and t.endswith((".pdf", ".tmp")))


def _dem_db(api):
    with api._ket_noi_doc() as cur:
        return tuple(cur.execute("SELECT COUNT(*) FROM %s" % b).fetchone()[0]
                     for b in ("match_results", "run_history"))


def test_mot_tep_moi_hoc_sinh_mot_trang(api, tmp_path):
    _dung(api)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"))
    assert r["ok"], r
    d = r["data"]
    assert d["n_trang"] == _n_trang(d["path"]) == 3
    assert os.path.getsize(d["path"]) > 0


@can_pypdf
def test_moi_trang_chi_co_du_lieu_cua_em_do(api, tmp_path):
    _dung(api)
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"))["data"]
    trang = _trang_pdf(d["path"])
    assert len(trang) == 3
    for t in trang:
        co = [sid for sid in HS if re.search(r"Mã:\s*%s\b" % sid, t)]
        assert len(co) == 1
        for sid, (ten, _) in HS.items():
            assert (ten in t) == (sid == co[0]), (sid, co)
    assert "Nguyễn Văn Ánh" in "\n".join(trang) and "Trần Thị Bé" in "\n".join(trang)   # dấu nguyên vẹn


def test_loc_theo_mot_lop(api, tmp_path):
    _dung(api)
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), lop="10A1")["data"]
    assert d["n_trang"] == _n_trang(d["path"]) == 2


def test_lop_khong_co_hoc_sinh(api, tmp_path):
    _dung(api)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), lop="12Z9")
    assert not r["ok"] and r["errors"][0]["code"] == "gt1_khong_co_hoc_sinh"
    assert _tep(tmp_path) == []


def test_theo_lop_mot_tep_moi_lop(api, tmp_path):
    _dung(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("INSERT INTO students (student_id, name) VALUES ('s9', 'Em Chưa Lớp')")
    assert api.run_pipeline(seed=3)["ok"]
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "thu_muc"), theo_lop=True)
    assert r["ok"], r
    d = r["data"]
    assert _tep(d["thu_muc"]) == ["10A1.pdf", "10A2.pdf", "_chua_co_lop.pdf"]
    assert d["n_tep"] == 3 and d["n_trang"] == 4
    assert _n_trang(os.path.join(d["thu_muc"], "10A1.pdf")) == 2
    assert _n_trang(os.path.join(d["thu_muc"], "_chua_co_lop.pdf")) == 1


@can_pypdf
def test_tep_lop_khong_lan_hoc_sinh_lop_khac(api, tmp_path):
    _dung(api)
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "tm"), theo_lop=True)["data"]
    chu = "\n".join(_trang_pdf(os.path.join(d["thu_muc"], "10A2.pdf")))
    assert "Trần Thị Bé" in chu and "Nguyễn Văn Ánh" not in chu and "s1" not in chu


def test_theo_lop_tu_mac_dinh_vao_thu_muc_tai_ve_khong_de(api, tmp_path):
    _dung(api)
    api.thu_muc_xuat = str(tmp_path)
    a = api.export_phieu_giai_trinh_pdf("", theo_lop=True)["data"]["thu_muc"]
    b = api.export_phieu_giai_trinh_pdf("", theo_lop=True)["data"]["thu_muc"]
    assert a != b and os.path.basename(a) == "phieu_giai_trinh_theo_lop"
    assert os.path.basename(b) == "phieu_giai_trinh_theo_lop (2)"
    assert _tep(a) == ["10A1.pdf", "10A2.pdf"]


def test_ten_lop_co_dau_va_gach_cheo_thanh_ten_tep_an_toan(api, tmp_path):
    _dung(api)
    with api._ket_noi_ghi() as cur:
        cur.execute("UPDATE students SET class_id = '10/Ánh' WHERE student_id = 's1'")
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "tm"), theo_lop=True)["data"]
    ten = _tep(d["thu_muc"])
    assert len(ten) == 3 and all("/" not in t for t in ten) and "10_Ánh.pdf" in ten


def test_chua_chay_thi_tu_choi_va_khong_tao_gi(api, tmp_path):
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"))
    assert not r["ok"] and r["errors"][0]["code"] == "gt1_chua_chay"
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "tm"), theo_lop=True)
    assert not r["ok"] and not (tmp_path / "tm").exists() and _tep(tmp_path) == []


def test_khong_doi_du_lieu(api, tmp_path):
    _dung(api)
    truoc = _dem_db(api)
    assert api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"))["ok"]
    assert api.export_phieu_giai_trinh_pdf(str(tmp_path / "tm"), theo_lop=True)["ok"]
    assert _dem_db(api) == truoc


def test_giai_trinh_co_loai_clb_cho_moi_lua_chon(api):
    _dung(api, fa=True)
    r = api.get_giai_trinh_hoc_sinh("s1")
    assert r["ok"], r
    loai = {x["club_id"]: x["loai_clb"] for b in r["data"]["buoi"] for x in b["cac_lua_chon"]}
    assert loai == {"A": "GIOI_HAN", "T": "TU_DO"}


def test_giai_trinh_loai_clb_none_khi_chua_co_loai(api):
    _dung(api)
    r = api.get_giai_trinh_hoc_sinh("s1")
    assert all(x["loai_clb"] is None for b in r["data"]["buoi"] for x in b["cac_lua_chon"])


@can_pypdf
def test_phieu_pdf_ghi_loai_clb_tung_dong(api, tmp_path):
    _dung(api, fa=True)
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), lop="10A1")["data"]
    chu = "\n".join(_trang_pdf(d["path"]))
    assert "Giới hạn" in chu and "Tự do" in chu


@can_pypdf
def test_phieu_pdf_chua_co_loai_ghi_gach(api, tmp_path):
    _dung(api)
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), lop="10A1")["data"]
    assert "Loại CLB" in "\n".join(_trang_pdf(d["path"]))


def test_phieu_html_co_cot_loai_clb(api, tmp_path):
    _dung(api, fa=True)
    r = api.export_phieu_giai_trinh(str(tmp_path / "p.html"))
    html = open(r["data"]["path"], encoding="utf-8").read()
    assert "<th>Loại CLB</th>" in html and "Giới hạn" in html and "Tự do" in html


def test_thieu_thu_vien_pdf_bao_loi_co_ten(api, tmp_path, monkeypatch):
    import xuat_pdf
    _dung(api)
    monkeypatch.setattr(xuat_pdf, "_THU_MUC_PHONG", str(tmp_path / "khong_co"))
    monkeypatch.setattr(xuat_pdf, "_da_dang_ky", False)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"))
    assert not r["ok"] and r["errors"][0]["code"] == "xp1_thieu_thu_vien_pdf"


def test_phieu_pdf_giao_vien_duoc_in_danh_sach_pdf_chi_quan_tri():
    # UX1I-I3: phiếu PDF cùng mức với phiếu HTML (giáo viên chủ nhiệm in phiếu lớp); danh sách có tên vẫn chỉ quản trị
    import phan_quyen
    assert phan_quyen.QUYEN["export_phieu_giai_trinh_pdf"] == phan_quyen.GIAO_VIEN
    assert phan_quyen.QUYEN["export_danh_sach_pdf"] == phan_quyen.QUAN_TRI


def test_mot_hoc_sinh_mot_tep_mot_trang(api, tmp_path):
    _dung(api)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "mot.pdf"), student_ids=["s2"])
    assert r["ok"], r
    assert r["data"]["n_trang"] == _n_trang(r["data"]["path"]) == 1


@can_pypdf
def test_mot_hoc_sinh_chi_co_du_lieu_cua_em_do(api, tmp_path):
    _dung(api)
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "mot.pdf"), student_ids=["s2"])["data"]
    chu = "\n".join(_trang_pdf(d["path"]))
    assert "Trần Thị Bé" in chu and "Nguyễn Văn Ánh" not in chu and "Lê Đức" not in chu


def test_mot_hoc_sinh_ten_tep_mac_dinh_theo_ma(api, tmp_path):
    _dung(api)
    api.thu_muc_xuat = str(tmp_path)
    d = api.export_phieu_giai_trinh_pdf("", student_ids=["s2"])["data"]
    assert os.path.basename(d["path"]) == "phieu_giai_trinh_s2.pdf"


def test_ma_hoc_sinh_la_hoac_rong_bi_tu_choi(api, tmp_path):
    _dung(api)
    for ids in (["khong_co"], []):
        r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "x.pdf"), student_ids=ids)
        assert not r["ok"] and r["errors"][0]["code"] == "gt1_khong_co_hoc_sinh"
    assert _tep(tmp_path) == []


def test_chon_nhieu_hoc_sinh_va_theo_lop(api, tmp_path):
    _dung(api)
    d = api.export_phieu_giai_trinh_pdf(str(tmp_path / "tm"), student_ids=["s1", "s3"], theo_lop=True)["data"]
    assert _tep(d["thu_muc"]) == ["10A1.pdf"] and d["n_trang"] == 2
