"""UX1 §6: cùng sổ có Loại + Huy chương, nạp vào 3 cấu hình (mặc định / tắt hết / FA bật). Dữ liệu MÔ PHỎNG, hạt giống 42."""
import base64, os, sys, tempfile, pathlib, sqlite3
GOC=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))); sys.path.insert(0,GOC); os.chdir(tempfile.mkdtemp())
from api import PipelineAPI
SO=base64.b64encode(pathlib.Path(GOC,"du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx").read_bytes()).decode()
def thu(ten, wharton, fa, xoa_huy=False):
    d=tempfile.mkdtemp(); api=PipelineAPI(os.path.join(d,"app.db"))
    import cau_hinh_ws as ch
    ch.ghi_cau_hinh(api.db_path, {"rules": {"wharton": wharton, "fa_daa": fa}})
    r=api.import_so_nhap(SO); w=[e["code"] for e in (r.get("data") or {}).get("warnings",[])] if r["ok"] else r["errors"][:3]
    db=api.db_path if hasattr(api,"db_path") else os.path.join(d,"app.db")
    if xoa_huy:
        c=sqlite3.connect(db); c.execute("DELETE FROM wharton_bids"); c.commit(); c.close()
    n_bid=sqlite3.connect(db).execute("SELECT COUNT(*) FROM wharton_bids").fetchone()[0]
    loai=sqlite3.connect(db).execute("SELECT COUNT(*) FROM clubs WHERE loai IS NOT NULL").fetchone()[0]
    rr=api.run_pipeline(seed=42)
    kq=sorted(sqlite3.connect(db).execute("SELECT student_id, buoi, club_id FROM match_results").fetchall()) if rr["ok"] else None
    print(f"{ten}: nap_ok={r['ok']} canh_bao={dict(__import__('collections').Counter(w)) if isinstance(w,list) and w and isinstance(w[0],str) else w} so_huy_chuong_luu={n_bid} clb_co_loai={loai} chay_ok={rr['ok']}", "" if rr["ok"] else dict(__import__("collections").Counter(e["code"] for e in rr["errors"])), "so_dong_kq=",len(kq) if kq else 0)
    return kq
a=thu("A wharton=ON fa=OFF (mac dinh)", True, False)
a0=thu("A' mac dinh, xoa huy chuong", True, False, True)
b=thu("B wharton=OFF fa=OFF", False, False)
b0=thu("B' wharton=OFF, xoa huy chuong", False, False, True)
c=thu("C fa=ON", True, True)
c0=thu("C' fa=ON, xoa huy chuong", True, True, True)
print("A==A'", a==a0, "| B==B'", b==b0, "| C==C'", c==c0, "| B==C", b==c)
dc=dict(((s,b),k) for s,b,k in c); dc0=dict(((s,b),k) for s,b,k in c0)
khac=[x for x in dc if dc[x]!=dc0.get(x)]
print("FA: so (hoc sinh, buoi) doi CLB khi bo huy chuong:", len(khac), "/", len(dc), "; so em:", len({s for s,_ in khac}))
