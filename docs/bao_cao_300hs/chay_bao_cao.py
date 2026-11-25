# -*- coding: utf-8 -*-
"""Chạy thử nghiệm 300 học sinh trên GIAO DIỆN THẬT (Chromium) và ghi số liệu + ảnh cho báo cáo.

    python docs/bao_cao_300hs/sinh_300hs.py        # sổ hợp lệ
    python docs/bao_cao_300hs/sinh_so_co_loi.py    # ba sổ cố ý sai
    python docs/bao_cao_300hs/chay_bao_cao.py      # -> anh/*.png, so_lieu.json
    python docs/bao_cao_300hs/tao_docx.py          # -> BAO_CAO_THU_NGHIEM_300HS.docx

DỮ LIỆU MÔ PHỎNG. Mọi số liệu là số đo trên dữ liệu bịa, không phải khảo sát thật.
"""
import base64
import collections
import json
import os
import sqlite3
import subprocess
import sys
import tempfile

D = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, GOC)
os.environ["RBDA_THU_MUC_TAI_VE"] = tempfile.mkdtemp()

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

ANH = os.path.join(D, "anh")
os.makedirs(ANH, exist_ok=True)
SO = os.path.join(D, "SO_NHAP_300HS_DOI_CHE_DO.xlsx")
SEED = 42
CA = {"thanh_cong": "DC002", "khong_dat_huy_chuong_boc_tham": "DC034", "khong_dat_diem": "DC008"}
SO_LIEU = {"seed": SEED}


def moi_api():
    d = tempfile.mkdtemp()
    goc = os.path.join(d, "goc")
    os.makedirs(goc)
    slug = ws.tao(goc, "Trường học", None)
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_goc_ws=goc, ws_da_chon=True)


def b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode()


def so_lan_chay(api):
    with sqlite3.connect(api.db_path) as c:
        return c.execute("SELECT COUNT(*) FROM run_history").fetchone()[0]


def ket_qua(api):
    rows = api.get_match_results()["data"]
    rows = rows["rows"] if isinstance(rows, dict) else rows
    return {(r["student_id"], r["buoi"]): r for r in rows}


def tom_tat(kq):
    dem = collections.Counter(r["rank_in_student_pref"] for r in kq.values())
    n = len(kq)
    return {"n_cho": n,
            "nv": {str(k): dem.get(k, 0) for k in (1, 2, 3, 4, 5)},
            "nv_6_tro_len": sum(v for k, v in dem.items() if isinstance(k, int) and k >= 6),
            "ngoai_nv": dem.get(None, 0),
            "ty_le_nv1": round(100.0 * dem.get(1, 0) / n, 1),
            "ty_le_top3": round(100.0 * sum(dem.get(k, 0) for k in (1, 2, 3)) / n, 1)}


def so_khac(a, b):
    return sum(1 for k in a if a[k]["club_id"] != b.get(k, {}).get("club_id"))


pw = sync_playwright().start()
br = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium"),
                        args=["--no-sandbox"])


def mo_trang(api):
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    p = br.new_page(locale="vi-VN", viewport={"width": 1366, "height": 860}, device_scale_factor=2)
    p.on("dialog", lambda dl: dl.accept())
    p.goto(url)
    p.wait_for_selector("#dropZone", state="attached")
    p.wait_for_timeout(800)
    return p


def the(p, tab):
    p.locator('.nav-item[data-tab="%s"]' % tab).click()
    p.wait_for_timeout(900)


def chup(p, ten, sel=None, full=False, an_toast=True):
    duong = os.path.join(ANH, ten)
    # Thông báo nổi (toast) che nội dung: ẩn khi chụp, trừ ảnh cần chính thông báo đó.
    p.evaluate("v=>document.querySelectorAll('.toast').forEach(t=>t.style.visibility=v?'hidden':'')", an_toast)
    if sel:
        p.locator(sel).first.scroll_into_view_if_needed()
        p.wait_for_timeout(300)
        p.locator(sel).first.screenshot(path=duong)
    else:
        p.screenshot(path=duong, full_page=full)
    print("  anh:", ten)


def bam_chay(p, api, seed=SEED):
    truoc = so_lan_chay(api)
    the(p, "pipeline")
    if not p.locator("#nangCao").evaluate("e=>e.open"):
        p.locator("#nangCao > summary").click()
    o = p.locator("#seedInput")
    if o.input_value() != str(seed):
        # Seed đã khoá cùng bộ số bốc thăm: đổi seed = "Vẽ lại số bốc thăm" (nút trên dòng khoá).
        if o.evaluate("e=>e.readOnly"):
            p.locator("#stbLockLine .redraw-toggle").click()
            p.wait_for_timeout(500)
        o.fill(str(seed))
    p.locator("#btnRun").click()
    p.wait_for_timeout(600)
    xn = p.locator("#runConfirmBar .btn-primary")
    if xn.count() and xn.first.is_visible():
        xn.first.click()
    for i in range(240):
        p.wait_for_timeout(500)
        if so_lan_chay(api) > truoc:
            break
        if i == 6:
            p.screenshot(path=os.path.join(D, "_go_loi_chay.png"))
    else:
        raise RuntimeError("Chạy không xong")
    p.wait_for_timeout(1500)


def mo_panel(p, panel):
    """Mở một panel số liệu ở thẻ 'Chi tiết và xuất tệp' (bấm nút thu gọn nếu đang đóng)."""
    the(p, "others")
    nut = p.locator("#%s .panel-toggle" % panel).first
    if nut.get_attribute("aria-expanded") != "true":
        nut.click()
        p.wait_for_timeout(800)


# ============================================================ 1. Nạp, chạy, đổi chế độ
print("1. Nạp sổ 300 HS và đổi chế độ")
api = moi_api()
# Sổ có cột Loại / Điểm sàn / Huy chương: chọn Huy chương TRƯỚC khi nạp để phần mềm giữ các cột đó
# (nạp ở chế độ khác thì cột bị bỏ qua — xem mục 5, xung đột chế độ).
api.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})
p = mo_trang(api)
chup(p, "01_trang_dau.png")
p.set_input_files("#fileAny", SO)
p.wait_for_timeout(800)
p.locator("#btnImportAll").click()
p.wait_for_function("()=>document.getElementById('viecTiepTheo').dataset.trangThai==='chay'", timeout=60000)
p.wait_for_timeout(800)
chup(p, "02_nap_xong.png")
SO_LIEU["suc_khoe"] = api.get_data_health_report()["data"]["warnings"]
SO_LIEU["clb"] = [{k: c.get(k) for k in ("club_id", "name", "capacity", "buoi", "loai", "diem_san")}
                  for c in (api.list_clubs_admin()["data"])]

# (khoá cấu hình, nút thẻ chế độ, bật chia loại?, tên hiển thị)
CHE_DO = [
    ("chi_xep", "#ux1aChiXep", False, "Chỉ xếp thứ tự"),
    ("chia100", "#ux1aChia100", False, "Chia 100 điểm"),
    ("chia100_loai", "#ux1aChia100", True, "Chia 100 điểm + Chia CLB theo loại"),
    ("huy_chuong", "#ux1aHuyChuong", None, "Huy chương (Vàng/Bạc/Đồng)"),
]
KQ = {}
SO_LIEU["che_do"] = []
for khoa, nut, loai, ten in CHE_DO:
    print(" che do", khoa)
    the(p, "admin")
    p.locator("#qlTabCachXep").click()
    p.wait_for_timeout(700)
    p.locator(nut).click()
    p.wait_for_timeout(1200)
    if loai is not None:
        p.locator("#qlTabClb").click()
        p.wait_for_timeout(600)
        ct = p.locator("#mt2CongTac")
        if ct.is_enabled() and ct.is_checked() != loai:
            ct.click()
            p.wait_for_timeout(1000)
        chup(p, "03_%s_cong_tac_loai.png" % khoa, "#mt2ChiaLoai")
        p.locator("#qlTabCachXep").click()
        p.wait_for_timeout(700)
    rules = api.get_workspace_config()["data"]["config"]["rules"]
    chup(p, "03_%s_cach_xep.png" % khoa, "#ux1aCaiDat")
    bam_chay(p, api)
    KQ[khoa] = ket_qua(api)
    mo_panel(p, "nvPanel")
    chup(p, "04_%s_muc_dap_ung.png" % khoa, "#nvPanel")
    SO_LIEU["che_do"].append({"khoa": khoa, "ten": ten, "rules": {k: rules.get(k) for k in
                              ("wharton", "fa_daa", "chia_loai", "priority")}, **tom_tat(KQ[khoa])})
SO_LIEU["khac_nhau"] = {"%s|%s" % (a, b): so_khac(KQ[a], KQ[b])
                        for i, a in enumerate(KQ) for b in list(KQ)[i + 1:]}
# Một vài em đổi CLB giữa hai chế độ (ví dụ cụ thể cho báo cáo)
vd = []
for k in sorted(KQ["chi_xep"]):
    a, b = KQ["chi_xep"][k], KQ["huy_chuong"][k]
    if a["club_id"] != b["club_id"]:
        vd.append({"student_id": k[0], "buoi": k[1], "ten": a["name"],
                   "chi_xep": "%s (NV%s)" % (a["club_name"], a["rank_in_student_pref"] or "–"),
                   "chia100": "%s (NV%s)" % (KQ["chia100"][k]["club_name"], KQ["chia100"][k]["rank_in_student_pref"] or "–"),
                   "huy_chuong": "%s (NV%s)" % (b["club_name"], b["rank_in_student_pref"] or "–")})
SO_LIEU["vi_du_doi_clb"] = vd[:8]

# ============================================================ 2. Ca thành công / không đạt (chế độ Huy chương)
print("2. Giai trinh tung ca")
SO_LIEU["ca"] = {}
the(p, "results")
for nhan, sid in CA.items():
    p.locator("#gtTim").fill(sid)
    p.wait_for_timeout(1200)
    p.locator("#gtDs li button, #gtDs li").first.click()
    p.wait_for_timeout(1500)
    chup(p, "05_ca_%s_%s.png" % (nhan, sid), "#gtPanel")
    g = api.get_giai_trinh_hoc_sinh(sid)["data"]
    SO_LIEU["ca"][nhan] = {"student_id": sid, "buoi": [
        {"buoi": b["buoi"], "ket_qua": b.get("ten_clb"),
         "lua_chon": [{"hang": x["hang"], "clb": x["ten_clb"], "loai": x.get("loai_clb"),
                       "huy_chuong": x.get("huy_chuong"), "diem": x.get("diem_em"), "stb": x.get("stb_em"),
                       "ma": x["ma"], "cau": x["cau"]} for x in b["cac_lua_chon"]]} for b in g["buoi"]]}
# Báo cáo tải về: phiếu giải trình (HTML in được) cho ba em + PDF
kq_html = api.export_phieu_giai_trinh(os.path.join(tempfile.mkdtemp(), "phieu.html"), student_ids=list(CA.values()))
p2 = br.new_page(viewport={"width": 900, "height": 1200}, device_scale_factor=2)
p2.goto("file://" + kq_html["data"]["path"])
p2.wait_for_timeout(800)
p2.screenshot(path=os.path.join(ANH, "06_phieu_giai_trinh_tai_ve.png"), full_page=False)
p2.close()
pdf = api.export_phieu_giai_trinh_pdf(os.path.join(tempfile.mkdtemp(), "phieu.pdf"), student_ids=[CA["khong_dat_huy_chuong_boc_tham"]])
if pdf.get("ok"):
    duong_pdf = pdf["data"].get("path") or pdf["data"].get("paths", [None])[0]
    subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", "1", "-l", "1", duong_pdf,
                    os.path.join(ANH, "06b_phieu_pdf")], check=False)
# Menu xuất trên thẻ Kết quả
the(p, "results")
p.locator("#ux1bPanel").scroll_into_view_if_needed()
p.locator("#ux1bThemMenu > summary").click()
p.wait_for_timeout(500)
p.evaluate("window.scrollBy(0,-120)")
chup(p, "07_menu_bao_cao.png")
p.locator("#ux1bThemMenu > summary").click()
# Bảng ở thẻ "Chi tiết và xuất tệp": tóm tắt + xuất
the(p, "others")
chup(p, "07b_chi_tiet_xuat.png")

# ============================================================ 3. Seed (mã bốc thăm) — chế độ Chỉ xếp thứ tự
print("3. Seed")
the(p, "admin")
p.locator("#qlTabCachXep").click()
p.wait_for_timeout(600)
p.locator("#ux1aChiXep").click()
p.wait_for_timeout(1000)
SEEDS = [42, 7, 2026, 12345]
KQ_SEED = {}
SO_LIEU["seed_bang"] = []
STB = {}
for s in SEEDS:
    bam_chay(p, api, s)
    KQ_SEED[s] = ket_qua(api)
    st = api.get_so_boc_tham_theo_buoi("")["data"]
    STB[s] = st
    if s in (42, 7):
        mo_panel(p, "thamPanel")
        p.locator("#thamSearch").fill("DC00")          # chỉ 9 em đầu cho ảnh gọn
        p.wait_for_timeout(1200)
        chup(p, "08_so_boc_tham_seed_%d.png" % s, "#thamPanel")
        p.locator("#thamSearch").fill("")
    SO_LIEU["seed_bang"].append({"seed": s, **tom_tat(KQ_SEED[s]), "khac_seed42": so_khac(KQ_SEED[s], KQ_SEED[42])})
SO_LIEU["stb_mau"] = {str(s): STB[s] if not isinstance(STB[s], dict) else
                      {k: (v[:10] if isinstance(v, list) else v) for k, v in STB[s].items()} for s in (42, 7)}
the(p, "pipeline")
if p.locator("#btnToggleHistory").is_visible():
    p.locator("#btnToggleHistory").click()
    p.wait_for_timeout(600)
    chup(p, "09_lich_su_chay.png", "#historyPanel")
if not p.locator("#nangCao").evaluate("e=>e.open"):
    p.locator("#nangCao > summary").click()
chup(p, "09b_o_ma_boc_tham.png", "#nangCao")
# Bảng tiêu chí xếp (thứ tự ưu tiên khi nhiều em cùng muốn một chỗ)
the(p, "admin")
p.locator("#qlTabCachXep").click()
p.wait_for_timeout(600)
p.locator("#ux1aHuyChuong").click()
p.wait_for_timeout(1000)
p.evaluate("document.getElementById('ux1aNangCao').open=true")
p.wait_for_timeout(700)
chup(p, "10_thu_tu_tieu_chi_huy_chuong.png", "#gt2TieuChiPanel")
p.locator("#ux1aChiXep").click()
p.wait_for_timeout(1000)
chup(p, "10_thu_tu_tieu_chi_chi_xep.png", "#gt2TieuChiPanel")
p.close()

# ============================================================ 4. Dữ liệu thiếu / sai / xung đột
print("4. Loi")
SO_LIEU["loi"] = {}
for ten_tep, nhan in (("SO_NHAP_300HS_LOI_CLB.xlsx", "loi_clb"), ("SO_NHAP_300HS_LOI_HS.xlsx", "loi_hs"),
                      ("SO_NHAP_300HS_THIEU_XUNG_DOT.xlsx", "thieu_xung_dot")):
    a = moi_api()
    a.update_workspace_config({"rules": {"wharton": True, "fa_daa": True}})
    q = mo_trang(a)
    q.set_input_files("#fileAny", os.path.join(D, ten_tep))
    q.wait_for_timeout(2500)
    nut = q.locator("#btnImportAll")
    if nut.is_visible() and nut.is_enabled():        # sổ sai: phần mềm khoá nút Nhập sau khi soát
        nut.click()
        q.wait_for_timeout(3500)
    chup(q, "11_%s_nhap.png" % nhan)
    kq = a.import_so_nhap(b64(os.path.join(D, ten_tep))) if nhan != "thieu_xung_dot" else None
    SO_LIEU["loi"][nhan] = {"import_errors": kq["errors"] if kq else []}
    if nhan == "thieu_xung_dot":
        SO_LIEU["loi"][nhan]["health"] = a.get_data_health_report()["data"]["warnings"]
        if q.locator("#healthChiTiet").count():
            q.evaluate("()=>{const e=document.getElementById('healthChiTiet'); if(e){e.hidden=false; e.open=true;}}")
            q.wait_for_timeout(500)
        chup(q, "12_thieu_xung_dot_canh_bao.png", full=True)
        truoc = so_lan_chay(a)
        q.locator("#btnRun").click()
        q.wait_for_timeout(800)
        if q.locator("#runConfirmBar .btn-primary").count():
            q.locator("#runConfirmBar .btn-primary").first.click()
        q.wait_for_timeout(4000)
        chup(q, "12b_thieu_xung_dot_chay_bi_chan.png", full=True, an_toast=False)
        r = a.run_pipeline(SEED)
        SO_LIEU["loi"][nhan]["run_errors"] = r.get("errors")
        SO_LIEU["loi"][nhan]["chay_duoc"] = so_lan_chay(a) > truoc
    q.close()

# Xung đột chế độ: nạp ở chế độ mặc định (Chia 100) rồi bật Huy chương
a = moi_api()
q = mo_trang(a)
q.set_input_files("#fileAny", SO)
q.wait_for_timeout(900)
q.locator("#btnImportAll").click()
q.wait_for_timeout(3500)
chup(q, "13_xung_dot_che_do_nap.png")
the(q, "admin")
q.locator("#qlTabCachXep").click()
q.wait_for_timeout(600)
q.locator("#ux1aHuyChuong").click()
q.wait_for_timeout(1500)
chup(q, "13b_xung_dot_che_do_bat_huy_chuong.png", "#ux1aCaiDat")
r = a.run_pipeline(SEED)
SO_LIEU["loi"]["xung_dot_che_do"] = {"run_errors": r.get("errors")}
q.close()

br.close()
pw.stop()
with open(os.path.join(D, "so_lieu.json"), "w", encoding="utf-8") as f:
    json.dump(SO_LIEU, f, ensure_ascii=False, indent=1, default=str)
print("Xong:", os.path.join(D, "so_lieu.json"))
