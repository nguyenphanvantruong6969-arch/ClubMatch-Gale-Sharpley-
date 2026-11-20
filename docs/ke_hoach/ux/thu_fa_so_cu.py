"""UX1 §6b: bật FA rồi nạp sổ cũ không có cột Loại — xem lần chạy có bị chặn không. Dữ liệu MÔ PHỎNG."""
import base64, os, sys, tempfile, pathlib, collections
GOC=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); sys.path.insert(0,GOC); os.chdir(tempfile.mkdtemp())
from api import PipelineAPI; import cau_hinh_ws as ch
for so in ["SO_NHAP_DQT_120HS_HOP_LE.xlsx","SO_NHAP_MAU_120HS_3BUOI.xlsx"]:
    d=tempfile.mkdtemp(); api=PipelineAPI(os.path.join(d,"app.db"))
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": True, "fa_daa": True}})
    r=api.import_so_nhap(base64.b64encode(pathlib.Path(GOC,"du_lieu_test",so).read_bytes()).decode())
    rr=api.run_pipeline(seed=42)
    print(so, "nap", r["ok"], "chay", rr["ok"], dict(collections.Counter(e["code"] for e in rr.get("errors") or [])))
