"""XP1-L5 — đóng gói xuất PDF: phông .ttf đi kèm giấy phép, reportlab ghim phiên bản, workflow Windows kiểm phông."""
import os
import re

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TTF = ("BeVietnamPro-Regular.ttf", "BeVietnamPro-Bold.ttf")


def _doc(duong):
    with open(os.path.join(GOC, duong), encoding="utf-8") as f:
        return f.read()


def test_phong_ttf_va_giay_phep_co_trong_assets():
    for ten in TTF + ("OFL-BeVietnamPro.txt",):
        assert os.path.getsize(os.path.join(GOC, "assets", "fonts", ten)) > 1000, ten
    assert "SIL Open Font License" in _doc("assets/fonts/OFL-BeVietnamPro.txt")


def test_spec_dong_goi_ca_thu_muc_phong_va_reportlab():
    spec = _doc("kiosk.spec")
    assert '("assets/fonts", "assets/fonts")' in spec
    assert 'collect_all("reportlab")' in spec


def test_reportlab_ghim_phien_ban_trong_requirements_chay():
    assert re.search(r"^reportlab==\d+\.\d+\.\d+\s*$", _doc("requirements.txt"), re.M)


def test_workflow_windows_kiem_phong_pdf_trong_ban_dong_goi():
    wf = _doc(".github/workflows/build-windows-exe.yml")
    for ten in TTF:
        assert ten in wf, ten


def test_xuat_pdf_tim_phong_dung_thu_muc_da_dong_goi():
    import xuat_pdf
    assert os.path.realpath(xuat_pdf._THU_MUC_PHONG) == os.path.realpath(os.path.join(GOC, "assets", "fonts"))
    for tep in xuat_pdf._PHONG.values():
        assert tep in TTF
