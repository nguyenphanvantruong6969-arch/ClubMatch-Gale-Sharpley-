"""CB1-L2 — API "Văn bản phương án xếp": chốt phương án, xem trạng thái, xuất PDF (bản dự kiến / bản chốt).

Chỉ quản trị (`phan_quyen._QUAN_TRI`). Chốt = MỘT hàng mới ở `workspace_settings` khoá `chot_phuong_an`
(`{nguoi, vai, luc, bam_luat, muc_tieu, luat_xep}`), không bảng, không cột, không `di_tru_schema`; `luat_xep` là
chuỗi `luat_xep_de_ghi(rules)` lúc chốt để so với `run_history.luat_xep` của lần xếp chính thức. Dòng nhật ký do
cổng `phan_quyen` ghi (`nhat_ky.nen_ghi`). `cau_hinh_ws.doc_cau_hinh` chỉ đọc khoá `config`, nên khoá mới KHÔNG
thể đổi kết quả. Xuất = chỉ đọc: không đụng `run_history`, `match_results`, `stb_lock`, cấu hình.
"""

import datetime
import json
import sqlite3

import muc_tieu as mt
import phuong_an_xep as pa
import tieu_chi
from api_workspace import CauHinhHong, LoiDuongXuat, loi_cau_hinh
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import luat_xep_de_ghi, run_chinh_thuc_moi_nhat

KHOA_CHOT = "chot_phuong_an"


def _bay_gio() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class PhuongAnMixin:
    def _doc_chot(self, cur):
        """Giá trị khoá `chot_phuong_an` (dict) hoặc None (chưa chốt / bảng chưa có / JSON hỏng)."""
        try:
            dong = cur.execute("SELECT value FROM workspace_settings WHERE key = ?", (KHOA_CHOT,)).fetchone()
        except sqlite3.OperationalError:
            return None
        if not dong or dong[0] is None:
            return None
        try:
            v = json.loads(dong[0])
        except (ValueError, TypeError):
            return None
        return v if isinstance(v, dict) else None

    def _moc_phuong_an(self, cfg: dict) -> dict:
        """Đọc năm mốc từ CSDL: `{chot, dvt, khoa, run, rules, lan_xep_khop}` (xem `phuong_an_xep.trang_thai_quy_trinh`)."""
        with self._ket_noi_doc() as cur:
            chot = self._doc_chot(cur)
            dvt = cur.execute("SELECT dau_van_tay, luc FROM dau_van_tay_chay WHERE id = 1").fetchone()
            khoa = cur.execute("SELECT is_locked, locked_at, seed FROM stb_lock WHERE id = 1").fetchone()
            run = run_chinh_thuc_moi_nhat(cur)
            luat_xep_run = run["luat_xep"] if run is not None and "luat_xep" in run.keys() else None
        khop = None
        if chot is not None and run is not None and "luat_xep" in chot:
            khop = (luat_xep_run or None) == (chot["luat_xep"] or None)
        return {
            "chot": {"nguoi": chot.get("nguoi"), "luc": chot.get("luc")} if chot else None,
            "dvt": {"dau_van_tay": dvt[0], "luc": dvt[1]} if dvt else None,
            "khoa": {"is_locked": khoa["is_locked"], "locked_at": khoa["locked_at"]} if khoa else None,
            "run": {"run_at": run["run_at"]} if run is not None else None,
            "rules": cfg["rules"], "lan_xep_khop": khop,
            "_chot_day_du": chot, "_seed": khoa["seed"] if khoa else None,
        }

    def _muc_tieu_hien_tai(self, cfg: dict):
        """`{id, nhom}` của thẻ mục tiêu đang hiệu lực, hoặc None khi luật bị sửa tay (`tuy_chinh`) / chưa chọn."""
        hs, clb = self._doc_hs_clb()
        da_chon = cfg.get("muc_tieu")
        mid = mt.nhan_dien_muc_tieu(cfg["rules"], clb, da_chon, hs)
        if mid not in mt.BO_MUC_TIEU:
            return None
        return {"id": mid, "nhom": (da_chon or {}).get("nhom") if da_chon and da_chon.get("id") == mid else None}

    def _hat_giong_khoa(self, moc: dict):
        k, seed = moc["khoa"], moc["_seed"]
        if k and k["is_locked"] and seed is not None:
            return {"seed": seed, "locked_at": k["locked_at"]}
        return None

    @staticmethod
    def _ly_do_ban_chot(moc: dict):
        """Mã lỗi vì sao chưa xuất được bản chốt, hoặc None (đủ: đã chốt + có lần xếp chính thức + đã khoá)."""
        if moc["chot"] and moc["run"] and moc["khoa"] and moc["khoa"]["is_locked"]:
            return None
        return "cb1_chua_du_dieu_kien_ban_chot"

    # ------------------------------------------------------------------ đọc
    def get_phuong_an_xep(self):
        """Trạng thái cho giao diện (chỉ đọc): đã chốt chưa (ai, lúc nào), năm mốc quy trình, cảnh báo,
        `co_the_xuat` (`du_kien` luôn True; `chot` + `ly_do_chot`), `co_the_in_hat_giong` (đã khoá), `muc_tieu`,
        `tom_tat_luat` (câu thường để hộp xác nhận hiện trước khi chốt). KHÔNG có hạt giống hay mã học sinh."""
        try:
            cfg = self._cfg_ws(nghiem=True)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        try:
            moc = self._moc_phuong_an(cfg)
            muc = self._muc_tieu_hien_tai(cfg)
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
        chot = moc["_chot_day_du"]
        bam = pa.bam_luat(cfg)
        nd = pa.dung_noi_dung("chot" if chot else "du_kien", tieu_chi.mo_ta_tieu_chi(cfg["rules"], "vi"), muc, moc,
                              chot, bam, False, None)
        ly_do = self._ly_do_ban_chot(moc)
        return _ok({
            "co_chot": chot is not None,
            "chot": moc["chot"],
            "khop_luc_chot": (chot.get("bam_luat") == bam) if chot else None,
            "quy_trinh": nd["quy_trinh"],
            "canh_bao": [c["ma"] for c in nd["canh_bao"]],
            "co_the_xuat": {"du_kien": True, "chot": ly_do is None, "ly_do_chot": ly_do},
            "co_the_in_hat_giong": self._hat_giong_khoa(moc) is not None,
            "muc_tieu": nd["muc_tieu"],
            "tom_tat_luat": [d["chu"] for d in nd["tieu_chi"] if d["nhom"] != "khong_dung"],
            # CB1-FIX3: hộp xác nhận hiện theo HAI nhóm có tiêu đề (trước đây hai nhóm gộp một danh sách, các dòng giống
            # nhau lặp lại nên trông như lỗi)
            "tom_tat_luat_tang": self._tom_tat_theo_tang(cfg["rules"], nd["tieu_chi"]),
        })

    @staticmethod
    def _tom_tat_theo_tang(rules, tieu_chi_dong):
        tieu_de = tieu_chi.tieu_de_tang(rules)
        ra = []
        for tang in ("tang_1", "tang_2"):
            dong = [d["chu"] for d in tieu_chi_dong if d["nhom"] == tang]
            if dong:
                ra.append({"tieu_de": tieu_de[tang]["vi"], "dong": dong})
        return ra

    # ------------------------------------------------------------------ chốt
    def chot_phuong_an(self):
        """Chốt phương án đang cài: ghi khoá `chot_phuong_an` (người, vai, lúc, dấu vân tay luật + mục tiêu, luật
        hiệu lực) trong MỘT giao dịch. Chốt lại được (ghi đè hàng cũ; mỗi lần có một dòng nhật ký). KHÔNG chạy xếp,
        KHÔNG đụng cấu hình, `run_history`, `match_results`, `stb_lock`. Trả `{nguoi, luc, bam_luat}`."""
        try:
            cfg = self._cfg_ws(nghiem=True)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        phien = self._dang_nhap.phien_hien_tai(self.db_path) if self._co_tai_khoan_nho() else None
        try:
            muc = self._muc_tieu_hien_tai(cfg)
            gia_tri = {"nguoi": phien["ten"] if phien else None, "vai": phien["vai"] if phien else None,
                       "luc": _bay_gio(), "bam_luat": pa.bam_luat(cfg), "muc_tieu": muc,
                       "luat_xep": luat_xep_de_ghi(cfg["rules"])}
            with self._ket_noi_ghi() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
                cur.execute("INSERT OR REPLACE INTO workspace_settings (key, value) VALUES (?, ?)",
                            (KHOA_CHOT, json.dumps(gia_tri, ensure_ascii=False)))
        except Exception as e:
            return _fail(err("cb1_khong_chot_duoc", detail=str(e)))
        return _ok({"nguoi": gia_tri["nguoi"], "luc": gia_tri["luc"], "bam_luat": gia_tri["bam_luat"]})

    # ------------------------------------------------------------------ xuất
    def export_van_ban_phuong_an_pdf(self, output_path: str = "", ban: str = "du_kien", in_hat_giong: bool = False):
        """PDF "Văn bản phương án xếp" bằng tiếng Việt (tệp xuất luôn tiếng Việt). `ban="du_kien"` luôn xuất được
        và KHÔNG có hạt giống; `ban="chot"` cần đã chốt + có lần xếp chính thức + đã khoá số bốc thăm
        (`cb1_chua_du_dieu_kien_ban_chot`). `in_hat_giong=True` chỉ ở bản chốt đã khoá, nếu không
        `cb1_hat_giong_chua_khoa`. Không mã, tên, điểm hay số bốc thăm của học sinh. Chỉ ĐỌC dữ liệu.
        Lỗi khác: `cb1_ban_la`, `xp1_thieu_thu_vien_pdf`. Trả `{path, n_trang, ban, canh_bao}`."""
        return self._khoa_xuat(self._export_van_ban_da_khoa, output_path, ban, in_hat_giong)

    def _export_van_ban_da_khoa(self, output_path, ban, in_hat_giong):
        import xuat_pdf
        try:
            if ban not in pa.BAN:
                return _fail(err("cb1_ban_la"))
            xuat_pdf.san_sang()
            cfg = self._cfg_ws(nghiem=True)
            moc = self._moc_phuong_an(cfg)
            if ban == "chot" and self._ly_do_ban_chot(moc):
                return _fail(err("cb1_chua_du_dieu_kien_ban_chot"))
            hat = self._hat_giong_khoa(moc)
            if in_hat_giong and (ban != "chot" or hat is None):
                return _fail(err("cb1_hat_giong_chua_khoa"))
            nd = pa.dung_noi_dung(ban, tieu_chi.mo_ta_tieu_chi(cfg["rules"], "vi"), self._muc_tieu_hien_tai(cfg),
                                  moc, moc["_chot_day_du"], pa.bam_luat(cfg), bool(in_hat_giong), hat, "vi")
            duong = self._duong_xuat(output_path, "phuong_an_xep_%s.pdf" % ban)
            duong = pa.dung_pdf(nd, duong)
            return _ok({"path": duong, "n_trang": xuat_pdf.dem_trang(duong), "ban": ban,
                        "canh_bao": [c["ma"] for c in nd["canh_bao"]]})
        except xuat_pdf.ThieuThuVienPdf:
            return _fail(err("xp1_thieu_thu_vien_pdf"))
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))
