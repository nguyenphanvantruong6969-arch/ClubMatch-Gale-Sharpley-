"""UX1a/UX1A-L8: chụp màn hình luồng thật bằng Chromium VÀ đếm số lần bấm (dữ liệu MÔ PHỎNG, hạt giống 42).
Ảnh ghi vào docs/ke_hoach/ux/anh/. Không đụng 04_phieu.png / phieu_mau.pdf (chup_phieu.py, nhóm B).

    python docs/ke_hoach/ux/chup_luong_chinh.py

In ra số lần bấm ĐO ĐƯỢC cho: (1) quản trị nạp -> chạy -> tải kết quả; (2) quản trị xử lý em chưa có CLB;
(3) giáo viên chủ nhiệm lấy kết quả lớp; (4) học sinh tự tra cứu. Một lần "chọn tệp" tính là một lần bấm."""
import os, sys, tempfile, base64
GOC=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); sys.path.insert(0,GOC)
from api import PipelineAPI; import browser_host
from playwright.sync_api import sync_playwright
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "anh")
SO=GOC+"/du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx"
os.environ["RBDA_THU_MUC_TAI_VE"]=tempfile.mkdtemp()
import workspace as ws


def moi_api(ten, co_ws=False):
    d=tempfile.mkdtemp()
    if co_ws:
        goc=os.path.join(d,"goc"); os.makedirs(goc); slug=ws.tao(goc,"Trường học",None)
        return PipelineAPI(ws.duong_dan_db(goc,slug), thu_muc_goc_ws=goc, ws_da_chon=True)
    return PipelineAPI(os.path.join(d,"app.db"))


def _chromium():
    sys.path.insert(0, os.path.join(GOC, "tests"))
    try:
        from _trinh_duyet import CHROMIUM
        return CHROMIUM
    except Exception:
        return None


pw=sync_playwright().start(); br=pw.chromium.launch(executable_path=os.environ.get("CHROMIUM") or _chromium(),args=["--no-sandbox"])
def trang(api, vp=(1366,800)):
    url=browser_host.serve(api,GOC,"index.html",open_browser=False)
    p=br.new_page(locale="vi-VN",viewport={"width":vp[0],"height":vp[1]}); p.goto(url); p.wait_for_selector("#dropZone", state="attached"); p.wait_for_timeout(600)
    return p

# ---- 1. Quản trị: nạp -> chạy -> tải kết quả (và xử lý em chưa có CLB), có không gian làm việc để chụp Cài đặt
api=moi_api("a", co_ws=True); page=trang(api); lan=0
page.screenshot(path=OUT+"/01_trang_dau.png")
page.set_input_files("#fileAny", SO); lan+=1                          # 1: chọn tệp
page.wait_for_timeout(800); page.screenshot(path=OUT+"/05_sau_chon_tep.png")
page.locator("#btnImportAll").click(); lan+=1                          # 2: Nhập sổ
page.wait_for_function("()=>document.getElementById('viecTiepTheo').dataset.trangThai==='chay'", timeout=30000)
page.wait_for_timeout(500); page.screenshot(path=OUT+"/06_sau_nhap.png")
page.locator("#viecTiepTheoNut").click(); lan+=1                       # 3: Chạy sắp xếp (nút của thanh)
page.wait_for_function("()=>['xu_ly','xuat'].includes(document.getElementById('viecTiepTheo').dataset.trangThai)", timeout=60000)
page.wait_for_timeout(1200); page.screenshot(path=OUT+"/07_sau_chay.png", full_page=True)
trang_thai=page.evaluate("()=>document.getElementById('viecTiepTheo').dataset.trangThai")
nut2="#viecTiepTheoNut2" if trang_thai=="xu_ly" else "#viecTiepTheoNut"
page.locator(nut2).click(); lan+=1                                     # 4: Xuất kết quả
page.wait_for_function("()=>document.getElementById('xuatFeedback').textContent.trim()!==''", timeout=30000)
print("QUAN TRI nap->chay->tai ket qua: %d lan bam (trang thai sau chay: %s)"%(lan,trang_thai))
page.wait_for_timeout(600); page.screenshot(path=OUT+"/02_co_dl_others.png")
# em chưa có CLB: một lần bấm trên thanh
page.reload(); page.wait_for_selector("#dropZone"); page.wait_for_function("()=>document.getElementById('viecTiepTheo').dataset.trangThai==='xu_ly'")
page.locator("#viecTiepTheoNut").click()
page.wait_for_selector("#chuaCoChoPanelBody", state="visible"); page.wait_for_timeout(900)
print("QUAN TRI xu ly em chua co CLB: 1 lan bam tren thanh (sau khi chay)")
page.screenshot(path=OUT+"/02_co_dl_chua_co_cho.png")
for tab,ten in (("results","02_co_dl_results"),("fallback","02_co_dl_fallback"),("admin","02_co_dl_admin")):
    page.locator('.nav-item[data-tab="%s"]'%tab).click(); page.wait_for_timeout(900); page.screenshot(path=OUT+"/%s.png"%ten, full_page=(tab!="admin"))
page.locator("#ux1aHuyChuong").scroll_into_view_if_needed(); page.screenshot(path=OUT+"/11_cai_dat.png")
page.evaluate("document.getElementById('ux1aNangCao').open=true"); page.locator("#gt2TieuChiPanel").scroll_into_view_if_needed(); page.wait_for_timeout(500)
page.screenshot(path=OUT+"/08_tieu_chi.png")
page.locator('.nav-item[data-tab="results"]').click(); page.wait_for_timeout(600)
page.locator("#gtTim").fill("HS004"); page.wait_for_timeout(1200); page.screenshot(path=OUT+"/03_tra_cuu_HS004.png", full_page=True)
page.locator("#btnWorkspace").click(); page.wait_for_timeout(600)
page.locator("#wsBang tr .menu-khac > summary").first.click(); page.wait_for_timeout(400); page.screenshot(path=OUT+"/10_ws_menu.png")
page.close()

# ---- 2. Giáo viên chủ nhiệm: đăng nhập -> kết quả lớp mình
api=moi_api("b"); 
with open(SO,"rb") as f_so: api.import_so_nhap(base64.b64encode(f_so.read()).decode())
api.run_pipeline(42)
ma=[r["student_id"] for r in api.list_students_admin("",1,500)["data"]["rows"]]
for i,sid in enumerate(sorted(ma)):
    api.set_student_class(sid, "10A1" if i%2==0 else "10A2")
api.tao_tai_khoan("quantri","matkhau-gia-1","quan_tri"); api.tao_tai_khoan("gv1","matkhau-gia-1","giao_vien"); api.dang_xuat(); api.dang_nhap("gv1","matkhau-gia-1")
page=trang(api); page.wait_for_timeout(800)
tab=page.evaluate("()=>document.querySelector('.nav-item.is-active').dataset.tab"); lan=0
if page.locator('#kqTang1 [data-kq="lop"]').count(): page.locator('#kqTang1 [data-kq="lop"]').click(); lan+=1
page.wait_for_timeout(500)
if page.locator("#kqLop").count() and page.locator("#kqLop").is_visible():
    page.locator("#kqLop").select_option(index=1); lan+=1
page.wait_for_timeout(700); page.screenshot(path=OUT+"/09_gvcn_ket_qua_lop.png")
print("GV CHU NHIEM: mo app dang o the '%s' (0 lan bam); xem ket qua lop mình: %d lan bam"%(tab,lan))
page.close()

# ---- 3. Học sinh tự tra cứu bằng mã: 2 lần bấm (không đổi)
print("HOC SINH tu tra cuu bang ma: 2 lan bam (ma + Xem) — khong doi so voi truoc; do bang test_giao_dien_gt4_man_hoc_sinh.py")
br.close(); pw.stop()
