"""UX1a: chụp màn hình luồng thật bằng Chromium (dữ liệu MÔ PHỎNG, hạt giống 42). Ảnh ghi vào docs/ke_hoach/ux/anh/."""
import os, sys, tempfile
GOC=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); sys.path.insert(0,GOC)
from api import PipelineAPI; import browser_host
from playwright.sync_api import sync_playwright
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), "anh"); d=tempfile.mkdtemp()
api=PipelineAPI(os.path.join(d,"app.db"))
url=browser_host.serve(api,GOC,"index.html",open_browser=False)
pw=sync_playwright().start(); br=pw.chromium.launch(executable_path=os.environ.get("CHROMIUM") or None,args=["--no-sandbox"])
page=br.new_page(locale="vi-VN",viewport={"width":1366,"height":800}); page.goto(url); page.wait_for_selector("#dropZone")
page.set_input_files("#fileAny", GOC+"/du_lieu_test/SO_NHAP_DQT_120HS_HOP_LE.xlsx")  # click 1 (chọn tệp)
page.wait_for_timeout(800); page.screenshot(path=OUT+"/05_sau_chon_tep.png")
page.locator("#btnImportAll").click()  # click 2
page.wait_for_function("()=>!document.getElementById('btnRun').disabled", timeout=30000)
page.wait_for_timeout(800); page.screenshot(path=OUT+"/06_sau_nhap.png")
page.locator("#btnRun").click()  # click 3
page.wait_for_timeout(500)
if page.locator("#runConfirmBar").count(): print("co thanh xac nhan")
page.wait_for_function("()=>document.getElementById('btnRun').textContent.indexOf('Đang')<0", timeout=60000)
page.wait_for_timeout(1500); page.screenshot(path=OUT+"/07_sau_chay.png", full_page=True)
print("tab dang mo:", page.evaluate("()=>document.querySelector('.nav-item.is-active').dataset.tab"))
print("toast:", page.evaluate("()=>[...document.querySelectorAll('.toast')].map(e=>e.innerText)"))
br.close(); pw.stop()
