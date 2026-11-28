# -*- coding: utf-8 -*-
"""DG1-L2 — bộ sinh DỮ LIỆU MÔ PHỎNG cho bộ đo định lượng. Mọi số sinh ra là mô phỏng, không phải khảo sát thật.

Mô hình (tham số và seed đều in vào JSON, không có hằng số ẩn):

  * Độ nổi tiếng pop(CLB) tuyến tính 1 → 0, hoán vị ngẫu nhiên theo seed (một lần cho cả trường).
  * Hữu dụng u(em, CLB) = α·pop(CLB) + (1−α)·ε, ε ~ U(0,1) riêng từng cặp em–CLB.
    Danh sách = top L CLB theo hữu dụng, L ~ đều {3..6} (nối nguyên vọng Forms Top 1–10, bị cắt), trong MỖI buổi.
    α = 0: ai cũng muốn khác nhau; α → 1: ai cũng muốn cùng vài CLB.
  * Chỉ tiêu: tổng = round(κ·N), chia tỉ lệ (pop + 0,2)·U(0,8; 1,2) (sàn 0,2 để CLB ít người vẫn có chỗ), tối thiểu 2 chỗ/CLB.
  * ~30 % CLB là «tuyển chọn» (thi). Em tick thi mỗi CLB tuyển chọn trong danh sách với xác suất 0,85, tối đa 5 CLB mỗi buổi.
    Điểm = round(10·(ρ·năng_lực + (1−ρ)·nhiễu), 1); năng_lực U(0,1) riêng từng em, nhiễu U(0,1) riêng từng cặp em–CLB.
    ρ = 0: điểm không liên quan năng lực; ρ = 0,7: liên quan mạnh.
  * Diện dự trữ: `chinh_sach` ≈ 15 % số em, `khoi_10` ≈ 6 % số em (chọn trong khối 10). Suất dự trữ ≈ 10 % chỉ tiêu ở 4 CLB
    nổi tiếng nhất (xen kẽ chinh_sach / khoi_10), mỗi CLB một diện (như phần mềm).
  * Khối 10/11/12 chia đều (dùng để tách nhóm khi tính chỉ số).
  * Nhiều buổi: CLB chia luân phiên theo độ nổi tiếng vào các buổi thu_2, thu_4, thu_6.

Hạt giống: `seed` (seed DỮ LIỆU = một trường mô phỏng khác). Seed bốc thăm (STB) KHÔNG nằm ở đây — xem `do_danh_gia.py`.
Bộ sinh dùng `random.Random(crc32(khoá))`, không dùng `hash()` (khác nhau giữa các lần chạy).
"""

import os
import random
import sys
import zlib

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, GOC)

import rbda_priority_pipeline as loi  # noqa: E402

TY_LE_TUYEN_CHON = 0.30
XAC_SUAT_TICK_THI = 0.85
TRAN_THI_MOI_BUOI = 5
TY_LE_CHINH_SACH = 0.15
TY_LE_KHOI_10 = 0.06
TY_LE_SUAT_DU_TRU = 0.10
SO_CLB_DU_TRU = 4
SAN_POP = 0.2
DAI_DANH_SACH = (3, 6)
TEN_BUOI = ["thu_2", "thu_4", "thu_6"]


def _rng(*khoa):
    return random.Random(zlib.crc32("|".join(str(k) for k in khoa).encode("utf-8")))


def tham_so_sinh():
    """Mọi hằng của mô hình, để ghi vào JSON."""
    return {
        "ty_le_clb_tuyen_chon": TY_LE_TUYEN_CHON, "xac_suat_tick_thi": XAC_SUAT_TICK_THI,
        "tran_thi_moi_buoi": TRAN_THI_MOI_BUOI, "ty_le_chinh_sach": TY_LE_CHINH_SACH, "ty_le_khoi_10": TY_LE_KHOI_10,
        "ty_le_suat_du_tru": TY_LE_SUAT_DU_TRU, "so_clb_du_tru": SO_CLB_DU_TRU, "san_pop": SAN_POP,
        "dai_danh_sach": list(DAI_DANH_SACH), "nhieu_buoi": TEN_BUOI,
        "chia_chi_tieu": "(pop + san_pop) × U(0,8; 1,2), largest remainder, tối thiểu 2",
        "diem": "round(10·(rho·nang_luc + (1−rho)·nhieu), 1)", "hat_giong": "random.Random(crc32(khoá))",
    }


def _chia_chi_tieu(rng, pop, tong):
    ids = sorted(pop)
    w = {c: (pop[c] + SAN_POP) * rng.uniform(0.8, 1.2) for c in ids}
    tw = sum(w.values())
    ra = {c: int(w[c] / tw * tong) for c in ids}
    du = sorted(ids, key=lambda c: (-(w[c] / tw * tong - ra[c]), c))
    for c in du[: max(0, tong - sum(ra.values()))]:
        ra[c] += 1
    return {c: max(2, v) for c, v in ra.items()}


def sinh_truong(n_hs, n_clb, alpha=0.5, rho=0.7, kappa=1.1, seed=1, so_buoi=1):
    """Một trường mô phỏng. Cùng tham số + cùng seed → cùng dữ liệu từng byte."""
    khoa = (n_hs, n_clb, alpha, rho, kappa, seed, so_buoi)
    rng = _rng("truong", *khoa)
    cids = ["clb%02d" % (j + 1) for j in range(n_clb)]
    thu_hang = list(cids)
    rng.shuffle(thu_hang)                                    # thu_hang[0] = nổi tiếng nhất
    pop = {c: (1.0 - i / (n_clb - 1)) if n_clb > 1 else 1.0 for i, c in enumerate(thu_hang)}

    buoi_cua = {c: (TEN_BUOI[i % so_buoi] if so_buoi > 1 else loi.BUOI_MAC_DINH) for i, c in enumerate(thu_hang)}
    cap = _chia_chi_tieu(rng, pop, round(kappa * n_hs))

    n_tc = max(1, round(TY_LE_TUYEN_CHON * n_clb))
    tuyen_chon = set(rng.sample(cids, n_tc))

    n_du_tru = min(SO_CLB_DU_TRU, max(1, n_clb // 2))
    nhom_clb = {}
    for i, c in enumerate(thu_hang[:n_du_tru]):
        nhom_clb[c] = "chinh_sach" if i % 2 == 0 else "khoi_10"
    clubs = {}
    for c in cids:
        g = nhom_clb.get(c, "")
        res = min(cap[c], max(1, round(TY_LE_SUAT_DU_TRU * cap[c]))) if g else 0
        clubs[c] = {"capacity": cap[c], "reserve_capacity": res, "reserve_group": g, "buoi": buoi_cua[c]}

    sids = ["hs%04d" % (i + 1) for i in range(n_hs)]
    khoi = {s: str(10 + (i % 3)) for i, s in enumerate(rng.sample(sids, n_hs))}
    lop10 = [s for s in sids if khoi[s] == "10"]
    n_k10 = min(len(lop10), round(TY_LE_KHOI_10 * n_hs))
    khoi_10 = set(rng.sample(lop10, n_k10))
    rest = [s for s in sids if s not in khoi_10]
    chinh_sach = set(rng.sample(rest, min(len(rest), round(TY_LE_CHINH_SACH * n_hs))))
    students = {s: {"reserve_group": "khoi_10" if s in khoi_10 else ("chinh_sach" if s in chinh_sach else ""), "stb": None}
                for s in sids}

    ds_buoi = sorted({clubs[c]["buoi"] for c in cids}, key=lambda b: TEN_BUOI.index(b) if b in TEN_BUOI else 0)
    clb_buoi = {b: [c for c in cids if clubs[c]["buoi"] == b] for b in ds_buoi}
    tren, duoi = DAI_DANH_SACH
    nang_luc = {s: rng.random() for s in sids}
    preferences, dang_ky_thi, scores = {}, {c: [] for c in cids}, {c: {} for c in cids}
    for s in sids:
        ds = []
        for b in ds_buoi:
            cs_b = clb_buoi[b]
            u = {c: alpha * pop[c] + (1.0 - alpha) * rng.random() for c in cs_b}
            L = min(len(cs_b), rng.randint(tren, duoi))
            top = sorted(cs_b, key=lambda c: (-u[c], c))[:L]
            ds.extend(top)
            tick = 0
            for c in top:
                if c in tuyen_chon:
                    nhieu = rng.random()
                    if tick < TRAN_THI_MOI_BUOI and rng.random() < XAC_SUAT_TICK_THI:
                        tick += 1
                        d = round(10.0 * (rho * nang_luc[s] + (1.0 - rho) * nhieu), 1)
                        dang_ky_thi[c].append(s)
                        scores[c][s] = min(10.0, max(0.0, d))
        preferences[s] = ds
    for c in cids:
        dang_ky_thi[c] = sorted(dang_ky_thi[c])
    applicants = loi.hop_ung_vien(dang_ky_thi, preferences)
    return {
        "students": students, "clubs": clubs, "tested_scores": scores, "applicants": applicants,
        "preferences": preferences, "dang_ky_thi": dang_ky_thi, "khoi": khoi, "do_nho_tieng": pop,
        "tuyen_chon": sorted(tuyen_chon), "ds_buoi": ds_buoi,
        "tham_so": {"n_hs": n_hs, "n_clb": n_clb, "alpha": alpha, "rho": rho, "kappa": kappa, "seed": seed,
                    "so_buoi": so_buoi, "kappa_thuc": round(sum(cap.values()) / n_hs, 3)},
    }


def sinh_so_nhap(truong, duong_dan):
    """Ghi trường mô phỏng ra Sổ nhập .xlsx qua `so_nhap.ghi_so_nhap` (đúng đường người dùng thật đi)."""
    import so_nhap
    clubs = [{
        "club_id": c, "name": "CLB %s" % c[3:], "capacity": v["capacity"], "reserve_capacity": v["reserve_capacity"],
        "reserve_group": v["reserve_group"], "buoi": "" if v["buoi"] == loi.BUOI_MAC_DINH else v["buoi"],
    } for c, v in sorted(truong["clubs"].items())]
    students = []
    for s in sorted(truong["students"]):
        nv = []
        for c in truong["preferences"][s]:
            thi = s in truong["tested_scores"].get(c, {})
            nv.append({"club_id": c, "thi": thi, "diem": truong["tested_scores"][c][s] if thi else ""})
        students.append({"student_id": s, "name": "Học sinh %s" % s[2:], "reserve_group": truong["students"][s]["reserve_group"],
                         "class_id": None, "nv": nv})
    so_nhap.ghi_so_nhap(duong_dan, clubs, students)
    return duong_dan


def doc_qua_phan_mem(duong_xlsx, thu_muc_tam):
    """Nạp Sổ nhập bằng PipelineAPI thật (Wharton tắt, như các bộ đo cũ) và đọc lại đúng dạng `load_from_sqlite`."""
    import base64
    from api import PipelineAPI
    import cau_hinh_ws
    api = PipelineAPI(os.path.join(thu_muc_tam, "app.db"))
    cau_hinh_ws.ghi_cau_hinh(api.db_path, {"rules": {"wharton": False}})
    with open(duong_xlsx, "rb") as f:
        kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
    if not kq["ok"]:
        raise RuntimeError("nạp sổ nhập thất bại: %r" % (kq["errors"],))
    return api.db_path, loi.load_from_sqlite(api.db_path)


def cau_truc_chay(truong):
    """(students, clubs, tested_scores, applicants, preferences) đúng dạng `run_rbda` nhận."""
    return (truong["students"], truong["clubs"], truong["tested_scores"], truong["applicants"], truong["preferences"])
