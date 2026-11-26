"""DK8 — chụp CẶP màn hình: bản mẫu v8 (`docs/phien/DK1_BAN_MAU_V8.html`, file://) và cổng thật (`dang_ky.html`).
DỮ LIỆU MÔ PHỎNG (30 học sinh, 6 giáo viên, 10 CLB, 8 phòng, giống «Demo nhỏ» của v8), không phải khảo sát thật.

    python du_lieu_test/chup_dk8.py <thư_mục_ra> [--chi v8|that] [--ten viec_2,landing]

Ảnh ghi ra `<thư_mục_ra>/v8_<tên>.png` và `that_<tên>.png` (KHÔNG commit PNG). Cổng thật dựng qua API `dk_*` (không ghi SQLite
trực tiếp) trong thư mục tạm. Danh sách màn: landing; dang_nhap_qt; viec_0..viec_5 (Việc bây giờ, sáu giai đoạn); ds (Danh sách);
cai_dat; them; gv_dang_nhap; gv_ds; gv_form; hs_dang_nhap; hs_xacnhan; hs_buoi; hs_xemlai; hs_dagui."""
import datetime
import os
import random
import re
import sys
import tempfile

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [GOC, os.path.join(GOC, "tests")]

from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from api import PipelineAPI  # noqa: E402

MK, MA = "admin123", "TRUONG2026"
BUOI = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]
PHONG = [("P101", 30), ("P102", 30), ("P201", 35), ("Lab Hoá", 20), ("Lab Tin", 25), ("Sân bóng", 40), ("Thư viện", 20), ("Phòng nhạc", 12)]
LOP = ["6A1", "7A1", "8A1", "9A1", "10A1"]
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ"]
DEM = ["Văn", "Thị", "Minh", "Ngọc", "Gia", "Quang", "Thanh", "Bảo"]
TEN = ["An", "Bình", "Châu", "Dũng", "Giang", "Hà", "Hải", "Hân", "Hiếu", "Hoa", "Huy", "Khang", "Khoa", "Lan", "Linh", "Long"]
GV = ["Cô Lê Mai", "Thầy Phạm Nam", "Cô Vũ Lan", "Thầy Trần Huy", "Cô Phan Hà", "Thầy Hoàng Long"]
CLB = ["Bóng rổ", "Cờ vua", "Robotics", "Guitar", "Hội hoạ", "Khoa học Lên men", "Toán Sáng tạo", "MC & Thuyết trình", "Bóng đá", "Bóng bàn"]


class Ra:
    def __init__(self, thu_muc, loc):
        self.thu_muc, self.loc, self.ds = thu_muc, [x for x in (loc or "").split(",") if x], []

    def anh(self, pg, tien_to, ten):
        if self.loc and ten not in self.loc:
            return
        pg.wait_for_timeout(500)
        duong = os.path.join(self.thu_muc, "%s_%s.png" % (tien_to, ten))
        pg.screenshot(path=duong, full_page=True)
        self.ds.append(duong)


def _ok(r):
    assert r["ok"] and r["errors"] == [], r
    return r["data"]


def _hop_dong(pg):
    pg.wait_for_timeout(300)


# ---------------------------------------------------------------- bản mẫu v8
def chup_v8(pw, ra):
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    pg = br.new_page(viewport={"width": 1200, "height": 900})
    pg.goto("file://" + os.path.join(GOC, "docs", "phien", "DK1_BAN_MAU_V8.html"))
    pg.evaluate("localStorage.clear()")  # v8 tự nạp lại S từ localStorage mỗi 3 giây: mọi chỉnh S phải save()
    pg.reload()
    pg.wait_for_selector(".doors")
    ev = pg.evaluate
    chup = lambda t: ra.anh(pg, "v8", t)  # noqa: E731
    chup("landing")
    ev("V.screen='admin'; save(); render()")
    chup("dang_nhap_qt")
    ev("V.screen='admin'; V.authed=true; V.tab='bayGio'; V.tmp={}; save(); render()")

    def pha(k):
        ev("S.phase=%d; V.tab='bayGio'; V.tmp={}; save(); render()" % k)
    pha(0)
    chup("viec_0")
    pha(1)
    chup("viec_1")
    for tab, ten in (("danhSach", "ds"), ("caiDat", "cai_dat"), ("them", "them")):
        ev("V.tab='%s'; V.tmp={}; save(); render()" % tab)
        chup(ten)
    ev("V.tab='bayGio'; save(); render()")
    # giáo viên (giai đoạn 1)
    ev("V.authed=false; V.screen='gv'; V.tmp={}; save(); render()")
    chup("gv_dang_nhap")
    ev("V.gv.user=S.teachers[0].id; V.gv.edit=null; save(); render()")
    ev("S.clubs.forEach(c=>{c.teacherId=S.teachers[0].id}); S.clubs.slice(2).forEach((c,i)=>{c.teacherId=S.teachers[(i%5)+1].id}); save(); render()")
    chup("gv_ds")
    pg.get_by_role("button", name="+ Đăng ký CLB mới").first.click()
    chup("gv_form")
    ev("V.gv.user=null; V.gv.edit=null; V.screen='admin'; V.authed=true; save(); render()")
    pha(2)
    chup("viec_2")
    ev("ACT.fakeApprove(); S.phase=3; S.deadline[3]=Date.now()+2*864e5; ACT.fakeRegs(); V.tab='bayGio'; save(); render()")
    chup("viec_3")
    pha(4)
    ev("ACT.fakeScores()")
    chup("viec_4")
    ev("S.exportVer=1")
    pha(5)
    chup("viec_5")
    # học sinh (giai đoạn 3, mở)
    ev("S.phase=3; V.authed=false; V.screen='hs'; V.hs={step:'login',user:null,draft:null,tab:null,err:''}; V.tmp={}; save(); render()")
    chup("hs_dang_nhap")
    sid, pin = ev("(()=>{const s=S.students.find(x=>!S.regs[x.id]);return [s.id,s.pin]})()")
    pg.fill("#h_id", sid)
    pg.fill("#h_pin", pin)
    pg.get_by_role("button", name="Đăng nhập").click()
    chup("hs_xacnhan")
    pg.get_by_role("button", name="Đúng là em").click()
    pg.get_by_role("button", name="+ Thêm").first.click()
    chup("hs_buoi")
    _di_den_xem_lai(pg)
    chup("hs_xemlai")
    pg.get_by_role("button", name="Gửi nguyện vọng").click()
    chup("hs_dagui")
    br.close()


def _di_den_xem_lai(pg):
    """Bấm «Tiếp…» (nút vàng) cho tới khi tới màn «Xem lại và gửi»; ở mỗi bước xếp thêm một CLB nếu còn nút «+ Thêm»."""
    for _ in range(30):
        if pg.get_by_role("heading", name="Xem lại và gửi").count():
            return
        them = pg.get_by_role("button", name="+ Thêm")
        if them.count() and them.first.is_enabled() and not pg.locator("ol.dk-xep li, ol.rank li").count():
            them.first.click()
        pg.get_by_role("button", name=re.compile("^Tiếp")).first.click()
        pg.wait_for_timeout(150)
    raise AssertionError("không tới được màn Xem lại và gửi")


# ---------------------------------------------------------------- cổng thật
def dung_that(tmp):
    rng = random.Random(11)
    api = PipelineAPI(os.path.join(tmp, "app.db"))
    __import__("cau_hinh_ws").ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})  # A13.13: mặc định đã BẬT; chụp màn cổng = tắt RÕ RÀNG
    _ok(api.dk_khoi_tao(MK, MA, BUOI, [6, 12]))
    qt = _ok(api.dk_dang_nhap("quan_tri", "", MK))["token"]
    for ten, sc in PHONG:
        _ok(api.dk_phong_luu(qt, ten, sc))
    phong = {r["ten"]: r["phong_id"] for r in _ok(api.dk_phong_danh_sach(qt))}
    dong, n = [], 0
    for lop in LOP:
        for _ in range(6):
            n += 1
            dong.append("HS%03d\t%s %s %s\t%s" % (n, rng.choice(HO), rng.choice(DEM), rng.choice(TEN), lop))
    _ok(api.dk_hs_nap_danh_sach(qt, "\n".join(dong)))
    return api, qt, phong


def han_sau(ngay):
    return (datetime.datetime.now() + datetime.timedelta(days=ngay)).strftime("%Y-%m-%dT%H:%M")


def mo_gv_va_gui_clb(api, qt, phong):
    _ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    _ok(api.dk_dat_han(qt, "gv_dang_ky", han_sau(2)))
    tok = {}
    for i, ten in enumerate(GV):
        _ok(api.dk_gv_tu_dang_ky(MA, ten, "%04d" % (1111 * (i + 1) % 10000 or 1111)))
        tok[i] = _ok(api.dk_dang_nhap("giao_vien", ten, "%04d" % (1111 * (i + 1) % 10000 or 1111)))["token"]
    ten_phong = [p[0] for p in PHONG]
    dem = {}
    for k, ten in enumerate(CLB):
        buoi = BUOI[k % 5]
        j = dem[buoi] = dem.get(buoi, -1) + 1
        loai = "Tự do" if j == 0 else "Tuyển chọn"
        p = (j * 3 + k % 5) % 8
        d = {"ten": "CLB " + ten, "buoi": buoi, "loai": loai, "phong_id": phong[ten_phong[p]], "khoi_tu": 6 + k % 3,
             "khoi_den": 10 + k % 3, "mo_ta": "Sinh hoạt hằng tuần, có sản phẩm cuối kỳ.", "yeu_cau": "Không"}
        if loai == "Tuyển chọn":
            d.update(chi_tieu=min(15, PHONG[p][1]), diem_san=5, link_forms="https://forms.gle/demo-%d" % k)
        _ok(api.dk_clb_luu(tok[k % 6], d))


def nop_gia(api, qt, rng, ty_le=0.7):
    ds = _ok(api.dk_hs_danh_sach(qt))
    for x in ds:
        if rng.random() > ty_le:
            continue
        pin = _ok(api.dk_hs_dat_lai_pin(qt, x["ma"]))["pin"]
        tk = _ok(api.dk_dang_nhap("hoc_sinh", x["ma"], pin))["token"]
        hop = _ok(api.dk_hs_clb_hop_le(tk))
        nv = []
        for b in BUOI:
            tu_do = [c for c in hop if c["buoi"] == b and c["loai"] == "Tự do"]
            khac = [c for c in hop if c["buoi"] == b and c["loai"] != "Tự do"]
            for c in rng.sample(khac, min(len(khac), rng.randint(0, 2))) + tu_do[:1]:
                nv.append({"clb_id": c["clb_id"], "thi": c["loai"] == "Tuyển chọn" and rng.random() < 0.7})
        _ok(api.dk_hs_luu(tk, nv))


def chup_that(pw, ra):
    tmp = tempfile.mkdtemp()
    api, qt, phong = dung_that(tmp)
    rng = random.Random(7)
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    url = browser_host.serve(api, GOC, "dang_ky.html", open_browser=False)

    def trang():
        pg = br.new_page(viewport={"width": 1200, "height": 900})
        pg.goto(url)
        pg.wait_for_selector("text=Chọn vai trò")
        return pg

    def vao_qt(pg):
        pg.get_by_role("button", name="Quản trị", exact=True).click()
        pg.fill("input[name=ma]", MK)
        pg.get_by_role("button", name="Đăng nhập").click()
        pg.wait_for_selector("text=Quản trị · ")
        pg.wait_for_timeout(400)

    def tab(pg, ten):
        pg.locator("nav.dk-the button", has_text=ten).first.click()
        pg.wait_for_timeout(400)

    chup = lambda pg, t: ra.anh(pg, "that", t)  # noqa: E731
    # giai đoạn 0: Chuẩn bị
    pg = trang()
    vao_qt(pg)
    chup(pg, "viec_0")
    pg.close()
    # giai đoạn 1: giáo viên đăng ký
    mo_gv_va_gui_clb(api, qt, phong)
    pg = trang()
    chup(pg, "landing")
    pg.get_by_role("button", name="Quản trị", exact=True).click()
    chup(pg, "dang_nhap_qt")
    pg.fill("input[name=ma]", MK)
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Quản trị · ")
    pg.wait_for_timeout(400)
    chup(pg, "viec_1")
    for t, ten in (("Danh sách", "ds"), ("Cài đặt", "cai_dat"), ("Thêm", "them")):
        tab(pg, t)
        chup(pg, ten)
    pg.close()
    pg = trang()
    pg.get_by_role("button", name="Giáo viên", exact=True).click()
    chup(pg, "gv_dang_nhap")
    pg.fill("input[name=ten]", GV[0])
    pg.fill("input[name=ma]", "1111")
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=CLB của tôi")
    chup(pg, "gv_ds")
    moi = pg.get_by_role("button", name="+ Đăng ký CLB mới")
    if moi.count():
        moi.first.click()
    chup(pg, "gv_form")
    pg.close()
    # giai đoạn 2: duyệt
    _ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    pg = trang()
    vao_qt(pg)
    chup(pg, "viec_2")
    pg.close()
    # giai đoạn 3: học sinh đăng ký
    for c in _ok(api.dk_clb_danh_sach(qt)):
        _ok(api.dk_clb_duyet(qt, c["clb_id"], "duyet"))
    _ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    _ok(api.dk_dat_han(qt, "hs_dang_ky", han_sau(2)))
    nop_gia(api, qt, rng)
    pg = trang()
    vao_qt(pg)
    chup(pg, "viec_3")
    pg.close()
    chua = [x for x in _ok(api.dk_hs_danh_sach(qt)) if not x["da_nop"]][0]
    pin = _ok(api.dk_hs_dat_lai_pin(qt, chua["ma"]))["pin"]
    pg = trang()
    pg.get_by_role("button", name="Học sinh", exact=True).click()
    chup(pg, "hs_dang_nhap")
    pg.fill("input[name=ten]", chua["ma"])
    pg.fill("input[name=ma]", pin)
    pg.get_by_role("button", name="Đăng nhập").click()
    pg.wait_for_selector("text=Đúng là em")
    chup(pg, "hs_xacnhan")
    pg.get_by_role("button", name="Đúng là em").click()
    pg.get_by_role("button", name="+ Thêm").first.click()
    chup(pg, "hs_buoi")
    _di_den_xem_lai(pg)
    chup(pg, "hs_xemlai")
    pg.get_by_role("button", name="Gửi nguyện vọng").click()
    pg.wait_for_selector("#dkBienNhan")
    chup(pg, "hs_dagui")
    pg.close()
    # giai đoạn 4 và 5
    _ok(api.dk_chuyen_giai_doan(qt, "nhap_diem"))
    for c in _ok(api.dk_diem_danh_sach(qt)):
        for x in c["hoc_sinh"]:
            if rng.random() < 0.85:
                _ok(api.dk_diem_dat(qt, x["ma"], c["clb_id"], str(round(rng.uniform(3, 10), 1))))
    pg = trang()
    vao_qt(pg)
    chup(pg, "viec_4")
    pg.close()
    for c in _ok(api.dk_diem_danh_sach(qt)):                  # điền nốt điểm còn thiếu để «Chốt và xếp» được
        for x in c["hoc_sinh"]:
            if x["diem"] is None:
                _ok(api.dk_diem_dat(qt, x["ma"], c["clb_id"], "7"))
    _ok(api.dk_chot_va_xep(qt, 7))
    pg = trang()
    vao_qt(pg)
    chup(pg, "viec_5")
    pg.close()
    br.close()


def main(argv):
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 2
    ra = Ra(os.path.abspath(argv[0]), next((a.split("=", 1)[1] for a in argv if a.startswith("--ten=")), None)
            or (argv[argv.index("--ten") + 1] if "--ten" in argv else None))
    os.makedirs(ra.thu_muc, exist_ok=True)
    che = argv[argv.index("--chi") + 1] if "--chi" in argv else "ca_hai"
    with sync_playwright() as pw:
        if che in ("ca_hai", "v8"):
            chup_v8(pw, ra)
        if che in ("ca_hai", "that"):
            chup_that(pw, ra)
    print("\n".join(ra.ds))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
