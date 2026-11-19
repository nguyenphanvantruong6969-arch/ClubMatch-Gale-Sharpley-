"""UX1I-I3: B gộp với XP1. Phiếu có cả cột "Loại CLB" (XP1) rồi "Huy chương" (B), HTML và PDF; giáo viên chủ nhiệm
in phiếu cả lớp (PDF) và "Báo cáo tổng hợp" (PDF) trong ≤ 2 lần bấm; quyền giáo viên đúng hai hàm đó. MÔ PHỎNG."""
import os

import pytest

pytest.importorskip("reportlab")
pypdf = pytest.importorskip("pypdf")
from test_ux1b_l7_phieu import _dung_fa  # noqa: E402

import phan_quyen  # noqa: E402
from test_giao_dien_ux1b_vai_gv import mo  # noqa: E402,F401,F811  (fixture: giáo viên gv1 đã đăng nhập, Chromium)


def _chu(duong):
    return "\n".join(p.extract_text() for p in pypdf.PdfReader(duong).pages)


def test_phieu_html_loai_clb_roi_huy_chuong(api, tmp_path):
    _dung_fa(api)
    r = api.export_phieu_giai_trinh(str(tmp_path / "p.html"), student_ids=["s1"])
    html = open(r["data"]["path"], encoding="utf-8").read()
    assert "<th>CLB</th><th>Loại CLB</th><th>Huy chương</th><th>Điểm thi</th>" in html


def test_phieu_pdf_co_cot_huy_chuong_sau_loai_clb(api, tmp_path):
    _dung_fa(api)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), student_ids=["s1"])
    assert r["ok"], r
    chu = _chu(r["data"]["path"])
    assert "Loại CLB" in chu and "Huy chương" in chu and "Vàng" in chu
    assert chu.index("Loại CLB") < chu.index("Huy chương")


def test_phieu_pdf_khong_fa_khong_co_cot_huy_chuong(api, tmp_path):
    from test_ux1b_l7_phieu import _dung_thuong
    _dung_thuong(api)
    r = api.export_phieu_giai_trinh_pdf(str(tmp_path / "p.pdf"), student_ids=["s1"])
    assert "Huy chương" not in _chu(r["data"]["path"]) and "Loại CLB" in _chu(r["data"]["path"])


def test_bao_cao_tong_hop_pdf_khong_ten_ma_diem(api, tmp_path):
    _dung_fa(api)
    r = api.export_bao_cao_tong_hop_pdf(str(tmp_path / "bc.pdf"))
    assert r["ok"], r
    chu = _chu(r["data"]["path"])
    assert "Báo cáo tổng hợp" in chu and r["data"]["n_trang"] >= 1
    assert not any(m in chu for m in ("s1", "s2", "s3"))       # mã học sinh mô phỏng


def test_bao_cao_tong_hop_pdf_chua_co_ket_qua(api, tmp_path):
    r = api.export_bao_cao_tong_hop_pdf(str(tmp_path / "bc.pdf"))
    assert not r["ok"] and r["errors"][0]["code"] == "xuat_chua_co_ket_qua"


def test_quyen_giao_vien_dung_hai_ham_pdf_nay_va_khong_them():
    q = phan_quyen.QUYEN
    assert q["export_phieu_giai_trinh_pdf"] == phan_quyen.GIAO_VIEN
    assert q["export_bao_cao_tong_hop_pdf"] == phan_quyen.GIAO_VIEN
    assert q["export_danh_sach_pdf"] == phan_quyen.QUAN_TRI          # danh sách có tên CHƯA mở cho giáo viên


# ---------------------------------------------------------------- giao diện giáo viên (Chromium)
def test_giao_vien_in_phieu_lop_pdf_mot_lan_bam_sau_khi_vao(mo, tmp_path):  # noqa: F811
    page, api, loi = mo
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    assert page.locator("#btnUx1bPhieuLop").is_visible()              # đã ở thẻ Kết quả: lần bấm 0
    page.locator("#ux1bLop").select_option(index=1)
    page.locator("#btnUx1bPhieuLop").click()                          # lần bấm 1
    page.wait_for_function("document.getElementById('ux1bPhanHoi').textContent.includes('.pdf')")
    tep = [t for t in os.listdir(api.thu_muc_xuat) if t.endswith(".pdf")]
    assert tep == ["phieu_giai_trinh.pdf"]
    chu = _chu(os.path.join(api.thu_muc_xuat, tep[0]))
    assert "Loại CLB" in chu and "Mã:" in chu
    assert not loi, loi


def test_giao_vien_bao_cao_tong_hop_pdf_mot_lan_bam(mo, tmp_path):  # noqa: F811
    page, api, loi = mo
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    page.locator("#btnUx1bBaoCaoPdf").click()                         # lần bấm 1
    page.wait_for_function("document.getElementById('ux1bPhanHoi').textContent.includes('.pdf')")
    assert [t for t in os.listdir(api.thu_muc_xuat) if t.endswith(".pdf")] == ["bao_cao_tong_hop.pdf"]
    assert not loi, loi


def test_giao_vien_khong_goi_duoc_danh_sach_pdf_cua_quan_tri(mo, tmp_path):  # noqa: F811
    page, api, loi = mo
    api.thu_muc_xuat = str(tmp_path / "tai_xuong")
    os.makedirs(api.thu_muc_xuat)
    r = page.evaluate("() => callApi('export_danh_sach_pdf', '', 'clb')")
    assert not r["ok"]
    assert not any(t.endswith(".pdf") for t in os.listdir(api.thu_muc_xuat) if os.path.isfile(os.path.join(api.thu_muc_xuat, t)))


# ---------------------------------------------------------------- fix1: cột Buổi không lộ mã nội bộ
def _dung_mot_buoi(api):
    from _fa import dung_fa_clb, dung_hs_fa
    from _wharton import tat_wharton
    tat_wharton(api)
    dung_fa_clb(api, A=(2, None), B=(2, None))                          # không đặt buổi: workspace một buổi mặc định
    dung_hs_fa(api, "s1", "s2", nv={"s1": ["A", "B"], "s2": ["A", "B"]})
    assert api.run_pipeline(seed=3)["ok"]


def test_bao_cao_html_khong_lo_ma_buoi_mac_dinh(api, tmp_path):
    _dung_mot_buoi(api)
    r = api.export_bao_cao_tong_hop(str(tmp_path / "bc.html"))
    assert r["ok"], r
    assert "__mac_dinh__" not in open(r["data"]["path"], encoding="utf-8").read()


def test_bao_cao_pdf_khong_lo_ma_buoi_mac_dinh(api, tmp_path):
    _dung_mot_buoi(api)
    r = api.export_bao_cao_tong_hop_pdf(str(tmp_path / "bc.pdf"))
    assert r["ok"], r
    assert "__mac_dinh__" not in _chu(r["data"]["path"])
