"""UX1 tich hop I4: do so lan bam va doc PDF tren nhanh tich hop (du lieu MO PHONG, hat giong 42). Anh: docs/ke_hoach/ux/anh/danh_gia_tich_hop/. Can pypdf."""
import os, sys, tempfile, base64, glob, pathlib
GOC=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); sys.path.insert(0,GOC); sys.path.insert(0,GOC+"/tests")
os.environ["RBDA_THU_MUC_TAI_VE"]=TAI=tempfile.mkdtemp()
from api import PipelineAPI; import browser_host, workspace as ws
from _trinh_duyet import CHROMIUM
from playwright.sync_api import sync_playwright
from pypdf import PdfReader
OUT=GOC+"/docs/ke_hoach/ux/anh/danh_gia_tich_hop"
SO=GOC+"/du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx"; FA=GOC+"/du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx"
loi=[]
pw=sync_playwright().start(); br=pw.chromium.launch(executable_path=CHROMIUM,args=["--no-sandbox"])
def trang(api):
    url=browser_host.serve(api,GOC,"index.html",open_browser=False)
    p=br.new_page(locale="vi-VN",viewport={"width":1366,"height":900}); p.on("pageerror",lambda e: loi.append(str(e)))
    p.goto(url); p.wait_for_selector("#dropZone",state="attached"); p.wait_for_timeout(700); return p
def pdf_text(path):
    r=PdfReader(path); return len(r.pages), "\n".join(pg.extract_text() or "" for pg in r.pages)
def phan_hoi(p,sel):
    p.wait_for_function("(s)=>document.querySelector(s).textContent.trim()!==''",arg=sel,timeout=60000); p.wait_for_timeout(500)
    return p.locator(sel).inner_text()
def moi(so, ws_=False):
    d=tempfile.mkdtemp()
    if ws_:
        g=os.path.join(d,"goc"); os.makedirs(g); s=ws.tao(g,"Trường học",None); return PipelineAPI(ws.duong_dan_db(g,s),thu_muc_goc_ws=g,ws_da_chon=True)
    a=PipelineAPI(os.path.join(d,"app.db"))
    if so==FA:
        import cau_hinh_ws as ch; ch.ghi_cau_hinh(a.db_path, {"rules": {"wharton": True, "fa_daa": True}})
    a.import_so_nhap(base64.b64encode(pathlib.Path(so).read_bytes()).decode()); rr=a.run_pipeline(42); print("run ok",rr["ok"]); return a
# 1 admin
api=moi(None,True); p=trang(api); n=0
p.set_input_files("#fileAny",SO); n+=1; p.wait_for_timeout(800)
p.locator("#btnImportAll").click(); n+=1
p.wait_for_function("()=>document.getElementById('viecTiepTheo').dataset.trangThai==='chay'",timeout=30000)
p.locator("#viecTiepTheoNut").click(); n+=1
p.wait_for_function("()=>['xu_ly','xuat'].includes(document.getElementById('viecTiepTheo').dataset.trangThai)",timeout=60000); p.wait_for_timeout(1000)
tt=p.evaluate("()=>document.getElementById('viecTiepTheo').dataset.trangThai")
p.locator("#viecTiepTheoNut2" if tt=="xu_ly" else "#viecTiepTheoNut").click(); n+=1
p.wait_for_function("()=>document.getElementById('xuatFeedback').textContent.trim()!==''",timeout=30000)
print("ADMIN nap->chay->xuat:",n,"state",tt)
p.screenshot(path=OUT+"/1_quan_tri_sau_xuat.png")
# admin Xuất… menu
p.locator('.nav-item[data-tab="others"]').click(); p.wait_for_timeout(500)
p.locator("#xuatMenu > summary").scroll_into_view_if_needed(); p.locator("#xuatMenu > summary").click(); p.wait_for_timeout(400)
print("MENU items:", [t.strip() for t in p.locator("#xuatMenu .menu-khac-muc").all_inner_texts()])
p.locator("#btnPdfDsClb").click(); print("DS CLB PDF:", phan_hoi(p,"#xuatFeedback")[:200])
# single-student PDF
p.locator('.nav-item[data-tab="results"]').click(); p.wait_for_timeout(400); n=1
p.locator("#gtTim").fill("HS004"); n+=0; p.wait_for_selector(".gt-chon"); p.locator(".gt-chon").first.click(); n+=1
p.wait_for_selector("#btnGtPdfMot",state="visible"); p.locator("#gtPanel").screenshot(path=OUT+"/3_tra_cuu_mot_em.png")
p.locator("#btnGtPdfMot").click(); n+=1
print("PDF 1 em clicks (tab+chon+luu, go ma khong tinh):",n, phan_hoi(p,"#gtXuatPhanHoi")[:200])
p.close()
for f in glob.glob(TAI+"/**/*.pdf",recursive=True): print("  file",os.path.relpath(f,TAI))
mot=[f for f in glob.glob(TAI+"/**/phieu_giai_trinh_HS004*.pdf",recursive=True)]
if mot:
    k,t=pdf_text(mot[0]); print("PHIEU HS004 pages",k); print(t[:1800])
dsclb=[f for f in glob.glob(TAI+"/**/*.pdf",recursive=True) if "danh_sach" in f]
if dsclb: k,t=pdf_text(sorted(dsclb)[0]); print("DS CLB sample",os.path.basename(sorted(dsclb)[0]),k,"pages\n",t[:700])
# 2 teacher (FA medals data)
for ten,so in (("DQT",SO),("FA",FA)):
    api=moi(so); ma=sorted(r["student_id"] for r in api.list_students_admin("",1,500)["data"]["rows"])
    for i,s in enumerate(ma): api.set_student_class(s,["10A1","10A2","10A3"][i%3])
    api.tao_tai_khoan("qt","matkhau-gia-1","quan_tri"); api.tao_tai_khoan("gv1","matkhau-gia-1","giao_vien"); api.dang_xuat(); api.dang_nhap("gv1","matkhau-gia-1")
    p=trang(api); p.wait_for_timeout(800)
    tab=p.evaluate("()=>document.querySelector('.nav-item.is-active').dataset.tab")
    p.locator("#kqChonLop").select_option("10A2"); p.wait_for_timeout(600)
    p.screenshot(path=OUT+"/4_gv_%s_trang_ket_qua.png"%ten)
    p.locator("#btnUx1bPhieuLop").click(); r1=phan_hoi(p,"#ux1bPhanHoi")
    print(ten,"GV tab:",tab,"| phieu lop:",r1[:200])
    print(ten,"GV sees btnGtPdfMot:",p.locator("#btnGtPdfMot").is_visible(),"| xuatMenu visible:",p.locator("#xuatMenu").is_visible())
    p.evaluate("document.getElementById('ux1bPhanHoi').textContent=''")
    p.locator("#btnUx1bBaoCaoPdf").click(); r2=phan_hoi(p,"#ux1bPhanHoi"); print(ten,"bao cao pdf:",r2[:200])
    p.close()
for f in sorted(glob.glob(TAI+"/**/*.pdf",recursive=True),key=os.path.getmtime)[-4:]:
    k,t=pdf_text(f); print("=====",os.path.basename(f),k,"pages"); print(t[:1500])
print("JS errors:",loi)
br.close(); pw.stop()
