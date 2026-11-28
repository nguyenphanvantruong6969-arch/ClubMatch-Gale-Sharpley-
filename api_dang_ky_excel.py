"""DK9: nạp MỘT tệp .xlsx cho cổng đăng ký — học sinh, giáo viên, phòng (giai đoạn Chuẩn bị, nhưng không khoá thêm luật nào).

Mô-đun này chỉ ĐỌC tệp, soát từng dòng rồi gọi lại đúng ba hàm có sẵn (`dk_hs_nap_danh_sach` chế độ "them", `dk_gv_tao_hang_loat`,
`dk_phong_luu`); mọi luật của từng danh sách (giai đoạn, PIN giữ nguyên, trùng tên bỏ qua) là luật của các hàm ấy, KHÔNG thêm luật mới.
Cổng tự kiểm quyền bằng phiên riêng (như mọi hàm `dk_*`): chỉ quản trị gọi được. Xem trước (`dk_excel_xem_truoc`) không ghi gì.

Tệp: chỉ .xlsx, ≤ 5 MB, ≤ 5 000 dòng dữ liệu mỗi trang tính, hàng 1 là tiêu đề. Trang tính «Học sinh» (Mã HS | Họ tên | Lớp), «Giáo viên»
(Họ tên), «Phòng» (Tên phòng | Sức chứa); khối suy từ lớp như ô dán (10A1 -> 10). Thiếu trang tính = danh sách ấy không nạp; không có
trang nào = lỗi. Mọi dữ liệu mẫu là DỮ LIỆU GIẢ LẬP.
"""

import base64
import binascii
import io
import os
import unicodedata
import zipfile

from api_dang_ky import GIAO_VIEN, HOC_SINH, QUAN_TRI, _bam, _khoi_cua_lop, _Loi, _pin_moi, _so_nguyen
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from so_nhap import bo_dau, o_thanh_chu

TOI_DA_MB = 5
TOI_DA_GIAI_NEN_MB = 50           # chặn tệp zip nén quá mức (cỡ sau giải nén), như `_soat_co_xlsx` của sổ nhập
TOI_DA_DONG = 5000                # dòng dữ liệu có chữ mỗi trang tính
TOI_DA_COT = 10                   # cột đầu được đọc (cột thừa phía sau bị bỏ qua)
TOI_DA_QUET = 20000               # dòng thô tối đa phải đọc (chặn trang tính toàn ô trống có định dạng)
TOI_DA_TEN = 60
TOI_DA_MA = 30

TEN_TRANG = {"hoc_sinh": "Học sinh", "giao_vien": "Giáo viên", "phong": "Phòng"}
TIEU_DE = {"hoc_sinh": ["Mã HS", "Họ tên", "Lớp"], "giao_vien": ["Họ tên"], "phong": ["Tên phòng", "Sức chứa"]}
# Tiêu đề chấp nhận được (so bằng `bo_dau`: không dấu, hoa/thường, gọn khoảng trắng; có thể thêm cột phụ phía sau).
TIEU_DE_CHAP_NHAN = {
    "hoc_sinh": [{"ma hs", "ma", "ma hoc sinh"}, {"ho ten", "ho va ten", "ten", "ten hoc sinh"}, {"lop"}],
    "giao_vien": [{"ho ten", "ho va ten", "ten", "ten giao vien"}],
    "phong": [{"ten phong", "phong", "ten"}, {"suc chua", "so cho", "chi tieu"}],
}
TRANG_HUONG_DAN = "Hướng dẫn"


def _gon(chu) -> str:
    """NFC, bỏ khoảng trắng đầu/cuối, gộp khoảng trắng giữa chữ thành một dấu cách."""
    return " ".join(unicodedata.normalize("NFC", str(chu)).split())


def _khoa_trang(ten) -> str:
    return unicodedata.normalize("NFC", str(ten or "")).strip().casefold()


def _loi_dong(sheet, dong, ly_do, **tham_so):
    return {"sheet": sheet, "dong": dong, "ly_do": ly_do, "params": tham_so}


class DangKyExcelMixin:
    # ------------------------------------------------------------ ghi tệp xuất ra đĩa (sửa 2026-11-28)
    # Trước đây hai nút dưới đây trả base64 để trình duyệt tự tải bằng `blob:`; cửa sổ pywebview của bản .exe CHẶN kiểu tải
    # đó (không báo gì), nên quản trị không nhận được tệp. Nay Python ghi tệp như mọi nút xuất khác (`_duong_xuat`: thư mục
    # Tải xuống, không ghi đè tệp cũ). `file_base64` vẫn trả kèm cho bên gọi cũ.
    def _dk_ghi_tep_xuat_dia(self, ten_tep, du_lieu):
        duong = self._duong_xuat("", ten_tep)
        with open(duong, "xb") as f:                           # "x": không bao giờ ghi đè (đã chọn tên chưa có)
            f.write(du_lieu)
        return duong

    def _dk_ghi_tep_xuat(self, ten_tep, du_lieu):
        """Ghi `du_lieu` (bytes) ra đĩa; hỏng thì ném `_Loi("dk_xuat_tep_hong")` để giao dịch đang mở rollback."""
        try:
            return self._dk_ghi_tep_xuat_dia(ten_tep, du_lieu)
        except Exception:
            import logging
            logging.getLogger(__name__).exception("dk: khong ghi duoc tep xuat %s", ten_tep)
            raise _Loi("dk_xuat_tep_hong") from None

    # ------------------------------------------------------------ đọc tệp (không đụng CSDL)
    @staticmethod
    def _dk_excel_giai_ma(file_base64, ten_tep):
        """base64 -> bytes của một .xlsx hợp lệ về hình thức (hoặc ném `_Loi`)."""
        if ten_tep and not str(ten_tep).strip().lower().endswith(".xlsx"):
            raise _Loi("dk_excel_khong_phai_xlsx")
        s = str(file_base64 or "")
        if s.startswith("data:") and "," in s:                       # FileReader.readAsDataURL
            s = s.split(",", 1)[1]
        try:
            du = base64.b64decode(s, validate=True)
        except (binascii.Error, ValueError):
            raise _Loi("dk_excel_khong_phai_xlsx") from None
        mb = 1024 * 1024
        if len(du) > TOI_DA_MB * mb:
            raise _Loi("dk_excel_qua_lon", max_mb=TOI_DA_MB)
        try:
            with zipfile.ZipFile(io.BytesIO(du)) as z:
                tong = sum(i.file_size for i in z.infolist())
        except zipfile.BadZipFile:
            raise _Loi("dk_excel_khong_phai_xlsx") from None         # gồm cả .csv đổi đuôi, tệp rỗng
        if tong > TOI_DA_GIAI_NEN_MB * mb:
            raise _Loi("dk_excel_qua_lon", max_mb=TOI_DA_MB)
        return du

    def _dk_excel_doc(self, file_base64, ten_tep=""):
        """Đọc ba trang tính. Trả `{khoá: [(số dòng Excel, [ô đã thành chuỗi]), ...]}` chỉ cho trang CÓ mặt (đã bỏ hàng tiêu đề và hàng trống).
        Ném `_Loi` ở lỗi mức tệp. Không đọc CSDL."""
        import openpyxl
        du = self._dk_excel_giai_ma(file_base64, ten_tep)
        try:
            wb = openpyxl.load_workbook(io.BytesIO(du), read_only=True, data_only=True)
        except Exception:
            raise _Loi("dk_excel_khong_phai_xlsx") from None
        try:
            theo_ten = {}
            for ten in wb.sheetnames:
                theo_ten.setdefault(_khoa_trang(ten), ten)
            ra = {}
            for khoa, ten_chuan in TEN_TRANG.items():
                ten = theo_ten.get(_khoa_trang(ten_chuan))
                if ten is None:
                    continue
                hang = self._dk_excel_hang(wb[ten], khoa)
                if hang is not None:
                    ra[khoa] = hang
            if not ra:
                raise _Loi("dk_excel_khong_co_sheet")
            return ra
        finally:
            wb.close()

    @staticmethod
    def _dk_excel_hang(ws, khoa):
        """Các hàng dữ liệu của một trang tính; None nếu trang hoàn toàn trống (coi như vắng)."""
        tieu_de, ra = None, []
        for so_dong, hang in enumerate(ws.iter_rows(max_col=TOI_DA_COT, values_only=True), start=1):      # chỉ đọc vài cột đầu: trang tính khai kích thước XFD1048576 vẫn nhanh
            if so_dong > TOI_DA_QUET + 1:
                raise _Loi("dk_excel_qua_nhieu_dong", sheet=TEN_TRANG[khoa], toi_da=TOI_DA_DONG)
            o = [o_thanh_chu(v) for v in hang]
            if not any(o):
                continue
            if tieu_de is None:
                tieu_de = o
                mong = TIEU_DE_CHAP_NHAN[khoa]
                if len(o) < len(mong) or any(bo_dau(o[i]) not in mong[i] for i in range(len(mong))):
                    raise _Loi("dk_excel_tieu_de_sai", sheet=TEN_TRANG[khoa], mong_doi=" | ".join(TIEU_DE[khoa]))
                continue
            if len(ra) >= TOI_DA_DONG:
                raise _Loi("dk_excel_qua_nhieu_dong", sheet=TEN_TRANG[khoa], toi_da=TOI_DA_DONG)
            ra.append((so_dong, o))
        return None if tieu_de is None else ra

    # ------------------------------------------------------------ soát từng dòng (thuần, không đụng CSDL)
    @staticmethod
    def _dk_excel_soat_hs(hang, k_tu, k_den):
        hop_le, loi, thay = [], [], set()
        for so_dong, o in hang:
            o = o + [""] * (3 - len(o))
            ma_, ten, lop = _gon(o[0]), _gon(o[1]), _gon(o[2])
            khoi = _khoi_cua_lop(lop)
            if not ma_:
                ly = ("dk_excel_ma_trong", {})
            elif " " in ma_ or len(ma_) > TOI_DA_MA:
                ly = ("dk_excel_ma_sai", {})
            elif not ten:
                ly = ("dk_excel_ten_trong", {})
            elif len(ten) > TOI_DA_TEN:
                ly = ("dk_excel_ten_dai", {})
            elif not lop:
                ly = ("dk_excel_lop_trong", {})
            elif khoi is None or not k_tu <= khoi <= k_den:
                ly = ("dk_excel_khoi_ngoai", {"tu": k_tu, "den": k_den})
            elif ma_ in thay:
                ly = ("dk_excel_trung_ma", {})
            else:
                thay.add(ma_)
                hop_le.append((so_dong, ma_, ten, lop))
                continue
            loi.append(_loi_dong("hoc_sinh", so_dong, ly[0], **ly[1]))
        return hop_le, loi

    @staticmethod
    def _dk_excel_soat_gv(hang):
        hop_le, loi, thay = [], [], set()
        for so_dong, o in hang:
            ten = _gon(o[0]) if o else ""
            if not ten:
                ly = "dk_excel_ten_trong"
            elif len(ten) > TOI_DA_TEN:
                ly = "dk_excel_ten_dai"
            elif ten in thay:
                ly = "dk_excel_trung_ten"
            else:
                thay.add(ten)
                hop_le.append((so_dong, ten))
                continue
            loi.append(_loi_dong("giao_vien", so_dong, ly))
        return hop_le, loi

    @staticmethod
    def _dk_excel_soat_phong(hang):
        hop_le, loi, thay = [], [], set()
        for so_dong, o in hang:
            o = o + [""] * (2 - len(o))
            ten = _gon(o[0])
            sc = _so_nguyen(_gon(o[1])) if o[1] else None
            if not ten:
                ly = "dk_excel_ten_trong"
            elif len(ten) > TOI_DA_TEN:
                ly = "dk_excel_ten_dai"
            elif sc is None or sc <= 0:
                ly = "dk_excel_suc_chua"
            elif ten in thay:
                ly = "dk_excel_trung_ten"
            else:
                thay.add(ten)
                hop_le.append((so_dong, ten, sc))
                continue
            loi.append(_loi_dong("phong", so_dong, ly))
        return hop_le, loi

    def _dk_excel_ke_hoach(self, token, file_base64, ten_tep="", bo_hoc_sinh=False):
        """Đọc + soát + đối chiếu CSDL (chỉ ĐỌC). Trả `{ke_hoach, tom_tat}`:
        `ke_hoach[khoá]` = {hop_le: [...], moi: [...], da_co: [...], loi: [...]}; `tom_tat` là phần xem trước cho giao diện.
        `bo_hoc_sinh` (giao diện đặt ở giai đoạn học sinh đã bắt đầu đăng ký, như ô dán: «không thêm hay thay danh sách nữa») bỏ qua trang
        «Học sinh»; mặc định False = hành vi như `dk_hs_nap_danh_sach` ("them" không có khoá giai đoạn ở máy chủ)."""
        def lam(cur, p):
            hang = self._dk_excel_doc(file_base64, ten_tep)
            _, (k_tu, k_den) = self._dk_buoi_khoi(cur)
            co_hs = {r[0] for r in cur.execute("SELECT student_id FROM dk_hoc_sinh")}
            co_gv = {r[0] for r in cur.execute("SELECT ten FROM dk_giao_vien")}
            co_ph = {r[0] for r in cur.execute("SELECT ten FROM dk_phong")}
            kh = {}
            if bo_hoc_sinh:
                hang.pop("hoc_sinh", None)
            if "hoc_sinh" in hang:
                hl, loi = self._dk_excel_soat_hs(hang["hoc_sinh"], k_tu, k_den)
                kh["hoc_sinh"] = dict(hop_le=hl, loi=loi, moi=[x for x in hl if x[1] not in co_hs], da_co=[x for x in hl if x[1] in co_hs])
            if "giao_vien" in hang:
                hl, loi = self._dk_excel_soat_gv(hang["giao_vien"])
                kh["giao_vien"] = dict(hop_le=hl, loi=loi, moi=[x for x in hl if x[1] not in co_gv], da_co=[x for x in hl if x[1] in co_gv])
            if "phong" in hang:
                hl, loi = self._dk_excel_soat_phong(hang["phong"])
                kh["phong"] = dict(hop_le=hl, loi=loi, moi=[x for x in hl if x[1] not in co_ph], da_co=[x for x in hl if x[1] in co_ph])
            tom = {"thieu_sheet": [k for k in TEN_TRANG if k not in kh and not (bo_hoc_sinh and k == "hoc_sinh")], "hs_bi_khoa": bool(bo_hoc_sinh)}
            for k in TEN_TRANG:
                m = kh.get(k)
                tom[k] = {"co": m is not None, "tong": len(m["hop_le"]) + len(m["loi"]) if m else 0, "moi": len(m["moi"]) if m else 0,
                          "da_co": len(m["da_co"]) if m else 0, "loi": list(m["loi"]) if m else []}
            tom["so_hop_le"] = sum(len(m["hop_le"]) for m in kh.values())
            tom["co_the_nap"] = tom["so_hop_le"] > 0
            return {"ke_hoach": kh, "tom_tat": tom}
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    # ------------------------------------------------------------ ba hàm công khai
    def dk_excel_mau(self, token):
        """Tệp mẫu: ba trang tính chỉ có hàng tiêu đề (không có dòng ví dụ, để khỏi nạp nhầm) + trang «Hướng dẫn» (bị bỏ qua khi nạp).
        Trả `{ten_tep, file_base64}`."""
        def lam(cur, p):
            import openpyxl
            from openpyxl.styles import Alignment, Font
            wb = openpyxl.Workbook()
            wb.remove(wb.active)
            rong = {"hoc_sinh": (14, 32, 12), "giao_vien": (36,), "phong": (22, 14)}
            for k, ten in TEN_TRANG.items():
                ws = wb.create_sheet(ten)
                ws.append(TIEU_DE[k])
                for c in ws[1]:
                    c.font = Font(bold=True)
                for i, w in enumerate(rong[k]):
                    ws.column_dimensions[chr(ord("A") + i)].width = w
                ws.freeze_panes = "A2"
                if k == "hoc_sinh":                                    # mã dạng chữ: không để Excel đổi 0123 thành 123
                    ws.column_dimensions["A"].number_format = "@"
            hd = wb.create_sheet(TRANG_HUONG_DAN)
            for dong in (
                ["Cách dùng"],
                ["1. Điền dữ liệu vào các trang «Học sinh», «Giáo viên», «Phòng», từ hàng 2 trở xuống. Không xoá hàng 1 (tiêu đề)."],
                ["2. Không cần điền đủ ba trang: trang nào để trống thì danh sách đó không được nạp."],
                ["3. Khối được suy từ lớp (10A1 là khối 10). Không có cột Khối."],
                ["4. Nạp lại tệp đã sửa được: học sinh cũ được cập nhật và giữ nguyên PIN; giáo viên, phòng đã có thì bỏ qua."],
                ["5. Trang này không được nạp. Ví dụ (dữ liệu giả lập):"],
                ["Học sinh", "10001", "Nguyễn Văn An", "10A1"],
                ["Giáo viên", "Cô Lê Thị Hoa"],
                ["Phòng", "P101", 40],
            ):
                hd.append(dong)
            hd["A1"].font = Font(bold=True)
            hd.column_dimensions["A"].width = 18
            for r in hd.iter_rows(min_row=2, max_row=5):
                r[0].alignment = Alignment(wrap_text=False)
            bo = io.BytesIO()
            wb.save(bo)
            duong = self._dk_ghi_tep_xuat("MAU_DANG_KY.xlsx", bo.getvalue())
            return {"ten_tep": "MAU_DANG_KY.xlsx", "file_base64": base64.b64encode(bo.getvalue()).decode("ascii"),
                    "path": duong, "dir": os.path.dirname(duong)}
        return self._dk_chay(lam, QUAN_TRI, ghi=False, token=token)

    def dk_pin_xuat_excel(self, token, pham_vi, lop=None, xac_nhan=False):
        """VG1-L2 (D2). PIN chỉ lưu băm nên không «xem lại» được: xuất = ĐẶT LẠI PIN rồi ghi tệp .xlsx (trang «Học sinh»: Mã | Họ tên |
        Lớp | PIN; trang «Giáo viên»: Họ tên | PIN). `pham_vi` = hs | gv | tat_ca; `lop` chỉ lọc học sinh. Chỉ quản trị; không có
        `xac_nhan=True` thì lỗi `dk_can_xac_nhan_pin` (n người) và KHÔNG đổi gì. Mỗi người một PIN mới, xoá bộ đếm khoá của họ,
        nhật ký chỉ ghi số người (không ghi PIN). Trả `{ten_tep, file_base64, so_hs, so_gv}`."""
        def lam(cur, p):
            if pham_vi not in ("hs", "gv", "tat_ca"):
                raise _Loi("dk_pham_vi_la")
            hs, gv = [], []
            if pham_vi in ("hs", "tat_ca"):
                q = "SELECT student_id, ho_ten, lop FROM dk_hoc_sinh"
                tham = ()
                if lop not in (None, ""):
                    q, tham = q + " WHERE lop = ?", (str(lop),)
                hs = cur.execute(q + " ORDER BY lop, student_id", tham).fetchall()
            if pham_vi in ("gv", "tat_ca"):
                gv = cur.execute("SELECT gv_id, ten FROM dk_giao_vien ORDER BY ten").fetchall()
            if xac_nhan is not True:
                raise _Loi("dk_can_xac_nhan_pin", n=len(hs) + len(gv))
            import openpyxl
            from openpyxl.styles import Font
            wb = openpyxl.Workbook()
            wb.remove(wb.active)
            dong_hs, dong_gv = [], []
            for ma, ten, lp in hs:
                pin = _pin_moi()
                b, m = _bam(pin)
                cur.execute("UPDATE dk_hoc_sinh SET pin_bam = ?, pin_muoi = ? WHERE student_id = ?", (b, m, ma))
                cur.execute("DELETE FROM dk_cai_dat WHERE khoa = ?", (self._dk_khoa_dn(HOC_SINH, ma),))
                dong_hs.append((ma, ten, lp, pin))
            for gid, ten in gv:
                pin = _pin_moi()
                b, m = _bam(pin)
                cur.execute("UPDATE dk_giao_vien SET pin_bam = ?, pin_muoi = ? WHERE gv_id = ?", (b, m, gid))
                cur.execute("DELETE FROM dk_cai_dat WHERE khoa = ?", (self._dk_khoa_dn(GIAO_VIEN, ten),))
                dong_gv.append((ten, pin))
            for ten_ws, tieu, dong, rong in (("Học sinh", ["Mã HS", "Họ tên", "Lớp", "PIN"], dong_hs, (14, 32, 12, 8)),
                                             ("Giáo viên", ["Họ tên", "PIN"], dong_gv, (36, 8))):
                ws = wb.create_sheet(ten_ws)
                ws.append(tieu)
                for c in ws[1]:
                    c.font = Font(bold=True)
                for d in dong:
                    ws.append([str(x) for x in d])                 # mọi ô là chữ: PIN «0042» và mã «0123» không bị Excel đổi thành số
                    for c in ws[ws.max_row]:
                        c.number_format = "@"
                for i, w in enumerate(rong):
                    ws.column_dimensions[chr(ord("A") + i)].width = w
                ws.freeze_panes = "A2"
            self._dk_ghi_nk(cur, QUAN_TRI, "xuat_pin", "%s hs=%d gv=%d" % (pham_vi, len(dong_hs), len(dong_gv)))
            bo = io.BytesIO()
            wb.save(bo)
            # Ghi tệp TRONG giao dịch đặt lại PIN: ghi hỏng thì `_Loi` -> rollback -> PIN cũ còn nguyên (trước đây PIN đã đổi
            # mà tệp không tới tay ai). Commit hỏng sau khi đã ghi thì xoá tệp (PIN trong tệp không còn hiệu lực).
            doi["path"] = self._dk_ghi_tep_xuat("PHIEU_PIN.xlsx", bo.getvalue())
            doi.update(hs=[x[0] for x in hs], gv=[x[0] for x in gv])
            return {"ten_tep": "PHIEU_PIN.xlsx", "file_base64": base64.b64encode(bo.getvalue()).decode("ascii"),
                    "so_hs": len(dong_hs), "so_gv": len(dong_gv), "path": doi["path"], "dir": os.path.dirname(doi["path"])}
        doi = {}
        r = self._dk_chay(lam, QUAN_TRI, token=token)
        if not r["ok"] and doi.get("path"):
            try:
                os.remove(doi["path"])
            except OSError:
                pass
        if r["ok"]:                                                # PIN đã đổi thì phiên cũ của những người đó chết
            self._dk_huy_phien(HOC_SINH, doi.get("hs", []))
            self._dk_huy_phien(GIAO_VIEN, doi.get("gv", []))
        return r

    def dk_excel_xem_truoc(self, token, file_base64, ten_tep="", bo_hoc_sinh=False):
        """Chỉ ĐỌC: trả `{hoc_sinh|giao_vien|phong: {co, tong, moi, da_co, loi: [{sheet, dong, ly_do, params}]}, thieu_sheet,
        so_hop_le, co_the_nap, hs_bi_khoa}`. `da_co`: học sinh = sẽ được cập nhật (giữ PIN); giáo viên / phòng = sẽ bị bỏ qua. Không ghi gì (kể cả nhật ký)."""
        r = self._dk_excel_ke_hoach(token, file_base64, ten_tep, bo_hoc_sinh)
        return _ok(r["data"]["tom_tat"]) if r["ok"] else r

    def dk_excel_nap(self, token, file_base64, ten_tep="", bo_hoc_sinh=False):
        """Nạp các dòng hợp lệ, bỏ dòng lỗi và liệt kê chúng. Đọc lại tệp (không tin kết quả xem trước của máy khách).
        Trả `{hoc_sinh: {moi, da_co, pin: [{ma, pin, ten, lop}]}, giao_vien: {moi, da_co, pin: [{ma, ten, pin}]}, phong: {moi, da_co},
        loi: [...], thieu_sheet}`; PIN chỉ có trong lần trả này (CSDL chỉ lưu băm). Mỗi danh sách là một giao dịch của hàm có sẵn;
        nạp lại cùng tệp an toàn (idempotent) nếu một bước giữa chừng hỏng."""
        r = self._dk_excel_ke_hoach(token, file_base64, ten_tep, bo_hoc_sinh)
        if not r["ok"]:
            return r
        kh, tom = r["data"]["ke_hoach"], r["data"]["tom_tat"]
        if not tom["so_hop_le"]:
            return self._dk_excel_het_dong(tom)
        ra = {"hoc_sinh": {"moi": 0, "da_co": 0, "pin": []}, "giao_vien": {"moi": 0, "da_co": 0, "pin": []},
              "phong": {"moi": 0, "da_co": 0}, "loi": [], "thieu_sheet": tom["thieu_sheet"]}
        if "phong" in kh:
            ra["phong"]["da_co"] = len(kh["phong"]["da_co"])
            for _, ten, sc in kh["phong"]["moi"]:
                rr = self.dk_phong_luu(token, ten, sc)
                if rr["ok"]:
                    ra["phong"]["moi"] += 1
                elif rr["errors"][0].get("code") == "dk_phong_trung":      # có người thêm cùng tên giữa lúc xem và nạp
                    ra["phong"]["da_co"] += 1
                else:
                    return rr
        if kh.get("giao_vien", {}).get("moi"):
            rr = self.dk_gv_tao_hang_loat(token, "\n".join(x[1] for x in kh["giao_vien"]["moi"]))
            if not rr["ok"]:
                return rr
            ra["giao_vien"]["moi"] = len(rr["data"]["da_tao"])
            ra["giao_vien"]["da_co"] = len(kh["giao_vien"]["da_co"]) + len(rr["data"]["bo_qua"])
            ra["giao_vien"]["pin"] = [{"ma": x["ten"], "ten": x["ten"], "pin": x["pin"]} for x in rr["data"]["da_tao"]]
        elif "giao_vien" in kh:
            ra["giao_vien"]["da_co"] = len(kh["giao_vien"]["da_co"])
        if kh.get("hoc_sinh", {}).get("hop_le"):
            ds = {x[1]: x for x in kh["hoc_sinh"]["hop_le"]}
            van = "\n".join("%s\t%s\t%s" % (ma_, ten, lop) for _, ma_, ten, lop in kh["hoc_sinh"]["hop_le"])
            rr = self.dk_hs_nap_danh_sach(token, van, "them")
            if not rr["ok"]:
                return rr
            d = rr["data"]
            ra["hoc_sinh"] = {"moi": d["moi"], "da_co": d["da_co"],
                              "pin": [{"ma": x["ma"], "pin": x["pin"], "ten": ds[x["ma"]][2], "lop": ds[x["ma"]][3]} for x in d["pin"]]}
        for k in ("hoc_sinh", "giao_vien", "phong"):
            ra["loi"] += tom[k]["loi"]
        return _ok(ra)

    @staticmethod
    def _dk_excel_het_dong(tom):
        """Không có dòng hợp lệ nào: báo lỗi (kèm số dòng lỗi) thay vì nạp rỗng."""
        so_loi = sum(len(tom[k]["loi"]) for k in TEN_TRANG)
        return _fail(err("dk_excel_khong_co_dong", n=so_loi))
