# -*- coding: utf-8 -*-
"""DG1-L1 — chỉ số định lượng THUẦN của một lần phân bổ (không đọc CSDL, không import phần mềm).

Nhận cấu trúc dữ liệu giống `rbda_priority_pipeline.load_from_sqlite`:

    hoc_sinh   {sid: {"reserve_group": ...}}
    clb        {cid: {"capacity", "reserve_capacity", "reserve_group"}}
    nguyen_vong{sid: [cid, ...]}            danh sách đã sắp (phần tử đầu = nguyện vọng 1)
    ung_vien   {cid: [sid, ...]}            (không dùng trong tính, giữ để chữ ký khớp phần mềm)
    diem       {cid: {sid: điểm}}           điểm thi; CLB có ≥ 1 điểm là CLB «tuyển chọn»
    xep        {sid: cid | None}
    tang       {sid: "reserve" | "general"}  chỉ có với em đã được xếp
    du_tru_fn  (sid, cid) -> bool           em có thuộc diện dự trữ của CLB đó không

Mẫu số LUÔN được ghi trong tên khoá: `*_tat_ca` = chia cho mọi học sinh, `*_da_xep` = chia cho em được xếp.
Mọi phần trăm làm tròn 1 chữ số thập phân; không có số nào gõ tay.
"""

DINH_NGHIA = {
    "pct_nv1_tat_ca": {"ten": "Tỉ lệ được nguyện vọng 1", "cong_thuc": "#(em được xếp ở nguyện vọng 1) / #học sinh",
                       "mau_so": "mọi học sinh (kể cả danh sách rỗng, chưa được xếp)", "nhom": "A"},
    "pct_nv1_da_xep": {"ten": "Tỉ lệ nguyện vọng 1 trên em được xếp", "cong_thuc": "#(nguyện vọng 1) / #(em được xếp)",
                       "mau_so": "em được xếp", "nhom": "A"},
    "duong_cong_don": {"ten": "Đường cong tích luỹ", "cong_thuc": "phần tử k = #(em được xếp ở nguyện vọng ≤ k) / #học sinh, k = 1..K",
                       "mau_so": "mọi học sinh; K = độ dài danh sách dài nhất", "nhom": "A"},
    "hang_tb": {"ten": "Hạng nguyện vọng trung bình", "cong_thuc": "trung bình hạng (1 = nguyện vọng đầu) của em được xếp",
                "mau_so": "em được xếp", "nhom": "A"},
    "ngoai_danh_sach": {"ten": "Xếp ngoài danh sách", "cong_thuc": "#(em được xếp vào CLB không có trong danh sách của em); phải = 0",
                        "mau_so": "—", "nhom": "A"},
    "cap_chan": {"ten": "Cặp phá vỡ (blocking pair)", "cong_thuc": "số cặp (em, CLB) em thích hơn và CLB nhận em theo hàm lựa chọn thật; RB-DA phải = 0",
                 "mau_so": "—", "nhom": "A"},
    "pct_chua_xep": {"ten": "Tỉ lệ chưa được xếp", "cong_thuc": "#(em chưa được xếp) / #học sinh", "mau_so": "mọi học sinh", "nhom": "B"},
    "can_tren_ghep_cuc_dai": {"ten": "Cận trên: ghép cực đại", "cong_thuc": "kích thước ghép cực đại đồ thị (học sinh × CLB đã liệt kê, sức chứa CLB), BỎ QUA ưu tiên và ổn định",
                              "mau_so": "—", "nhom": "B"},
    "khong_the_tranh": {"ten": "Không thể tránh (do dữ liệu)", "cong_thuc": "#học sinh − cận trên", "mau_so": "—", "nhom": "B"},
    "gia_uu_tien_on_dinh": {"ten": "Cái giá của ưu tiên + ổn định", "cong_thuc": "cận trên − #(em được xếp)", "mau_so": "—", "nhom": "B"},
    "nguyen_nhan": {"ten": "Nguyên nhân chưa xếp (loại trừ nhau, theo thứ tự)",
                    "cong_thuc": "danh_sach_rong: danh sách rỗng; khong_diem: có ≥1 CLB tuyển chọn trong danh sách và em không có điểm ở CLB tuyển chọn nào đã khai; "
                                 "het_cho_uu_tien_cao_hon: còn lại (mọi CLB đã khai đều đầy người ưu tiên cao hơn)",
                    "mau_so": "em chưa được xếp", "nhom": "B"},
    "tong_chi_tieu_nho_hon_hs": {"ten": "Tổng chỉ tiêu < số học sinh", "cong_thuc": "Σ chỉ tiêu < #học sinh (cờ cho cả lần chạy)", "mau_so": "—", "nhom": "B"},
    "lech_cho": {"ten": "Lệch chỗ", "cong_thuc": "#(em chưa được xếp mà còn CLB em KHÔNG khai còn chỗ trống)", "mau_so": "tính trên số em, không phải số CLB", "nhom": "B"},
    "ty_le_lap_day": {"ten": "Tỉ lệ lấp đầy", "cong_thuc": "#(em được xếp) / Σ chỉ tiêu", "mau_so": "tổng chỉ tiêu", "nhom": "C"},
    "phan_vi_lap_day": {"ten": "Phân vị lấp đầy theo CLB", "cong_thuc": "min, p25, trung vị, max của (đã xếp / chỉ tiêu) trên các CLB; nội suy tuyến tính", "mau_so": "mỗi CLB", "nhom": "C"},
    "du_tru": {"ten": "Suất dự trữ", "cong_thuc": "đã dùng = #(em xếp với tầng 'reserve'); cung cấp = Σ reserve_capacity",
               "mau_so": "Σ reserve_capacity", "nhom": "C"},
    "ti_le_cau": {"ten": "Tỉ lệ cầu", "cong_thuc": "#(em xếp CLB này làm nguyện vọng 1) / chỉ tiêu CLB", "mau_so": "chỉ tiêu CLB", "nhom": "C"},
}


# ---------------------------------------------------------------------------
# Cận trên: ghép cực đại (đường tăng, không thư viện ngoài)
# ---------------------------------------------------------------------------

def ghep_cuc_dai(nguyen_vong, suc_chua):
    """Kích thước ghép cực đại: học sinh × CLB đã liệt kê, mỗi CLB nhận tối đa `suc_chua[cid]` em.

    Bỏ qua thứ tự ưu tiên của CLB và thứ tự nguyện vọng của em — đây là CẬN TRÊN của mọi cơ chế
    chỉ xếp em vào CLB em đã khai. Đường tăng bằng BFS (lặp, không đệ quy → an toàn với 2 000 em).
    """
    cho_tong = {cid: int(c) for cid, c in suc_chua.items() if int(c) > 0}
    cung = {sid: [c for c in dict.fromkeys(ds) if c in cho_tong] for sid, ds in nguyen_vong.items()}
    giu = {cid: [] for cid in cho_tong}       # CLB -> các em đang giữ
    cua = {}                                  # em -> CLB đang giữ
    so = 0
    for goc in sorted(cung):
        if not cung[goc]:
            continue
        cha = {goc: None}                     # em -> (em trước, CLB đã đi qua)
        hang = [goc]
        cuoi = None                           # CLB còn chỗ cuối đường
        i = 0
        while i < len(hang) and cuoi is None:
            s = hang[i]
            i += 1
            for c in cung[s]:
                if len(giu[c]) < cho_tong[c]:
                    cha[("clb", c)] = (s, None)
                    cuoi = c
                    break
                for t in giu[c]:
                    if t not in cha:
                        cha[t] = (s, c)
                        hang.append(t)
        if cuoi is None:
            continue
        # Lần ngược đường tăng: gán lại từng em.
        c = cuoi
        s = cha[("clb", c)][0]
        while True:
            c_cu = cua.get(s)
            if c_cu is not None:
                giu[c_cu].remove(s)
            giu[c].append(s)
            cua[s] = c
            if cha[s] is None:
                break
            s_truoc, c_qua = cha[s]
            s, c = s_truoc, c_qua
        so += 1
    return so


# ---------------------------------------------------------------------------
# Tiện ích số học (xác định, không phụ thuộc thư viện)
# ---------------------------------------------------------------------------

def _pct(tu, mau):
    return round(100.0 * tu / mau, 1) if mau else None


def phan_vi(gia_tri, q):
    """Phân vị q (0..1), nội suy tuyến tính giữa hai giá trị kề (như numpy mặc định)."""
    xs = sorted(gia_tri)
    if not xs:
        return None
    pos = q * (len(xs) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def trung_vi(gia_tri):
    return phan_vi(gia_tri, 0.5)


def _hang(nguyen_vong, xep):
    """{sid: hạng 1-based | None | 0}. 0 = được xếp vào CLB KHÔNG có trong danh sách của em."""
    ra = {}
    for sid, cid in xep.items():
        if cid is None:
            ra[sid] = None
        else:
            ds = nguyen_vong.get(sid, [])
            ra[sid] = ds.index(cid) + 1 if cid in ds else 0
    return ra


def _thong_ke_nhom(sids, hang, k_tren=3):
    n = len(sids)
    da = [hang[s] for s in sids if hang.get(s)]
    return {
        "n": n, "da_xep": sum(1 for s in sids if hang.get(s) is not None),
        "pct_da_xep": _pct(sum(1 for s in sids if hang.get(s) is not None), n),
        "pct_nv1": _pct(sum(1 for h in da if h == 1), n),
        "pct_top3": _pct(sum(1 for h in da if h <= k_tren), n),
    }


# ---------------------------------------------------------------------------
# Chỉ số một lần chạy
# ---------------------------------------------------------------------------

def tinh_chi_so(hoc_sinh, clb, nguyen_vong, ung_vien, diem, xep, tang, du_tru_fn, nhom=None, cap_chan=None):
    """Chỉ số A (nguyện vọng), B (chưa xếp, cận trên), C (chỉ tiêu) của MỘT lần chạy MỘT buổi.

    `nhom` = {tên nhóm: {sid: nhãn}} (vd "du_tru", "khoi"); thêm vào `a.theo_nhom`. Nhóm "tang" luôn có:
    Tầng 1 = em có điểm ở ≥ 1 CLB trong danh sách của em, Tầng 2 = còn lại.
    `cap_chan` = số cặp phá vỡ do bên gọi tính bằng `verify_stability` (None = không đo).
    """
    sids = sorted(hoc_sinh)
    n = len(sids)
    hang = _hang(nguyen_vong, {s: xep.get(s) for s in sids})
    da_xep = [s for s in sids if xep.get(s) is not None]
    hang_hop_le = [hang[s] for s in da_xep if hang[s]]
    k_max = max([len(nguyen_vong.get(s, [])) for s in sids] + [1])

    # --- A
    tang_hs = {}
    for s in sids:
        co_diem = any(s in diem.get(c, {}) for c in nguyen_vong.get(s, []))
        tang_hs[s] = "tang_1" if co_diem else "tang_2"
    theo_nhom = {}
    for ten, bang in [("tang", tang_hs)] + sorted((nhom or {}).items()):
        gom = {}
        for s in sids:
            gom.setdefault(str(bang.get(s, "?")), []).append(s)
        theo_nhom[ten] = {k: _thong_ke_nhom(v, hang) for k, v in sorted(gom.items())}
    a = {
        "n_hs": n, "n_da_xep": len(da_xep),
        "pct_nv1_tat_ca": _pct(sum(1 for h in hang_hop_le if h == 1), n),
        "pct_top2_tat_ca": _pct(sum(1 for h in hang_hop_le if h <= 2), n),
        "pct_top3_tat_ca": _pct(sum(1 for h in hang_hop_le if h <= 3), n),
        "pct_nv1_da_xep": _pct(sum(1 for h in hang_hop_le if h == 1), len(da_xep)),
        "pct_top3_da_xep": _pct(sum(1 for h in hang_hop_le if h <= 3), len(da_xep)),
        "duong_cong_don": [_pct(sum(1 for h in hang_hop_le if h <= k), n) for k in range(1, k_max + 1)],
        "hang_tb": round(sum(hang_hop_le) / len(hang_hop_le), 3) if hang_hop_le else None,
        "hang_trung_vi": trung_vi(hang_hop_le),
        "ngoai_danh_sach": sum(1 for s in da_xep if hang[s] == 0),
        "theo_nhom": theo_nhom,
        "cap_chan": cap_chan,
    }

    # --- B
    suc_chua = {c: v["capacity"] for c, v in clb.items()}
    can = ghep_cuc_dai(nguyen_vong, suc_chua)
    chua = [s for s in sids if xep.get(s) is None]
    dem = {c: 0 for c in clb}
    for s in da_xep:
        if xep[s] in dem:
            dem[xep[s]] += 1
    con_cho = {c for c in clb if dem[c] < clb[c]["capacity"]}
    ts = {c for c, d in diem.items() if d}        # CLB tuyển chọn
    nn = {"danh_sach_rong": 0, "khong_diem": 0, "het_cho_uu_tien_cao_hon": 0}
    lech = 0
    for s in chua:
        ds = nguyen_vong.get(s, [])
        if not ds:
            nn["danh_sach_rong"] += 1
        else:
            thi = [c for c in ds if c in ts]
            if thi and not any(s in diem.get(c, {}) for c in thi):
                nn["khong_diem"] += 1
            else:
                nn["het_cho_uu_tien_cao_hon"] += 1
        if any(c not in ds for c in con_cho):
            lech += 1
    b = {
        "n_chua_xep": len(chua), "pct_chua_xep": _pct(len(chua), n),
        "can_tren_ghep_cuc_dai": can,
        "khong_the_tranh": n - can,
        "gia_uu_tien_on_dinh": can - len(da_xep),
        "nguyen_nhan": nn,
        "tong_chi_tieu_nho_hon_hs": sum(suc_chua.values()) < n,
        "lech_cho": lech,
    }

    # --- C
    nv1 = {c: 0 for c in clb}
    for s in sids:
        ds = nguyen_vong.get(s, [])
        if ds and ds[0] in nv1:
            nv1[ds[0]] += 1
    theo_clb = []
    for c in sorted(clb):
        cap = clb[c]["capacity"]
        theo_clb.append({
            "club_id": c, "capacity": cap, "da_xep": dem[c], "nv1": nv1[c],
            "lap_day": round(dem[c] / cap, 3) if cap else None,
            "ti_le_cau": round(nv1[c] / cap, 3) if cap else None,
        })
    ld = [x["lap_day"] for x in theo_clb if x["lap_day"] is not None]
    cung_cap = sum(v["reserve_capacity"] for v in clb.values())
    da_dung = sum(1 for s in da_xep if tang.get(s) == "reserve")
    qua_du_tru = qua_thuong = 0
    for s in da_xep:
        if xep[s] in clb and du_tru_fn(s, xep[s]):
            if tang.get(s) == "reserve":
                qua_du_tru += 1
            else:
                qua_thuong += 1
    tong_cap = sum(suc_chua.values())
    c = {
        "ty_le_lap_day": _pct(len(da_xep), tong_cap),
        "phan_vi_lap_day": {"min": min(ld), "p25": phan_vi(ld, 0.25), "median": phan_vi(ld, 0.5), "max": max(ld)} if ld else None,
        "n_clb_day": sum(1 for x in theo_clb if x["capacity"] and dem[x["club_id"]] >= x["capacity"]),
        "n_clb_duoi_50": sum(1 for v in ld if v < 0.5),
        "du_tru_cung_cap": cung_cap, "du_tru_da_dung": da_dung,
        "du_tru_dien_qua_du_tru": qua_du_tru, "du_tru_dien_qua_thuong": qua_thuong,
        "theo_clb": theo_clb,
    }
    return {"a": a, "b": b, "c": c}


def tong_hop_theo_hoc_sinh(xep_theo_buoi, nv_theo_buoi):
    """Chỉ số THEO HỌC SINH qua mọi buổi. `xep_theo_buoi` {buoi: {sid: cid|None}}, `nv_theo_buoi` {buoi: {sid: [cid]}}.

    `pct_du_moi_buoi_da_khai` = % em có chỗ ở MỌI buổi mà em đã khai ≥ 1 CLB (mẫu số: em có khai ít nhất một buổi).
    """
    sids = sorted({s for b in xep_theo_buoi.values() for s in b})
    tong_co_cho = 0
    du = khong_cho = co_khai = 0
    for s in sids:
        khai = [b for b in xep_theo_buoi if nv_theo_buoi.get(b, {}).get(s)]
        co = [b for b in xep_theo_buoi if xep_theo_buoi[b].get(s) is not None]
        tong_co_cho += len(co)
        if khai:
            co_khai += 1
            if all(xep_theo_buoi[b].get(s) is not None for b in khai):
                du += 1
        if not co:
            khong_cho += 1
    return {
        "n_hs": len(sids),
        "so_buoi_co_cho_tb": round(tong_co_cho / len(sids), 3) if sids else None,
        "pct_du_moi_buoi_da_khai": _pct(du, co_khai),
        "pct_khong_co_cho_nao": _pct(khong_cho, len(sids)),
    }
