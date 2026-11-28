"""CT1 — "Xem xét chỉ tiêu": phần THUẦN (không đọc/ghi CSDL, không import gói giải).

Ba việc: (1) chỉ số từng CLB từ kết quả xếp và nguyện vọng thật; (2) luật đề xuất chỉ tiêu kỳ sau, giữ nguyên
tổng chỗ; (3) ghép các chênh lệch thành các bước "chuyển k chỗ từ A sang B" (mỗi bước trung hoà tổng).
Chỉ ĐỌC thứ hạng nguyện vọng để BÁO CÁO nhu cầu của CLB; không có đường nào đưa thứ hạng này vào
`compute_club_priority` (bất biến 2): hàm ở đây chỉ trả số đếm và đề xuất, không ảnh hưởng thuật toán xếp.

Luật (đo bằng mô phỏng, DỮ LIỆU MÔ PHỎNG, `du_lieu_test/ct1_mo_phong/`):
  mục tiêu_c = round(T · nv1_c / N)  (T = tổng chỗ, N = số em có nguyện vọng trong buổi);
  chỉ TĂNG khi `chua_dap_c ≥ 1`; kẹp trong [cap·(1−tran), cap·(1+tran)] và không dưới `toi_thieu`
  (không bao giờ ép một CLB lên trên chỗ hiện tại chỉ vì tối thiểu); cân ±1 để Σ cap_moi == T.
Mọi con số theo TỪNG BUỔI (chỗ chỉ chuyển giữa các CLB cùng buổi).

Dạng dữ liệu:
  `clubs`/`chi_so`: {club_id: {"cap", "nv1", "chua_dap", "buoi", "loai_tru", "reserve_capacity"}}
  `prefs`: {(student_id, buoi): [club_id theo thứ tự nguyện vọng TRONG buổi]}
  `gan`  : {(student_id, buoi): club_id | None}
"""

TRAN_MAC_DINH = 0.20       # mỗi CLB đổi tối đa ±20 % chỗ mỗi kỳ
TOI_THIEU_MAC_DINH = 8     # quy mô tối thiểu của một CLB (không bao giờ cao hơn chỗ hiện tại)
TOI_DA_BUOC = 20           # số bước tự chọn tối đa trong một lần thử


def chi_so_clb_ct1(clubs: dict, prefs: dict, gan: dict) -> dict:
    """Chỉ số từng CLB: `cap`, `buoi`, `loai_tru`, `reserve_capacity`, `nv1` (em xếp CLB này đầu danh sách buổi),
    `chua_dap` (em xếp CLB này CAO HƠN CLB đã nhận; chưa có CLB = dưới mọi CLB trong danh sách), `da_nhan`, `trong`."""
    ra = {}
    for cid, c in clubs.items():
        ra[cid] = {"cap": c.get("cap") or 0, "buoi": c.get("buoi"), "loai_tru": bool(c.get("loai_tru")),
                   "reserve_capacity": c.get("reserve_capacity") or 0, "nv1": 0, "chua_dap": 0, "da_nhan": 0}
    for khoa, ds in prefs.items():
        ds = [c for c in ds if c in ra]
        if not ds:
            continue
        ra[ds[0]]["nv1"] += 1
        nhan = gan.get(khoa)
        if nhan in ds:
            ds_cao = ds[:ds.index(nhan)]
        else:
            ds_cao = ds                                   # chưa có CLB: mọi CLB trong danh sách đều "muốn mà chưa được"
        for c in ds_cao:
            ra[c]["chua_dap"] += 1
    for nhan in gan.values():
        if nhan in ra:
            ra[nhan]["da_nhan"] += 1
    for v in ra.values():
        v["trong"] = max(0, v["cap"] - v["da_nhan"])
    return ra


def hang_ket_qua(prefs: dict, gan: dict) -> dict:
    """{(em, buổi): hạng CLB đã nhận trong danh sách buổi (1 = thích nhất); chưa có CLB = độ dài danh sách + 1}."""
    ra = {}
    for khoa, ds in prefs.items():
        nhan = gan.get(khoa)
        ra[khoa] = ds.index(nhan) + 1 if nhan in ds else len(ds) + 1
    return ra


def thong_ke_ket_qua(prefs: dict, gan: dict) -> dict:
    """`{tong, nv1, chua_co}`: số (em, buổi), số em vào đúng CLB thích nhất, số em chưa có CLB."""
    h = hang_ket_qua(prefs, gan)
    return {"tong": len(h),
            "nv1": sum(1 for v in h.values() if v == 1),
            "chua_co": sum(1 for k in h if gan.get(k) is None)}


def _theo_buoi(chi_so: dict) -> dict:
    nhom = {}
    for cid in sorted(chi_so):
        v = chi_so[cid]
        if v.get("loai_tru") or not (v.get("cap") or 0) >= 1:
            continue
        nhom.setdefault(v.get("buoi"), []).append(cid)
    return {b: nhom[b] for b in sorted(nhom, key=lambda x: "" if x is None else str(x))}


def _can_mot_buoi(chi_so: dict, ds: list, tran: float, toi_thieu: int) -> dict:
    cap = {c: chi_so[c]["cap"] for c in ds}
    T = sum(cap.values())
    N = sum(chi_so[c]["nv1"] for c in ds)
    if N <= 0:
        return dict(cap)
    thap = {c: min(cap[c], max(toi_thieu, round(cap[c] * (1 - tran)), chi_so[c].get("reserve_capacity") or 0))
            for c in ds}                                  # không bớt xuống dưới chỗ giữ cho nhóm dự trữ
    cao = {c: max(cap[c], round(cap[c] * (1 + tran))) for c in ds}
    moi = {}
    for c in ds:
        muc = round(T * chi_so[c]["nv1"] / N)
        x = muc if (muc < cap[c] or chi_so[c]["chua_dap"] >= 1) else cap[c]
        moi[c] = min(max(x, thap[c]), cao[c])
    uu = {c: chi_so[c]["chua_dap"] / cap[c] for c in ds}
    thu_tu_tang = sorted(ds, key=lambda c: (-uu[c], c))
    thu_tu_giam = sorted(ds, key=lambda c: (uu[c], c))
    while sum(moi.values()) < T:
        c = next((c for c in thu_tu_tang
                  if moi[c] < cao[c] and (chi_so[c]["chua_dap"] >= 1 or moi[c] < cap[c])), None)
        if c is None:                                     # không xảy ra (Σ thấp ⇒ còn CLB bị bớt), giữ cho chắc
            break
        moi[c] += 1
    while sum(moi.values()) > T:
        c = next((c for c in thu_tu_giam if moi[c] > thap[c]), None)
        if c is None:
            break
        moi[c] -= 1
    return moi


def khuyen_nghi_chi_tieu(chi_so: dict, tran: float = TRAN_MAC_DINH, toi_thieu: int = TOI_THIEU_MAC_DINH) -> dict:
    """`{club_id: chỉ tiêu mới}` cho MỌI CLB trong `chi_so` (CLB loại trừ / không có chỗ giữ nguyên). Σ theo buổi giữ nguyên."""
    moi = {c: v.get("cap") or 0 for c, v in chi_so.items()}
    for ds in _theo_buoi(chi_so).values():
        moi.update(_can_mot_buoi(chi_so, ds, tran, toi_thieu))
    return moi


def ghep_buoc_chuyen(chi_so: dict, cap_moi: dict) -> list:
    """Danh sách `(từ, đến, k)`: ghép tham lam bên bớt chỗ với bên thêm chỗ, chênh lệch lớn nhất trước.

    Hoà: bên nhận ưu tiên "chưa đáp ứng trên chỗ" cao hơn rồi mã CLB; bên cho ưu tiên "chưa đáp ứng trên chỗ" thấp
    hơn rồi mã CLB. Mỗi bước trung hoà tổng; chỗ chỉ chuyển giữa các CLB cùng buổi."""
    ra = []
    for ds in _theo_buoi(chi_so).values():
        delta = {c: cap_moi.get(c, chi_so[c]["cap"]) - chi_so[c]["cap"] for c in ds}
        uu = {c: chi_so[c]["chua_dap"] / chi_so[c]["cap"] for c in ds}
        cho = {c: -d for c, d in delta.items() if d < 0}
        nhan = {c: d for c, d in delta.items() if d > 0}
        while cho and nhan:
            a = min(cho, key=lambda c: (-cho[c], uu[c], c))
            b = min(nhan, key=lambda c: (-nhan[c], -uu[c], c))
            k = min(cho[a], nhan[b])
            ra.append((a, b, k))
            cho[a] -= k
            nhan[b] -= k
            if cho[a] == 0:
                del cho[a]
            if nhan[b] == 0:
                del nhan[b]
    return ra


def kiem_buoc_tu_chon(buoc, clubs: dict):
    """Kiểm các bước tự chọn `[{"tu", "den", "k"}]`. Trả `([(từ, đến, k)], None)` hoặc `(None, {"code", "params"})`.

    Từ chối: không phải danh sách / sai dạng, quá `TOI_DA_BUOC` bước, CLB lạ hoặc CLB loại trừ (tự do), từ == đến,
    k không phải số nguyên ≥ 1; kiểm CỘNG DỒN: chỗ sau mỗi bước không dưới 1 và không dưới chỗ giữ dự trữ."""
    def loi(ma, **p):
        return None, {"code": ma, "params": p}

    if not isinstance(buoc, (list, tuple)):
        return loi("ct1_buoc_khong_hop_le")
    if len(buoc) > TOI_DA_BUOC:
        return loi("ct1_qua_nhieu_buoc", toi_da=TOI_DA_BUOC)
    cap = {c: v.get("cap") or 0 for c, v in clubs.items()}
    ra = []
    for b in buoc:
        if not isinstance(b, dict) or not {"tu", "den", "k"} <= set(b):
            return loi("ct1_buoc_khong_hop_le")
        tu, den, k = b["tu"], b["den"], b["k"]
        if isinstance(k, bool) or not isinstance(k, int) or k < 1 or tu == den:
            return loi("ct1_buoc_khong_hop_le")
        for c in (tu, den):
            if not isinstance(c, str) or c not in clubs or clubs[c].get("loai_tru"):
                return loi("ct1_clb_la", club_id=str(c))
        if clubs[tu].get("buoi") != clubs[den].get("buoi"):
            return loi("ct1_khac_buoi", tu=tu, den=den)     # chỗ chỉ chuyển giữa hai CLB CÙNG buổi
        cap[tu] -= k
        cap[den] += k
        san = max(1, clubs[tu].get("reserve_capacity") or 0)
        if cap[tu] < san:
            return loi("ct1_cap_qua_thap", club_id=tu, con_lai=cap[tu], toi_thieu=san)
        ra.append((tu, den, k))
    return ra, None
