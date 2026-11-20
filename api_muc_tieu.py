"""MT1-L2 — API ba thẻ mục tiêu: đọc thẻ đang dùng, chọn thẻ, hoàn tác. Chỉ quản trị (`phan_quyen.QUYEN`).

Chọn thẻ = ghi MỘT giao dịch gồm: luật xếp (bốn khoá của thẻ), khoá cấp trên `muc_tieu` `{id, nhom, truoc?}`
của cấu hình, và — ở thẻ "Dành chỗ cho một nhóm" — nhóm + số chỗ giữ của từng CLB. Sao lưu trước. KHÔNG chạy xếp,
KHÔNG đụng `run_history`, `match_results`, `stb_lock`. `muc_tieu` nằm ngoài `rules` nên không vào `luat_xep` / dấu
vân tay. Thẻ không chạm `wharton` / `fa_daa`; riêng `co_hoi` khi "Chia 100 điểm" đang bật thì `wharton` tự tắt đúng
như luật nhất quán sẵn có của `cau_hinh_ws` (xem `_khoa_nhom` bên dưới), kèm dòng ghi chú; Hoàn tác trả lại.
"""

import copy

import muc_tieu as mt
import muc_tieu_do as dd
import tieu_chi
from api_workspace import CauHinhHong, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import (
    cac_dong_match_results,
    loi_suc_chua,
    luat_xep_de_ghi,
    run_chinh_thuc_moi_nhat,
)


def _dat_cho_giu(conn, cho):
    """Ghi `{club_id: (nhóm|None, số chỗ)}` vào bảng `clubs`, trên kết nối (giao dịch) của người gọi."""
    for cid, (nhom, so_cho) in cho.items():
        conn.execute("UPDATE clubs SET reserve_group = ?, reserve_capacity = ? WHERE club_id = ?",
                     (nhom, so_cho, cid))


def _cho_hien_co(clubs):
    return {cid: [c["reserve_group"], c["reserve_capacity"] or 0] for cid, c in clubs.items()}


class MucTieuMixin:
    def _doc_hs_clb(self):
        """`(students, clubs)` cho `muc_tieu`: chỉ nhóm của học sinh, sức chứa và chỗ giữ của CLB."""
        with self._ket_noi_doc() as cur:
            hs = {r[0]: {"reserve_group": r[1]} for r in cur.execute(
                "SELECT student_id, reserve_group FROM students ORDER BY student_id")}
            clb = {r[0]: {"capacity": r[1], "reserve_capacity": r[2] or 0, "reserve_group": r[3],
                          "name": r[4] or r[0]}
                   for r in cur.execute(
                       "SELECT club_id, capacity, reserve_capacity, reserve_group, name FROM clubs "
                       "ORDER BY club_id")}
        return hs, clb

    # ------------------------------------------------------------------ đọc
    def get_muc_tieu(self):
        """Ba thẻ, thẻ đang hiệu lực, nhóm có trong danh sách, lần chọn cuối và lý do khoá thẻ (nếu có).

        data: cac_the[{id, tieu_de, cau, khoa, ly_do, ghi_chu}], hien_tai (nang_luc/co_hoi/danh_cho/tuy_chinh),
        lan_cuoi ({id, nhom} hoặc None), nhom ([{nhan, so_em}]). Không ghi gì."""
        try:
            cfg = self._cfg_ws(nghiem=True)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        try:
            hs, clb = self._doc_hs_clb()
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
        nhom = mt.cac_nhom(hs)
        da_chon = cfg.get("muc_tieu")
        luat = cfg["rules"]
        cac_the = []
        for t in mt.BO_MUC_TIEU.values():
            khoa, ly_do, ghi_chu = False, None, []
            if t["id"] == mt.CO_HOI:
                if luat.get("fa_daa") is True:
                    khoa, ly_do = True, err("mt_the_can_diem")
                elif luat.get("wharton") is True:
                    ghi_chu.append(err("mt_diem_chia_khong_dung"))
            if t["id"] == mt.DANH_CHO and not nhom:
                khoa, ly_do = True, err("mt_khong_co_nhom")
            cac_the.append({"id": t["id"], "tieu_de": dict(t["tieu_de"]), "cau": dict(t["cau"]),
                            "khoa": khoa, "ly_do": ly_do, "ghi_chu": ghi_chu})
        return _ok({
            "cac_the": cac_the,
            "hien_tai": mt.nhan_dien_muc_tieu(luat, clb, da_chon, hs),
            "lan_cuoi": ({"id": da_chon["id"], "nhom": da_chon.get("nhom")} if da_chon else None),
            "nhom": nhom,
        })

    # ------------------------------------------------------------------ chọn
    def _ke_hoach(self, muc_tieu, nhom):
        """Kế hoạch của thẻ `muc_tieu` trên dữ liệu HIỆN TẠI, chưa ghi gì: `(kế hoạch, None)` hoặc `(None, lỗi)`.

        Dùng chung cho `chon_muc_tieu` (áp thật) và `uoc_tinh_muc_tieu` (giả định, chỉ đọc). Gọi trong `_khoa_ghi`."""
        if not isinstance(muc_tieu, str) or muc_tieu not in mt.BO_MUC_TIEU:
            return None, _fail(err("mt_muc_tieu_la"))
        try:
            cfg = self._cfg_ws(nghiem=True)
        except CauHinhHong as e:
            return None, _fail(loi_cau_hinh(e))
        try:
            hs, clb = self._doc_hs_clb()
        except Exception as e:
            return None, _fail(err("error_reading_results", detail=str(e)))
        luat0 = cfg["rules"]
        if muc_tieu == mt.CO_HOI and luat0.get("fa_daa") is True:
            return None, _fail(err("mt_the_can_diem"))

        cu = cfg.get("muc_tieu")
        hien_tai = mt.nhan_dien_muc_tieu(luat0, clb, cu, hs)
        luat = mt.rules_cua_muc_tieu(muc_tieu, luat0)
        canh_bao = []
        if muc_tieu == mt.CO_HOI and luat.get("wharton") is True:
            luat["wharton"] = False       # luật nhất quán sẵn có: bốc thăm thuần không dùng điểm chia
            canh_bao.append(err("mt_diem_chia_khong_dung"))

        nhom_chon, cho, truoc, thong_tin = None, None, None, {}
        if muc_tieu == mt.DANH_CHO:
            nhom_co = mt.cac_nhom(hs)
            if not nhom_co:
                return None, _fail(err("mt_khong_co_nhom"))
            if nhom is None or (isinstance(nhom, str) and not nhom.strip()):
                if len(nhom_co) > 1:
                    return None, _fail(err("mt_can_chon_nhom"))
                nhom_chon = nhom_co[0]["nhan"]
            else:
                khoa = mt._khoa_nhom(nhom)
                khop = [g["nhan"] for g in nhom_co if mt._khoa_nhom(g["nhan"]) == khoa]
                if not khop:
                    return None, _fail(err("mt_nhom_khong_co", nhom=str(nhom)))
                nhom_chon = khop[0]
            thong_tin = mt.de_xuat_cho_giu(hs, clb, nhom_chon)
            cho = {cid: (nhom_chon, n) for cid, n in thong_tin["cho_giu"].items()}
            # Chỗ giữ nhập ban đầu: giữ nguyên bản đã nhớ khi đang ở (hoặc đã từng ở) thẻ này.
            truoc = (cu or {}).get("truoc") if (cu or {}).get("id") == mt.DANH_CHO else _cho_hien_co(clb)
            if truoc is None:
                truoc = _cho_hien_co(clb)
        elif (cu or {}).get("id") == mt.DANH_CHO and hien_tai == mt.DANH_CHO and (cu or {}).get("truoc"):
            # Rời thẻ "Dành chỗ" khi chưa ai sửa tay: trả chỗ giữ nhập ban đầu (chỉ CLB còn tồn tại).
            cho = {cid: (v[0], v[1]) for cid, v in cu["truoc"].items() if cid in clb}
        return {"cfg": cfg, "hs": hs, "clb": clb, "luat0": luat0, "cu": cu, "hien_tai": hien_tai,
                "luat": luat, "canh_bao": canh_bao, "nhom_chon": nhom_chon, "cho": cho,
                "truoc": truoc, "thong_tin": thong_tin}, None

    def chon_muc_tieu(self, muc_tieu, nhom=None):
        """Áp thẻ `muc_tieu` (luật + chỗ giữ) trong MỘT giao dịch, sao lưu trước.

        `nhom` chỉ cần cho `danh_cho` khi có nhiều nhóm (một nhóm duy nhất thì tự chọn). Trả `hoan_tac`: gói
        luật + `muc_tieu` + chỗ giữ của MỌI CLB trước khi đổi, đưa nguyên cho `hoan_tac_muc_tieu`."""
        if not isinstance(muc_tieu, str) or muc_tieu not in mt.BO_MUC_TIEU:
            return _fail(err("mt_muc_tieu_la"))
        with self._khoa_ghi:
            kh, loi = self._ke_hoach(muc_tieu, nhom)
            if loi is not None:
                return loi
            moi = {"id": muc_tieu, "nhom": kh["nhom_chon"]}
            if kh["truoc"] is not None:
                moi["truoc"] = kh["truoc"]
            cfg2 = copy.deepcopy(kh["cfg"])
            cfg2["rules"] = kh["luat"]
            cfg2["muc_tieu"] = moi
            hoan_tac = {"rules": copy.deepcopy(kh["luat0"]), "muc_tieu": copy.deepcopy(kh["cu"]),
                        "clubs": _cho_hien_co(kh["clb"])}
            try:
                self._backup_db()
            except Exception:
                pass                            # hỏng sao lưu không chặn, như các thao tác khác
            try:
                self._ghi_the(cfg2, kh["cho"])
            except Exception as e:
                return _fail(err("mt_khong_ap_dung", detail=str(e)))
            tt = kh["thong_tin"]
            kq = {"muc_tieu": muc_tieu, "nhom": kh["nhom_chon"], "canh_bao": kh["canh_bao"],
                  "hoan_tac": hoan_tac, "cho_giu": tt.get("cho_giu"), "clb_it": tt.get("clb_it", []),
                  "clb_ghi_de": tt.get("clb_ghi_de", [])}
        kq["hien_tai"] = self.get_muc_tieu()["data"]["hien_tai"]
        return _ok(kq)

    def _ghi_the(self, cfg2, cho):
        """Ghi cấu hình + chỗ giữ (nếu có) trong một giao dịch; ném lỗi thì cả hai nguyên vẹn."""
        import cau_hinh_ws
        viec = (lambda conn: _dat_cho_giu(conn, cho)) if cho else None
        cau_hinh_ws.ghi_cau_hinh(self.db_path, cfg2, cung_giao_dich=viec)

    # ------------------------------------------------------------------ hoàn tác
    def hoan_tac_muc_tieu(self, hoan_tac):
        """Trả đúng luật, khoá `muc_tieu` và chỗ giữ của từng CLB như gói `hoan_tac` của `chon_muc_tieu`.

        Gói hỏng thì từ chối, chưa ghi gì. Hoàn tác hai lần cùng một gói ra cùng một trạng thái."""
        khong_hop_le = _fail(err("mt_hoan_tac_khong_hop_le"))
        if (not isinstance(hoan_tac, dict) or not isinstance(hoan_tac.get("rules"), dict)
                or not isinstance(hoan_tac.get("clubs"), dict)):
            return khong_hop_le
        with self._khoa_ghi:
            try:
                cfg = self._cfg_ws(nghiem=True)
            except CauHinhHong as e:
                return _fail(loi_cau_hinh(e))
            try:
                _hs, clb = self._doc_hs_clb()
            except Exception as e:
                return _fail(err("error_reading_results", detail=str(e)))
            cho = {}
            for cid, v in hoan_tac["clubs"].items():
                if (not isinstance(cid, str) or not isinstance(v, list) or len(v) != 2
                        or not (v[0] is None or isinstance(v[0], str))
                        or not isinstance(v[1], int) or isinstance(v[1], bool)):
                    return khong_hop_le
                if cid in clb:
                    if loi_suc_chua(clb[cid]["capacity"] or 0, v[1]):
                        return khong_hop_le
                    cho[cid] = (v[0], v[1])
            cfg2 = copy.deepcopy(cfg)
            cfg2["rules"] = copy.deepcopy(hoan_tac["rules"])
            if hoan_tac.get("muc_tieu") is None:
                cfg2.pop("muc_tieu", None)
            else:
                cfg2["muc_tieu"] = copy.deepcopy(hoan_tac["muc_tieu"])
            import cau_hinh_ws
            try:
                cau_hinh_ws.chuan_hoa(cfg2, kiem_trung=False)
            except ValueError:
                return khong_hop_le
            try:
                self._backup_db()
            except Exception:
                pass
            try:
                self._ghi_the(cfg2, cho)
            except Exception as e:
                return _fail(err("mt_khong_ap_dung", detail=str(e)))
        return _ok({"hien_tai": self.get_muc_tieu()["data"]["hien_tai"]})

    # ------------------------------------------------------------------ MT1-L3: ước tính + kết quả (CHỈ ĐỌC)
    @staticmethod
    def _hang_ket_qua(rows) -> dict:
        """`{(student_id, buoi): (club_id|None, rank|None)}` từ các dòng `(sid, buoi, club_id, rank)`."""
        return {(r[0], r[1]): (r[2], r[3]) for r in rows}

    def _doc_moc_chinh_thuc(self):
        """`(dòng run_history chính thức mới nhất | None, seed đã khoá, kết quả đó, đếm NV1 từng CLB)`."""
        with self._ket_noi_doc() as cur:
            goc = run_chinh_thuc_moi_nhat(cur)
            if goc is None:
                return None, None, {}, {}
            khoa = cur.execute("SELECT is_locked, seed FROM stb_lock WHERE id = 1").fetchone()
            if not khoa or not khoa["is_locked"]:
                return None, None, {}, {}
            seed = khoa["seed"] if khoa["seed"] is not None else goc["seed"]
            rows = self._hang_ket_qua(cur.execute(
                "SELECT student_id, buoi, club_id, rank_in_student_pref FROM match_results"))
            nv1 = {r[0]: r[1] for r in cur.execute(
                "SELECT club_id, COUNT(*) FROM preferences WHERE rank = 1 GROUP BY club_id")}
        return goc, seed, rows, nv1

    def _giai_gia_dinh(self, luat, seed, goc, cho):
        """Giải trong bộ nhớ với `luat` và chỗ giữ `cho` ({club_id: (nhóm, số chỗ)} hoặc None); không ghi, không sao lưu.

        Trả `(kết quả {(em, buổi): (clb, hạng)}, None)` hoặc `(None, lỗi)`. Cùng bộ số bốc thăm đã khoá."""
        def sua(clubs):
            for cid, (nhom, n) in (cho or {}).items():
                if cid in clubs:
                    clubs[cid]["reserve_group"], clubs[cid]["reserve_capacity"] = nhom, n
        chi_buoi = [b for b in (goc["buoi_da_chay"] or "").split(",") if b] or None
        result, loi = self._giai_trong_bo_nho(luat, seed, chi_buoi, [], sao_luu=False, sua_clb=sua)
        if loi is not None:
            return None, loi
        return {(r[0], r[1]): (r[2], r[5]) for r in cac_dong_match_results(result)}, None

    def uoc_tinh_muc_tieu(self, muc_tieu, nhom=None):
        """Ước tính thẻ `muc_tieu` (và `nhom`) trên dữ liệu hiện tại MÀ CHƯA ÁP. Chỉ ĐỌC: không ghi bảng nào (kể
        cả `run_history`, `stb_lock`), không sao lưu, không gọi `run_thu`; cùng bộ số bốc thăm đã khoá.

        Chưa có lần xếp chính thức thì chỉ có lời mô tả (`co_so_sanh` = False). Có thì so với lần chính thức mới
        nhất: `tot_hon` / `xuong_sau` (số em; 1–4 bị ẩn thành "dưới 5" ngay ở đây). Chế độ huy chương: `mt_uoc_tinh_fa`."""
        with self._khoa_ghi:
            kh, loi = self._ke_hoach(muc_tieu, nhom)
            if loi is not None:
                return loi
            if kh["luat0"].get("fa_daa") is True:
                return _fail(err("mt_uoc_tinh_fa"))
            luat, tt = kh["luat"], kh["thong_tin"]
            canh_bao = list(kh["canh_bao"])
            if tt.get("clb_it"):
                canh_bao.append(err("mt_cho_it", n=len(tt["clb_it"])))
            du = {"muc_tieu": muc_tieu, "nhom": kh["nhom_chon"], "luat": luat,
                  "mo_ta": tieu_chi.mo_ta_tieu_chi(luat, "vi"),
                  "mo_ta_en": tieu_chi.mo_ta_tieu_chi(luat, "en"),
                  "giu_cho": ([{"club_id": cid, "ten": kh["clb"][cid]["name"], "giu": n,
                                "suc_chua": kh["clb"][cid]["capacity"]}
                               for cid, n in tt["cho_giu"].items()] if muc_tieu == mt.DANH_CHO else None),
                  "co_so_sanh": False, "canh_bao": canh_bao}
            try:
                goc, seed, truoc, _nv1 = self._doc_moc_chinh_thuc()
                if goc is None:
                    return _ok(du)
                sau, loi = self._giai_gia_dinh(luat, seed, goc, kh["cho"])
            except Exception as e:
                return _fail(err("error_running_pipeline", detail=str(e)))
            if loi is not None:
                return loi
            tot, xuong = dd.so_sanh_hang(truoc, sau)
            if muc_tieu == mt.DANH_CHO:
                khoa = mt._khoa_nhom(kh["nhom_chon"])
                thanh_vien = {s for s, i in kh["hs"].items() if mt._khoa_nhom(i["reserve_group"]) == khoa}
                if thanh_vien and not dd.co_khoang_cach(truoc, thanh_vien):
                    du["canh_bao"].append(err("mt_khong_co_khoang_cach"))
            du.update({"co_so_sanh": True, "tot_hon": dd.an_so(len(tot)), "xuong_sau": dd.an_so(len(xuong))})
            return _ok(du)

    def bao_cao_muc_tieu(self, run_id=None):
        """Dòng kết quả của lần xếp CHÍNH THỨC mới nhất: mục tiêu đang dùng đạt chưa, bao nhiêu em được giúp /
        nhường chỗ so với cùng dữ liệu không dùng thẻ (giải lại trong bộ nhớ, cùng bộ số đã khoá). Chỉ ĐỌC.

        `ap_dung` False khi lần xếp đó không chạy theo thẻ hiện tại (luật đã đổi sau đó, hay luật sửa tay).
        Số 1–4 bị ẩn thành "dưới 5" ngay ở đây."""
        with self._khoa_ghi:
            try:
                cfg = self._cfg_ws(nghiem=True)
            except CauHinhHong as e:
                return _fail(loi_cau_hinh(e))
            try:
                hs, clb = self._doc_hs_clb()
                goc, seed, thuc, nv1 = self._doc_moc_chinh_thuc()
                if goc is None:
                    return _fail(err("mt_chua_co_ket_qua"))
                if run_id is not None:
                    with self._ket_noi_doc() as cur:
                        dong = (None if isinstance(run_id, bool) or not isinstance(run_id, int) else
                                cur.execute("SELECT run_id, loai_chay FROM run_history WHERE run_id = ?",
                                            (run_id,)).fetchone())
                    if dong is None or dong["loai_chay"] == "thu":
                        return _fail(err("gt2_lan_chay_khong_co", run_id=str(run_id)))
                    if dong["run_id"] != goc["run_id"]:
                        return _fail(err("gt2_so_sanh_lan_cu", run_id=str(run_id)))
                da_chon = cfg.get("muc_tieu")
                hien_tai = mt.nhan_dien_muc_tieu(cfg["rules"], clb, da_chon, hs)
                co_the = hien_tai in mt.BO_MUC_TIEU and luat_xep_de_ghi(cfg["rules"]) == goc["luat_xep"]
                if not co_the:
                    return _ok({"ap_dung": False, "hien_tai": hien_tai, "run_id": goc["run_id"]})
                kq = {"ap_dung": True, "run_id": goc["run_id"], "muc_tieu": hien_tai, "co_so_sanh": False,
                      "nhom": (da_chon or {}).get("nhom") if hien_tai == mt.DANH_CHO else None,
                      "dat": None,
                      "an_toan": {"nguyen_vong_1_pct": dd.pct_nguyen_vong_1(thuc),
                                  "chua_co_cho": dd.an_so(dd.so_chua_co_cho(thuc))}}
                if hien_tai == mt.NANG_LUC:
                    return _ok(kq)
                # Cùng dữ liệu, KHÔNG dùng thẻ: luật `nang_luc` và chỗ giữ nhập ban đầu.
                truoc_clb = ({cid: (v[0], v[1]) for cid, v in (da_chon or {}).get("truoc", {}).items()
                              if cid in clb} if hien_tai == mt.DANH_CHO else None)
                thanh_vien = set()
                if hien_tai == mt.DANH_CHO:
                    khoa = mt._khoa_nhom(kq["nhom"])
                    thanh_vien = {s for s, i in hs.items() if mt._khoa_nhom(i["reserve_group"]) == khoa}
                    so_dat, so_clb = dd.dat_o_clb(thuc, thanh_vien, len(hs), dd.clb_dong_nhat(nv1, 5))
                    kq["dat"] = {"so_dat": so_dat, "so_clb": so_clb}
                    if not truoc_clb:
                        # Không còn biết chỗ giữ nhập ban đầu (khoá đã sửa tay / bản cũ): không có mốc để so,
                        # nên KHÔNG báo "được giúp / nhường chỗ" (0 sẽ là một sự thật giả).
                        return _ok(kq)
                luat_cf = mt.rules_cua_muc_tieu(mt.NANG_LUC, cfg["rules"])
                cf, loi = self._giai_gia_dinh(luat_cf, seed, goc, truoc_clb)
            except Exception as e:
                return _fail(err("error_reading_results", detail=str(e)))
            if loi is not None:
                return loi
            giup, nhuong = dd.so_sanh_hang(cf, thuc)             # `thuc` so với lần không dùng thẻ
            kq.update({"co_so_sanh": True, "duoc_giup": dd.an_so(len(giup)),
                       "nhuong_cho": dd.an_so(len(nhuong)),
                       "an_toan_truoc": {"nguyen_vong_1_pct": dd.pct_nguyen_vong_1(cf)}})
            if hien_tai == mt.DANH_CHO:
                kq["nhom_duoc_giup"] = dd.an_so(len(giup & thanh_vien))
            return _ok(kq)
