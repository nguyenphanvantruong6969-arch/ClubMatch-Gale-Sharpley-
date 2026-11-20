"""UX1F-L3 — giáo viên "Lưu PDF" phiếu của MỘT học sinh: backend (giáo viên được, chế độ học sinh bị từ chối, tệp chỉ
chứa em đó) và Chromium (tìm → chọn → Lưu PDF ≤ 4 lần bấm). Dữ liệu MÔ PHỎNG."""
import os
import re

import pytest

pytest.importorskip("reportlab")
pypdf = pytest.importorskip("pypdf")
from test_giao_dien_ux1b_vai_gv import mo  # noqa: E402,F401,F811  (fixture: giáo viên gv1 đã đăng nhập, Chromium)
from test_ux1b_l7_phieu import _dung_thuong  # noqa: E402

MK = "matkhau-gia-1"


def _chu(duong):
    return "\n".join(p.extract_text() for p in pypdf.PdfReader(duong).pages)


def _co_tai_khoan(api):
    _dung_thuong(api)
    assert api.tao_tai_khoan("quantri", MK, "quan_tri")["ok"]
    assert api.tao_tai_khoan("gv1", MK, "giao_vien")["ok"]
    api.dang_xuat()


def test_giao_vien_luu_pdf_mot_em_chi_co_em_do(api, tmp_path):
    _co_tai_khoan(api)
    assert api.dang_nhap("gv1", MK)["ok"]
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), student_ids=["s2"])
    assert r["ok"], r
    chu = _chu(r["data"]["path"])
    assert re.search(r"Mã:\s*s2\b", chu)
    assert not any(re.search(r"Mã:\s*%s\b" % s, chu) for s in ("s1", "s3", "s4"))
    assert r["data"]["n_trang"] >= 1 and os.path.basename(r["data"]["path"]) == "p.pdf"


def test_che_do_hoc_sinh_khong_luu_duoc_pdf_phieu(api, tmp_path):
    _co_tai_khoan(api)
    assert api.dang_nhap("quantri", MK)["ok"]
    assert api.vao_che_do_hoc_sinh()["data"]["khoa"] is True
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), student_ids=["s2"])
    assert not r["ok"] and r["errors"][0]["code"] == "gt3_che_do_hoc_sinh"
    assert not [t for t in os.listdir(tmp_path) if t.endswith(".pdf")]


def test_giao_vien_chua_dang_nhap_khong_luu_duoc(api, tmp_path):
    _co_tai_khoan(api)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), student_ids=["s2"])
    assert not r["ok"] and r["errors"][0]["code"] == "gt3_can_dang_nhap"


def test_giao_vien_tim_chon_luu_pdf_toi_da_bon_lan_bam(mo, tmp_path):  # noqa: F811
    page, api, loi = mo
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    with api._ket_noi_doc() as cur:
        sid = cur.execute("SELECT student_id FROM students ORDER BY student_id").fetchone()[0]
        khac = [r[0] for r in cur.execute("SELECT student_id FROM students WHERE student_id <> ?", (sid,))]
    nut = page.locator("#btnGtPdfMot")
    assert nut.is_hidden()                                   # chưa chọn em nào
    bam = 0
    page.fill("#gtTim", sid)
    bam += 1                                                 # tìm
    page.wait_for_selector("#gtDs .gt-chon")
    page.click("#gtDs .gt-chon")
    bam += 1                                                 # chọn
    page.wait_for_selector("#gtKetQua .gt-bang")
    assert nut.is_visible()                                  # giáo viên THẤY nút
    nut.click()
    bam += 1                                                 # Lưu PDF
    page.wait_for_function("document.getElementById('gtXuatPhanHoi').textContent.includes('.pdf')")
    assert bam <= 4 and not loi, (bam, loi)
    tep = [t for t in os.listdir(api.thu_muc_xuat) if t.endswith(".pdf")]
    assert len(tep) == 1 and sid in tep[0]
    chu = _chu(os.path.join(api.thu_muc_xuat, tep[0]))
    assert re.search(r"Mã:\s*%s\b" % re.escape(sid), chu)
    assert not any(re.search(r"Mã:\s*%s\b" % re.escape(x), chu) for x in khac)     # riêng tư: chỉ em đó
