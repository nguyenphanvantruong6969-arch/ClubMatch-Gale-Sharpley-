"""GT2 — API tiêu chí xếp (chỉ ĐỌC): mô tả luật đã lưu bằng lời thường + giá trị cho phép.

Lưu thay đổi vẫn đi qua `update_workspace_config` (không có đường lưu mới). Dùng được cả khi chạy
với một CSDL riêng, không cần bật chế độ workspace.
"""

import cau_hinh_ws
import tieu_chi
from api_chung import _fail_co_buoc, _ghi_csv, _now
from api_workspace import CauHinhHong, LoiDuongXuat, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import (
    BUOI_MAC_DINH,
    LUAT_XEP_MAC_DINH,
    CHE_DO_BOC_THAM_MAC_DINH,
    cac_dong_match_results,
    cat_du_lieu_theo_buoi,
    connect_db,
    default_reserve_eligible_fn,
    diem_wharton_hieu_luc,
    doc_stb_buoi,
    dung_fa_daa,
    dung_wharton,
    kiem_ho_so_wharton,
    load_from_sqlite_kem_dau_van_tay,
    load_from_sqlite_kem_dau_van_tay_wharton,
    luat_xep_cua,
    luat_xep_hieu_luc,
    luat_xep_de_ghi,
    nhom_theo_buoi,
    run_chinh_thuc_moi_nhat,
    run_rbda_nhieu_buoi,
    sanity_check_result,
    sap_buoi,
    tham_so_luat,
    tu_dien_wharton_mot_clb,
    validate_data_integrity,
    verify_stability,
)


class TieuChiMixin:
    def get_tieu_chi(self):
        """Luật xếp đã lưu của workspace đang mở, mô tả bằng lời thường (hai ngôn ngữ).

        data: luat (năm khoá luật xếp), mo_ta (vi), mo_ta_en, tang (tiêu đề hai tầng),
        lua_chon (giá trị cho phép), ghi_chu (câu cố định: không dùng thứ hạng nguyện vọng...).
        Cấu hình đọc không được thì báo lỗi, không lặng lẽ lùi về luật mặc định."""
        try:
            luat_tho = self._cfg_ws(nghiem=True)["rules"]
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        luat = luat_xep_cua(luat_tho)
        return _ok({
            "luat": luat,
            "mo_ta": tieu_chi.mo_ta_tieu_chi(luat_tho, "vi"),
            "mo_ta_en": tieu_chi.mo_ta_tieu_chi(luat_tho, "en"),
            "tang": tieu_chi.tieu_de_tang(luat_tho),
            "lua_chon": tieu_chi.cac_lua_chon_hop_le(),
            "ghi_chu": dict(tieu_chi.GHI_CHU),
        })

    # ------------------------------------------------------------------------------------------
    # L2 — chạy thử (không công bố, không đụng kết quả chính thức)
    # ------------------------------------------------------------------------------------------
    def run_thu(self, rules_thu: dict, chi_buoi=None):
        """Chạy thử một bộ tiêu chí: ghi MỘT dòng `run_history` (`loai_chay = 'thu'`) và kết quả vào
        `ket_qua_thu`. KHÔNG ghi `match_results`, `ket_qua_truoc`, `dau_van_tay_chay`, `stb_lock`, `fa_*`,
        tệp xuất; KHÔNG bốc thăm lại (dùng đúng bộ số đã khoá của lần chính thức)."""
        with self._khoa_ghi:
            return self._run_thu_da_khoa(rules_thu, chi_buoi)

    def _run_thu_da_khoa(self, rules_thu, chi_buoi):
        steps_log = []
        conn = None
        try:
            # 1) Luật thử: trộn lên cấu hình đã lưu rồi kiểm bằng CHÍNH bộ kiểm khi lưu.
            try:
                da_luu = self._cfg_ws(nghiem=True)
            except CauHinhHong as e:
                return _fail(loi_cau_hinh(e))
            if not isinstance(rules_thu, dict):
                return _fail(err("gt2_tieu_chi_khong_hop_le", chi_tiet=""))
            la_khoa = sorted(str(k) for k in rules_thu if k not in LUAT_XEP_MAC_DINH)
            if la_khoa:
                return _fail(err("gt2_tieu_chi_khong_hop_le", chi_tiet=", ".join(la_khoa)))
            try:
                cfg = cau_hinh_ws._chuan_hoa(
                    cau_hinh_ws.tron_len(da_luu, {"rules": rules_thu}), kiem_trung=False)
            except ValueError as e:
                return _fail(err("gt2_tieu_chi_khong_hop_le", chi_tiet=str(e)))
            luat = cfg["rules"]
            if dung_fa_daa(luat):
                return _fail(err("gt2_thu_chua_ho_tro_fa"))

            # 2) Cần một lần chính thức và bộ số bốc thăm đã khoá.
            with self._ket_noi_doc() as cur:
                goc = run_chinh_thuc_moi_nhat(cur)
                khoa = cur.execute("SELECT is_locked, seed FROM stb_lock WHERE id = 1").fetchone()
            if goc is None or not khoa or not khoa["is_locked"]:
                return _fail(err("gt2_chua_co_lan_chinh_thuc"))
            seed = khoa["seed"] if khoa["seed"] is not None else goc["seed"]

            # 3) Sao lưu (hỏng không chặn, như lần chính thức) rồi kiểm dữ liệu.
            try:
                self._backup_db()
            except Exception:
                pass
            wharton = None
            if dung_wharton(luat):
                du_lieu, _dvt, wharton = load_from_sqlite_kem_dau_van_tay_wharton(self.db_path, luat)
            else:
                du_lieu, _dvt = load_from_sqlite_kem_dau_van_tay(self.db_path, luat)
            (students, clubs, tested_scores, applicants, preferences, _) = du_lieu
            errors = validate_data_integrity(
                students, clubs, preferences, applicants, tran_nguyen_vong=luat["max_choices"])
            if errors:
                return _fail_co_buoc(steps_log, errors)
            diem_wharton = None
            if wharton is not None:
                w1_dien, w2_dien = tu_dien_wharton_mot_clb(
                    preferences, wharton["clb_thi"], wharton["w1"], wharton["w2"], clubs)
                loi_w = kiem_ho_so_wharton(
                    preferences, wharton["clb_thi"], w1_dien, w2_dien, clubs,
                    tran_nguyen_vong=luat["max_choices"])
                diem_wharton, thong_bao = diem_wharton_hieu_luc(
                    preferences, w1_dien, w2_dien, tested_scores)
                loi_w += [e for e in thong_bao if e["code"] != "wharton_vang_thi"]
                if loi_w:
                    n_em = len({e["params"].get("student_id") for e in loi_w})
                    return _fail_co_buoc(
                        steps_log, [err("wharton_ho_so_chua_hop_le", n=n_em)] + loi_w)

            # 4) Buổi cần chạy (như lần chính thức; không có thì chạy hết).
            ds_buoi_tat_ca = sap_buoi({(c.get("buoi") or BUOI_MAC_DINH) for c in clubs.values()})
            chi_buoi_chuan = None
            if chi_buoi is not None:
                def _chuan(b):
                    if b in ds_buoi_tat_ca:
                        return b
                    ma = self.chuan_hoa_buoi(b) or BUOI_MAC_DINH
                    return next((x for x in ds_buoi_tat_ca
                                 if x == ma or self.chuan_hoa_buoi(x) == ma), ma)
                chi_buoi_chuan = [_chuan(b) for b in chi_buoi]
                la = sorted(set(chi_buoi_chuan) - set(ds_buoi_tat_ca))
                if la:
                    return _fail(err("buoi_khong_ton_tai", buoi=", ".join(la),
                                     dang_co=", ".join(ds_buoi_tat_ca)))
                if not chi_buoi_chuan:
                    return _fail(err("chua_chon_buoi_nao"))
                if set(chi_buoi_chuan) == set(ds_buoi_tat_ca):
                    chi_buoi_chuan = None

            # 5) Số bốc thăm: CHỈ ĐỌC từ bộ đã khoá. Thiếu số (người mới) thì từ chối, không bốc.
            thieu = [sid for sid, info in students.items() if info.get("stb") is None]
            if thieu:
                return _fail(err("gt2_thu_stb_chua_day", n=len(thieu)))
            stb_lottery = {sid: info["stb"] for sid, info in students.items()}
            with self._ket_noi_doc() as cur:
                stb_buoi_da_khoa = doc_stb_buoi(cur) or None

            # 6) Giải + hai chốt, y như lần chính thức.
            reserve_fn = default_reserve_eligible_fn(students, clubs)
            tham_so = tham_so_luat(luat, students)
            result = run_rbda_nhieu_buoi(
                students, clubs, tested_scores, applicants, preferences,
                stb_lottery, is_reserve_eligible_fn=reserve_fn,
                che_do_boc_tham=CHE_DO_BOC_THAM_MAC_DINH, seed=seed,
                chi_buoi=chi_buoi_chuan,
                tier_rank=tham_so["tier_rank"], bo_qua_du_tru=tham_so["bo_qua_du_tru"],
                diem_wharton=diem_wharton, stb_buoi_da_khoa=stb_buoi_da_khoa)
            van_de = []
            _nhom = nhom_theo_buoi(clubs)
            for _buoi, _kq in result.per_buoi.items():
                _clubs_b, _, _, _prefs_b = cat_du_lieu_theo_buoi(
                    _buoi, _nhom[_buoi], clubs, tested_scores, applicants, preferences)
                van_de += sanity_check_result(_kq, _clubs_b, _prefs_b)
                van_de += verify_stability(
                    _kq, _clubs_b, _prefs_b, reserve_fn, bo_qua_du_tru=tham_so["bo_qua_du_tru"])
            if van_de:
                return _fail_co_buoc(steps_log, van_de)

            # 7) Ghi trong MỘT giao dịch: một dòng run_history + các dòng ket_qua_thu. Lỗi thì rollback.
            conn = connect_db(self.db_path)
            cur = conn.cursor()
            dong = cac_dong_match_results(result)
            n_matched = len({r[0] for r in dong if r[2] is not None})
            run_at = _now()
            cur.execute(
                "INSERT INTO run_history "
                "(seed, run_at, rounds_run, n_matched, n_total, stb_redrawn, che_do_boc_tham, "
                " so_buoi, buoi_da_chay, luat_xep, loai_chay) "
                "VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, 'thu')",
                (seed, run_at, result.rounds_run, n_matched, len(result.so_clb_moi_em()),
                 result.che_do_boc_tham, len(result.ds_buoi), ",".join(result.ds_buoi),
                 luat_xep_de_ghi(luat)))
            run_id = cur.lastrowid
            cur.executemany(
                "INSERT INTO ket_qua_thu (run_id, buoi, student_id, club_id, rank_in_list) "
                "VALUES (?, ?, ?, ?, ?)",
                [(run_id, r[1], r[0], r[2], r[5]) for r in dong])
            conn.commit()
            conn.close()
            conn = None
            return _ok({
                "run_id": run_id, "loai_chay": "thu", "n_matched": n_matched,
                "n_total": len(result.assignment), "rounds_run": result.rounds_run,
                "luat": luat_xep_cua(luat),
                "mo_ta": tieu_chi.mo_ta_tieu_chi(luat, "vi"),
                "mo_ta_en": tieu_chi.mo_ta_tieu_chi(luat, "en"),
            })
        except Exception as e:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
                conn.close()
                conn = None
            return _fail_co_buoc(steps_log, [err("error_running_pipeline", detail=str(e))])
        finally:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
                conn.close()

    # ------------------------------------------------------------------------------------------
    # L3 — so sánh hai lần chạy (chỉ ĐỌC; danh sách em đổi chỗ chỉ cho màn quản lý / giáo viên)
    # ------------------------------------------------------------------------------------------
    def list_lan_chay(self):
        """Lần chính thức mới nhất + các lần chạy thử (mới trước): run_id, run_at, nhãn, tóm tắt tiêu chí.

        Chạy thử không bị xoá nên luôn so lại được. Lần chính thức CŨ hơn không còn dòng kết quả
        (bảng kết quả chỉ giữ lần mới nhất) nên không có trong danh sách."""
        try:
            with self._ket_noi_doc() as cur:
                cot = {r[1] for r in cur.execute("PRAGMA table_info(run_history)")}
                if "loai_chay" not in cot:
                    return _ok({"chinh_thuc": None, "thu": []})
                goc = run_chinh_thuc_moi_nhat(cur)
                thu = cur.execute(
                    "SELECT run_id, run_at, luat_xep, n_matched, n_total, buoi_da_chay FROM run_history "
                    "WHERE loai_chay = 'thu' ORDER BY run_id DESC").fetchall()
            return _ok({"chinh_thuc": self._dong_lan_chay(goc, "chinh_thuc") if goc else None,
                        "thu": [self._dong_lan_chay(r, "thu") for r in thu]})
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))

    @staticmethod
    def _luat_tu_dong(dong) -> dict:
        import json
        try:
            v = json.loads(dong["luat_xep"]) if dong["luat_xep"] else {}
        except (ValueError, TypeError):
            v = {}
        return v if isinstance(v, dict) else {}

    def _dong_lan_chay(self, dong, nhan: str) -> dict:
        luat = self._luat_tu_dong(dong)
        return {"run_id": dong["run_id"], "run_at": dong["run_at"], "nhan": nhan,
                "n_matched": dong["n_matched"], "n_total": dong["n_total"],
                "mo_ta": tieu_chi.mo_ta_tieu_chi(luat, "vi"),
                "mo_ta_en": tieu_chi.mo_ta_tieu_chi(luat, "en")}

    def _tai_lan_chay(self, cur, run_id, goc):
        """(lần chạy, None) hoặc (None, lỗi). Chính thức: chỉ lần MỚI NHẤT (kết quả cũ không còn dòng)."""
        if isinstance(run_id, bool) or not isinstance(run_id, int):
            return None, err("gt2_lan_chay_khong_co", run_id=str(run_id))
        dong = cur.execute("SELECT * FROM run_history WHERE run_id = ?", (run_id,)).fetchone()
        if dong is None:
            return None, err("gt2_lan_chay_khong_co", run_id=str(run_id))
        if dong["loai_chay"] == "thu":
            rows = [tuple(r) for r in cur.execute(
                "SELECT student_id, buoi, club_id, rank_in_list FROM ket_qua_thu WHERE run_id = ? "
                "ORDER BY student_id", (run_id,))]
            nhan = "thu"
        else:
            if goc is None or goc["run_id"] != run_id:
                return None, err("gt2_so_sanh_lan_cu", run_id=str(run_id))
            rows = [tuple(r) for r in cur.execute(
                "SELECT student_id, buoi, club_id, rank_in_student_pref FROM match_results "
                "ORDER BY student_id")]
            nhan = "chinh_thuc"
        return {"nhan": nhan, "run_id": run_id, "luat": self._luat_tu_dong(dong), "rows": rows}, None

    def _so_sanh_da_doc(self, run_a, run_b):
        with self._ket_noi_doc() as cur:
            goc = run_chinh_thuc_moi_nhat(cur)
            if goc is None:
                return None, err("gt2_chua_co_lan_chinh_thuc")
            if run_b is None:
                run_b = goc["run_id"]
            a, loi = self._tai_lan_chay(cur, run_a, goc)
            if loi:
                return None, loi
            b, loi = self._tai_lan_chay(cur, run_b, goc)
            if loi:
                return None, loi
            hs = {r[0]: {"ten": r[1] or "", "lop": r[2] or "", "nhom": r[3] or ""} for r in cur.execute(
                "SELECT student_id, name, class_id, reserve_group FROM students")}
            clb = {r[0]: {"ten": r[1] or r[0], "capacity": r[2]} for r in cur.execute(
                "SELECT club_id, name, capacity FROM clubs")}
            diem = {}
            for sid, cid, d in cur.execute("SELECT student_id, club_id, score FROM club_scores"):
                diem.setdefault(cid, {})[sid] = d
        try:
            tiers = luat_xep_cua(self._cfg_ws(nghiem=True)["rules"])["tiers"]
        except CauHinhHong as e:
            return None, loi_cau_hinh(e)
        return tieu_chi.so_sanh_lan_chay(
            a, b, {"students": hs, "clubs": clb, "diem": diem, "tiers": tiers}), None

    def so_sanh_lan_chay(self, run_a, run_b=None):
        """So sánh hai lần chạy (mặc định B = lần chính thức mới nhất). Chỉ đọc; không ghi gì.

        data: a, b (nhãn "chinh_thuc"/"thu", run_id, tiêu chí bằng lời), buoi_chung, tong, clb, nhom, lop,
        doi (em đổi chỗ — CHỈ cho màn quản lý / giáo viên), so_doi. Lần chính thức cũ không còn dòng
        kết quả thì báo `gt2_so_sanh_lan_cu` (không bịa số)."""
        try:
            kq, loi = self._so_sanh_da_doc(run_a, run_b)
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
        return _fail(loi) if loi else _ok(kq)

    def export_so_sanh_csv(self, output_path: str = "", run_a=None, run_b=None):
        """CSV (UTF-8 có BOM) các em đổi chỗ giữa hai lần chạy. Màn quản lý / giáo viên, không cho học sinh."""
        return self._khoa_xuat(self._export_so_sanh_da_khoa, "csv", output_path, run_a, run_b)

    def export_so_sanh_html(self, output_path: str = "", run_a=None, run_b=None):
        """Trang HTML một tệp, mở được khi không có mạng (không nạp gì từ ngoài), bản so sánh hai lần chạy."""
        return self._khoa_xuat(self._export_so_sanh_da_khoa, "html", output_path, run_a, run_b)

    def _export_so_sanh_da_khoa(self, kieu, output_path, run_a, run_b):
        try:
            kq, loi = self._so_sanh_da_doc(run_a, run_b)
            if loi:
                return _fail(loi)
            ten = "so_sanh_%s_%s.%s" % (kq["a"]["run_id"], kq["b"]["run_id"], kieu)
            try:
                duong = self._duong_xuat(output_path, ten, kem_duoi=())
            except LoiDuongXuat as e:
                return _fail(e.loi)
            if kieu == "csv":
                _ghi_csv(duong, ["student_id", "ho_ten", "lop", "buoi", "clb_a", "clb_b"],
                         [[d["student_id"], d["ten"], d["lop"], d["buoi"], d["tu_ten"], d["den_ten"]]
                          for d in kq["doi"]])
            else:
                with open(duong, "w", encoding="utf-8") as f:
                    f.write(tieu_chi.dung_html_so_sanh(kq))
            return _ok({"path": duong, "so_doi": kq["so_doi"]})
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    # ------------------------------------------------------------------------------------------
    # L4 — dùng tiêu chí của một lần chạy thử cho lần chính thức kế tiếp (chỉ lưu cấu hình)
    # ------------------------------------------------------------------------------------------
    def ap_dung_tieu_chi(self, run_id, slug=""):
        """Lưu luật xếp của MỘT lần chạy thử vào cấu hình workspace (qua `update_workspace_config`,
        giữ nguyên mọi khoá ngoài tiêu chí). KHÔNG chạy xếp, KHÔNG chép kết quả thử vào bảng chính
        thức: kết quả chính thức chỉ đổi khi quản trị chạy xếp chính thức. Chỉ nhận lần chạy THỬ."""
        try:
            with self._ket_noi_doc() as cur:
                cot = {r[1] for r in cur.execute("PRAGMA table_info(run_history)")}
                dong = None
                if "loai_chay" in cot and isinstance(run_id, int) and not isinstance(run_id, bool):
                    dong = cur.execute(
                        "SELECT luat_xep FROM run_history WHERE run_id = ? AND loai_chay = 'thu'",
                        (run_id,)).fetchone()
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
        if dong is None:
            return _fail(err("gt2_lan_chay_khong_co", run_id=str(run_id)))
        luat = luat_xep_hieu_luc(self._luat_tu_dong(dong))
        rules = {k: luat[k] for k in LUAT_XEP_MAC_DINH if k in luat}
        kq = self.update_workspace_config({"rules": rules}, slug)
        if not kq.get("ok"):
            return kq
        return _ok({"run_id": run_id, "luat": rules,
                    "mo_ta": tieu_chi.mo_ta_tieu_chi(rules, "vi"),
                    "mo_ta_en": tieu_chi.mo_ta_tieu_chi(rules, "en")})
