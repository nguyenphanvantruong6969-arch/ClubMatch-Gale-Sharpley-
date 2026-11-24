"""CB1-L2 — API + PDF "Văn bản phương án xếp" (`api_phuong_an.py`). Dữ liệu MÔ PHỎNG (bộ `bo_sach`, 140 em / 12 CLB).

Kiểm: chốt ghi MỘT khoá `chot_phuong_an` (+ dòng nhật ký), chốt không đổi cấu hình / `run_history`, `run_thu` và
`chon_muc_tieu` không ghi đè chốt, bản dự kiến không bao giờ có hạt giống, bản chốt phải đủ điều kiện, giáo viên bị
từ chối ở backend, chữ trong PDF không có mã / tên / điểm / số bốc thăm của học sinh, cảnh báo khi đổi sau chốt.
"""

import os
import sqlite3
import sys

import pytest

import api as api_mod
import cau_hinh_ws
import nhat_ky as nk
import phuong_an_xep as pa

pypdf = pytest.importorskip("pypdf")
xuat_pdf = pytest.importorskip("xuat_pdf")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402

BO_SACH = d.BO_DU_LIEU[1][1]
MK = "matkhau-gia-1"
SEED = 31415926          # số lạ để bắt rò rỉ: không đoạn nào khác của PDF trùng chuỗi này


def _sql(db, cau, tham=()):
    c = sqlite3.connect(db)
    try:
        return c.execute(cau, tham).fetchall()
    finally:
        c.close()


def _mo(tmp_path):
    db = d.nap_bo(str(tmp_path), BO_SACH)
    return api_mod.PipelineAPI(db), db


def _chu(duong):
    return "\n".join(p.extract_text() for p in pypdf.PdfReader(duong).pages)


def _xep(a):
    assert a.run_pipeline(seed=SEED)["ok"]


def _ma(r):
    return [e["code"] for e in r["errors"]]


def _chot_row(db):
    return _sql(db, "SELECT value FROM workspace_settings WHERE key = 'chot_phuong_an'")


def _xuat(a, tmp_path, ban, ten="x", **kw):
    r = a.export_van_ban_phuong_an_pdf(str(tmp_path / (ten + ".pdf")), ban, **kw)
    return r


# ----- chốt -----

def test_chot_ghi_mot_khoa_va_khong_doi_cau_hinh_hay_lich_su(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    cfg0 = cau_hinh_ws.doc_cau_hinh(db)
    n_run = _sql(db, "SELECT COUNT(*) FROM run_history")[0][0]
    ket_qua0 = _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi")
    r = a.chot_phuong_an()
    assert r["ok"] and r["data"]["bam_luat"] == pa.bam_luat(cau_hinh_ws.doc_cau_hinh(db))
    assert len(_chot_row(db)) == 1
    assert cau_hinh_ws.doc_cau_hinh(db) == cfg0
    assert _sql(db, "SELECT COUNT(*) FROM run_history")[0][0] == n_run
    assert _sql(db, "SELECT * FROM match_results ORDER BY student_id, buoi") == ket_qua0


def test_chot_nen_ghi_nhat_ky_con_get_thi_khong():
    assert nk.nen_ghi("chot_phuong_an") and nk.nen_ghi("export_van_ban_phuong_an_pdf")
    assert not nk.nen_ghi("get_phuong_an_xep")


def test_chot_co_tai_khoan_ghi_nguoi_va_nhat_ky(tmp_path):
    a, db = _mo(tmp_path)
    assert a.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert a.dang_nhap("quantri", MK)["ok"]
    r = a.chot_phuong_an()
    assert r["ok"] and r["data"]["nguoi"] == "quantri"
    hang = _sql(db, "SELECT nguoi, hanh_dong, ket_qua FROM nhat_ky_thao_tac WHERE hanh_dong = 'chot_phuong_an'")
    assert hang == [("quantri", "chot_phuong_an", "ok")]
    assert a.get_phuong_an_xep()["data"]["chot"]["nguoi"] == "quantri"


def test_chot_lai_ghi_de_mot_hang(tmp_path):
    a, db = _mo(tmp_path)
    assert a.chot_phuong_an()["ok"] and a.chot_phuong_an()["ok"]
    assert len(_chot_row(db)) == 1


def test_run_thu_va_chon_muc_tieu_khong_ghi_de_chot(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    assert a.chot_phuong_an()["ok"]
    chot = _chot_row(db)
    assert a.run_thu({"priority": "tier"})["ok"]
    assert _chot_row(db) == chot
    assert a.chon_muc_tieu("co_hoi")["ok"]
    assert _chot_row(db) == chot
    assert a.run_pipeline(seed=SEED)["ok"]
    assert _chot_row(db) == chot


def test_khoa_chot_khong_doi_doc_cau_hinh(tmp_path):
    a, db = _mo(tmp_path)
    cfg0 = cau_hinh_ws.doc_cau_hinh(db)
    a.chot_phuong_an()
    assert cau_hinh_ws.doc_cau_hinh(db) == cfg0
    assert "chot_phuong_an" not in cfg0


# ----- vai -----

@pytest.mark.parametrize("ham,args", [("get_phuong_an_xep", ()), ("chot_phuong_an", ()),
                                       ("export_van_ban_phuong_an_pdf", ("", "du_kien"))])
def test_giao_vien_bi_tu_choi_o_backend(tmp_path, ham, args):
    a, db = _mo(tmp_path)
    assert a.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert a.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    assert a.dang_nhap("gv1", MK)["ok"]
    r = getattr(a, ham)(*args)
    assert not r["ok"] and _ma(r) == ["gt3_khong_du_quyen"]
    assert _chot_row(db) == []
    a.dang_xuat()
    assert a.dang_nhap("quantri", MK)["ok"]
    assert getattr(a, ham)(*args)["ok"]


# ----- trạng thái -----

def test_get_trang_thai_truoc_va_sau_chot(tmp_path):
    a, db = _mo(tmp_path)
    t = a.get_phuong_an_xep()["data"]
    assert t["co_chot"] is False and t["co_the_xuat"]["du_kien"] is True and t["co_the_xuat"]["chot"] is False
    assert t["co_the_xuat"]["ly_do_chot"] == "cb1_chua_du_dieu_kien_ban_chot"
    assert t["co_the_in_hat_giong"] is False and len(t["quy_trinh"]) == 5 and t["tom_tat_luat"]
    assert t["tom_tat_luat_tang"] and all(g["tieu_de"] and g["dong"] for g in t["tom_tat_luat_tang"])   # CB1-FIX3
    assert str(SEED) not in str(t)
    _xep(a)
    a.chot_phuong_an()
    t = a.get_phuong_an_xep()["data"]
    assert t["co_chot"] and t["khop_luc_chot"] is True and t["co_the_xuat"]["chot"] is True
    assert t["co_the_in_hat_giong"] is True and t["canh_bao"] == []
    assert str(SEED) not in str(t)


def test_get_canh_bao_sau_khi_doi_luat(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    a.chot_phuong_an()
    assert a.chon_muc_tieu("co_hoi")["ok"]
    t = a.get_phuong_an_xep()["data"]
    assert t["khop_luc_chot"] is False and "doi_sau_chot" in t["canh_bao"]


# ----- xuất PDF -----

def test_du_kien_xuat_duoc_khi_chua_chay_chua_chot(tmp_path):
    a, db = _mo(tmp_path)
    r = _xuat(a, tmp_path, "du_kien")
    assert r["ok"] and r["data"]["ban"] == "du_kien" and r["data"]["n_trang"] == 1
    chu = _chu(r["data"]["path"])
    assert "BẢN DỰ KIẾN" in chu and "chưa chốt dữ liệu" in chu and "Chưa làm" in chu


def test_ban_chot_bi_tu_choi_neu_thieu_dieu_kien(tmp_path):
    a, db = _mo(tmp_path)
    r = _xuat(a, tmp_path, "chot")
    assert not r["ok"] and _ma(r) == ["cb1_chua_du_dieu_kien_ban_chot"]
    _xep(a)
    assert _ma(_xuat(a, tmp_path, "chot")) == ["cb1_chua_du_dieu_kien_ban_chot"]       # có xếp nhưng chưa chốt
    assert not os.listdir(tmp_path) or not any(f.endswith(".pdf") for f in os.listdir(tmp_path))
    a.chot_phuong_an()
    assert _xuat(a, tmp_path, "chot")["ok"]


def test_ban_chot_dau_van_tay_nguoi_thoi_gian_khoa_va_khong_hat_giong_mac_dinh(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    a.chot_phuong_an()
    r = _xuat(a, tmp_path, "chot")
    chu = _chu(r["data"]["path"])
    dvt = _sql(db, "SELECT dau_van_tay FROM dau_van_tay_chay")[0][0]
    assert "BẢN CHỐT" in chu and dvt[:20] in chu.replace("\n", "")
    assert r["data"]["n_trang"] == 1                       # CB1-FIX5: bản chốt đầy đủ vẫn vừa MỘT trang
    assert chu.count("BẢN CHỐT") == 1 and "Từng bước đi đến kết quả" in chu and "Dấu xác nhận" in chu   # CB1-FIX4: bố cục mới, nhãn không lặp
    assert pa.bam_luat(cau_hinh_ws.doc_cau_hinh(db))[:20] in chu.replace("\n", "")
    assert str(SEED) not in chu and "Hạt giống:" not in chu
    assert "Đã làm" in chu


def test_hat_giong_chi_khi_tick_o_ban_chot_da_khoa(tmp_path):
    a, db = _mo(tmp_path)
    r = _xuat(a, tmp_path, "du_kien", in_hat_giong=True)
    assert not r["ok"] and _ma(r) == ["cb1_hat_giong_chua_khoa"]
    _xep(a)
    a.chot_phuong_an()
    r = _xuat(a, tmp_path, "du_kien", ten="dk", in_hat_giong=True)
    assert not r["ok"] and _ma(r) == ["cb1_hat_giong_chua_khoa"]            # dự kiến KHÔNG BAO GIỜ có hạt giống
    assert str(SEED) not in _chu(_xuat(a, tmp_path, "du_kien", ten="dk2")["data"]["path"])
    r = _xuat(a, tmp_path, "chot", ten="ck", in_hat_giong=True)
    assert r["ok"] and str(SEED) in _chu(r["data"]["path"])


def test_hat_giong_chua_khoa_bi_tu_choi_o_ban_chot(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    a.chot_phuong_an()
    _sql_ghi = sqlite3.connect(db)
    _sql_ghi.execute("UPDATE stb_lock SET is_locked = 0")
    _sql_ghi.commit()
    _sql_ghi.close()
    assert _ma(_xuat(a, tmp_path, "chot", in_hat_giong=True)) in (["cb1_hat_giong_chua_khoa"],
                                                                 ["cb1_chua_du_dieu_kien_ban_chot"])


def test_ban_la_va_khong_ghi_gi(tmp_path):
    a, db = _mo(tmp_path)
    r = _xuat(a, tmp_path, "khac")
    assert not r["ok"] and _ma(r) == ["cb1_ban_la"]


def test_pdf_khong_ro_ri_ma_ten_diem_so_boc_tham(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    a.chot_phuong_an()
    # số bốc thăm và điểm của MỖI học sinh đổi thành giá trị lạ, riêng từng người, để bắt rò rỉ (xuất không đọc hai cột này)
    c = sqlite3.connect(db)
    c.execute("UPDATE students SET stb_number = 700000 + rowid")
    c.execute("UPDATE club_scores SET score = 8123.25 + rowid")
    c.commit()
    c.close()
    ds = _sql(db, "SELECT student_id, name, stb_number FROM students")
    diem = [str(r[0]) for r in _sql(db, "SELECT score FROM club_scores")]
    assert len(ds) >= 100 and diem and all(x.startswith("8") for x in diem)
    chu = ""
    for ban in ("du_kien", "chot"):
        chu += _chu(_xuat(a, tmp_path, ban, ten="rr_" + ban, in_hat_giong=(ban == "chot"))["data"]["path"])
    gop = chu.replace("\n", " ")
    for sid, ten, stb in ds:
        assert str(sid) not in gop
        assert str(stb) not in gop
        if ten and len(ten.strip()) > 3:
            assert ten.strip() not in gop
    assert not any(x in gop for x in diem) and "8123" not in gop
    assert "sha256" not in gop.lower() and "Số bốc thăm của" not in gop
    # chữ cấm của văn bản: không bảng so sánh, không "Phụ lục"
    assert "Phụ lục" not in gop and "So sánh" not in gop


def test_canh_bao_trong_pdf_sau_khi_doi_sau_chot(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    a.chot_phuong_an()
    chu = _chu(_xuat(a, tmp_path, "chot", ten="a")["data"]["path"])
    assert "Phương án đã đổi sau khi chốt" not in chu
    assert a.chon_muc_tieu("co_hoi")["ok"]
    r = _xuat(a, tmp_path, "chot", ten="b")
    assert r["ok"] and "doi_sau_chot" in r["data"]["canh_bao"]
    assert "Phương án đã đổi sau khi chốt" in _chu(r["data"]["path"]).replace("\n", " ")


def test_canh_bao_lan_xep_khong_dung_phuong_an_da_chot(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)                                   # xếp với luật trường học mặc định
    assert a.chon_muc_tieu("co_hoi")["ok"]
    assert a.chot_phuong_an()["ok"]           # chốt luật "cơ hội như nhau" sau khi xếp bằng luật khác
    r = _xuat(a, tmp_path, "chot")
    assert r["ok"] and "xep_khac_chot" in r["data"]["canh_bao"]
    a.run_pipeline(seed=SEED)                 # xếp lại bằng đúng phương án đã chốt
    assert "xep_khac_chot" not in _xuat(a, tmp_path, "chot", ten="c")["data"]["canh_bao"]


def test_xuat_khong_chay_lai_khong_doi_lich_su_va_khong_de_tep(tmp_path):
    a, db = _mo(tmp_path)
    _xep(a)
    a.chot_phuong_an()
    n_run = _sql(db, "SELECT COUNT(*) FROM run_history")[0][0]
    cu = _sql(db, "SELECT * FROM stb_lock")
    p1 = _xuat(a, tmp_path, "chot", ten="m")["data"]["path"]
    p2 = _xuat(a, tmp_path, "chot", ten="m")["data"]["path"]
    assert p1 != p2 and os.path.exists(p1) and os.path.exists(p2)
    assert _sql(db, "SELECT COUNT(*) FROM run_history")[0][0] == n_run
    assert _sql(db, "SELECT * FROM stb_lock") == cu


def test_thieu_reportlab_ra_ma_loi_khong_tao_tep(tmp_path, monkeypatch):
    a, db = _mo(tmp_path)

    def hong():
        raise xuat_pdf.ThieuThuVienPdf("reportlab")
    monkeypatch.setattr(xuat_pdf, "san_sang", hong)
    r = _xuat(a, tmp_path, "du_kien")
    assert not r["ok"] and _ma(r) == ["xp1_thieu_thu_vien_pdf"]
    assert not any(f.endswith(".pdf") for f in os.listdir(tmp_path))


def test_workspace_nhan_tuy_bien_van_xuat_duoc(tmp_path):
    a, db = _mo(tmp_path)
    nhan = cau_hinh_ws.doc_cau_hinh(db)["labels"]
    nhan["person"] = {"vi": "Nhân viên", "en": "Employee"}
    nhan["slot"] = {"vi": "Dự án", "en": "Project"}
    cau_hinh_ws.ghi_cau_hinh(db, {"labels": nhan})
    r = _xuat(a, tmp_path, "du_kien")
    assert r["ok"], r["errors"]
