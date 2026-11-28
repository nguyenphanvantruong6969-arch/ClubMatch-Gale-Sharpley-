"""CT1-L2 — "Xem xét chỉ tiêu": API chỉ ĐỌC (`get_xem_xet_chi_tieu`) và hai hàm xuất CSV. Chỉ quản trị (`phan_quyen`).

Từ lần xếp CHÍNH THỨC mới nhất và nguyện vọng thật, phần mềm: (1) tính chỉ số từng CLB, (2) đề xuất chỉ tiêu kỳ sau giữ nguyên
tổng chỗ (`chi_tieu_ct1`), (3) xếp lại cả trường sau từng bước chuyển chỗ, trong bộ nhớ, bằng CHÍNH thuật toán, cùng luật
đã lưu và cùng bộ số bốc thăm ĐÃ KHOÁ (không bốc lại).

KHÔNG ghi gì: không `match_results`, `run_history`, `stb_lock`, không đổi chỉ tiêu, không sao lưu (`sao_luu=False`),
không tạo tệp ngoài hai hàm xuất. Không dùng `fa_daa.goi_y_chi_tieu`. Bất biến 1–5 không bị chạm: đường giải là
`_giai_trong_bo_nho` y như chạy thử (GT2) và ước tính mục tiêu (MT1).

Hợp đồng: `{ok, data, errors}`. `data`: tong_cho, so_hoc_sinh, che_do ("de_xuat" | "tu_chon"), clb[], khuyen_nghi, buoc[],
truoc, sau, so_tot_hon, so_kem_hon, o_chua_co, canh_bao[], loi_giai (None | danh sách lỗi: lý do không có kết quả từng bước).
"""

from api_chung import _ghi_csv
from api_workspace import CauHinhHong, LoiDuongXuat, loi_cau_hinh
from chi_tieu_ct1 import (
    chi_so_clb_ct1,
    ghep_buoc_chuyen,
    hang_ket_qua,
    khuyen_nghi_chi_tieu,
    kiem_buoc_tu_chon,
    thong_ke_ket_qua,
)
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import (
    BUOI_MAC_DINH,
    cac_dong_match_results,
    dung_fa_daa,
    run_chinh_thuc_moi_nhat,
)
from so_nhap import TU_DO
import tieu_chi


def _huong(truoc, sau, h_truoc, h_sau):
    """vao / ra / len / xuong của một em đổi CLB giữa hai bước (hạng: chưa có CLB = dưới mọi CLB)."""
    if truoc is None:
        return "vao"
    if sau is None:
        return "ra"
    return "len" if h_sau <= h_truoc else "xuong"


class ChiTieuMixin:
    # ------------------------------------------------------------------ đọc
    def get_xem_xet_chi_tieu(self, buoc_tu_chon=None):
        """Đề xuất chỉ tiêu + kết quả sau từng bước. `buoc_tu_chon=[{tu, den, k}]` thay các bước đề xuất bằng bước tự chọn
        (thử một thay đổi). Chỉ ĐỌC."""
        with self._khoa_ghi:
            d, loi = self._xem_xet_da_khoa(buoc_tu_chon)
        return _fail(loi) if loi else _ok(d)

    def _doc_ct1(self):
        """Đọc một lượt: `(goc, seed, clubs, students, prefs, ket_qua_chinh_thuc)` hoặc `(None, loi)`."""
        with self._ket_noi_doc() as cur:
            goc = run_chinh_thuc_moi_nhat(cur)
            khoa = cur.execute("SELECT is_locked, seed FROM stb_lock WHERE id = 1").fetchone()
            if goc is None or not khoa or not khoa["is_locked"]:
                return None, err("gt2_chua_co_lan_chinh_thuc")
            seed = khoa["seed"] if khoa["seed"] is not None else goc["seed"]
            clubs = {}
            for r in cur.execute("SELECT club_id, name, capacity, reserve_capacity, loai, buoi FROM clubs "
                                 "ORDER BY club_id"):
                clubs[r["club_id"]] = {"ten": r["name"] or r["club_id"], "cap": r["capacity"] or 0,
                                       "reserve_capacity": r["reserve_capacity"] or 0,
                                       "loai_tru": r["loai"] == TU_DO, "buoi": r["buoi"] or BUOI_MAC_DINH}
            hs = {r[0]: {"ten": r[1] or "", "lop": r[2] or "", "nhom": r[3] or ""} for r in cur.execute(
                "SELECT student_id, name, class_id, reserve_group FROM students")}
            prefs = {}
            for sid, cid in cur.execute("SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
                if cid in clubs:
                    prefs.setdefault((sid, clubs[cid]["buoi"]), []).append(cid)
            chinh_thuc = {(r[0], r[1]): r[2] for r in cur.execute(
                "SELECT student_id, buoi, club_id FROM match_results")}
        return (goc, seed, clubs, hs, prefs, chinh_thuc), None

    def _giai_voi_cap(self, luat, seed, chi_buoi, cap):
        """Giải lại cả trường với chỉ tiêu `cap` ({club_id: số chỗ}). `({(em, buổi): club|None}, None)` hoặc `(None, lỗi)`."""
        def sua(clubs):
            for cid, n in cap.items():
                if cid in clubs:
                    clubs[cid]["capacity"] = n
        result, loi = self._giai_trong_bo_nho(luat, seed, chi_buoi, [], sao_luu=False, sua_clb=sua)
        if loi is not None:
            return None, loi["errors"]
        return {(r[0], r[1]): r[2] for r in cac_dong_match_results(result)}, None

    def _xem_xet_da_khoa(self, buoc_tu_chon):
        """`(data, None)` hoặc `(None, lỗi)`. Gọi trong `_khoa_ghi`."""
        try:
            cfg = self._cfg_ws(nghiem=True)
        except CauHinhHong as e:
            return None, loi_cau_hinh(e)
        luat = cfg["rules"]
        if dung_fa_daa(luat):
            return None, err("gt2_thu_chua_ho_tro_fa")
        try:
            doc, loi = self._doc_ct1()
            if loi is not None:
                return None, loi
            goc, seed, clubs, hs, prefs, chinh_thuc = doc
            chi_buoi = [b for b in (goc["buoi_da_chay"] or "").split(",") if b] or None
            cap0 = {c: v["cap"] for c, v in clubs.items()}
            canh_bao, loi_giai = [], None

            # Mốc: giải lại với chỉ tiêu KHÔNG đổi; phải trùng lần chính thức (nếu không, báo nhưng vẫn cho xem số).
            gan0, loi_giai = self._giai_voi_cap(luat, seed, chi_buoi, cap0)
            if gan0 is not None:
                lech = sum(1 for k, v in gan0.items() if chinh_thuc.get(k) != v)
                if lech:
                    canh_bao.append(err("ct1_moc_khong_khop", n=lech))
                gan_dung = gan0
            else:
                gan_dung = {k: chinh_thuc.get(k) for k in prefs}

            chi_so = chi_so_clb_ct1(clubs, prefs, gan_dung)
            if buoc_tu_chon is None:
                che_do = "de_xuat"
                buoc = ghep_buoc_chuyen(chi_so, khuyen_nghi_chi_tieu(chi_so))
            else:
                che_do = "tu_chon"
                buoc, loi = kiem_buoc_tu_chon(buoc_tu_chon, clubs)
                if loi is not None:
                    return None, err(loi["code"], **loi["params"])
            cap_moi = dict(cap0)
            for a, b, k in buoc:
                cap_moi[a] -= k
                cap_moi[b] += k

            res = None
            if gan0 is not None:
                res, loi_buoc = self._buoc_ket_qua(luat, seed, chi_buoi, clubs, hs, chi_so, prefs, gan0, buoc, cap0)
                loi_giai = loi_buoc
            if res is not None:
                ds_buoc, truoc, sau, o_chua_co = res["buoc"], res["truoc"], res["sau"], res["o"]
                moi_mat = res["moi_mat_cho"]
                tot = sum(1 for k, h in res["hang"].items() if h < res["hang0"][k])
                kem = sum(1 for k, h in res["hang"].items() if h > res["hang0"][k])
            else:                              # không có kết quả từng bước: vẫn trả đề xuất + số chỗ từng bước
                ds_buoc, cap = [], dict(cap0)
                for stt, (a, b, k) in enumerate(buoc, 1):
                    cap_t = dict(cap)
                    cap[a] -= k
                    cap[b] += k
                    ds_buoc.append(self._mo_ta_buoc(stt, a, b, k, clubs, chi_so, cap_t, dict(cap), ket_qua=False))
                truoc = sau = tot = kem = moi_mat = None
                o_chua_co = []

            tong_cho = sum(v["cap"] for v in clubs.values() if not v["loai_tru"])
            return {
                "tong_cho": tong_cho, "so_hoc_sinh": len(hs), "che_do": che_do,
                "clb": [{"club_id": c, "ten": clubs[c]["ten"], "buoi": clubs[c]["buoi"], "cap": cap0[c],
                         "cap_moi": cap_moi[c], "doi": cap_moi[c] - cap0[c], "nv1": chi_so[c]["nv1"],
                         "chua_dap": chi_so[c]["chua_dap"], "da_nhan": chi_so[c]["da_nhan"],
                         "trong": chi_so[c]["trong"], "loai_tru": clubs[c]["loai_tru"]}
                        for c in sorted(clubs, key=lambda x: (clubs[x]["buoi"], x))],
                "khuyen_nghi": {"so_cho_chuyen": sum(k for _a, _b, k in buoc),
                                "so_clb_cho": len({a for a, _b, _k in buoc}),
                                "so_clb_nhan": len({b for _a, b, _k in buoc})},
                "buoc": ds_buoc, "truoc": truoc, "sau": sau, "so_tot_hon": tot, "so_kem_hon": kem,
                "o_chua_co": o_chua_co, "so_moi_mat_cho": moi_mat, "canh_bao": canh_bao, "loi_giai": loi_giai,
            }, None
        except Exception as e:
            return None, err("error_reading_results", detail=str(e))

    @staticmethod
    def _mo_ta_buoc(stt, a, b, k, clubs, chi_so, cap_t, cap_s, ket_qua):
        """Phần của một bước không cần giải lại: CLB cho / nhận, số chỗ trước-sau và "Vì sao" (số liệu cho câu giải thích)."""
        return {"stt": stt, "tu": a, "den": b, "k": k, "tu_ten": clubs[a]["ten"], "den_ten": clubs[b]["ten"],
                "cap_tu_truoc": cap_t[a], "cap_tu_sau": cap_s[a], "cap_den_truoc": cap_t[b], "cap_den_sau": cap_s[b],
                "ly_do": {"tu_trong": chi_so[a]["trong"], "tu_nv1": chi_so[a]["nv1"],
                          "den_chua_dap": chi_so[b]["chua_dap"], "den_cap": chi_so[b]["cap"],
                          "den_nv1": chi_so[b]["nv1"]},
                "co_ket_qua": ket_qua}

    def _buoc_ket_qua(self, luat, seed, chi_buoi, clubs, hs, chi_so, prefs, gan0, buoc, cap0):
        """Giải lại cộng dồn sau từng bước: `({buoc, truoc, sau, hang, hang0, o}, None)` hoặc `(None, lỗi)` nếu một bước không giải được."""
        ctx = {"students": hs, "diem": {}, "tiers": [],
               "clubs": {c: {"ten": v["ten"], "capacity": v["cap"]} for c, v in clubs.items()}}
        hang0 = hang_ket_qua(prefs, gan0)
        truoc = thong_ke_ket_qua(prefs, gan0)

        def dong(gan):
            return [(s, b, c, None) for (s, b), c in sorted(gan.items())]

        cap = dict(cap0)
        gan_truoc, hang_truoc, tk_truoc = gan0, hang0, truoc
        xep_o_buoc = {}                        # (em, buổi) chưa có CLB ở mốc -> bước đầu tiên từ đó em có CLB đến hết
        ra = []
        for stt, (a, b, k) in enumerate(buoc, 1):
            cap_t = dict(cap)
            cap[a] -= k
            cap[b] += k
            gan, loi = self._giai_voi_cap(luat, seed, chi_buoi, cap)
            if loi is not None:
                return None, loi
            hang = hang_ket_qua(prefs, gan)
            so_sanh = tieu_chi.so_sanh_lan_chay(
                {"nhan": "thu", "run_id": stt - 1, "luat": luat, "rows": dong(gan_truoc)},
                {"nhan": "thu", "run_id": stt, "luat": luat, "rows": dong(gan)}, ctx)
            doi = []
            for d in so_sanh["doi"]:
                key = (d["student_id"], d["buoi"])
                ht, hs_ = hang_truoc.get(key), hang.get(key)
                if ht is None or hs_ is None:
                    continue
                doi.append({"student_id": d["student_id"], "ten": d["ten"], "lop": d["lop"], "buoi": d["buoi"],
                            "tu": d["tu"], "den": d["den"], "tu_ten": d["tu_ten"], "den_ten": d["den_ten"],
                            "nv_truoc": None if d["tu"] is None else ht, "nv_sau": None if d["den"] is None else hs_,
                            "huong": _huong(d["tu"], d["den"], ht, hs_)})
                if d["den"] is None:
                    xep_o_buoc.pop(key, None)          # đã được xếp ở bước trước nhưng sau bước này lại mất chỗ
                elif gan0.get(key) is None:
                    xep_o_buoc.setdefault(key, stt)    # bước đầu từ đó em luôn có CLB cho đến hết
            tk = thong_ke_ket_qua(prefs, gan)
            mo = self._mo_ta_buoc(stt, a, b, k, clubs, chi_so, cap_t, dict(cap), ket_qua=True)
            mo.update({
                "nv1_sau": tk["nv1"], "nv1_them": tk["nv1"] - tk_truoc["nv1"],
                "chua_co_sau": tk["chua_co"], "chua_co_doi": tk["chua_co"] - tk_truoc["chua_co"],
                "so_len": sum(1 for e in doi if e["huong"] in ("len", "vao")),
                "so_xuong": sum(1 for e in doi if e["huong"] in ("xuong", "ra")),
                "so_mat_cho": sum(1 for e in doi if e["huong"] == "ra"),
                "so_doi": len(doi), "doi": doi})
            ra.append(mo)
            gan_truoc, hang_truoc, tk_truoc = gan, hang, tk
        o = [xep_o_buoc.get(k) for k in sorted(k for k, c in gan0.items() if c is None)]
        mat = sum(1 for k, c in gan0.items() if c is not None and gan_truoc.get(k) is None)
        return {"buoc": ra, "truoc": truoc, "sau": tk_truoc, "hang": hang_truoc, "hang0": hang0, "o": o,
                "moi_mat_cho": mat}, None

    # ------------------------------------------------------------------ xuất
    def export_xem_xet_chi_tieu_csv(self, output_path: str = "", buoc_tu_chon=None):
        """CSV (UTF-8 có BOM) bảng đối chiếu: từng em đổi chỗ ở từng bước (có tên, chỉ màn quản trị)."""
        return self._khoa_xuat(self._xuat_ct1_da_khoa, "doi_chieu", output_path, buoc_tu_chon)

    def export_de_xuat_chi_tieu_csv(self, output_path: str = "", buoc_tu_chon=None):
        """CSV (UTF-8 có BOM) bảng chỉ tiêu đề xuất cho từng CLB."""
        return self._khoa_xuat(self._xuat_ct1_da_khoa, "de_xuat", output_path, buoc_tu_chon)

    def _xuat_ct1_da_khoa(self, kieu, output_path, buoc_tu_chon):
        try:
            d, loi = self._xem_xet_da_khoa(buoc_tu_chon)
            if loi:
                return _fail(loi)
            if kieu == "doi_chieu" and d["loi_giai"]:
                return _fail(d["loi_giai"])
            try:
                duong = self._duong_xuat(
                    output_path, "doi_chieu_chi_tieu.csv" if kieu == "doi_chieu" else "de_xuat_chi_tieu.csv",
                    kem_duoi=())
            except LoiDuongXuat as e:
                return _fail(e.loi)

            def buoi(b):
                return "" if b == BUOI_MAC_DINH else b

            if kieu == "doi_chieu":
                dong = [[b["stt"], e["student_id"], e["ten"], e["lop"], buoi(e["buoi"]), e["tu_ten"], e["den_ten"],
                         "" if e["nv_truoc"] is None else e["nv_truoc"], "" if e["nv_sau"] is None else e["nv_sau"],
                         e["huong"]] for b in d["buoc"] for e in b["doi"]]
                _ghi_csv(duong, ["buoc", "student_id", "ho_ten", "lop", "buoi", "clb_truoc", "clb_sau",
                                 "nv_truoc", "nv_sau", "huong"], dong)
                return _ok({"path": duong, "so_dong": len(dong)})
            dong = [[c["club_id"], c["ten"], buoi(c["buoi"]), c["cap"], c["nv1"], c["chua_dap"], c["trong"],
                     c["cap_moi"], c["doi"]] for c in d["clb"]]
            _ghi_csv(duong, ["club_id", "ten_clb", "buoi", "cho_hien_co", "em_thich_nhat", "muon_vao_chua_duoc",
                             "cho_trong", "de_xuat_ky_sau", "thay_doi"], dong)
            return _ok({"path": duong, "so_dong": len(dong)})
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))
