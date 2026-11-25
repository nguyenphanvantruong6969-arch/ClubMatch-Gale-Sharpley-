"""DK4: nối "bảng đăng ký (dk_*)" với "Sổ nhập" và bộ xếp.

L1  `so_nhap_b64_tu_dk`   — dữ liệu đăng ký -> Sổ nhập (qua `dk2_so_nhap`) -> base64 cho `import_so_nhap`.
                            Cố ý đi ĐÚNG đường nhập sổ có sẵn: cùng một đường với tệp xuất tay nên kết quả trùng khít.
L2  `dk_chot_va_xep`      — "Chốt và xếp": sao lưu -> soát -> nhập -> (khoá STB, xếp, ghi 1 giao dịch) -> chuyển giai đoạn.
                            Hỏng ở bước nào thì CSDL về nguyên trạng trước khi bấm; `run_history` không bao giờ bị xoá.
"""
import base64
import os
import sqlite3
import tempfile

import dk2_so_nhap
from api_dang_ky import CAC_GIAI_DOAN, QUAN_TRI, _Loi
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail

LUAT_BAT = ("fa_daa", "wharton")


def so_nhap_b64_tu_dk(du_lieu_ban_mau: dict) -> str:
    """JSON `dinhDang` 1 -> nội dung Sổ nhập .xlsx dạng base64. Dữ liệu sai: ném `dk2_so_nhap.LoiBanMau`."""
    with tempfile.TemporaryDirectory() as thu_muc:
        duong = os.path.join(thu_muc, "SO_NHAP_CLB.xlsx")
        dk2_so_nhap.ghi_tu_ban_mau(du_lieu_ban_mau, duong)
        with open(duong, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")


class DangKySangXepMixin:
    def _dk_bao_dam_luat(self):
        """Đăng ký cần chế độ giữ chỗ + huy chương (bản mẫu v8). Đã bật thì KHÔNG đụng vào cấu hình."""
        import cau_hinh_ws as ch
        cfg = ch.doc_cau_hinh(self.db_path)
        luat = dict(cfg.get("rules") or {})
        if all(luat.get(k) for k in LUAT_BAT):
            return False
        luat.update({k: True for k in LUAT_BAT})
        ch.ghi_cau_hinh(self.db_path, {**cfg, "rules": luat})
        return True

    def _dk_chup_bo_nho(self):
        """Ảnh chụp CSDL trong bộ nhớ (SQLite Backup API) để hoàn nguyên nếu bước sau hỏng."""
        nguon = sqlite3.connect(self.db_path)
        anh = sqlite3.connect(":memory:")
        try:
            nguon.backup(anh)
        finally:
            nguon.close()
        return anh

    def _dk_hoan_nguyen(self, anh):
        dich = sqlite3.connect(self.db_path)
        try:
            anh.backup(dich)
        finally:
            dich.close()

    def _dk_tom_tat_xep(self, cur):
        buoi = [r[0] for r in cur.execute("SELECT DISTINCT buoi FROM match_results ORDER BY buoi")]
        tong = cur.execute("SELECT COUNT(DISTINCT student_id) FROM match_results").fetchone()[0]
        theo_buoi = []
        for b in buoi:
            xep = cur.execute("SELECT COUNT(*) FROM match_results WHERE buoi = ? AND club_id IS NOT NULL", (b,)).fetchone()[0]
            hang = {}
            for h, n in cur.execute("SELECT rank_in_student_pref, COUNT(*) FROM match_results "
                                    "WHERE buoi = ? AND club_id IS NOT NULL GROUP BY 1", (b,)):
                hang[str(h)] = n
            theo_buoi.append({"buoi": b, "da_xep": xep, "chua_xep": cur.execute(
                "SELECT COUNT(*) FROM match_results WHERE buoi = ? AND club_id IS NULL", (b,)).fetchone()[0],
                "theo_nguyen_vong": hang})
        return {"so_hoc_sinh": tong, "theo_buoi": theo_buoi}

    def dk_ket_qua_xep(self, token):
        """Quản trị: tóm tắt lần xếp gần nhất (chỉ đọc). `da_xep` False nếu chưa xếp lần nào."""
        def lam(cur, p):
            r = cur.execute("SELECT run_id, seed, run_at, n_matched, n_total FROM run_history ORDER BY run_id DESC LIMIT 1").fetchone()
            if not r:
                return {"da_xep": False}
            return {"da_xep": True, "run_id": r[0], "seed": r[1], "run_at": r[2], "n_matched": r[3], "n_total": r[4],
                    **self._dk_tom_tat_xep(cur)}
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    def dk_chot_va_xep(self, token, seed=None):
        """Quản trị: nút "Chốt và xếp". Từ giai đoạn Nhập điểm; còn bài thi chưa có điểm thì từ chối.

        Thứ tự (bất biến 5): sao lưu (nhập sổ + chạy xếp đều sao lưu) -> soát -> nhập Sổ nhập (MỘT giao dịch) ->
        khoá/vẽ STB, xếp, ghi kết quả (MỘT giao dịch trong `run_pipeline`) -> chuyển giai đoạn "xuat".
        Hỏng sau khi đã nhập: hoàn nguyên CSDL về ảnh chụp trước khi bấm, trả `dk_chot_that_bai`."""
        if seed is not None:
            try:
                seed = int(seed)
            except (TypeError, ValueError):
                return _fail(err("dk_chot_seed_sai"))

        def doc(cur, p):
            if CAC_GIAI_DOAN.index(self._dk_gd) < CAC_GIAI_DOAN.index("nhap_diem"):
                raise _Loi("dk_sai_giai_doan", phan="nhap_diem")
            thieu = cur.execute("SELECT COUNT(*) FROM dk_nguyen_vong WHERE thi = 1 AND diem IS NULL").fetchone()[0]
            if thieu:
                raise _Loi("dk_thieu_diem", n=thieu)
            if seed is None:       # chưa chỉ định: dùng lại hạt giống của lần xếp trước (đã khoá), không có thì 42
                r = cur.execute("SELECT seed FROM run_history ORDER BY run_id DESC LIMIT 1").fetchone()
                return self._dk_ban_mau(cur), self._dk_gd, (r[0] if r and r[0] is not None else 42)
            return self._dk_ban_mau(cur), self._dk_gd, seed
        r = self._dk_chay(doc, QUAN_TRI, ghi=False, token=token)
        if not r["ok"]:
            return r
        ban_mau, giai_doan_cu, seed = r["data"]
        try:
            b64 = so_nhap_b64_tu_dk(ban_mau)
        except dk2_so_nhap.LoiBanMau as e:
            return _fail(err("dk_khong_xuat_duoc", detail="; ".join(e.loi[:3])))

        with self._khoa_ghi:
            anh = self._dk_chup_bo_nho()
            try:
                try:
                    self._backup_db()
                except Exception:
                    pass
                da_bat_luat = self._dk_bao_dam_luat()
                nap = self.import_so_nhap(b64)
                if not nap["ok"]:
                    self._dk_hoan_nguyen(anh)
                    return _fail(err("dk_chot_that_bai", buoc="nhap", detail="; ".join(
                        str(e.get("code")) for e in nap["errors"][:3])))
                xep = self.run_pipeline(seed=seed)
                if not xep["ok"]:
                    self._dk_hoan_nguyen(anh)
                    return _fail(err("dk_chot_that_bai", buoc="xep", detail="; ".join(
                        str(e.get("code")) for e in xep["errors"][:3])))
            except Exception as e:
                self._dk_hoan_nguyen(anh)
                return _fail(err("dk_chot_that_bai", buoc="loi", detail=str(e)))
            finally:
                anh.close()

        def ghi(cur, p):
            self._dk_dat(cur, "giai_doan", "xuat")
            self._dk_ghi_nk(cur, QUAN_TRI, "chot_va_xep", "seed %d, %s -> xuat" % (seed, giai_doan_cu))
            tt = self._dk_tom_tat_xep(cur)
            rid = cur.execute("SELECT MAX(run_id) FROM run_history").fetchone()[0]
            return {"da_xep": True, "seed": seed, "run_id": rid, "da_bat_luat": da_bat_luat,
                    "canh_bao": nap["data"].get("warnings", []), **tt}
        return self._dk_chay(ghi, QUAN_TRI, token=token)
