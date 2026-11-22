"""Báo cáo lịch sử thay đổi (docs/giai_trinh/tao_lich_su.py): mọi mã commit được trích phải có thật, sơ đồ hợp lệ, không lộ thư điện tử."""

import os
import re
import subprocess
import sys
import xml.dom.minidom

import pytest

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GT = os.path.join(GOC, "docs", "giai_trinh")
sys.path.insert(0, GT)


def _kho_day_du() -> bool:
    r = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=GOC, capture_output=True, text=True)
    return r.returncode == 0 and r.stdout.strip() == "false"


def test_so_do_xu_ly_la_xml_hop_le_va_noi_la_du_lieu_mo_phong():
    xml.dom.minidom.parse(os.path.join(GT, "so_do_xu_ly.svg"))
    with open(os.path.join(GT, "so_do_xu_ly.svg"), encoding="utf-8") as f:
        van_ban = f.read()
    assert "mô phỏng" in van_ban and "chưa có chỗ" in van_ban.lower()


def test_so_do_xu_ly_dung_lai_dung_tu_script():
    import ve_so_do_xu_ly
    with open(os.path.join(GT, "so_do_xu_ly.svg"), encoding="utf-8") as f:
        assert f.read() == ve_so_do_xu_ly.dung()


def test_moi_ma_commit_trich_dan_co_that():
    if not _kho_day_du():
        pytest.skip("kho là bản shallow: không kiểm được mã commit cũ")
    import tao_lich_su
    for _, _, _, ds in tao_lich_su.MINH_CHUNG:
        for ma, vai_tro in ds:
            assert tao_lich_su.doc_commit(ma)["ngan"].startswith(ma[:7]), ma
            assert vai_tro.strip()


def test_bao_cao_khong_lo_thu_dien_tu_va_noi_ro_gioi_han():
    with open(os.path.join(GT, "LICH_SU_THAY_DOI.md"), encoding="utf-8") as f:
        van_ban = f.read()
    assert not re.search(r"[\w.]+@[\w.]+\.\w+", van_ban)
    assert "Giới hạn của minh chứng này" in van_ban and "RB-STUFF-AFTER-UP" in van_ban
