"""MT1-L2 — API ba thẻ mục tiêu: đọc thẻ đang dùng, chọn thẻ, hoàn tác. Chỉ quản trị (`phan_quyen.QUYEN`).

Chọn thẻ = ghi MỘT giao dịch gồm: luật xếp (bốn khoá của thẻ), khoá cấp trên `muc_tieu` `{id, nhom, truoc?}`
của cấu hình, và — ở thẻ "Dành chỗ cho một nhóm" — nhóm + số chỗ giữ của từng CLB. Sao lưu trước. KHÔNG chạy xếp,
KHÔNG đụng `run_history`, `match_results`, `stb_lock`. `muc_tieu` nằm ngoài `rules` nên không vào `luat_xep` / dấu
vân tay. Thẻ không chạm `wharton` / `fa_daa`; riêng `co_hoi` khi "Chia 100 điểm" đang bật thì `wharton` tự tắt đúng
như luật nhất quán sẵn có của `cau_hinh_ws` (xem `_khoa_nhom` bên dưới), kèm dòng ghi chú; Hoàn tác trả lại.
"""

import copy

import muc_tieu as mt
from api_workspace import CauHinhHong, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import loi_suc_chua


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
            clb = {r[0]: {"capacity": r[1], "reserve_capacity": r[2] or 0, "reserve_group": r[3]}
                   for r in cur.execute(
                       "SELECT club_id, capacity, reserve_capacity, reserve_group FROM clubs "
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
    def chon_muc_tieu(self, muc_tieu, nhom=None):
        """Áp thẻ `muc_tieu` (luật + chỗ giữ) trong MỘT giao dịch, sao lưu trước.

        `nhom` chỉ cần cho `danh_cho` khi có nhiều nhóm (một nhóm duy nhất thì tự chọn). Trả `hoan_tac`: gói
        luật + `muc_tieu` + chỗ giữ của MỌI CLB trước khi đổi, đưa nguyên cho `hoan_tac_muc_tieu`."""
        if not isinstance(muc_tieu, str) or muc_tieu not in mt.BO_MUC_TIEU:
            return _fail(err("mt_muc_tieu_la"))
        with self._khoa_ghi:
            try:
                cfg = self._cfg_ws(nghiem=True)
            except CauHinhHong as e:
                return _fail(loi_cau_hinh(e))
            try:
                hs, clb = self._doc_hs_clb()
            except Exception as e:
                return _fail(err("error_reading_results", detail=str(e)))
            luat0 = cfg["rules"]
            if muc_tieu == mt.CO_HOI and luat0.get("fa_daa") is True:
                return _fail(err("mt_the_can_diem"))

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
                    return _fail(err("mt_khong_co_nhom"))
                if nhom is None or (isinstance(nhom, str) and not nhom.strip()):
                    if len(nhom_co) > 1:
                        return _fail(err("mt_can_chon_nhom"))
                    nhom_chon = nhom_co[0]["nhan"]
                else:
                    khoa = mt._khoa_nhom(nhom)
                    khop = [g["nhan"] for g in nhom_co if mt._khoa_nhom(g["nhan"]) == khoa]
                    if not khop:
                        return _fail(err("mt_nhom_khong_co", nhom=str(nhom)))
                    nhom_chon = khop[0]
                thong_tin = mt.de_xuat_cho_giu(hs, clb, nhom_chon)
                cho = {cid: (nhom_chon, n) for cid, n in thong_tin["cho_giu"].items()}
                # Chỗ giữ nhập ban đầu: giữ nguyên bản đã nhớ khi đang ở (hoặc đã từng ở) thẻ này.
                truoc = (cu or {}).get("truoc") if (cu or {}).get("id") == mt.DANH_CHO \
                    else _cho_hien_co(clb)
                if truoc is None:
                    truoc = _cho_hien_co(clb)
            elif (cu or {}).get("id") == mt.DANH_CHO and hien_tai == mt.DANH_CHO and (cu or {}).get("truoc"):
                # Rời thẻ "Dành chỗ" khi chưa ai sửa tay: trả chỗ giữ nhập ban đầu (chỉ CLB còn tồn tại).
                cho = {cid: (v[0], v[1]) for cid, v in cu["truoc"].items() if cid in clb}

            moi = {"id": muc_tieu, "nhom": nhom_chon}
            if truoc is not None:
                moi["truoc"] = truoc
            cfg2 = copy.deepcopy(cfg)
            cfg2["rules"] = luat
            cfg2["muc_tieu"] = moi
            hoan_tac = {"rules": copy.deepcopy(luat0), "muc_tieu": copy.deepcopy(cu),
                        "clubs": _cho_hien_co(clb)}
            try:
                self._backup_db()
            except Exception:
                pass                            # hỏng sao lưu không chặn, như các thao tác khác
            try:
                self._ghi_the(cfg2, cho)
            except Exception as e:
                return _fail(err("mt_khong_ap_dung", detail=str(e)))
            kq = {"muc_tieu": muc_tieu, "nhom": nhom_chon, "canh_bao": canh_bao, "hoan_tac": hoan_tac,
                  "cho_giu": thong_tin.get("cho_giu"), "clb_it": thong_tin.get("clb_it", []),
                  "clb_ghi_de": thong_tin.get("clb_ghi_de", [])}
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
