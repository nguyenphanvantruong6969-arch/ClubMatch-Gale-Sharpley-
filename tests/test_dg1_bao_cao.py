"""DG1-L5: báo cáo khoa học sinh từ JSON — banner mô phỏng, ô học sinh để trống và được GIỮ khi sinh lại,
không câu đánh giá trong phần AI soạn, mọi hình SVG hợp lệ."""

import os
import sys
import xml.dom.minidom

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test", "danh_gia"))

import viet_bao_cao as vb  # noqa: E402


def _chay(tmp_path, monkeypatch):
    monkeypatch.setattr(vb, "RA_MD", str(tmp_path / "bc.md"))
    monkeypatch.setattr(vb, "RA_HTML", str(tmp_path / "bc.html"))
    monkeypatch.setattr(vb, "THU_MUC_ANH", str(tmp_path / "anh"))
    assert vb.main([]) == 0
    return (tmp_path / "bc.md").read_text(encoding="utf-8")


def test_banner_o_hs_trong_va_khong_tu_danh_gia(tmp_path, monkeypatch):
    md = _chay(tmp_path, monkeypatch)
    assert vb.BANNER in md.split("\n## ")[0]
    o = vb.doc_o_hs(md)
    assert set(o) == {"tom_tat", "dong_co", "gia_thuyet", "thao_luan", "han_che", "ket_luan"}
    assert all(v == vb.TRONG_HS for v in o.values())
    assert vb.kiem_tu_cam(md) == []
    for f in os.listdir(tmp_path / "anh"):
        xml.dom.minidom.parse(str(tmp_path / "anh" / f))


def test_sinh_lai_giu_chu_hoc_sinh(tmp_path, monkeypatch):
    md = _chay(tmp_path, monkeypatch)
    chu = "Em cho rằng RB-DA tốt hơn Boston."   # chữ HỌC SINH: được phép có từ đánh giá, không bị ghi đè
    md = md.replace(vb.MO_HS % "ket_luan" + "\n" + vb.TRONG_HS, vb.MO_HS % "ket_luan" + "\n" + chu)
    (tmp_path / "bc.md").write_text(md, encoding="utf-8")
    md2 = _chay(tmp_path, monkeypatch)
    assert vb.doc_o_hs(md2)["ket_luan"] == chu
    assert chu in (tmp_path / "bc.html").read_text(encoding="utf-8")
