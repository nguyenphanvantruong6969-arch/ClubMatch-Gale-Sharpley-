# -*- coding: utf-8 -*-
"""DC1 — kiểm ĐỘC LẬP đầu vào ⇄ kết quả (phạm vi B: chỉ kiểm bảo toàn).

Chỉ dùng thư viện chuẩn của Python và openpyxl; không import mô-đun nào của phần mềm.
Đọc: Sổ nhập (.xlsx) và bộ tệp xuất CSV mặc định (`ket_qua_phan_bo.csv`,
`ket_qua_phan_bo_theo_club/`, `ket_qua_phan_bo_tong_hop.csv`).
Ghi: bảng PASS/FAIL ra màn hình và `dau_vao_ket_qua.csv` (mỗi học sinh một dòng).

    python kiem_doc_lap.py --so-nhap SO_NHAP.xlsx --ket-qua ket_qua_phan_bo.csv [--ra dau_vao_ket_qua.csv]

Mã thoát: 0 = mọi phép kiểm PASS; 1 = có FAIL; 2 = đầu vào không đọc được / chưa hỗ trợ.
Chỉ in dữ kiện và PASS/FAIL. Mọi số liệu trong bộ mẫu là dữ liệu MÔ PHỎNG.
"""
import argparse
import csv
import os
import re
import sys
import unicodedata

import openpyxl

DIEN_THUONG, DIEN_DU_TRU = "Thường", "Dự trữ"
CHUA_XEP = "_chua_duoc_xep.csv"
CHAN_DAU = ("=", "+", "-", "@", "\t", "\r")
CHU_THICH = (
    "Phạm vi B: chỉ kiểm bảo toàn. KHÔNG kiểm đúng luật ưu tiên / ổn định: CLB có hai quỹ chỗ "
    "(dự trữ rồi chung), phép thử 'CLB đầy và người nhận cuối kém hơn tôi' sẽ báo sai cho em nhận "
    "bằng quỹ dự trữ."
)


class DauVaoKhongDung(Exception):
    """Đầu vào không đọc được hoặc ngoài phạm vi hỗ trợ -> mã thoát 2."""


# ------------------------------------------------------------------ tiện ích ----

def khoa_ten(s):
    """Tên CLB để so khớp: NFC + casefold + gộp khoảng trắng."""
    return " ".join(unicodedata.normalize("NFC", str(s or "")).casefold().split())


def khoa_nhom(s):
    """'Chính sách' / 'CHINH-SACH' -> 'chinh_sach' (cùng luật với phần mềm khi nạp nhóm)."""
    chu = str(s or "").strip().replace("Đ", "D").replace("đ", "d")
    chu = "".join(c for c in unicodedata.normalize("NFD", chu) if not unicodedata.combining(c))
    return re.sub(r"[^0-9a-zA-Z]+", "_", chu.lower()).strip("_")


def doc_diem(o):
    """Ô điểm -> float hoặc None. Nhận '8,5' (đúng một dấu phẩy, không dấu chấm)."""
    chu = str(o if o is not None else "").strip()
    if chu.count(",") == 1 and "." not in chu:
        chu = chu.replace(",", ".")
    try:
        so = float(chu)
    except ValueError:
        return None
    return so if so == so and abs(so) != float("inf") else None


def so_nguyen(o):
    d = doc_diem(o)
    return int(d) if d is not None and d == int(d) else None


def go_nhay(o):
    """Hoàn tác đúng một việc: dấu ' phần mềm thêm trước ô bắt đầu bằng = + - @ (chống công thức)."""
    return o[1:] if o[:1] == "'" and o[1:2] in CHAN_DAU else o


def doc_csv(duong):
    try:
        with open(duong, encoding="utf-8-sig", newline="") as f:
            return [[go_nhay(o) for o in dong] for dong in csv.reader(f)]
    except OSError as e:
        raise DauVaoKhongDung(f"không đọc được {duong}: {e.strerror}")


def vai(ids, toi_da=5):
    ids = sorted(set(ids), key=str)
    return ", ".join(map(str, ids[:toi_da])) + (f" (+{len(ids) - toi_da})" if len(ids) > toi_da else "")


# ------------------------------------------------------------------- Sổ nhập ----

def _o(row, i):
    return row[i] if i < len(row) else None


def _tim_sheet(wb, so):
    for ten in wb.sheetnames:
        if ten.strip().startswith(f"{so}."):
            return wb[ten]
    if len(wb.sheetnames) >= so:
        return wb[wb.sheetnames[so - 1]]
    raise DauVaoKhongDung("Sổ nhập thiếu trang CLB hoặc trang học sinh")


def doc_so_nhap(duong):
    """-> (clubs, hs). clubs: list dict(ten, buoi, chi_tieu, du_tru, nhom, ma);
    hs: list dict(id, ten, nhom, nv=[(tên CLB thô, điểm thô)])."""
    try:
        wb = openpyxl.load_workbook(duong, data_only=True)
    except Exception as e:
        raise DauVaoKhongDung(f"không đọc được Sổ nhập {duong}: {e}")
    clubs = []
    for r in _tim_sheet(wb, 1).iter_rows(min_row=2, values_only=True):
        if str(_o(r, 0) or "").strip():
            clubs.append({"ten": str(r[0]).strip(), "buoi": str(_o(r, 1) or "").strip(),
                          "chi_tieu": so_nguyen(_o(r, 2)), "du_tru": so_nguyen(_o(r, 3)) or 0,
                          "nhom": khoa_nhom(_o(r, 4)), "ma": str(_o(r, 5) or "").strip()})
    hang = list(_tim_sheet(wb, 2).iter_rows(values_only=True))
    if len(hang) < 2:
        raise DauVaoKhongDung("trang học sinh trống")
    cot_clb, cot_diem = {}, {}
    if str(_o(hang[0], 3) or "").strip().casefold().startswith("nguyện vọng"):   # hai dòng tiêu đề
        dau, k = 2, None
        for c in range(3, len(hang[0])):
            m = re.match(r"nguyện vọng\s*(\d+)", str(hang[0][c] or "").strip().casefold())
            if m:
                k, moi = int(m.group(1)), True
            else:
                moi = False
            con = str(_o(hang[1], c) or "").strip().casefold()
            if k is not None and moi:
                cot_clb[k] = c
            elif k is not None and con.startswith("điểm") and "quyết tâm" not in con:
                cot_diem[k] = c
    else:                                                                       # một dòng tiêu đề
        dau = 1
        for c in range(3, len(hang[0])):
            h = str(hang[0][c] or "").strip().casefold()
            m = re.fullmatch(r"nv\s*(\d+)", h)
            if m:
                cot_clb[int(m.group(1))] = c
            m = re.fullmatch(r"điểm\s*(\d+)", h)
            if m:
                cot_diem[int(m.group(1))] = c
    if not cot_clb:
        raise DauVaoKhongDung("không thấy cột nguyện vọng trong Sổ nhập")
    hs = []
    for r in hang[dau:]:
        sid = str(_o(r, 0) or "").strip()
        if not sid:
            continue
        nv = []
        for k in sorted(cot_clb):
            ten = str(_o(r, cot_clb[k]) or "").strip()
            if ten:
                nv.append((ten, _o(r, cot_diem[k]) if k in cot_diem else None))
        hs.append({"id": sid, "ten": str(_o(r, 1) or "").strip(),
                   "nhom": khoa_nhom(_o(r, 2)), "nv": nv})
    return clubs, hs


# ------------------------------------------------------------------- kết quả ----

def doc_ket_qua(duong):
    """-> list dict(sid, ten, clb, ten_clb, nv, dien, nhom). Chỉ hỗ trợ tệp 8 cột (một buổi)."""
    d = doc_csv(duong)
    if not d:
        raise DauVaoKhongDung("tệp kết quả trống")
    if len(d[0]) != 8:
        raise DauVaoKhongDung(
            f"tệp kết quả có {len(d[0])} cột: nhiều buổi: chưa hỗ trợ, xem DC1 giới hạn"
            if len(d[0]) == 9 else f"tệp kết quả có {len(d[0])} cột, cần 8")
    return [{"sid": r[0].strip(), "ten": r[1], "clb": r[3].strip(), "ten_clb": r[4],
             "nv": r[5].strip(), "dien": r[6].strip(), "nhom": khoa_nhom(r[7])}
            for r in d[1:] if len(r) >= 8 and any(o.strip() for o in r)]


def doc_tep_theo_clb(thu_muc):
    """-> {tên tệp: set((sid, nv, dien, nhom))}; None nếu không có thư mục."""
    if not os.path.isdir(thu_muc):
        return None
    ra = {}
    for ten in sorted(os.listdir(thu_muc)):
        if ten.lower().endswith(".csv"):
            d = doc_csv(os.path.join(thu_muc, ten))
            ra[ten] = [(r[0].strip(), r[3].strip(), r[4].strip(), khoa_nhom(r[5]))
                       for r in d[1:] if len(r) >= 6 and r[0].strip()]
    return ra


def doc_tong_hop(duong):
    """Mục 'TỪNG ...' của `_tong_hop.csv` -> list (mã, tên, đã xếp, dự trữ); None nếu không có tệp/mục."""
    if not os.path.isfile(duong):
        return None
    d = doc_csv(duong)
    for i, r in enumerate(d):
        if r and r[0].startswith("TỪNG ") and i + 1 < len(d):
            tieu = [o.strip() for o in d[i + 1]]
            if "Đã xếp" not in tieu or "Trong đó diện dự trữ" not in tieu:
                return None
            x, t = tieu.index("Đã xếp"), tieu.index("Trong đó diện dự trữ")
            ra = []
            for r2 in d[i + 2:]:
                if not any(o.strip() for o in r2):
                    break
                ra.append((r2[1].strip(), r2[2].strip(), so_nguyen(r2[x]), so_nguyen(r2[t])))
            return ra
    return None


# ------------------------------------------------------------------- đối chiếu ----

class DoiChieu:
    def __init__(self, clubs, hs, kq, tep_clb, tong_hop=None):
        self.clubs, self.hs, self.kq, self.tep_clb = clubs, hs, kq, tep_clb
        self.tong_hop = tong_hop
        self.theo_ma = {c["ma"]: c for c in clubs if c["ma"]}
        theo_ten = {}
        for c in clubs:
            theo_ten.setdefault(khoa_ten(c["ten"]), []).append(c)
        self.theo_ten = {k: v[0] for k, v in theo_ten.items() if len(v) == 1}
        self.hs_theo_id = {h["id"]: h for h in hs}
        self.clb_cua_dong = [self._ghep(r) for r in kq]
        # G2 (đo trên 3 bộ): em không còn nguyện vọng nào VẪN có một dòng (chưa xếp) trong kết quả; Sổ nhập có
        # CLB lạ hoặc CLB lặp trong một dòng bị từ chối nguyên sổ, nên thứ hạng = vị trí trong danh sách đã bỏ trùng.
        # Sổ nhập: nguyện vọng hợp lệ = tên khớp một CLB; bỏ trùng, giữ thứ tự (luật nạp của phần mềm).
        self.nv_hop_le = {}
        for h in hs:
            ds = []
            for ten, _ in h["nv"]:
                c = self.theo_ten.get(khoa_ten(ten))
                if c is not None and id(c) not in [id(x) for x in ds]:
                    ds.append(c)
            self.nv_hop_le[h["id"]] = ds

    def _ghep(self, r):
        if not r["clb"]:
            return None
        return self.theo_ma.get(r["clb"]) or self.theo_ten.get(khoa_ten(r["ten_clb"]))

    def kiem(self):
        return [self.k0(), self.k1(), self.k2(), self.k3(), self.k4(), self.k5(), self.k6(), self.k7()]

    def _dong_xep(self):
        """(dòng, CLB) của các dòng đã xếp và đối chiếu được."""
        return [(r, c) for r, c in zip(self.kq, self.clb_cua_dong) if r["clb"] and c is not None]

    @staticmethod
    def _kq(ma, loi, ok_text, fail_text):
        return (ma, "FAIL" if loi else "PASS", f"{fail_text}: {loi}" if loi else ok_text)

    def k0(self):
        la = sorted({r["clb"] for r, c in zip(self.kq, self.clb_cua_dong) if r["clb"] and c is None})
        buoi = {c["buoi"] for c in self.clubs if c["buoi"]}
        if len(buoi) > 1:
            raise DauVaoKhongDung("Sổ nhập có nhiều buổi: nhiều buổi: chưa hỗ trợ, xem DC1 giới hạn")
        if la:
            return ("K0", "FAIL", f"không đối chiếu được {len(la)} CLB của kết quả với Sổ nhập: {vai(la)}")
        return ("K0", "PASS", f"đọc được cả hai tệp, một buổi, {len(self.clubs)} CLB đều khớp")

    def k1(self):
        dem = {}
        for r in self.kq:
            dem[r["sid"]] = dem.get(r["sid"], 0) + 1
        thieu = [i for i in self.hs_theo_id if i not in dem]
        la = [i for i in dem if i not in self.hs_theo_id]
        lap = [i for i, n in dem.items() if n > 1]
        loi = "; ".join(f"{ten} {len(ds)}: {vai(ds)}" for ten, ds in
                        (("thiếu", thieu), ("lạ", la), ("lặp", lap)) if ds)
        return self._kq("K1", loi, f"{len(self.hs)} học sinh, mỗi em đúng một dòng", "không khớp danh sách")

    def k2(self):
        dem, loi, bo = {}, [], 0
        for _, c in self._dong_xep():
            dem[c["ten"]] = dem.get(c["ten"], 0) + 1
        for c in self.clubs:
            if not c["chi_tieu"]:
                bo += 1
            elif dem.get(c["ten"], 0) > c["chi_tieu"]:
                loi.append(f"{c['ten']} {dem[c['ten']]}>{c['chi_tieu']}")
        ghi_chu = f"; bỏ qua {bo} CLB không có chỉ tiêu" if bo else ""
        return self._kq("K2", vai(loi), f"mọi CLB có số xếp ≤ chỉ tiêu{ghi_chu}", "vượt chỉ tiêu")

    def k3(self):
        loi, dem = [], {}
        for r, c in self._dong_xep():
            if r["dien"] not in (DIEN_THUONG, DIEN_DU_TRU):
                loi.append(f"{r['sid']} diện '{r['dien']}'")
            if r["dien"] == DIEN_DU_TRU:
                dem[c["ten"]] = dem.get(c["ten"], 0) + 1
                if not c["nhom"] or khoa_nhom(self.hs_theo_id.get(r["sid"], {}).get("nhom")) != c["nhom"]:
                    loi.append(f"{r['sid']} dự trữ nhưng nhóm không khớp CLB")
        for c in self.clubs:
            if dem.get(c["ten"], 0) > c["du_tru"]:
                loi.append(f"{c['ten']} dự trữ {dem[c['ten']]}>{c['du_tru']}")
        for r in self.kq:
            h = self.hs_theo_id.get(r["sid"])
            if h is not None and r["nhom"] != h["nhom"]:
                loi.append(f"{r['sid']} nhóm xuất khác Sổ nhập")
        return self._kq("K3", vai(loi), "suất dự trữ, nhóm ưu tiên và diện đều khớp Sổ nhập", "dự trữ/nhóm")

    def k4(self):
        loi = [r["sid"] for r, c in self._dong_xep()
               if r["sid"] in self.nv_hop_le and c not in self.nv_hop_le[r["sid"]]]
        return self._kq("K4", vai(loi), "mọi CLB nhận nằm trong danh sách nguyện vọng của em đó",
                        "CLB nhận ngoài nguyện vọng")

    def k5(self):
        loi = []
        for r, c in zip(self.kq, self.clb_cua_dong):
            if not r["clb"]:
                if r["nv"]:
                    loi.append(f"{r['sid']} chưa xếp mà có nguyện vọng thứ {r['nv']}")
            elif c is not None and r["sid"] in self.nv_hop_le:
                ds = self.nv_hop_le[r["sid"]]
                vt = next((i + 1 for i, x in enumerate(ds) if x is c), None)
                if vt is None or r["nv"] != str(vt):
                    loi.append(f"{r['sid']} xuất {r['nv'] or 'trống'}, Sổ nhập {vt}")
        return self._kq("K5", vai(loi), "'Nguyện vọng thứ' bằng vị trí CLB trong danh sách của em đó",
                        "thứ hạng nguyện vọng")

    def k6(self):
        if self.tep_clb is None:
            return ("K6", "FAIL", "không thấy thư mục *_theo_club")
        chinh = {}
        for r, c in zip(self.kq, self.clb_cua_dong):
            k = c["ten"] if c is not None else (r["clb"] or None)
            chinh.setdefault(k, set()).add((r["sid"], r["nv"], r["dien"], r["nhom"]))
        tep = {t: set(ds) for t, ds in self.tep_clb.items()}
        loi = []
        chua = tep.pop(CHUA_XEP, set())
        if chua != chinh.pop(None, set()):
            loi.append("tệp _chua_duoc_xep khác tập chưa xếp")
        con = list(tep.items())
        for k, tap in chinh.items():
            khop = [t for t, s in con if s == tap]
            if not khop:
                loi.append(f"không tệp nào khớp CLB {k}")
            else:
                con = [(t, s) for t, s in con if t != khop[0]]
        loi += [f"tệp {t} không khớp CLB nào" for t, _ in con]
        n_dong = sum(len(v) for v in self.tep_clb.values())
        if n_dong != len(self.kq) and not loi:
            loi.append(f"tổng dòng {n_dong} khác {len(self.kq)}")
        return self._kq("K6", vai(loi), "tệp theo CLB và tệp chính cùng một tập học sinh", "tệp theo CLB")

    def k7(self):
        if self.tong_hop is None:
            return ("K7", "FAIL", "không thấy mục 'TỪNG ...' trong tệp *_tong_hop.csv")
        xep, dtru = {}, {}
        for r, c in self._dong_xep():
            xep[c["ten"]] = xep.get(c["ten"], 0) + 1
            dtru[c["ten"]] = dtru.get(c["ten"], 0) + (r["dien"] == DIEN_DU_TRU)
        loi, thay = [], set()
        for ma, ten, n_xep, n_dt in self.tong_hop:
            c = self.theo_ma.get(ma) or self.theo_ten.get(khoa_ten(ten))
            if c is None:
                loi.append(f"{ma or ten} không có trong Sổ nhập")
                continue
            thay.add(c["ten"])
            if (n_xep, n_dt) != (xep.get(c["ten"], 0), dtru.get(c["ten"], 0)):
                loi.append(f"{c['ten']} tổng hợp {n_xep}/{n_dt}, tệp chính {xep.get(c['ten'], 0)}/{dtru.get(c['ten'], 0)}")
        loi += [f"{t} xếp {n} em nhưng không có dòng tổng hợp" for t, n in xep.items() if t not in thay]
        return self._kq("K7", vai(loi), "'Đã xếp' và 'Trong đó diện dự trữ' của tệp tổng hợp khớp tệp chính",
                        "tệp tổng hợp")


# ---------------------------------------------------------------------- xuất ----

def ghi_dau_vao(duong, dc):
    k = max([len(h["nv"]) for h in dc.hs] or [0])
    tieu_de = (["student_id", "ho_ten", "nhom"] + [f"nv_{i}" for i in range(1, k + 1)]
               + [f"diem_{i}" for i in range(1, k + 1)]
               + ["club_id_nhan", "ten_clb_nhan", "dien", "hang_nhan"])
    kq = {}
    for r in dc.kq:
        kq.setdefault(r["sid"], r)
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(tieu_de)
        for h in dc.hs:
            nv = [h["nv"][i][0] if i < len(h["nv"]) else "" for i in range(k)]
            dm = []
            for i in range(k):
                o = h["nv"][i][1] if i < len(h["nv"]) else None
                dm.append("" if o is None else (doc_diem(o) if doc_diem(o) is not None else str(o).strip()))
            r = kq.get(h["id"], {})
            w.writerow([h["id"], h["ten"], h["nhom"]] + nv + dm
                       + [r.get("clb", ""), r.get("ten_clb", "") if r.get("clb") else "",
                          r.get("dien", ""), r.get("nv", "")])


def main(argv=None):
    ap = argparse.ArgumentParser(description="DC1: đối chiếu độc lập Sổ nhập ⇄ kết quả xuất CSV")
    ap.add_argument("--so-nhap", required=True)
    ap.add_argument("--ket-qua", required=True)
    ap.add_argument("--ra", default=None, help="mặc định: dau_vao_ket_qua.csv cạnh tệp kết quả")
    a = ap.parse_args(argv)
    try:
        clubs, hs = doc_so_nhap(a.so_nhap)
        kq = doc_ket_qua(a.ket_qua)
        tep = doc_tep_theo_clb(os.path.splitext(a.ket_qua)[0] + "_theo_club")
        dc = DoiChieu(clubs, hs, kq, tep, doc_tong_hop(os.path.splitext(a.ket_qua)[0] + "_tong_hop.csv"))
        bang = dc.kiem()
    except DauVaoKhongDung as e:
        print(f"LỖI ĐẦU VÀO: {e}", file=sys.stderr)
        print(f"LỖI ĐẦU VÀO: {e}")
        return 2
    xep = sum(1 for r in kq if r["clb"])
    print(f"Sổ nhập: {a.so_nhap} | Kết quả: {a.ket_qua}")
    print(f"Học sinh: {len(hs)} | CLB: {len(clubs)} | dòng kết quả: {len(kq)} | đã xếp: {xep}"
          f" | chưa xếp: {len(kq) - xep}")
    for ma, tt, nd in bang:
        print(f"{ma} {tt} {nd}")
    n_fail = sum(1 for _, tt, _ in bang if tt == "FAIL")
    print(f"Tổng: {len(bang) - n_fail} PASS, {n_fail} FAIL")
    ra = a.ra or os.path.join(os.path.dirname(os.path.abspath(a.ket_qua)), "dau_vao_ket_qua.csv")
    ghi_dau_vao(ra, dc)
    print(f"Đã ghi {ra}")
    print(CHU_THICH)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
