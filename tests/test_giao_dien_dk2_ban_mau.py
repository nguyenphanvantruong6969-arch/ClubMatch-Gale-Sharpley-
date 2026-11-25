"""DK2-L2: bản mẫu v8 (Playwright + Chromium, tệp file://). Dữ liệu MÔ PHỎNG.

Xuất JSON đúng dạng `dk2_so_nhap` và phần mềm nhập 0 lỗi; học sinh đi từng buổi (D39); nhãn loại
ngắn không đè nút (D40); không còn mã biên nhận (D41); tối đa 5 bài thi MỖI buổi kèm cảnh báo (D44);
thiết kế khớp phần mềm (phông cục bộ, chỉ giao diện sáng, một nút vàng mỗi màn hình).
"""
import base64
import json
import os
import pathlib

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import cau_hinh_ws as ch  # noqa: E402
import dk2_so_nhap as dk  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = pathlib.Path(GOC, "docs", "phien", "DK1_BAN_MAU_V8.html").as_uri()


@pytest.fixture(scope="module")
def trang():
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    pg = br.new_page(viewport={"width": 1366, "height": 900})
    pg.route("http*://**", lambda r: r.abort())          # offline như máy kiosk
    loi = []
    pg.on("pageerror", lambda e: loi.append(str(e)))
    pg.goto(URL)
    pg.loi = loi
    yield pg
    br.close()
    pw.stop()


def _du_lieu(pg, kieu):
    return pg.evaluate("""k => {seed(k);save();ACT.fakeApprove();ACT.fakeRegs();ACT.fakeScores();
        missingScores().forEach(m=>(S.scores[m.cid]=S.scores[m.cid]||{})[m.sid]=7);  // đủ điểm: FA chặn CLB Tuyển chọn chưa có điểm
        return JSON.stringify(buildExport().json)}""", kieu)


@pytest.mark.parametrize("kieu", ["nho", "ca"])
def test_xuat_thanh_so_nhap_phan_mem_nhan_0_loi(trang, api, tmp_path, kieu):
    d = json.loads(_du_lieu(trang, kieu))
    assert d["dinhDang"] == 1 and d["hocSinh"]
    p = str(tmp_path / "so.xlsx")
    dk.ghi_tu_ban_mau(d, p)
    ch.ghi_cau_hinh(api.db_path, {"rules": {"fa_daa": True, "wharton": True}})
    with open(p, "rb") as f:
        ra = api.import_so_nhap(base64.b64encode(f.read()).decode("ascii"))
    assert ra["ok"] and ra["errors"] == [], ra
    assert api.run_pipeline(seed=5)["ok"]
    assert not trang.loi


def _vao_hoc_sinh(pg):
    pg.evaluate("""() => {V.hs={};seed('nho');ACT.fakeApprove();S.phase=3;S.deadline[3]=Date.now()+864e5;save();
        V.screen='hs';V.hs={};render()}""")
    sid, pin = pg.evaluate("() => [S.students[0].id, S.students[0].pin]")
    pg.fill("#h_id", sid)
    pg.fill("#h_pin", pin)
    pg.click("form[data-form=hsLogin] button")
    pg.click("[data-act=hsYes]")
    return sid


def _mot_nut_vang(pg):
    vang = pg.locator("button.pri:visible")
    assert vang.count() <= 1
    assert not any(vang.nth(i).is_disabled() for i in range(vang.count()))


def test_tung_buoi_nhan_ngan_khong_ma_bien_nhan(trang):
    pg = trang
    _vao_hoc_sinh(pg)
    n, co_the = pg.evaluate("S.sessions.length"), 0
    for k in range(n):
        assert pg.locator(f".steps[data-buoi='{k + 1}']").count() == 1      # D39: đang ở buổi k+1
        assert pg.locator("nav.tabs[aria-label='Buổi']").count() == 0       # không còn chuyển buổi tự do
        for rong in (1366, 390):
            pg.set_viewport_size({"width": rong, "height": 900})
            for the in pg.locator(".card:has([data-act=hsAdd])").all()[:6]:
                chip, nut = the.locator(".chip").first.bounding_box(), the.locator("[data-act=hsAdd]").bounding_box()
                o = the.bounding_box()
                assert chip["x"] + chip["width"] <= nut["x"] + 0.5           # D40: chip không đè nút
                assert chip["x"] + chip["width"] <= o["x"] + o["width"]      # và không tràn thẻ
        pg.set_viewport_size({"width": 1366, "height": 900})
        if pg.locator("[data-act=hsAdd]").count():
            co_the += 1
            assert "–" not in pg.locator(".card .chip").first.inner_text()
            pg.locator("[data-act=hsAdd]").first.click()
        _mot_nut_vang(pg)
        pg.click("[data-act=hsStep][data-s=medals]")
        _mot_nut_vang(pg)
        pg.click("[data-act=hsStep][data-s=tests]")
        _mot_nut_vang(pg)
        if k < n - 1:
            pg.click("[data-act=hsNextDay]")
    assert co_the >= 1
    pg.click("[data-act=hsStep][data-s=review]")
    _mot_nut_vang(pg)
    pg.click("[data-act=hsSubmit]")
    van_ban = pg.locator("main, body").first.inner_text()
    assert "Đã gửi lúc" in van_ban and "Mã biên nhận" not in van_ban             # D41
    assert not pg.loi


def test_toi_da_5_bai_moi_buoi_co_canh_bao(trang):
    pg = trang
    _vao_hoc_sinh(pg)
    pg.evaluate("""() => {const st=S.students.find(s=>s.id===V.hs.user), se=S.sessions[0].id, ids=[];
        for(let i=0;i<6;i++){const id='TT'+i;S.clubs.push({id,name:'Tuyển '+i,sessionId:se,roomId:S.rooms[0].id,quota:5,
          adminQuota:null,grades:[st.khoi],loai:'tuyen',diemSan:5,hasTest:true,link:'',desc:'',req:'',status:'duyet',
          teacherId:S.teachers[0].id});ids.push(id)}
        V.hs.draft.prefs[se]=ids;V.hs.step='tests';render()}""")
    hop = pg.locator("input[data-chg=hsTest]")
    assert hop.count() == 6
    for i in range(5):
        hop.nth(i).check()
    assert hop.nth(5).is_disabled()
    assert pg.locator("[data-canh-bao=tran-thi]").count() == 1
    assert pg.evaluate("testsIn(V.hs.draft,S.sessions[0].id)") == 5


def test_thiet_ke_khop_phan_mem(trang):
    with open(os.path.join(GOC, "docs", "phien", "DK1_BAN_MAU_V8.html"), encoding="utf-8") as f:
        html = f.read()
    assert "../../assets/fonts/fonts.css" in html                             # phông cục bộ như style.css
    assert "prefers-color-scheme: dark" not in html and "color-scheme:light" in html
    assert "border-radius:8px" not in html and "border-radius:12px" not in html
    for mau in ("#1C2321", "#F3F4F1", "#C98A1F", "#3F6B52", "#B84A3E", "#173F8C"):
        assert mau in html                                                    # bảng màu của style.css
