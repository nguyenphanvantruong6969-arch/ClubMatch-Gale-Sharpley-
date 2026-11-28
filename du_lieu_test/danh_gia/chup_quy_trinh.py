# -*- coding: utf-8 -*-
"""DG1-L5: chụp màn hình QUY TRÌNH thật của phần mềm cho báo cáo khoa học (DỮ LIỆU MÔ PHỎNG, tên do bộ sinh đặt).

    python du_lieu_test/danh_gia/chup_quy_trinh.py [THƯ_MỤC_RA]      (mặc định docs/nghien_cuu/anh_dg1)

Dựng một trường mô phỏng cấu hình mặc định (800 HS × 20 CLB, α 0,5, ρ 0,7, κ 1,1, seed dữ liệu 101), ghi Sổ nhập bằng
`so_nhap.ghi_so_nhap`, nạp qua `PipelineAPI.import_so_nhap` trong THƯ MỤC TẠM (không đụng app.db), chạy `run_pipeline`,
rồi mở giao diện thật (`browser_host`) bằng Chromium và chụp từng màn. Cần gói `playwright` (requirements-dev) và Chromium.
"""

import base64
import html
import os
import sys
import tempfile

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(THU_MUC))
sys.path[:0] = [GOC, os.path.join(GOC, "tests"), THU_MUC]

import _sinh  # noqa: E402

RA_MAC_DINH = os.path.join(GOC, "docs", "nghien_cuu", "anh_dg1")
SEED_DL, SEED_BT = 101, 1


def _chup(pg, duong, toan_trang=True):
    pg.wait_for_timeout(700)
    pg.screenshot(path=duong, full_page=toan_trang)
    print("  ", os.path.relpath(duong, GOC))


def _tab(pg, ten):
    """Bấm thẻ nếu thẻ đang hiện (thẻ chỉ dành cho quản trị bị ẩn thì bỏ qua); trả True nếu đã bấm."""
    nut = pg.locator('[data-tab="%s"]:visible' % ten)
    if nut.count() == 0:
        print("   (bỏ qua thẻ ẩn: %s)" % ten)
        return False
    nut.first.click()
    pg.wait_for_timeout(900)
    return True


def _excel_html(duong_xlsx, trang="Thống kê"):
    import openpyxl
    ws = openpyxl.load_workbook(duong_xlsx)[trang]
    dong = []
    for r in ws.iter_rows(values_only=True):
        if any(v is not None for v in r):
            dong.append("<tr>%s</tr>" % "".join("<td>%s</td>" % html.escape("" if v is None else str(v)) for v in r))
    return ('<!doctype html><meta charset="utf-8"><style>body{font:13px system-ui,sans-serif;margin:16px;background:#fff;color:#1c2321}'
            'td{border:1px solid #dbdcd5;padding:3px 8px}table{border-collapse:collapse}h3{font-size:15px}</style>'
            '<h3>Sổ Excel kết quả — trang «%s» (dựng lại từ tệp .xlsx bằng openpyxl)</h3><table>%s</table>' % (html.escape(trang), "".join(dong)))


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    ra = os.path.abspath(a[0]) if a else RA_MAC_DINH
    os.makedirs(ra, exist_ok=True)
    from playwright.sync_api import sync_playwright
    from _trinh_duyet import CHROMIUM
    import browser_host
    from api import PipelineAPI
    import cau_hinh_ws

    tam = tempfile.mkdtemp(prefix="dg1_chup_")
    truong = _sinh.sinh_truong(800, 20, alpha=0.5, rho=0.7, kappa=1.1, seed=SEED_DL)
    xlsx = _sinh.sinh_so_nhap(truong, os.path.join(tam, "SO_NHAP_DG1_MAC_DINH.xlsx"))
    api = PipelineAPI(os.path.join(tam, "app.db"))
    cau_hinh_ws.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
    with open(xlsx, "rb") as f:
        kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"], kq["errors"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        pg = br.new_page(viewport={"width": 1280, "height": 860}, device_scale_factor=2, bypass_csp=True)
        pg.goto(url)
        pg.wait_for_selector("#dropZone", state="attached")
        pg.wait_for_timeout(800)
        _tab(pg, "pipeline")
        _chup(pg, os.path.join(ra, "S1_sau_nap_truoc_khi_chay.png"))
        r = api.run_pipeline(seed=SEED_BT)
        assert r["ok"], r["errors"]
        pg.reload()
        pg.wait_for_selector("#dropZone", state="attached")
        pg.wait_for_timeout(800)
        _tab(pg, "results")
        _chup(pg, os.path.join(ra, "S2_ket_qua.png"), toan_trang=False)   # danh sách 800 em: chỉ chụp khung nhìn
        _tab(pg, "others")
        pg.wait_for_selector("#chiSoPhanBo:not([hidden])")
        pg.locator("#chiSoPhanBo").scroll_into_view_if_needed()
        _chup(pg, os.path.join(ra, "S3_chi_tiet_chi_so_phan_bo.png"))
        pg.locator("#chiSoPhanBo").screenshot(path=os.path.join(ra, "S4_khoi_chi_so_phan_bo.png"))
        print("  ", os.path.relpath(os.path.join(ra, "S4_khoi_chi_so_phan_bo.png"), GOC))
        duong = api.export_ket_qua("")["data"]["path"]
        hx = os.path.join(tam, "thong_ke.html")
        with open(hx, "w", encoding="utf-8") as f:
            f.write(_excel_html(duong))
        p2 = br.new_page(viewport={"width": 1000, "height": 860}, device_scale_factor=2)
        p2.goto("file://" + hx)
        _chup(p2, os.path.join(ra, "S5_excel_thong_ke.png"))
        bc = os.path.join(GOC, "docs", "nghien_cuu", "DG1_BAO_CAO_KHOA_HOC.html")
        if os.path.exists(bc):
            p2.goto("file://" + bc)
            _chup(p2, os.path.join(ra, "S6_bao_cao_trang_dau.png"), toan_trang=False)
        br.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
