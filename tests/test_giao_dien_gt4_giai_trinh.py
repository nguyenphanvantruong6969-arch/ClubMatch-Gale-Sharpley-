"""GT4-L4 — khung tra cứu hiện đúng: chỗ dành riêng không có số, có câu chú thích, giọng trung tính. Chromium."""

import os
import re
import shutil
import sys

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import api as api_mod  # noqa: E402
import browser_host  # noqa: E402
import cau_hinh_ws  # noqa: E402
import fa_ly_do  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
import do_anh_huong_seed as d  # noqa: E402


def test_khung_tra_cuu_cho_danh_rieng_va_giong_trung_tinh(tmp_path):
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    os.makedirs(str(tmp_path / "nguon"))
    nguon = d.nap_bo(str(tmp_path / "nguon"), d.BO_DU_LIEU[1][1])
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Thử", {})
    db = ws.duong_dan_db(goc, slug)
    shutil.copyfile(nguon, db)
    cau_hinh_ws.ghi_cau_hinh(db, {"rules": {"wharton": False}})
    api = api_mod.PipelineAPI(db, thu_muc_goc_ws=goc)
    assert api.run_pipeline(seed=3)["ok"]
    with api._ket_noi_doc() as cur:
        hs = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
    sid = next(s for s in hs if any(x["ma"] == "RESERVED" for b in api.get_giai_trinh_hoc_sinh(s)["data"]["buoi"]
                                    for x in b["cac_lua_chon"]))
    with sync_playwright() as pw:
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        page = br.new_page(locale="vi-VN", bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#gtPanel", state="attached")
        page.click('button.nav-item[data-tab="results"]')
        page.fill("#gtTim", sid)
        page.wait_for_selector("#gtDs .gt-chon")
        page.click("#gtDs .gt-chon")
        page.wait_for_selector("#gtKetQua .gt-bang")
        hang = [r for r in page.locator("#gtKetQua .gt-bang tbody tr").all()
                if "dành một số chỗ cho nhóm được giữ chỗ" in r.inner_text()]
        assert hang
        for r in hang:
            o = r.locator("td").all_inner_texts()
            assert o[4] == "Chỗ dành riêng", o
        assert page.locator("#gtKetQua .gt-chu-thich").first.inner_text() == fa_ly_do.CAU_GIU_CHO
        assert not re.search(r"\b[Ee]m\b", page.inner_text("#gtKetQua"))
        br.close()
    assert not loi, loi
