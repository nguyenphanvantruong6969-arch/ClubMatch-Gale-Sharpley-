# -*- coding: utf-8 -*-
"""Bộ dữ liệu DEMO HACKATHON: mọi tính năng + dữ liệu cổng đăng nhập. DỮ LIỆU MÔ PHỎNG.

    python du_lieu_test/bo_demo_hackathon/tao_bo_demo.py            # ghi vào thư mục này
    python du_lieu_test/bo_demo_hackathon/tao_bo_demo.py --ra ./ra  # ghi chỗ khác

⚠️  Tên, lớp, nguyện vọng, điểm, mật khẩu và PIN đều do máy bịa (seed cố định). Không phải
học sinh hay khảo sát có thật; mật khẩu chỉ dùng cho buổi demo, KHÔNG dùng ở trường thật.

Ghi ra:
  SO_NHAP_DEMO_240HS.xlsx     240 em · 12 CLB · 3 buổi · suất ưu tiên · thi tuyển · điểm quyết tâm
  SO_NHAP_DEN_MUON_6HS.xlsx   6 em đến muộn (nạp SAU lần chạy đầu: thử khoá bốc thăm)
  demo-truong-thpt-mo-phong.zip  workspace: sổ trên đã nạp + lớp + mã tra cứu + 3 tài khoản (quản trị, 2 GV)
  demo-cong-dang-ky.zip          workspace: cổng đăng ký đang mở cho HS — 4 GV, 8 CLB đã duyệt, 60 em (50 đã nộp)
  TAI_KHOAN_DEMO.csv          mọi thông tin đăng nhập của hai workspace trên (một bảng)
  MA_TRA_CUU_DEMO.csv         mã tra cứu từng em (chế độ học sinh tự tra cứu)
  DIEM_DAN_CONG_DANG_KY.txt   điểm thi cho CLB Tuyển chọn của em nộp sau (dán ở bước nhập điểm)
  KIEM_CHUNG.json             số liệu phần mềm thật trả về khi tự kiểm (seed=42)

Sổ ghi bằng `so_nhap.ghi_so_nhap` (qua kỹ năng `sinh-du-lieu-clb`); CSDL dựng chỉ qua API công khai
của `PipelineAPI` (`{ok, data, errors}`), không ghi SQLite trực tiếp. Script tự kiểm bằng phần mềm
thật trên bản sao tạm (nhập 0 cảnh báo, chạy được, đăng nhập đúng/sai, khoá sau 5 lần sai) rồi mới ghi.
"""
import argparse
import base64
import csv
import json
import os
import random
import shutil
import sys
import tempfile

DAY = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(DAY))
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, ".claude", "skills", "sinh-du-lieu-clb", "scripts"))

import sinh_du_lieu as sd  # noqa: E402
import workspace as ws  # noqa: E402

from api import PipelineAPI  # noqa: E402

NHAN = "DỮ LIỆU MÔ PHỎNG — CHỈ DÙNG DEMO"
TEN_WS_KIOSK = "DEMO Trường THPT Mô Phỏng"
TEN_WS_DANG_KY = "DEMO Cổng đăng ký"
SEED = 20261128
SEED_XEP = 42
DO_CHOI = 1.3          # đủ chật để có NV2/NV3 và em chưa có chỗ, đủ rộng để ~80% em có CLB
N_HS, N_MUON = 240, 6
BUOI = ["thu_2", "thu_4", "thu_6"]
LOP = ["10A1", "10A2", "10A3", "11A1", "11A2", "11A3", "12A1", "12A2"]

# Cổng đăng nhập của phần mềm chính (GT3). Mật khẩu ≥ 8 ký tự.
TAI_KHOAN = [("quantri.demo", "Demo@2026", "quan_tri"),
             ("gv.nguyen", "GiaoVien@01", "giao_vien"),
             ("gv.tran", "GiaoVien@02", "giao_vien")]

# Cổng đăng ký (DK). Quản trị dùng mật khẩu riêng; GV / HS dùng PIN 4 số (không dễ đoán).
DK_MK_QT = "DangKy@2026"
DK_MA_TRUONG = "THPTDEMO"
DK_BUOI = ["Thứ 2", "Thứ 4"]
DK_KHOI = [10, 12]
DK_GV = [("Cô Lê Thu Hà", "4817"), ("Thầy Phạm Quốc Huy", "6093"),
         ("Cô Vũ Minh Chi", "3752"), ("Thầy Đỗ Gia Bảo", "8146")]
DK_PHONG = [("Phòng 101", 40), ("Phòng 102", 40), ("Sân trường", 80), ("Phòng STEM", 30)]
# (tên, buổi, loại, phòng, giáo viên, chỉ tiêu, điểm sàn)
DK_CLB = [("CLB Bóng rổ", 0, "Tự do", 2, 0, None, None),
          ("CLB Văn học", 0, "Tự do", 0, 1, None, None),
          ("CLB Cờ vua", 0, "Giới hạn", 1, 2, 12, None),
          ("CLB Robotics", 0, "Tuyển chọn", 3, 3, 8, 5),
          ("CLB Bóng đá", 1, "Tự do", 2, 1, None, None),
          ("CLB Âm nhạc", 1, "Tự do", 0, 0, None, None),
          ("CLB Hội hoạ", 1, "Giới hạn", 1, 3, 12, None),
          ("CLB Tin học", 1, "Tuyển chọn", 3, 2, 8, 5)]
DK_N_HS, DK_N_CHUA_NOP = 60, 10


def ok(r, *, cho_canh_bao=False):
    assert r["ok"] and r["errors"] == [], r
    d = r["data"]
    if not cho_canh_bao and isinstance(d, dict):
        assert not d.get("warnings"), d.get("warnings")
    return d


def ten_bia(rnd):
    return "%s %s %s" % (rnd.choice(sd._HO), rnd.choice(sd._DEM), rnd.choice(sd._TEN))


# --------------------------------------------------------------------------- sổ nhập
def tao_so(thu_muc):
    clb, hs = sd.sinh_ngau_nhien(N_HS + N_MUON, BUOI, 4, SEED, do_choi=DO_CHOI)
    sd.ap_diem_quyet_tam(clb, hs, SEED, "hop_le", "tron")
    loi = sd.soat(clb, hs) + sd.soat_diem_quyet_tam(clb, hs)
    assert not loi, loi
    chinh, muon = hs[:N_HS], hs[N_HS:]
    for i, h in enumerate(muon):                       # mã riêng, dễ nhận ra khi demo
        h["student_id"] = "MUON%02d" % (i + 1)
    assert not sd.soat(clb, chinh) and not sd.soat(clb, muon)
    p1 = sd.ghi_bo(thu_muc, clb, chinh, sd.CFG_DQT, "SO_NHAP_DEMO_240HS.xlsx")[0]
    p2 = sd.ghi_bo(thu_muc, clb, muon, sd.CFG_DQT, "SO_NHAP_DEN_MUON_6HS.xlsx")[0]
    return clb, chinh, muon, p1, p2


def b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode()


# --------------------------------------------------------------------------- CSDL kiosk
def tao_db_kiosk(db, thu_xuat, so_chinh, hs):
    api = PipelineAPI(db, thu_muc_xuat=thu_xuat)
    ok(api.import_so_nhap(b64(so_chinh)))
    rnd = random.Random(SEED + 1)
    lop = {}
    for h in sorted(hs, key=lambda x: x["student_id"]):
        lop[h["student_id"]] = rnd.choice(LOP)
        ok(api.set_student_class(h["student_id"], lop[h["student_id"]]))
    ok(api.tao_ma_tra_cuu(True))
    ma = ok(api.export_ma_tra_cuu_csv(os.path.join(thu_xuat, "ma.csv")))["path"]
    with open(ma, encoding="utf-8-sig") as f:
        ma_tra_cuu = list(csv.DictReader(f))
    for ten, mk, vai in TAI_KHOAN:                     # SAU dữ liệu: có tài khoản là cổng quyền bật
        ok(api.tao_tai_khoan(ten, mk, vai))
    ok(api.dang_xuat())
    return ma_tra_cuu


def kiem_kiosk(db_goc, thu_xuat, so_muon, ma_tra_cuu):
    """Trên BẢN SAO: đăng nhập sai/đúng, giáo viên bị chặn việc quản trị, chạy, nạp đến muộn, chạy lại, tra cứu."""
    d = tempfile.mkdtemp()
    db = os.path.join(d, "app.db")
    shutil.copy(db_goc, db)
    api = PipelineAPI(db, thu_muc_xuat=thu_xuat)
    kq = {}
    assert not api.run_pipeline(seed=SEED_XEP)["ok"], "chưa đăng nhập mà chạy được"
    kq["dang_nhap_sai"] = api.dang_nhap("quantri.demo", "sai-mat-khau")["errors"][0]["code"]
    ok(api.dang_nhap("gv.nguyen", "GiaoVien@01"))
    kq["giao_vien_bam_chay"] = api.run_pipeline(seed=SEED_XEP)["errors"][0]["code"]
    ok(api.get_data_health_report(), cho_canh_bao=True)
    ok(api.dang_xuat())
    ok(api.dang_nhap("quantri.demo", "Demo@2026"))
    suc_khoe = ok(api.get_data_health_report(), cho_canh_bao=True)["warnings"]
    la = [w for w in suc_khoe if w["code"] != "health_oversubscribed_buoi"]
    assert la == [], la
    kq["canh_bao_suc_khoe"] = sorted({w["code"] for w in suc_khoe})
    kq["lan_1"] = tom_tat(api, ok(api.run_pipeline(seed=SEED_XEP), cho_canh_bao=True))
    stb_1 = so_boc_tham(api)
    kq_1 = ket_qua(api)
    # Sau lần chạy đầu điểm quyết tâm bị KHOÁ: nạp sổ đến muộn lúc này thì phần điểm bị bỏ (`wharton_da_khoa`)
    # và lần chạy bị chặn. Quy trình đúng: mở khoá (gõ "MO") rồi mới nạp.
    ok(api.mo_khoa_wharton("MO"), cho_canh_bao=True)
    kq["canh_bao_nap_den_muon"] = sorted({w["code"] for w in ok(api.import_so_nhap(b64(so_muon)),
                                                                   cho_canh_bao=True).get("warnings") or []})
    r2 = api.run_pipeline(seed=SEED_XEP)
    assert r2["ok"], r2["errors"]
    kq["lan_2_sau_den_muon"] = tom_tat(api, r2["data"])
    stb_2 = so_boc_tham(api)
    giu = all(sorted(stb_1[b], key=stb_1[b].get) == sorted(stb_1[b], key=stb_2[b].get) for b in stb_1)
    assert giu, "thứ tự bốc thăm của em cũ bị đổi"
    kq["thu_tu_boc_tham_em_cu_giu_nguyen"] = giu
    kq_2 = ket_qua(api)
    kq["luot_cho_em_cu_doi_sau_den_muon"] = sum(1 for k in kq_1 if kq_1[k] != kq_2.get(k))   # đếm theo (em, buổi)
    kq["run_history"] = len(ok(api.get_run_history(), cho_canh_bao=True) or [])
    for ten, r in (("excel", api.export_ket_qua(os.path.join(thu_xuat, "kq.xlsx"))),
                   ("pdf_danh_sach", api.export_danh_sach_pdf(os.path.join(thu_xuat, "pdf"))),
                   ("pdf_bao_cao", api.export_bao_cao_tong_hop_pdf(os.path.join(thu_xuat, "bc.pdf")))):
        assert r["ok"], (ten, r["errors"])
    kq["xuat_duoc"] = ["excel", "pdf_danh_sach", "pdf_bao_cao"]
    ok(api.dang_xuat())
    em = ma_tra_cuu[0]                                 # chế độ học sinh: tra cứu đúng mã ra lời giải thích
    kq["tra_cuu_dung_ma"] = bool(ok(api.tra_cuu_hoc_sinh(em["student_id"], em["code"]), cho_canh_bao=True))
    sid = sorted(kq_1)[0][0]
    for _ in range(5):                                 # tra cứu: 5 lần sai cùng một mã thì khoá
        assert not api.tra_cuu_hoc_sinh(sid, "SAIMA000")["ok"]
    kq["tra_cuu_sai_5_lan"] = api.tra_cuu_hoc_sinh(sid, "SAIMA000")["errors"][0]["code"]
    return kq


def tom_tat(api, r):
    pb = ok(api.get_phan_bo_nguyen_vong(), cho_canh_bao=True)
    du_tru = ok(api.get_suat_du_tru(), cho_canh_bao=True)
    return {"em_co_it_nhat_1_clb": "%d/%d" % (r["n_matched"], r["n_total"]),
            "cho_da_xep_theo_hang_nguyen_vong": {str(x["hang"]) + ("+" if x["gop"] else ""): x["so_em"]
                                                 for x in pb["phan_bo"]},
            "tong_cho_da_xep": pb["tong_da_xep"],
            "suat_uu_tien_da_dung": sum(x["da_dung"] for x in du_tru)}


def so_boc_tham(api):
    d = ok(api.get_so_boc_tham_theo_buoi(), cho_canh_bao=True)
    return {b: {h["student_id"]: h["so"][b] for h in d["hoc_sinh"] if h["so"].get(b) is not None
                and not h["student_id"].startswith("MUON")} for b in d["ds_buoi"]}


def ket_qua(api):
    return {(r["student_id"], r["buoi"]): r["club_id"] for r in ok(api.get_match_results(), cho_canh_bao=True)
            if not r["student_id"].startswith("MUON")}


# --------------------------------------------------------------------------- CSDL cổng đăng ký
def tao_db_dang_ky(db, thu_xuat):
    api = PipelineAPI(db, thu_muc_xuat=thu_xuat)
    rnd = random.Random(SEED + 2)
    ok(api.dk_khoi_tao(DK_MK_QT, DK_MA_TRUONG, DK_BUOI, DK_KHOI))
    qt = ok(api.dk_dang_nhap("quan_tri", "", DK_MK_QT))["token"]
    for ten, sc in DK_PHONG:
        ok(api.dk_phong_luu(qt, ten, sc))
    phong = {r["ten"]: r["phong_id"] for r in ok(api.dk_phong_danh_sach(qt))}
    hs = []
    for i in range(DK_N_HS):
        lop = ["10A1", "10A2", "11A1", "11A2", "12A1"][i % 5]
        hs.append({"ma": "DK%03d" % (i + 1), "ten": ten_bia(rnd), "lop": lop, "khoi": int(lop[:2])})
    ok(api.dk_hs_nap_danh_sach(qt, "\n".join("%s\t%s\t%s" % (h["ma"], h["ten"], h["lop"]) for h in hs)))
    ok(api.dk_chuyen_giai_doan(qt, "gv_dang_ky"))
    for ten, pin in DK_GV:
        ok(api.dk_gv_tu_dang_ky(DK_MA_TRUONG, ten, pin))
    tk_gv = [ok(api.dk_dang_nhap("giao_vien", ten, pin))["token"] for ten, pin in DK_GV]
    ids = {}
    for ten, b, loai, ph, gv, ct, ds in DK_CLB:
        d = {"ten": ten, "buoi": DK_BUOI[b], "loai": loai, "phong_id": phong[DK_PHONG[ph][0]], "chi_tieu": ct,
             "khoi_tu": DK_KHOI[0], "khoi_den": DK_KHOI[1], "diem_san": ds,
             "mo_ta": "CLB mô phỏng cho buổi demo."}
        ids[ten] = ok(api.dk_clb_luu(tk_gv[gv], d))["clb_id"]
    qt = ok(api.dk_dang_nhap("quan_tri", "", DK_MK_QT))["token"]
    ok(api.dk_chuyen_giai_doan(qt, "duyet"))
    for cid in ids.values():
        ok(api.dk_clb_duyet(qt, cid, "duyet"))
    ok(api.dk_chuyen_giai_doan(qt, "hs_dang_ky"))
    pins = {h["ma"]: ok(api.dk_hs_dat_lai_pin(qt, h["ma"]))["pin"] for h in hs}
    diem, diem_sau = {}, {}
    for i, h in enumerate(hs):
        nv = []
        for b in range(len(DK_BUOI)):
            cac = [c for c in DK_CLB if c[1] == b]
            chon = rnd.sample(cac, rnd.randint(2, 4))
            for c in chon:
                thi = c[2] == "Tuyển chọn"
                nv.append({"clb_id": ids[c[0]], "thi": thi})
                if thi:
                    (diem if i < DK_N_HS - DK_N_CHUA_NOP else diem_sau).setdefault(c[0], []).append(
                        (h["ma"], round(rnd.uniform(3, 10), 1)))
        h["nv"] = nv
        if i < DK_N_HS - DK_N_CHUA_NOP:
            t = ok(api.dk_dang_nhap("hoc_sinh", h["ma"], pins[h["ma"]]))["token"]
            ok(api.dk_hs_luu(t, nv), cho_canh_bao=True)
            ok(api.dk_dang_xuat(t))
    qt = ok(api.dk_dang_nhap("quan_tri", "", DK_MK_QT))["token"]
    for c, ds in diem.items():
        r = ok(api.dk_diem_dan(qt, ids[c], "\n".join("%s\t%s" % x for x in ds)))
        assert r.get("loi", []) == [], r
    ok(api.dk_dang_xuat(qt))
    for ten, mk, vai in TAI_KHOAN:                     # cổng chính: cùng ba tài khoản như CSDL kiosk
        ok(api.tao_tai_khoan(ten, mk, vai))
    ok(api.dang_xuat())
    return hs, pins, diem_sau


def kiem_dang_ky(db_goc, thu_xuat, hs, pins):
    d = tempfile.mkdtemp()
    db = os.path.join(d, "app.db")
    shutil.copy(db_goc, db)
    api = PipelineAPI(db, thu_muc_xuat=thu_xuat)
    kq = {"giai_doan": ok(api.dk_trang_thai()).get("giai_doan")}
    em = hs[-1]                                        # một em CHƯA nộp: đăng nhập và nộp được
    t = ok(api.dk_dang_nhap("hoc_sinh", em["ma"], pins[em["ma"]]))["token"]
    ok(api.dk_hs_luu(t, em["nv"]), cho_canh_bao=True)
    for ten, pin in DK_GV:
        ok(api.dk_dang_nhap("giao_vien", ten, pin))
    assert not api.dk_dang_nhap("hoc_sinh", "DK001", "0000")["ok"]
    sai = "1357" if pins["DK002"] != "1357" else "1358"
    for _ in range(5):
        api.dk_dang_nhap("hoc_sinh", "DK002", sai)
    kq["khoa_sau_5_lan_sai"] = api.dk_dang_nhap("hoc_sinh", "DK002", pins["DK002"])["errors"][0]["code"]
    qt = ok(api.dk_dang_nhap("quan_tri", "", DK_MK_QT))["token"]
    kq["tien_do"] = ok(api.dk_tien_do(qt))
    return kq


# --------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ra", default=DAY)
    ns = ap.parse_args(argv)
    ra = os.path.abspath(ns.ra)
    os.makedirs(ra, exist_ok=True)
    tam = tempfile.mkdtemp()
    xuat = os.path.join(tam, "xuat")
    os.makedirs(xuat)

    clb, chinh, muon, so1, so2 = tao_so(tam)
    goc_ws = os.path.join(tam, "ws")
    slug_k = ws.tao(goc_ws, TEN_WS_KIOSK, None)        # cấu hình mặc định: trường học, điểm quyết tâm BẬT
    db_k = ws.duong_dan_db(goc_ws, slug_k)
    ma_tra_cuu = tao_db_kiosk(db_k, xuat, so1, chinh)
    kq_k = kiem_kiosk(db_k, xuat, so2, ma_tra_cuu)
    # Cổng đăng ký: tắt điểm quyết tâm tường minh (luật F1); «Chốt và xếp» tự bật luật cổng cần (`_dk_bao_dam_luat`).
    slug_d = ws.tao(goc_ws, TEN_WS_DANG_KY, {"rules": {"wharton": False}})
    db_d = ws.duong_dan_db(goc_ws, slug_d)
    dk_hs, pins, diem_sau = tao_db_dang_ky(db_d, xuat)
    kq_d = kiem_dang_ky(db_d, xuat, dk_hs, pins)

    for p in (so1, so2):
        shutil.copy(p, os.path.join(ra, os.path.basename(p)))
    for slug, db in ((slug_k, db_k), (slug_d, db_d)):
        for tep in os.listdir(os.path.dirname(db)):    # bản sao lưu lúc nạp không đi theo
            if tep != ws.TEN_DB:
                q = os.path.join(os.path.dirname(db), tep)
                shutil.rmtree(q) if os.path.isdir(q) else os.remove(q)
        ws.xuat_zip(goc_ws, slug, os.path.join(ra, slug + ".zip"))
    with open(os.path.join(ra, "TAI_KHOAN_DEMO.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["workspace", "cong", "vai", "ten_dang_nhap", "mat_khau_hoac_pin", "ghi_chu"])
        for db in (slug_k + ".zip", slug_d + ".zip"):
            for ten, mk, vai in TAI_KHOAN:
                w.writerow([db, "phan_mem_chinh", vai, ten, mk, NHAN])
        w.writerow([slug_d + ".zip", "cong_dang_ky", "quan_tri", "(bỏ trống)", DK_MK_QT,
                    "mã trường cho GV tự đăng ký: " + DK_MA_TRUONG])
        for ten, pin in DK_GV:
            w.writerow([slug_d + ".zip", "cong_dang_ky", "giao_vien", ten, pin, NHAN])
        n_nop = DK_N_HS - DK_N_CHUA_NOP
        for i, h in enumerate(dk_hs):
            w.writerow([slug_d + ".zip", "cong_dang_ky", "hoc_sinh", h["ma"], pins[h["ma"]],
                        "%s · %s · %s" % (h["ten"], h["lop"], "đã nộp" if i < n_nop else "CHƯA NỘP — dùng để demo trực tiếp")])
    with open(os.path.join(ra, "MA_TRA_CUU_DEMO.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(ma_tra_cuu[0]))
        w.writeheader()
        w.writerows(ma_tra_cuu)
    with open(os.path.join(ra, "DIEM_DAN_CONG_DANG_KY.txt"), "w", encoding="utf-8") as f:
        f.write("# %s\n# Điểm thi của các em CHƯA NỘP (DK051–DK060), nếu em nộp đúng như dữ liệu sinh sẵn.\n" % NHAN)
        f.write("# Bước Nhập điểm: chọn CLB, dán các dòng «mã<TAB>điểm» bên dưới tên CLB đó.\n")
        for c, ds in sorted(diem_sau.items()):
            f.write("\n[%s]\n" % c)
            f.writelines("%s\t%s\n" % x for x in ds)
    kiem = {"nhan": NHAN, "seed_du_lieu": SEED, "seed_xep": SEED_XEP, "kiosk": kq_k, "cong_dang_ky": kq_d,
            "workspace": [slug_k + ".zip", slug_d + ".zip"], "so_clb": len(clb), "so_hs": len(chinh), "so_den_muon": len(muon)}
    with open(os.path.join(ra, "KIEM_CHUNG.json"), "w", encoding="utf-8") as f:
        json.dump(kiem, f, ensure_ascii=False, indent=2, sort_keys=True, default=str)
    print(json.dumps(kiem, ensure_ascii=False, indent=2, default=str))
    shutil.rmtree(tam, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
