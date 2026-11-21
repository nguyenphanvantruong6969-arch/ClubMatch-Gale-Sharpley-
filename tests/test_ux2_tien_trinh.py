"""UX2-L5 (tĩnh): bảng UX2_PHA trong js/02_van_hanh.js phủ MỌI tên bước trong api.py run_pipeline, đúng thứ tự bất biến 5."""
import os
import re

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _doc(ten):
    with open(os.path.join(GOC, ten), encoding="utf-8") as f:
        return f.read()


def _pha_js():
    ma = _doc("js/02_van_hanh.js")
    khoi = ma[ma.index("const UX2_PHA = ["):ma.index("];", ma.index("const UX2_PHA = ["))]
    pha = re.findall(r'ma:\s*"(\w+)",\s*buoc:\s*\[([^\]]*)\]', khoi)
    bo_qua = re.search(r"const UX2_PHA_BO_QUA = \[([^\]]*)\]", ma).group(1)
    return [(m, re.findall(r'"(\w+)"', b)) for m, b in pha], re.findall(r'"(\w+)"', bo_qua)


def _buoc_api():
    ma = _doc("api.py")
    ten = []
    for m in re.finditer(r'"step":\s*"(\w+)"', ma):
        if m.group(1) not in ten:
            ten.append(m.group(1))
    return ten


def test_moi_buoc_cua_api_co_trong_bang_pha_hoac_bi_bo_qua_co_chu_y():
    pha, bo_qua = _pha_js()
    trong_bang = {b for _, bs in pha for b in bs}
    for b in _buoc_api():
        assert b in trong_bang or b in bo_qua, "bước %r trong api.py chưa có trong UX2_PHA" % b
    assert bo_qua == ["unknown"]


def test_moi_buoc_trong_bang_pha_co_that_trong_api():
    pha, _ = _pha_js()
    api = set(_buoc_api())
    for _, bs in pha:
        for b in bs:
            assert b in api, "UX2_PHA có bước %r mà api.py không còn" % b


def test_thu_tu_pha_dung_thu_tu_bat_bien_5():
    pha, _ = _pha_js()
    assert [m for m, _ in pha] == ["kiem_tra", "xep", "ghi", "xuat"]
    thu_tu_bang = [b for _, bs in pha for b in bs if b != "rollback"]
    thu_tu_api = [b for b in _buoc_api() if b not in ("rollback", "unknown")]
    assert thu_tu_bang == thu_tu_api == ["backup", "validate", "stb_lottery", "rbda_cascade", "write_results", "export"]
    # rollback thuộc pha Ghi nhưng mã không bao giờ tính nó là "xong"
    assert dict(pha)["ghi"][-1] == "rollback"
    ma = _doc("js/02_van_hanh.js")
    assert 'b !== "rollback"' in ma
