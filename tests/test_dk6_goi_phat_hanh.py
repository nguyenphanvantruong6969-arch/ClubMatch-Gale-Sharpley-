"""DK6-L4: gói phát hành chứa đủ cổng đăng ký. `test_dong_goi_du_tep.py` chỉ soát index.html và recovery.html; cổng
`dang_ky.html` cũng nạp tệp .js/.css, mà thiếu một tệp thì chỉ bản .exe trắng trang (bản chạy từ mã nguồn vẫn xanh)."""
import os
import re

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _doc(ten):
    with open(os.path.join(GOC, ten), encoding="utf-8") as f:
        return f.read()


def _tep_cong():
    return [d for d in re.findall(r'(?:src|href)="([^"#:]+)"', _doc("dang_ky.html"))]


def test_moi_tep_cong_dang_ky_nap_ton_tai_va_duoc_dong_goi():
    spec = _doc("kiosk.spec")
    khai = set(re.findall(r'\("([^"]+)",\s*"[^"]*"\)', spec))
    assert "dang_ky.html" in khai
    thieu, vang = [], []
    for tep in _tep_cong():
        if not os.path.exists(os.path.join(GOC, tep)):
            vang.append(tep)
        if tep not in khai and not any(tep.startswith(d.rstrip("/") + "/") for d in khai):
            thieu.append(tep)
    assert vang == [], "dang_ky.html nạp tệp không có trong kho: %s" % vang
    assert thieu == [], "kiosk.spec thiếu: %s" % thieu


def test_moi_tep_js_dang_ky_trong_kho_deu_duoc_trang_nap():
    nap = {os.path.basename(t) for t in _tep_cong() if t.startswith("js/")}
    co = {f for f in os.listdir(os.path.join(GOC, "js")) if f.startswith("dang_ky_") and f.endswith(".js")}
    assert co == {n for n in nap if n.startswith("dang_ky_")}, (co ^ nap)     # tệp mồ côi hoặc tệp nạp mà không có


def test_buoc_soat_sha256_cua_workflow_kiem_moi_tep_goc_cua_cong():
    wf = _doc(".github/workflows/build-windows-exe.yml")
    kiem = set(re.findall(r'"([^"]+)"', re.search(r'foreach \(\$f in @\(([^)]*)\)\)', wf, re.S).group(1)))
    o_goc = {t for t in _tep_cong() + ["dang_ky.html"] if "/" not in t}
    assert o_goc - kiem == set(), o_goc - kiem


def test_phan_mem_nap_hai_mo_dun_cua_cong_de_trinh_dong_goi_thay():
    ma = _doc("api.py")
    assert "from api_dang_ky import DangKyMixin" in ma
    assert "from dang_ky_sang_xep import DangKySangXepMixin" in ma
