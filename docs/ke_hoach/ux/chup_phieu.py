"""UX1a: chụp màn hình luồng thật bằng Chromium (dữ liệu MÔ PHỎNG, hạt giống 42). Ảnh ghi vào docs/ke_hoach/ux/anh/."""
import base64, os, pathlib, sys, tempfile
GOC=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); sys.path.insert(0,GOC)
from api import PipelineAPI; import browser_host
from playwright.sync_api import sync_playwright
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "anh"); d=tempfile.mkdtemp()
api=PipelineAPI(os.path.join(d,"app.db"))
api.import_so_nhap(base64.b64encode(pathlib.Path(GOC, "du_lieu_test", "SO_NHAP_DQT_120HS_HOP_LE.xlsx").read_bytes()).decode())
api.run_pipeline(seed=42)
url=browser_host.serve(api,GOC,"index.html",open_browser=False)
pw=sync_playwright().start(); br=pw.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None,args=["--no-sandbox"])
page=br.new_page(locale="vi-VN",viewport={"width":1366,"height":800}); page.goto(url); page.wait_for_selector("#dropZone")
page.locator('[data-tab="results"]').click()
page.locator("#gtTim").fill("HS004"); page.wait_for_selector(".gt-chon"); page.locator(".gt-chon").first.click()
page.wait_for_selector("#gtIn:not([hidden])"); page.wait_for_timeout(500)
page.locator("#gtPanel").screenshot(path=OUT+"/03_tra_cuu_HS004.png")
page.locator("#btnGtInMot").click(); page.wait_for_timeout(1500)
print("phan hoi:", page.locator("#gtXuatPhanHoi").inner_text())
r=api.export_phieu_giai_trinh("",["HS004","HS001"]); print(r["ok"], r.get("data"))
p=r["data"]["path"]; pg=br.new_page(); pg.goto("file://"+p); pg.pdf(path=OUT+"/phieu_mau.pdf", format="A4")
pg.set_viewport_size({"width":900,"height":1200}); pg.screenshot(path=OUT+"/04_phieu.png", full_page=True)
br.close(); pw.stop()
