"""Xuất kết quả: tệp tổng, tệp tổng hợp, tệp theo CLB/buổi và tệp Excel.

Một phần của PipelineAPI (xem api.py) — tách riêng cho dễ đọc; mọi hàm
public ở đây vẫn là hàm của PipelineAPI và giao diện gọi được như cũ.
"""

import datetime
import os
import shutil
import sys
import time

from api_chung import (
    _an_toan_cho_excel,
    _ghi_csv,
    _now,
    _phan_tram_vn,
    _so_vn,
    duong_dan_khong_de,
    thu_muc_tai_ve,
)
from cau_hinh_ws import doc_cau_hinh
from api_workspace import CauHinhHong, LoiDuongXuat, loi_cau_hinh
from i18n_errors import err
from lop_hoc_sinh import chuan_hoa_lop
from nhan_ws import dien as dien_nhan
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import (
    dung_fa_daa,
    BUOI_MAC_DINH, dau_van_tay_du_lieu, diem_theo_nguoi, dung_wharton, khoa_sap_buoi,
    loc_chinh_thuc,
)
import fa_bien_ban
import fa_ly_do
import so_nhap


class XuatKetQuaMixin:
    # -----------------------------------------------------------------
    # XUẤT KẾT QUẢ
    #
    # File này là SẢN PHẨM CUỐI của cả quy trình — nhà trường dán bảng,
    # gửi phụ huynh, phát cho giáo viên phụ trách từng CLB. Bản cũ chỉ
    # xuất hai cột mã (student_id,club_id): nhìn vào không biết em nào
    # tên gì, đỗ CLB nào, đỗ nguyện vọng thứ mấy. Toàn bộ dữ liệu đó ĐÃ
    # có sẵn trong DB, chỉ là câu lệnh xuất không lấy.
    # -----------------------------------------------------------------

    # Ký tự KHÔNG được phép có trong tên file trên Windows, cộng thêm
    # dấu phân cách đường dẫn. club_id do trường tự đặt và
    # create_or_update_club KHÔNG giới hạn ký tự, nên một mã như
    # "../ngoai" hay "khoi 10/11" sẽ làm file rơi ra ngoài thư mục kết
    # quả (hoặc ghi đè file khác) nếu ghép thẳng vào tên file.
    _KY_TU_CAM_TRONG_TEN_FILE = '<>:"/\\|?*'

    @staticmethod
    def _ten_file_an_toan(raw: str, mac_dinh: str = "club") -> str:
        ten = "".join(
            "_" if (c in XuatKetQuaMixin._KY_TU_CAM_TRONG_TEN_FILE or ord(c) < 32) else c
            for c in (raw or "")
        ).strip(" .")
        # "..", "." và chuỗi rỗng đều không dùng làm tên file được
        if not ten or ten in (".", ".."):
            return mac_dinh
        # Windows không cho tạo tệp tên CON, NUL, COM1... (kể cả khi có
        # đuôi: "nul.csv" cũng hỏng). CLB mã "CON" từng làm lần xuất báo lỗi.
        if ten.split(".")[0].upper() in XuatKetQuaMixin._TEN_DANH_RIENG_WINDOWS:
            return "_" + ten
        return ten

    _TEN_DANH_RIENG_WINDOWS = frozenset(
        ["CON", "PRN", "AUX", "NUL"]
        + ["COM%d" % i for i in range(1, 10)]
        + ["LPT%d" % i for i in range(1, 10)])

    @staticmethod
    def _ten_chua_dung(ten: str, da_dung: set) -> str:
        """`ten`, hoặc `ten_2`, `ten_3`... — cái đầu tiên CHƯA dùng.

        So KHÔNG phân biệt hoa/thường: ổ NTFS trên Windows coi `clb_a.csv`
        và `CLB_A.csv` là một tệp, mà phần mềm lại cho phép hai mã CLB đó
        cùng tồn tại (_khop_club_id) — tệp sau từng ghi đè tệp trước, một
        giáo viên cầm nhầm danh sách. Thử đến khi trống thật, vì cách cũ
        (ghép số đếm) vẫn đụng một CLB tên sẵn là `a_2`.
        """
        ung_vien, n = ten, 1
        while ung_vien.casefold() in da_dung:
            n += 1
            ung_vien = f"{ten}_{n}"
        da_dung.add(ung_vien.casefold())
        return ung_vien

    # -----------------------------------------------------------------
    # SỔ EXCEL KẾT QUẢ
    #
    # Thứ tự trang = thứ tự người đọc cần: mở ra là trang hướng dẫn với
    # mấy con số chính và mục lục bấm được, rồi danh sách, rồi từng CLB để
    # phát cho giáo viên; phần kỹ thuật (hạt giống, số bốc thăm) để cuối.
    # -----------------------------------------------------------------
    TRANG_SO_EXCEL = ("Hướng dẫn", "Danh sách {person_l}", "Theo {slot_sl}",
                      "Theo {cohort_l}", "Chưa có chỗ", "Thống kê", "Dấu vết (kỹ thuật)")
    # Chỉ có khi workspace bật điểm quyết tâm (A13.4); đứng sau "Chưa có chỗ". Tắt thì sổ có đúng
    # sáu trang như trước.
    TRANG_DIEM_CHUAN = "Điểm chuẩn"

    def _khoa_trang_so_excel(self) -> tuple:
        """Các trang của sổ kết quả, theo thứ tự: sáu trang cũ, thêm "Điểm chuẩn" khi bật."""
        if not dung_wharton(self._cfg_ws(nghiem=True)["rules"]):
            return self.TRANG_SO_EXCEL
        cu = self.TRANG_SO_EXCEL
        i = cu.index("Chưa có chỗ") + 1
        return cu[:i] + (self.TRANG_DIEM_CHUAN,) + cu[i:]

    def _nhan_xuat(self) -> dict:
        """Nhãn tiếng Việt của workspace đang mở, cho chữ trong tệp xuất.

        Tệp xuất luôn viết tiếng Việt (như trước). Đọc MỘT lần mỗi lần xuất rồi truyền
        xuống các hàm viết tệp — không hàm nào tự lục trạng thái chung."""
        return doc_cau_hinh(self.db_path)["labels"]

    @staticmethod
    def _ten_trang_hop_le(ten: str, da_dung: set) -> str:
        """Tên trang Excel: bỏ ký tự Excel cấm (`[ ] : * ? / \\`), tối đa 31 ký tự, không trùng.

        Nhãn do người dùng đặt ("Dự án/Phòng") có thể mang ký tự cấm; để nguyên thì
        openpyxl từ chối và cả lần xuất hỏng. Phần lọc ký tự dùng `so_nhap._ten_sheet` (nguồn
        duy nhất); ở đây chỉ thêm khử trùng."""
        sach = so_nhap._ten_sheet(ten) or "Trang"      # MỘT bộ lọc ký tự cấm, chung với sổ nhập
        ung_vien, n = sach, 1
        while ung_vien.casefold() in da_dung:
            n += 1
            hau = " (%d)" % n
            ung_vien = sach[:31 - len(hau)] + hau
        da_dung.add(ung_vien.casefold())
        return ung_vien

    def _ghi_so_excel(self, path: str, du: dict) -> list:
        """Ghi sổ kết quả sáu trang từ `_du_lieu_xuat`. Trả về tên các trang.

        Mọi trang đều có dòng tên trang và một câu nói trang dùng làm gì,
        in vừa khổ A4 theo chiều ngang, có số trang ở chân. Trang danh sách
        khoá dòng tiêu đề và bật bộ lọc. Các trang luôn có mặt, kể cả khi
        trống (kèm một dòng nói vì sao trống) — thứ tự trang cố định thì
        người dùng quen tay, không phải đi tìm.
        """
        from openpyxl import Workbook

        from so_excel import Trang

        nhan = du.get("nhan")
        wb = Workbook()
        wb.remove(wb.active)
        # Khoá trong `TRANG_SO_EXCEL` là tên MẪU (có chỗ giữ danh từ); tên thật điền
        # nhãn của workspace. `du["ten_trang"]` đưa tên thật cho các trang liên kết nhau.
        da_dung: set = set()
        du["khoa_trang"] = self._khoa_trang_so_excel()
        du["ten_trang"] = {
            khoa: self._ten_trang_hop_le(dien_nhan(khoa, nhan), da_dung)
            for khoa in du["khoa_trang"]}
        trang = {khoa: Trang(wb.create_sheet(du["ten_trang"][khoa]), nhan)
                 for khoa in du["khoa_trang"]}

        bao = self._bang_bao_cao(so=True)
        xuat_luc = _now()
        tt = self.get_trang_thai_ket_qua()
        co_ket_qua = bool(tt.get("ok") and tt["data"]["co_ket_qua"])
        ket_qua_cu = bool(co_ket_qua and tt["data"]["ket_qua_cu"])

        self._trang_huong_dan(trang["Hướng dẫn"], du, bao, xuat_luc,
                              co_ket_qua, ket_qua_cu)
        self._trang_danh_sach(trang["Danh sách {person_l}"], du, co_ket_qua)
        self._trang_theo_clb(trang["Theo {slot_sl}"], du)
        du["ket_qua_cu"] = ket_qua_cu
        self._trang_theo_lop(trang["Theo {cohort_l}"], du)
        self._trang_chua_co_cho(trang["Chưa có chỗ"], bao, co_ket_qua)
        if self.TRANG_DIEM_CHUAN in trang:
            self._trang_diem_chuan(trang[self.TRANG_DIEM_CHUAN], du, co_ket_qua, ket_qua_cu)
        self._trang_thong_ke(trang["Thống kê"], bao, du)
        self._trang_dau_vet(trang["Dấu vết (kỹ thuật)"], du, xuat_luc)

        wb.active = 0
        wb.save(path)
        return [du["ten_trang"][khoa] for khoa in du["khoa_trang"]]

    def _luu_so_excel(self, path: str, du: dict) -> list:
        """Ghi sổ vào tệp TẠM cạnh `path`, xong mới đổi tên đè lên `path`.

        Hỏng giữa chừng (đầy đĩa, dữ liệu lạ) thì chỉ xoá tệp tạm: tệp cũ ở
        `path` — có khi là tệp người dùng chỉ định — còn nguyên, và Tải
        xuống không bao giờ có một tệp .xlsx dở mở ra báo hỏng. Trước đây
        nhánh lỗi xoá thẳng `path`, tức xoá luôn tệp có sẵn của người dùng.
        """
        import uuid

        # Khong dung tempfile.mkstemp: tep do mang quyen 0600 va giu nguyen
        # quyen ay sau khi doi ten, khac voi moi tep xuat khac.
        tam = os.path.join(os.path.dirname(os.path.abspath(path)),
                           ".~%s.xlsx" % uuid.uuid4().hex)
        try:
            trang = self._ghi_so_excel(tam, du)
            os.replace(tam, path)
            return trang
        finally:
            if os.path.exists(tam):
                try:
                    os.remove(tam)
                except OSError:
                    pass

    def _trang_huong_dan(self, t, du, bao, xuat_luc, co_ket_qua, ket_qua_cu):
        from so_excel import CHU_CANH_BAO

        t.tieu_de("KẾT QUẢ PHÂN BỔ {slot_u}", "Xuất lúc %s." % xuat_luc)
        # Tep mang di hop phai tu noi duoc no con dung khong. Man hinh co dai
        # canh bao, nhung tep ra khoi phan mem thi chi con dong nay.
        if not co_ket_qua:
            t.ghi_chu("Chưa chạy sắp xếp lần nào: các trang danh sách đang "
                      "trống. Hãy chạy sắp xếp rồi xuất lại.", CHU_CANH_BAO)
        elif ket_qua_cu:
            t.ghi_chu("CHÚ Ý: dữ liệu đã sửa sau lần chạy này, kết quả có thể "
                      "đã cũ. Hãy chạy lại rồi xuất lại.", CHU_CANH_BAO)

        co_cho: dict = {}
        for r in du["rows"]:
            co_cho[r["student_id"]] = co_cho.get(r["student_id"], False) or bool(r["club_id"])
        so_co = sum(co_cho.values())

        t.muc("SỐ LIỆU CHÍNH")
        t.dong("Số {person_l}", len(co_cho))
        t.dong("Số {person_l} đã có {slot_l}", so_co)
        t.dong("Số {person_l} chưa có chỗ", len(co_cho) - so_co)
        if du["nhieu_buoi"]:
            t.dong("Số {session_l}", len(du["ds_buoi"]))
        if "clb" in bao:
            dong_clb = bao["clb"][2]
            t.dong("Số {slot_l}", len(dong_clb))
            t.dong("Chỗ đã xếp", sum(d[6] or 0 for d in dong_clb))
            t.dong("Tổng sức chứa", sum(d[7] for d in dong_clb if isinstance(d[7], (int, float))))
        if "nv" in bao and bao["nv"][2]:
            dau = bao["nv"][2][0]
            if dau[0] == "Nguyện vọng 1":
                t.dong("Tỉ lệ chỗ là nguyện vọng 1 (%)", dau[2])

        t.muc("CÁC TRANG TRONG TỆP NÀY: bấm tên trang để mở")
        mo_ta = {
            "Danh sách {person_l}": (
                "Thời khoá biểu: mỗi {person_l} một dòng, mỗi {session_l} một cột."
                if du["nhieu_buoi"] else
                "Mỗi {person_l} một dòng, kèm {slot_l} của {person_l}. Lọc được theo {slot_l}."),
            "Theo {slot_sl}": "Danh sách từng {slot_l} để phát cho giáo viên phụ "
                        "trách. In ra mỗi {slot_l} một trang.",
            "Theo {cohort_l}": "Danh sách từng {cohort_l} để gửi giáo viên chủ nhiệm. "
                               "Trang này không có {score_l} hay số bốc thăm, gửi được.",
            "Chưa có chỗ": "Những {person_l} chưa vào {slot_l} nào: nhà trường cần xử lý tiếp.",
            "Điểm chuẩn": "Điểm thấp nhất đã được nhận ở từng {slot_l}, tách theo cách xét "
                          "(điểm thi, điểm quyết tâm) và suất thường hay dự trữ. Chỉ dành cho nhà trường.",
            "Thống kê": "Số liệu để họp: {slot_l} nào đông, bao nhiêu {person_l} được "
                        "nguyện vọng 1, suất dự trữ dùng tới đâu.",
            "Dấu vết (kỹ thuật)": "Hạt giống và số bốc thăm để tính lại kết quả. "
                                  "Không cần đọc trang này để dùng kết quả.",
        }
        for ten in du["khoa_trang"][1:]:
            t.lien_ket(du["ten_trang"][ten], mo_ta[ten])

        t.muc("LƯU Ý")
        t.ghi_chu("Tệp có {score_l} chấm và số bốc thăm: không gửi cho giáo viên chấm {score_l}.")
        t.ghi_chu("Đây là dữ liệu {person_l}. Cân nhắc trước khi gửi qua email "
                  "hay chép lên máy dùng chung.")
        t.xong(ngang=False, rong_co_dinh={1: 34, 2: 90})

    def _trang_danh_sach(self, t, du, co_ket_qua):
        if du["nhieu_buoi"]:
            cot, dong = du["tkb_xlsx"]
            t.tieu_de("THỜI KHOÁ BIỂU {slot_u} CẢ TUẦN",
                      "Mỗi {person_l} một dòng, mỗi {session_l} một cột. Bấm mũi tên ở dòng "
                      "tiêu đề để lọc. Dòng tô đỏ: {person_l} chưa có {slot_l} nào.")
            i_chua = len(cot) - 1          # cot "So CLB"
        else:
            cot, dong = du["cot_tong"], du["dong_tong"]
            t.tieu_de("DANH SÁCH {person_u} VÀ {slot_u}",
                      "Mỗi {person_l} một dòng. Bấm mũi tên ở dòng tiêu đề để lọc theo "
                      "{slot_l}. Dòng tô đỏ: {person_l} chưa được xếp.")
            i_chua = cot.index("Mã {slot_sl}")

        def chua_co_cho(d):
            return not d[i_chua]

        dau, _ = t.bang(cot, dong, to_do=chua_co_cho, khoa=True, loc=True,
                        rong="" if co_ket_qua else
                        "(chưa có kết quả, hãy chạy sắp xếp trước)")
        t.xong(lap_hang=dau)

    def _trang_theo_clb(self, t, du):
        t.tieu_de("DANH SÁCH TỪNG {slot_u}",
                  "Mỗi {slot_l} một khối. Khi in, mỗi {slot_l} sang một "
                  "trang riêng: phát thẳng cho giáo viên phụ trách.")
        cot = ["STT", "Mã {person_l}", "Họ tên", "{cohort}", "Nguyện vọng thứ",
               "Diện trúng tuyển", "Nhóm dự trữ"]

        lap = self.get_club_fill_stats()
        ds_clb = lap["data"] if lap.get("ok") else []
        thu_tu = {b: i for i, b in enumerate(du["ds_buoi"])}
        ds_clb = sorted(ds_clb, key=lambda c: (
            thu_tu.get(c.get("buoi"), len(thu_tu)),
            (c.get("name") or c["club_id"]).casefold()))

        theo_clb: dict = {}
        for r in du["rows"]:
            if r["club_id"]:
                theo_clb.setdefault(r["club_id"], []).append(r)

        if not ds_clb:
            t.ghi_chu("(chưa có {slot_l} nào)")
        for n, c in enumerate(ds_clb):
            if n:
                t.ngat_trang()
            ten = c.get("name") or c["club_id"]
            # Ten qua dai thi cat, de "Ma CLB" va "Da xep" con nam tren dong.
            if len(ten) > 120:
                ten = ten[:119] + "…"
            # `ten` là tên người dùng đặt: không điền. Chỉ phần chữ của phần mềm được điền.
            phan = [ten, t.n("Mã {slot_sl}: ") + str(c["club_id"])]
            if du["nhieu_buoi"]:
                phan.append(t.n("{session}: ") + str(c.get("buoi")))
            if c.get("tu_do"):      # CLB Tự do: chỉ tiêu lưu chỉ là số tạm, không in "x/y"
                phan.append("Đã xếp %d · không giới hạn chỗ" % (c.get("matched") or 0))
            else:
                phan.append("Đã xếp %d/%d chỗ" % (c.get("matched") or 0,
                                                  c.get("capacity") or 0))
            # SG-6: giờ / địa điểm giáo viên khai (chỉ khi có). Là chữ người dùng gõ: không điền.
            if (c.get("gio") or "").strip():
                phan.append(t.n("Giờ: ") + c["gio"].strip())
            if (c.get("dia_diem") or "").strip():
                phan.append(t.n("Địa điểm: ") + c["dia_diem"].strip())
            t.khoi(" · ".join(phan), len(cot))
            t.bang(cot, [
                [i, r["student_id"], r["ho_ten"] or "", r["lop"] or "",
                 r["rank_in_student_pref"] or "",
                 self._nhan_dien(r["matched_tier"]), r["reserve_group"] or ""]
                for i, r in enumerate(theo_clb.get(c["club_id"], []), 1)
            ], rong="(chưa có {person_l} nào)")
            t.hang += 1
        t.xong(ngang=False)

    # -----------------------------------------------------------------
    # THEO LỚP (A14): bản để GỬI GIÁO VIÊN CHỦ NHIỆM. Chỉ có kết quả — KHÔNG điểm thi, điểm
    # quyết tâm, số bốc thăm hay diện trúng tuyển. Một khối mỗi lớp, em chưa có chỗ tô đỏ.
    # -----------------------------------------------------------------
    @staticmethod
    def _o_clb_kem_gio(r) -> str:
        """Tên CLB, kèm "(giờ, địa điểm)" khi CLB đã khai (SG-6). Chưa khai: đúng tên như cũ."""
        ten = r["ten_club"] or r["club_id"] or ""
        gd = ", ".join(x for x in ((r["gio"] or "").strip(), (r["dia_diem"] or "").strip()) if x)
        return "%s (%s)" % (ten, gd) if gd else ten

    def _du_lieu_theo_lop(self, rows, ds_buoi, nhieu_buoi) -> dict:
        """{"cot": tiêu đề cột, "nhom": [(lớp|None, [dòng])]}; dòng = [mã, họ tên, ô buổi...].

        Lớp theo thứ tự tự nhiên; nhóm "chưa có lớp" (None) đứng cuối và chỉ có khi có em."""
        theo_em: dict = {}
        for r in rows:
            em = theo_em.setdefault(r["student_id"], {
                "ho_ten": r["ho_ten"] or "", "lop": r["lop"] or None, "o": {}})
            em["o"][r["buoi"]] = self._o_clb_kem_gio(r) if r["club_id"] else ""
        theo_lop: dict = {}
        for sid, em in sorted(theo_em.items()):
            o = [em["o"].get(b, "") for b in ds_buoi] if nhieu_buoi else [
                next(iter(em["o"].values()), "")]
            theo_lop.setdefault(em["lop"], []).append([sid, em["ho_ten"]] + o)
        thu_tu = sorted((k for k in theo_lop if k is not None), key=self._khoa_lop_tu_nhien)
        nhom = [(k, theo_lop[k]) for k in thu_tu]
        if None in theo_lop:
            nhom.append((None, theo_lop[None]))
        cot = ["STT", "Mã {person_l}", "Họ tên"] + (
            list(ds_buoi) if nhieu_buoi else ["{slot} được xếp"])
        return {"cot": cot, "nhom": nhom}

    def _khoi_theo_lop(self, t, tl, lop, dong):
        """MỘT khối lớp: dòng tên lớp + bảng. Em chưa có chỗ ở buổi nào cũng tô đỏ."""
        n_chua = sum(1 for d in dong if not any(d[2:]))
        phan = [t.n("Chưa có {cohort_l}") if lop is None else t.n("{cohort}: ") + str(lop),
                t.n("%d {person_l}" % len(dong))]
        if n_chua:
            phan.append(t.n("%d {person_l} chưa có chỗ" % n_chua))
        t.khoi(" · ".join(phan), len(tl["cot"]))
        t.bang(tl["cot"], [[i] + d for i, d in enumerate(dong, 1)],
               to_do=lambda d: not any(d[3:]), rong="(chưa có {person_l} nào)")
        t.hang += 1

    @staticmethod
    def _dong_ket_qua_cu(t, du):
        """Dòng cảnh báo đỏ khi dữ liệu đã sửa sau lần chạy (như trang Hướng dẫn): tệp này đi
        thẳng tới giáo viên chủ nhiệm, nên phải tự nói được nó có thể đã cũ."""
        from so_excel import CHU_CANH_BAO

        if du.get("ket_qua_cu"):
            t.ghi_chu("CHÚ Ý: dữ liệu đã sửa sau lần chạy này, kết quả có thể "
                      "đã cũ. Hãy chạy lại rồi xuất lại.", CHU_CANH_BAO)

    def _trang_theo_lop(self, t, du):
        t.tieu_de("DANH SÁCH TỪNG {cohort_u}",
                  "Mỗi {cohort_l} một khối, in mỗi {cohort_l} một trang để gửi giáo viên chủ "
                  "nhiệm. Dòng tô đỏ: {person_l} chưa có {slot_l}.")
        self._dong_ket_qua_cu(t, du)
        tl = du["theo_lop"]
        for n, (lop, dong) in enumerate(tl["nhom"]):
            if n:
                t.ngat_trang()
            self._khoi_theo_lop(t, tl, lop, dong)
        t.xong(ngang=len(tl["cot"]) > 7)

    def _ghi_tep_lop(self, path: str, du: dict, lop, dong, da_dung: set) -> None:
        """Một tệp .xlsx một trang cho MỘT lớp (hoặc nhóm chưa có lớp)."""
        from openpyxl import Workbook

        from so_excel import Trang

        tl = du["theo_lop"]
        wb = Workbook()
        ws = wb.active
        ws.title = self._ten_trang_hop_le(
            dien_nhan("Chưa có {cohort_l}" if lop is None else str(lop), du.get("nhan")),
            da_dung)
        t = Trang(ws, du.get("nhan"))
        t.tieu_de("DANH SÁCH {cohort_u}" + ("" if lop is None else " " + str(lop).upper()),
                  "Gửi giáo viên chủ nhiệm. Dòng tô đỏ: {person_l} chưa có {slot_l}.")
        self._dong_ket_qua_cu(t, du)
        self._khoi_theo_lop(t, tl, lop, dong)
        t.xong(ngang=len(tl["cot"]) > 7)
        wb.save(path)

    @staticmethod
    def _cat_ten_tep(ten: str, toi_da: int = 100) -> str:
        """Cắt tên tệp còn tối đa `toi_da` ký tự VÀ chừng 200 byte UTF-8 (hệ điều hành giới hạn
        255 byte một tên, tiếng Việt có dấu 3 byte một chữ). Tên lớp do người dùng đặt có thể
        rất dài; tên thật vẫn đủ trong tiêu đề khối, tên tệp chỉ cần nhận ra. Gọi TRƯỚC
        `_ten_chua_dung` để hai tên cùng phần đầu vẫn ra hai tệp khác nhau."""
        ten = ten[:toi_da]
        while len(ten.encode("utf-8")) > 200:
            ten = ten[:-1]
        return ten.rstrip(" .") or "lop"

    def export_theo_lop(self, output_path: str = ""):
        """Xuất MỘT THƯ MỤC, mỗi lớp một tệp .xlsx một trang (để gửi giáo viên chủ nhiệm), cộng
        `_chua_co_lop.xlsx` nếu có em chưa có lớp. Không có điểm hay số bốc thăm.

        Chỗ đặt theo `_duong_xuat` (rỗng/tương đối → Tải xuống; không ghi đè: trùng thì "x (2)").
        Chưa có kết quả thì từ chối `xuat_chua_co_ket_qua`, không tạo gì. Trả về {thu_muc, n_tep}."""
        return self._khoa_xuat(self._export_theo_lop_da_khoa, output_path)

    def export_danh_sach_pdf(self, output_path: str = "", theo: str = "clb"):
        """XP1-L3: danh sách thành viên dạng PDF, MỘT THƯ MỤC (A4 dọc). Cùng nguồn dữ liệu với `export_theo_lop`
        (`_du_lieu_xuat`); không điểm, không số bốc thăm, không diện trúng tuyển.

        `theo="clb"`: mỗi CLB một tệp (nhiều buổi: mỗi CLB mỗi buổi một tệp; có tiêu đề, loại CLB, giờ, địa điểm)
        + `_chua_duoc_xep.pdf` nếu có em chưa có chỗ. `theo="lop"`: mỗi lớp một tệp (em chưa có chỗ ở mục riêng)
        + `_chua_co_lop.pdf`. Chỗ đặt theo `_duong_xuat` (không ghi đè: trùng thì "x (2)"). Chỉ ĐỌC dữ liệu.
        Lỗi: `xuat_chua_co_ket_qua`, `xp1_kieu_xuat_la`, `xp1_thieu_thu_vien_pdf`.
        Trả {thu_muc, n_tep, n_trang, n_dong (số dòng kết quả đã xuất), ket_qua_cu}."""
        return self._khoa_xuat(self._export_danh_sach_pdf_da_khoa, output_path, theo)

    def _loai_clb_theo_ma(self) -> dict:
        """{club_id: mã loại|None} đọc từ `clubs.loai` (chỉ để HIỂN THỊ); cột chưa có thì rỗng."""
        with self._ket_noi_doc() as cur:
            if not any(r[1] == "loai" for r in cur.execute("PRAGMA table_info(clubs)")):
                return {}
            return dict(cur.execute("SELECT club_id, loai FROM clubs"))

    def _export_danh_sach_pdf_da_khoa(self, output_path, theo):
        import danh_sach_pdf
        import phieu_giai_trinh
        import xuat_pdf
        from so_nhap import NHAN_LOAI_HIEN_THI
        thu_muc, da_tao = None, False
        try:
            if theo not in ("clb", "lop"):
                return _fail(err("xp1_kieu_xuat_la"))
            xuat_pdf.san_sang()
            if self._chua_co_ket_qua():
                return _fail(err("xuat_chua_co_ket_qua"))
            thu_muc = self._thu_muc_xuat_moi(output_path, "danh_sach_theo_" + theo)
            du = self._du_lieu_xuat()
            nhan = du.get("nhan")
            n = lambda chu: dien_nhan(chu, nhan)  # noqa: E731
            canh_bao = ("Dữ liệu đã sửa sau lần chạy này, kết quả có thể đã cũ. Hãy chạy lại rồi xuất lại."
                        if self._ket_qua_cu() else None)
            nhan_buoi = phieu_giai_trinh._nhan_buoi
            os.makedirs(thu_muc)
            da_tao = True                         # từ đây thư mục là CỦA lần xuất này
            n_tep = n_trang = 0
            if theo == "clb":
                loai = self._loai_clb_theo_ma()
                nhom: dict = {}
                for r in du["rows"]:
                    khoa = (r["club_id"], r["buoi"] if du["nhieu_buoi"] and r["club_id"] else None) \
                        if r["club_id"] else (None, None)
                    nhom.setdefault(khoa, []).append(r)
                da_dung: set = {"_chua_duoc_xep"}     # giữ chỗ trước: CLB tên "_chua_duoc_xep" không đè
                cot = ["STT", n("Mã {person_l}"), "Họ tên", n("{cohort}")]
                for (club_id, buoi), ds in sorted(nhom.items(), key=lambda kv: (kv[0][0] is None, str(kv[0]))):
                    if club_id is None:
                        ten = "_chua_duoc_xep"
                        cot_nay = cot + ([n("{session}")] if du["nhieu_buoi"] else [])
                        hang = [[i, r["student_id"], r["ho_ten"] or "", r["lop"] or ""]
                                + ([nhan_buoi(r["buoi"])] if du["nhieu_buoi"] else [])
                                for i, r in enumerate(ds, 1)]
                        duong = danh_sach_pdf.dung_pdf_clb(
                            os.path.join(thu_muc, ten + ".pdf"), n("{person_l} chưa có {slot_l}"),
                            [(n("Số {person_l}"), len(ds))], cot_nay, hang, canh_bao)
                    else:
                        ten = self._ten_chua_dung(self._cat_ten_tep(self._ten_file_an_toan(
                            club_id + ("_" + buoi if buoi else ""), "clb")), da_dung)
                        r0 = ds[0]
                        hang = [[i, r["student_id"], r["ho_ten"] or "", r["lop"] or ""]
                                for i, r in enumerate(ds, 1)]
                        duong = danh_sach_pdf.dung_pdf_clb(
                            os.path.join(thu_muc, ten + ".pdf"), r0["ten_club"] or club_id,
                            [(n("Mã {slot_sl}"), club_id),
                             (n("Loại {slot_l}"), NHAN_LOAI_HIEN_THI.get(loai.get(club_id)) or None),
                             (n("{session}"), nhan_buoi(buoi) if buoi else None),
                             ("Giờ", r0["gio"]), ("Địa điểm", r0["dia_diem"]),
                             (n("Số {person_l}"), len(ds))], cot, hang, canh_bao)
                    n_tep += 1
                    n_trang += xuat_pdf.dem_trang(duong)
            else:
                tl = du["theo_lop"]
                da_dung = {"_chua_co_lop"}            # giữ chỗ trước: lớp tên "_chua_co_lop" không đè
                cot = [n(c) for c in tl["cot"]]
                cot_chua = cot[:3]
                for lop, dong in tl["nhom"]:
                    ten = "_chua_co_lop" if lop is None else self._ten_chua_dung(
                        self._cat_ten_tep(self._ten_file_an_toan(str(lop), "lop")), da_dung)
                    co = [d for d in dong if any(d[2:])]
                    chua = [d for d in dong if not any(d[2:])]
                    if du["nhieu_buoi"]:
                        cot_nay = cot[:3] + [nhan_buoi(b) for b in du["ds_buoi"]]
                    else:
                        cot_nay = cot
                    duong = danh_sach_pdf.dung_pdf_lop(
                        os.path.join(thu_muc, ten + ".pdf"),
                        n("Chưa có {cohort_l}") if lop is None else n("DANH SÁCH {cohort_u} ") + str(lop).upper(),
                        [(n("Số {person_l}"), len(dong))], cot_nay,
                        [[i] + d for i, d in enumerate(co, 1)],
                        n("Chưa có {slot_l}"), cot_chua, [[i] + d[:2] for i, d in enumerate(chua, 1)], canh_bao)
                    n_tep += 1
                    n_trang += xuat_pdf.dem_trang(duong)
            return _ok({"thu_muc": thu_muc, "n_tep": n_tep, "n_trang": n_trang, "n_dong": len(du["rows"]),
                        "ket_qua_cu": bool(canh_bao)})
        except xuat_pdf.ThieuThuVienPdf:
            if da_tao and thu_muc:
                shutil.rmtree(thu_muc, ignore_errors=True)
            return _fail(err("xp1_thieu_thu_vien_pdf"))
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            if da_tao and thu_muc:                # không để lại thư mục thiếu tệp trông như đã xuất đủ
                shutil.rmtree(thu_muc, ignore_errors=True)
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def _thu_muc_xuat_moi(self, output_path: str, ten_mac_dinh: str) -> str:
        """Chỗ đặt MỘT THƯ MỤC xuất mới (chưa tạo). Đường tuyệt đối đã có thì thành "x (2)" (không ghi đè);
        `_duong_xuat` sẽ từ chối vì nó coi thư mục có sẵn là nhầm với tệp."""
        if os.path.isabs((output_path or "").strip()):
            return duong_dan_khong_de(output_path.strip().rstrip("/\\"))
        return self._duong_xuat(output_path, ten_mac_dinh)

    def _export_theo_lop_da_khoa(self, output_path: str):
        thu_muc, da_tao = None, False
        try:
            if self._chua_co_ket_qua():
                return _fail(err("xuat_chua_co_ket_qua"))
            thu_muc = self._thu_muc_xuat_moi(output_path, "ket_qua_theo_lop")
            du = self._du_lieu_xuat()
            du["ket_qua_cu"] = self._ket_qua_cu()
            os.makedirs(thu_muc)
            da_tao = True              # từ đây thư mục là CỦA lần xuất này
            da_dung: set = {"_chua_co_lop"}        # giữ chỗ trước: lớp tên "_chua_co_lop" không đè
            n = 0
            for lop, dong in du["theo_lop"]["nhom"]:
                ten = "_chua_co_lop" if lop is None else self._ten_chua_dung(
                    self._cat_ten_tep(self._ten_file_an_toan(str(lop), "lop")), da_dung)
                self._ghi_tep_lop(os.path.join(thu_muc, ten + ".xlsx"), du, lop, dong, set())
                n += 1
            return _ok({"thu_muc": thu_muc, "n_tep": n, "ket_qua_cu": du["ket_qua_cu"]})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            # Lỗi giữa chừng: xoá thư mục dở do CHÍNH lần xuất này tạo ra (không bao giờ thư mục
            # có sẵn), để không còn thư mục thiếu lớp trông như đã xuất đủ.
            if da_tao and thu_muc:
                shutil.rmtree(thu_muc, ignore_errors=True)
            return _fail(err("error_exporting_excel", detail=self._chi_tiet_loi_xuat(e)))

    # -----------------------------------------------------------------
    # T3-19: "Tải bảng này (Excel)" ở thẻ 02 Kết quả. Xuất đúng bảng đang xem (một lớp, một
    # CLB hoặc danh sách theo mã), cùng cột với màn hình. KHÔNG điểm thi, điểm quyết tâm,
    # số bốc thăm hay diện trúng tuyển (như bản theo lớp).
    # -----------------------------------------------------------------
    def export_bang_dang_xem(self, kieu: str, gia_tri=None, output_path: str = "", thu_tu=None):
        """Xuất MỘT tệp .xlsx một trang cho bảng đang xem ở thẻ Kết quả.

        `kieu`: "lop" (`gia_tri` = lớp, "" là chưa có lớp), "clb" (`gia_tri` = mã CLB) hoặc "ma"
        (`gia_tri` = chữ đang tìm, rỗng là tất cả). Chỗ đặt theo `_duong_xuat` (không ghi đè).
        `thu_tu` (tuỳ chọn): danh sách mã theo thứ tự đang hiện trên màn hình; hàng tệp đi theo thứ tự đó
        (mã không có trong danh sách xếp cuối, giữ thứ tự cũ). Chỉ đổi thứ tự hàng, không đổi cột.
        Chưa có kết quả thì từ chối `xuat_chua_co_ket_qua`. Trả về {path, n_dong}."""
        return self._khoa_xuat(self._export_bang_dang_xem_da_khoa, kieu, gia_tri, output_path, thu_tu)

    def _export_bang_dang_xem_da_khoa(self, kieu, gia_tri, output_path, thu_tu=None):
        from openpyxl import Workbook

        from so_excel import Trang

        path, da_tao = None, False
        try:
            if self._chua_co_ket_qua():
                return _fail(err("xuat_chua_co_ket_qua"))
            if kieu not in ("lop", "clb", "ma"):
                return _fail(err("error_exporting_excel", detail="kieu=%s" % kieu))
            tieu_de_phu = "Chỉ có kết quả xếp. Dòng tô đỏ: {person_l} chưa có {slot_l}."
            if kieu == "clb":
                res = self.get_danh_sach_clb(str(gia_tri or ""))
                if not res["ok"]:
                    return res
                d = res["data"]
                ten = d["club_name"] or d["club_id"]
                cot = ["Mã {person_l}", "Họ tên", "{cohort}"]
                dong = [[m["student_id"], m["name"] or "", m["class_id"] or ""]
                        for m in sorted(d["thanh_vien"], key=lambda m: str(m["student_id"]))]
                tieu_de, to_do = "DANH SÁCH {slot_u} " + str(ten).upper(), None
                ten_trang = str(ten)
            else:
                res = (self.get_thoi_khoa_bieu("", "" if gia_tri in (None, "") else str(gia_tri))
                       if kieu == "lop"
                       else self.get_thoi_khoa_bieu(str(gia_tri or "").strip()))
                if not res["ok"]:
                    return res
                ds_buoi = res["data"]["ds_buoi"]
                nhieu = len(ds_buoi) > 1
                co_lop = kieu == "ma"
                cot = (["Mã {person_l}", "Họ tên"] + (["{cohort}"] if co_lop else [])
                       + (list(ds_buoi) if nhieu else ["{slot} được xếp"]))
                dong = []
                for em in res["data"]["hoc_sinh"]:
                    o = []
                    for b in ds_buoi:
                        x = em["theo_buoi"].get(b)
                        o.append((x.get("club_name") or x.get("club_id") or "")
                                 if x and x.get("club_id") else "")
                    dong.append([em["student_id"], em["name"] or ""]
                                + ([em["class_id"] or ""] if co_lop else []) + o)
                tl = 3 if co_lop else 2
                to_do = lambda r: not any(r[tl:])  # noqa: E731
                if kieu == "lop":
                    tieu_de = ("DANH SÁCH {cohort_u} " + str(gia_tri).upper()) if gia_tri \
                        else "DANH SÁCH {person_u} CHƯA CÓ {cohort_u}"
                    ten_trang = str(gia_tri) if gia_tri else "Chưa có {cohort_l}"
                else:
                    tieu_de, ten_trang = "DANH SÁCH {person_u}", "Danh sách"
            if isinstance(thu_tu, (list, tuple)) and thu_tu:
                vt = {}
                for i, m in enumerate(thu_tu):
                    vt.setdefault(str(m), i)
                dong.sort(key=lambda r: vt.get(str(r[0]), len(vt)))      # ổn định: mã lạ giữ thứ tự cũ
            du = {"nhan": self._nhan_xuat()}
            path = self._duong_xuat(output_path, self._ten_file_an_toan(
                "bang_" + (str(gia_tri) if gia_tri else kieu), "bang") + ".xlsx", (".xlsx",))
            wb = Workbook()
            ws = wb.active
            ws.title = self._ten_trang_hop_le(dien_nhan(ten_trang, du["nhan"]), set())
            t = Trang(ws, du["nhan"])
            t.tieu_de(tieu_de, tieu_de_phu)
            du["ket_qua_cu"] = self._ket_qua_cu()
            self._dong_ket_qua_cu(t, du)
            t.bang(cot, dong, to_do=to_do, rong="(chưa có {person_l} nào)")
            t.xong(ngang=len(cot) > 7)
            wb.save(path)
            da_tao = True
            return _ok({"path": path, "n_dong": len(dong), "ket_qua_cu": du["ket_qua_cu"]})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            if path and not da_tao and os.path.exists(path):
                os.remove(path)
            return _fail(err("error_exporting_excel", detail=self._chi_tiet_loi_xuat(e)))

    def _trang_chua_co_cho(self, t, bao, co_ket_qua):
        from openpyxl.styles import Alignment

        so_em, cot, dong = bao.get("tt") or (0, [
            "Mã {person_l}", "Họ tên", "Số nguyện vọng đã khai",
            "Đã khai những {slot_l} (kèm tỉ lệ chọi)"], [])
        t.tieu_de("{person_u} CHƯA CÓ {slot_u} NÀO: %d {person_l}" % so_em,
                  "Nhà trường cần xếp tay hoặc liên hệ {person_pl} này. Cột cuối "
                  "cho biết {person_l} đã khai những {slot_l} nào và chúng chọi đến đâu.")
        dau, cuoi = t.bang(
            cot, dong, khoa=True, loc=True,
            rong="(không có {person_l} nào, mọi {person_l} đều có ít nhất một chỗ)"
            if co_ket_qua else "(chưa có kết quả, hãy chạy sắp xếp trước)")
        for h in range(dau + 1, cuoi + 1):
            t.ws.cell(row=h, column=len(cot)).alignment = Alignment(wrap_text=True)
        t.xong(lap_hang=dau, rong_co_dinh={len(cot): 70})

    @staticmethod
    def _so_chuan(x) -> str:
        """Số trong ô điểm chuẩn: bỏ phần thập phân thừa, dấu phẩy như người Việt viết."""
        if isinstance(x, float) and not x.is_integer():
            return ("%g" % x).replace(".", ",")
        return str(int(x))

    def _o_diem_chuan(self, muc, tang) -> str:
        if muc is None:
            return "—"
        if muc.get("con_cho"):
            return "0 (còn %d chỗ)" % muc["con_cho"]
        if tang == 1:
            return "%s điểm thi · %s điểm quyết tâm" % (
                self._so_chuan(muc["diem_thi"]), self._so_chuan(muc["diem_quyet_tam"]))
        return self._so_chuan(muc["diem_quyet_tam"])

    def _trang_diem_chuan(self, t, du, co_ket_qua, ket_qua_cu):
        """Điểm chuẩn từng {slot_l} (A13.4): mỗi {slot_l} (và {session_l}) một dòng, hai tầng x
        hai mức. Dùng `get_diem_chuan`, cùng nguồn với màn hình quản trị."""
        from so_excel import CHU_CANH_BAO

        t.tieu_de("ĐIỂM CHUẨN TỪNG {slot_u}",
                  "Điểm quyết tâm thấp nhất đã được nhận, tách theo cách xét (điểm thi, điểm quyết tâm) và theo suất thường hay "
                  "suất dự trữ. Ô \"—\": không có {person_l} nào ở mục đó. Chỉ dành cho nhà "
                  "trường, không phát cho {person_l}.")
        if ket_qua_cu:
            t.ghi_chu("CHÚ Ý: dữ liệu đã sửa sau lần chạy này, điểm chuẩn có thể đã cũ.",
                      CHU_CANH_BAO)
        cot = ["Mã {slot_sl}", "Tên {slot_l}"] + (["{session}"] if du["nhieu_buoi"] else []) \
            + ["Chỗ", "Số đơn", "Đã nhận", "Còn chỗ", "Xét điểm quyết tâm, suất thường",
               "Xét điểm quyết tâm, suất dự trữ", "Xét điểm thi, suất thường", "Xét điểm thi, suất dự trữ"]
        kq = self.get_diem_chuan()
        rows = kq["data"]["rows"] if kq.get("ok") else []
        loi_dc = not kq.get("ok")
        if loi_dc:
            # Không xuất trang trống im lặng (A13.8): ghi lý do vào trang và báo ra ngoài.
            ma = ", ".join(str(e.get("code")) for e in kq.get("errors", []) if isinstance(e, dict))
            t.ghi_chu("KHÔNG ĐỌC ĐƯỢC ĐIỂM CHUẨN khi xuất (mã lỗi: %s). Trang này đang trống do lỗi, "
                      "không phải vì chưa có dữ liệu. Hãy xuất lại." % (ma or "không rõ"), CHU_CANH_BAO)
            du.setdefault("canh_bao", []).append(err("xuat_diem_chuan_loi"))
        dong = []
        for r in rows:
            dong.append([r["club_id"], r["ten"]] + ([r["buoi"]] if du["nhieu_buoi"] else [])
                        + [r["suc_chua"], r["so_don"], r["so_nhan"], r["con_cho"],
                           self._o_diem_chuan(r["tang2"]["thuong"], 2),
                           self._o_diem_chuan(r["tang2"]["du_tru"], 2),
                           self._o_diem_chuan(r["tang1"]["thuong"], 1),
                           self._o_diem_chuan(r["tang1"]["du_tru"], 1)])
        dau, _ = t.bang(cot, dong, khoa=True, loc=True,
                        rong="(không đọc được điểm chuẩn, xem dòng cảnh báo phía trên)" if loi_dc
                        else ("" if co_ket_qua else "(chưa có kết quả, hãy chạy sắp xếp trước)"))
        t.xong(lap_hang=dau)

    def _trang_thong_ke(self, t, bao, du):
        t.tieu_de("THỐNG KÊ",
                  "Số liệu để họp: {slot_l} nào đông, {session_l} nào chật, bao "
                  "nhiêu {person_l} được nguyện vọng 1, suất dự trữ dùng tới đâu.")
        co_gi = False
        if "clb" in bao:
            _, cot, dong = bao["clb"]
            t.muc("TỪNG {slot_u}")
            # Cot "So em dang ky" KHONG cong don duoc — xem _bang_tong_hop.
            t.ghi_chu('Cột "Số {person_l} đăng ký" không cộng dồn được: một {person_l} khai ba '
                      '{slot_l} được đếm ở cả ba dòng.')
            t.bang(cot, dong)
            co_gi = True

        tai = self.get_tai_theo_buoi()
        if du["nhieu_buoi"] and tai.get("ok") and len(tai["data"]) > 1:
            t.muc("TẢI TỪNG {session_u}: {session_l} nào chật, {session_l} nào rộng")
            t.bang(["{session}", "Số {slot_sl}", "Tổng chỗ", "Chỉ tiêu dự trữ",
                    "Số {person_l} khai nguyện vọng", "Tỉ lệ chọi"],
                   [[x.get("buoi"), x.get("so_clb"), x.get("tong_cho"),
                     x.get("tong_du_tru"), x.get("so_hoc_sinh"), x.get("ti_le_choi")]
                    for x in tai["data"]])

        dp = self.get_do_phu()
        if dp.get("ok") and dp["data"]["tong_hoc_sinh"]:
            d = dp["data"]
            tong = d["tong_hoc_sinh"]
            t.muc("ĐỘ PHỦ: bao nhiêu {person_l} được mấy {slot_l}")
            t.bang(["Số {slot_l}", "Số {person_l}", "Tỉ lệ %"],
                   [[h["so_clb"], h["so_em"], round(100 * h["so_em"] / tong, 1)]
                    for h in d["phan_bo"]])

        if "nv" in bao:
            tong, cot, dong = bao["nv"]
            t.muc("NGUYỆN VỌNG THỨ MẤY THÌ ĐƯỢC: trên %d chỗ đã xếp" % tong)
            t.bang(cot, dong)
        if "dt" in bao:
            thua, cot, dong = bao["dt"]
            t.muc("SUẤT DỰ TRỮ DÙNG TỚI ĐÂU: còn thừa %d suất" % thua)
            t.bang(cot, dong)
        if not co_gi:
            t.ghi_chu("(chưa có {slot_l} nào)")
        t.xong(ngang=True)

    def _trang_dau_vet(self, t, du, xuat_luc):
        t.ws.sheet_properties.tabColor = "808080"
        t.tieu_de("DẤU VẾT LẦN CHẠY",
                  "Hạt giống + bộ số bốc thăm đã khoá + cách bốc thăm là đủ để "
                  "bất kỳ ai tính lại và ra đúng kết quả này. Không cần đọc "
                  "trang này để dùng kết quả.")
        t.bang(["Mục", "Giá trị"],
               self._dong_dau_vet() + [["Thời điểm xuất tệp này", xuat_luc]],
               bo_soc=True)
        if du["tham"]:
            # Phan mem xao lai thu tu o moi buoi; bang nay la ham TAT DINH cua
            # bo so da khoa va hat giong — ai cung tinh lai duoc.
            t.muc("SỐ BỐC THĂM TỪNG {session_u}: tính lại được từ bộ số đã khoá và hạt giống")
            t.bang(*du["tham"])
        t.xong()

    def _bang_bao_cao(self, so: bool) -> dict:
        """Bốn bảng báo cáo cả trường, dựng MỘT lần cho cả hai nơi dùng.

        Tệp tổng hợp (.csv, đọc bằng mắt) và các trang Excel (để tính tiếp)
        trước đây mỗi nơi tự dựng lại cùng bốn bảng — cùng cột, cùng phép
        tính, chỉ khác cách viết số. Sửa một nơi mà quên nơi kia là hai tệp
        của CÙNG một lần xuất nói hai điều khác nhau.

        `so=False`: số viết kiểu Việt để đọc ("84,5%", "(không có chỗ)").
        `so=True` : số thô để Excel tính được (84.5, ô trống).

        Trả về {tên: (số tóm tắt cho tiêu đề, [cột], [[ô]])}, chỉ gồm bảng
        đọc được dữ liệu.
        """
        def ti_le_choi(x):
            if x is None:
                return "" if so else "(không có chỗ)"
            return x if so else _so_vn(x)

        def phan_tram(a, b):
            if so:
                return round(100 * a / b, 1) if b else ""
            return _phan_tram_vn(a, b)

        def khai(e):
            return "; ".join(
                "%s (%s)" % (k["ten_clb"] or k["club_id"],
                             # Day la CHU (mot o ghep nhieu CLB), nen ke ca
                             # ban so=True cung viet so kieu Viet.
                             _so_vn(k["ti_le_choi"])
                             if k["ti_le_choi"] is not None
                             else "không giới hạn chỗ" if k.get("tu_do") else "không có chỗ")
                for k in e["da_khai"]) or "(chưa khai nguyện vọng nào)"

        ra = {}
        lap = self.get_club_fill_stats()
        if lap.get("ok"):
            ra["clb"] = (len(lap["data"]), [
                "{session}", "Mã {slot_sl}", "Tên {slot_sl}", "Số {person_l} đăng ký",
                "Đặt nguyện vọng 1", "Tỉ lệ chọi", "Đã xếp", "Sức chứa",
                "Tỉ lệ lấp đầy" + (" %" if so else ""),
                "Trong đó diện dự trữ", "Chỉ tiêu dự trữ"],
                [[c.get("buoi"), c.get("club_id"), c.get("name"),
                  c.get("so_dang_ky"), c.get("so_dat_nv1"),
                  "" if c.get("tu_do") else ti_le_choi(c.get("ti_le_choi")),
                  c.get("matched"),
                  "không giới hạn chỗ" if c.get("tu_do") else c.get("capacity") or 0,
                  "" if c.get("tu_do")
                  else phan_tram(c.get("matched") or 0, c.get("capacity") or 0),
                  c.get("matched_reserve"), c.get("reserve_capacity")]
                 for c in lap["data"]])

        nv = self.get_phan_bo_nguyen_vong()
        if nv.get("ok") and nv["data"]["tong_da_xep"]:
            n = nv["data"]
            tong = n["tong_da_xep"]
            dong = [[("Nguyện vọng %d trở lên" % h["hang"]) if h["gop"]
                     else ("Nguyện vọng %d" % h["hang"]),
                     h["so_em"], phan_tram(h["so_em"], tong)]
                    for h in n["phan_bo"]]
            if n.get("ngoai_danh_sach"):
                dong.append(["Xếp ngoài danh sách nguyện vọng", n["ngoai_danh_sach"],
                             phan_tram(n["ngoai_danh_sach"], tong)])
            if n["khong_ro"]:
                dong.append(["Không rõ thứ hạng", n["khong_ro"],
                             phan_tram(n["khong_ro"], tong)])
            ra["nv"] = (tong, ["Nguyện vọng", "Số chỗ",
                               "Tỉ lệ %" if so else "Tỉ lệ"], dong)

        dt = self.get_suat_du_tru()
        if dt.get("ok") and dt["data"]:
            ra["dt"] = (sum(c["con_thua"] for c in dt["data"]), [
                "{session}", "Mã {slot_sl}", "Tên {slot_sl}", "Nhãn dự trữ",
                "Chỉ tiêu dự trữ", "{person} thuộc nhóm có đăng ký",
                "Đã dùng", "Còn thừa"],
                [[c["buoi"], c["club_id"], c["name"], c["reserve_group"],
                  c["reserve_capacity"], c["nhom_dang_ky"], c["da_dung"],
                  c["con_thua"]] for c in dt["data"]])

        tt = self.get_em_chua_co_cho()
        if tt.get("ok"):
            d = tt["data"]
            ra["tt"] = (d["so_em"], [
                "Mã {person_l}", "Họ tên", "Số nguyện vọng đã khai",
                "Đã khai những {slot_l} (kèm tỉ lệ chọi)"],
                [[e["student_id"], e["name"] or "", e["so_nguyen_vong"], khai(e)]
                 for e in d["danh_sach"]])
        return ra

    def _dong_dau_vet(self) -> list[list]:
        """[mục, giá trị] của lần chạy gần nhất — ba dòng đầu đủ để tính lại.

        Dùng chung cho tệp tổng hợp và trang "Dấu vết" của sổ Excel. Trả chữ ĐÃ điền nhãn
        (các dòng này đi vào `Trang.bang` như dữ liệu, nơi không điền thêm).
        """
        nhan = self._nhan_xuat()
        meta = self.get_last_run_info()
        m = meta.get("data") if meta.get("ok") else None
        if not m:
            return [["(chưa chạy lần nào)", ""]]
        khoa = self.get_stb_lock_status()
        k = khoa.get("data") if khoa.get("ok") else {}
        return [
            ["Hạt giống bốc thăm", m.get("seed")],
            ["Cách bốc thăm", m.get("che_do_boc_tham")],
            ["Bộ số bốc thăm khoá lúc", (k or {}).get("locked_at") or "(chưa khoá)"],
            ["Thời điểm chạy", m.get("run_at")],
            ["Số vòng xử lý", m.get("rounds_run")],
            [dien_nhan("Số {session_l} lần chạy này phủ", nhan), m.get("so_buoi")],
            [dien_nhan("{session} đã chạy", nhan), (m.get("buoi_da_chay") or "").replace(",", ", ")],
        ]

    def _bang_tong_hop(self) -> list[list]:
        """Các dòng của tệp tổng hợp — dùng chung cho bản CSV và bản Excel.

        VÌ SAO TỆP NÀY PHẢI CÓ. Mọi tệp xuất ra trước đây đều nói *ai vào câu
        lạc bộ nào*, không tệp nào nói *kết quả này đến từ đâu*. Hai lần chạy
        khác hạt giống cho ra hai bộ tệp trông y hệt nhau: cùng tên cột, cùng
        số dòng, cùng hình dạng. Trường in ra dán bảng rồi sáu tháng sau bị
        hỏi "bảng này tính thế nào" thì không còn gì để trả lời.

        Mà cả thiết kế của phần mềm dựa trên một lời hứa: *ai cũng tính lại
        được*. Lời hứa ấy cần đúng ba thứ — bộ số bốc thăm đã khoá, hạt
        giống, và cách bốc thăm — và trước bản vá này **không thứ nào** đi
        theo tệp kết quả ra khỏi phần mềm.

        Bảng còn gộp mấy con số vốn chỉ xem được trên màn hình: độ phủ, tỉ lệ
        lấp đầy từng câu lạc bộ, tải từng buổi, và danh sách em chưa có chỗ
        nào. Đó đúng là những thứ nhà trường phải xử lý tiếp, nên chúng cần
        nằm trong tệp mang đi họp chứ không nằm trong một tab phải mở phần
        mềm mới thấy.
        """
        nhan = self._nhan_xuat()

        def N(mau):
            return dien_nhan(mau, nhan)

        def NL(cac_o):
            """Điền cả một dòng tiêu đề cột (chữ của phần mềm, không phải dữ liệu)."""
            return [N(o) for o in cac_o]

        def phan(tieu_de):
            return [[], [N(tieu_de)]]

        ra: list[list] = [[N("TỔNG HỢP KẾT QUẢ PHÂN BỔ {slot_u} (RB-DA)")]]

        # ---- 1. Dau vet lan chay ----
        ra += phan("DẤU VẾT LẦN CHẠY: ba dòng đầu là thứ cần để tính lại")
        ra.append(["Mục", "Giá trị"])
        ra += self._dong_dau_vet()
        ra.append(["Thời điểm xuất tệp này", _now()])
        # Tep mang di hop phai tu noi duoc no con dung khong. Man hinh co dai
        # canh bao, nhung tep ra khoi phan mem thi chi con dong nay.
        tt = self.get_trang_thai_ket_qua()
        if tt.get("ok") and tt["data"]["co_ket_qua"]:
            ra.append(["Kết quả còn khớp dữ liệu",
                       "CÓ" if not tt["data"]["ket_qua_cu"] else
                       "KHÔNG: dữ liệu đã sửa sau lần chạy này, kết quả có "
                       "thể đã cũ. Hãy chạy lại rồi xuất lại."])

        # ---- 2. Do phu ----
        dp = self.get_do_phu()
        if dp.get("ok"):
            d = dp["data"]
            tong = d["tong_hoc_sinh"] or 0
            ra += phan("ĐỘ PHỦ: bao nhiêu {person_l} được mấy {slot_l}")
            ra.append(NL(["Số {slot_l} trong tuần", "Số {person_l}", "Tỉ lệ"]))
            for h in d["phan_bo"]:
                ra.append([h["so_clb"], h["so_em"],
                           _phan_tram_vn(h["so_em"], tong)])
            ra.append([N("Tổng số {person_l}"), tong, ""])
            ra.append([N("Trung bình số {slot_l} mỗi {person_l}"),
                       _so_vn(d["trung_binh_clb"]), ""])

        bang = self._bang_bao_cao(so=False)

        # ---- 3. Ti le lap day tung CLB ----
        # Cot "So em dang ky" KHONG cong don duoc: trong cung mot buoi, mot em
        # khai ba cau lac bo thi duoc dem o ca ba dong, ma em ay chi lay duoc
        # MOT cho. Cong cot nay roi chia cho tong chi tieu se ra mot ti le
        # choi phong len vo nghia — nen cau canh bao di ngay trong tieu de.
        if "clb" in bang:
            _, cot, dong = bang["clb"]
            ra += phan("TỪNG {slot_u}: \"số {person_l} đăng ký\" KHÔNG cộng dồn "
                       "được (một {person_l} khai ba {slot_l} được đếm ở cả ba dòng)")
            ra.append(NL(cot))
            ra += dong

        # ---- 4. Tai tung buoi ----
        tai = self.get_tai_theo_buoi()
        if tai.get("ok") and len(tai["data"]) > 1:
            ra += phan("TẢI TỪNG {session_u}: đọc để biết {session_l} nào chật, {session_l} nào rộng")
            ra.append(NL(["{session}", "Số {slot_sl}", "Tổng chỗ", "Chỉ tiêu dự trữ",
                          "Số {person_l} khai nguyện vọng", "Tỉ lệ chọi"]))
            for t in tai["data"]:
                ra.append([
                    t.get("buoi"), t.get("so_clb"), t.get("tong_cho"),
                    t.get("tong_du_tru"), t.get("so_hoc_sinh"),
                    # None = khong co cho nao, khac han "thua cho" — xem
                    # chu thich trong get_tai_theo_buoi.
                    _so_vn(t.get("ti_le_choi")) if t.get("ti_le_choi") is not None
                    else "(không có chỗ)",
                ])

        # ---- 5. Nguyen vong thu may thi duoc ----
        # Do phu noi bao nhieu em co cho, khong noi cho ay co phai thu em
        # muon khong. Hai lan chay rat khac nhau van cho cung mot con so do
        # phu — day la con so phan biet duoc chung.
        if "nv" in bang:
            tong, cot, dong = bang["nv"]
            ra += phan("NGUYỆN VỌNG THỨ MẤY THÌ ĐƯỢC: trên %d chỗ đã xếp" % tong)
            ra.append(NL(cot))
            ra += dong

        # ---- 6. Suat du tru dung toi dau ----
        # Mot suat khong ai dung KHONG bao loi va KHONG hien o dau — no lang
        # le thanh mot suat thuong, co che van chay dung, con y dinh uu tien
        # thi boc hoi. Cot cuoi la con so de quyet dinh noi nhan chinh sach
        # hay ha chi tieu du tru nam sau.
        if "dt" in bang:
            thua, cot, dong = bang["dt"]
            ra += phan("SUẤT DỰ TRỮ DÙNG TỚI ĐÂU: còn thừa %d suất" % thua)
            ra.append(NL(cot))
            ra += dong

        # ---- 7. Em chua co CLB nao ----
        # Nhom nha truong phai xu ly tiep, nen no nam trong tep mang di hop.
        # Doc tu `get_em_chua_co_cho` chu khong tu `get_do_phu`: ban kia cat
        # danh sach con 200 em cho giao dien, va chi co TEN — ma cach xu ly
        # phu thuoc vao em da khai may nguyen vong, vao CLB chat den dau.
        if "tt" in bang:
            so_em, cot, dong = bang["tt"]
            ra += phan("{person_u} CHƯA CÓ {slot_u} NÀO: %d {person_l}" % so_em)
            if dong:
                ra.append(NL(cot))
                ra += dong
            else:
                ra.append(["(không có {person_l} nào, mọi {person_l} đều có ít nhất một chỗ)", ""])

        return ra
    def _chi_tiet_loi_xuat(self, e) -> str:
        """`detail` AN TOÀN cho lỗi xuất tệp (A13.11): kiểu lỗi (và lý do hệ điều hành nếu là
        OSError), KHÔNG kèm tên tệp / đường dẫn máy như `str(e)`. Chi tiết đầy đủ (có đường dẫn)
        vào `loi_ung_dung.txt` cạnh app.db. Chỉ gọi trong khối `except`."""
        import chan_doan

        try:
            chan_doan.ghi_ngoai_le_canh_db(self.db_path, "Loi xuat: %s" % type(e).__name__)
        except Exception:
            pass
        if isinstance(e, OSError) and e.strerror:
            return "%s: %s" % (type(e).__name__, e.strerror)
        return type(e).__name__

    def _duong_xuat(self, output_path: str, ten_mac_dinh: str,
                    kem_duoi: tuple = (), thu_muc_du_phong: str = "") -> str:
        """Chỗ đặt một tệp (hoặc thư mục) xuất ra — MỘT luật cho mọi lần xuất.

        Rỗng hoặc TƯƠNG ĐỐI -> thư mục Tải xuống (lùi về cạnh app.db nếu
        không ghi được). Đường dẫn TUYỆT ĐỐI -> đúng chỗ bên gọi chỉ định.
        Cả hai đều KHÔNG ghi đè tệp đã có: `x.csv` thành `x (2).csv` như
        trình duyệt (A13.9: trước đây đường tuyệt đối ghi đè im lặng, nên
        xuất hai lần ra cùng một chỗ là mất tệp lần trước). Xem `export_csv`.

        `thu_muc_du_phong`: chỗ lùi về khi Tải xuống không ghi được; mặc định là thư mục chứa
        app.db. Việc xuất KHÔNG thuộc workspace đang mở (export_workspace) truyền chỗ trung tính
        để tệp không nằm lẫn trong dữ liệu của một workspace khác.
        """
        output_path = (output_path or "").strip() or ten_mac_dinh
        if os.path.isabs(output_path):
            # Đường là THƯ MỤC có sẵn: "trùng tên → x (2)" sẽ đẻ ra tệp `x (2)` không đuôi NGOÀI
            # thư mục đó (A13.11, N1). Từ chối bằng lỗi có tên, như trước A13.9.
            if os.path.isdir(output_path):
                # Chỉ TÊN thư mục, không phải cả đường dẫn máy: phản hồi lỗi không mang đường dẫn.
                raise LoiDuongXuat(err(
                    "xuat_duong_la_thu_muc",
                    path=os.path.basename(output_path.rstrip("/\\")) or output_path))
            return duong_dan_khong_de(output_path, kem_duoi)
        thu_muc = self.thu_muc_xuat or thu_muc_tai_ve()
        if not (thu_muc and os.path.isdir(thu_muc)
                and os.access(thu_muc, os.W_OK)):
            thu_muc = thu_muc_du_phong or os.path.dirname(os.path.abspath(self.db_path))
        # Chi tranh ghi de o duong CHUONG TRINH tu chon.
        # `kem_duoi`: tep di kem cung ten goc (so Excel + bo .csv) — ten goc
        # phai con trong cho moi duoi.
        return duong_dan_khong_de(
            os.path.join(thu_muc, os.path.basename(output_path)), kem_duoi)
    def _goc_xuat_hop_le(self) -> list:
        """Những thư mục GỐC mà tệp xuất có thể nằm trong — xem `_duong_xuat`."""
        goc = [self.thu_muc_xuat or thu_muc_tai_ve(),
               os.path.dirname(os.path.abspath(self.db_path))]
        return [os.path.realpath(g) for g in goc if g]
    @staticmethod
    def _nam_trong(thu_muc: str, goc: str) -> bool:
        """`thu_muc` là `goc` hoặc nằm bên trong nó.

        `commonpath` ném ValueError khi hai đường dẫn KHÁC Ổ ĐĨA (Windows:
        C:\\ và D:\\). Khác ổ thì chắc chắn không nằm trong nhau — trả False
        để phép so đi tiếp tới gốc hợp lệ kế tiếp, thay vì hỏng cả lần mở
        (tải xuống ở C: không ghi được, tệp rơi về cạnh app.db ở D:).
        """
        try:
            return os.path.commonpath([thu_muc, goc]) == goc
        except ValueError:
            return False
    def mo_thu_muc(self, path: str):
        """Mở thư mục chứa tệp vừa xuất trong trình quản lý tệp của máy.

        Chỉ hiện đường dẫn thì giáo viên phải tự lần tới thư mục Tải xuống
        — việc không phải ai cũng làm được. `path` là một TỆP (mở thư mục
        chứa nó) hoặc một THƯ MỤC (mở chính nó, vd thư mục dữ liệu đầu vào).

        AN TOÀN: hàm này gọi được từ JavaScript, nên CHỈ mở thư mục nằm
        trong chỗ phần mềm tự đặt tệp xuất (`_goc_xuat_hop_le`). So bằng
        `realpath` + `commonpath` để "..", liên kết tượng trưng hay đường
        dẫn lạ đều không lọt ra ngoài. Không bao giờ chạy qua shell.
        """
        try:
            p = os.path.realpath((path or "").strip() or ".")
            thu_muc = p if os.path.isdir(p) else os.path.dirname(p)
            if not os.path.isdir(thu_muc):
                return _fail(err("thu_muc_khong_hop_le", path=path))
            if not any(self._nam_trong(thu_muc, g) for g in self._goc_xuat_hop_le()):
                return _fail(err("thu_muc_khong_hop_le", path=path))
            if sys.platform == "win32":
                os.startfile(thu_muc)  # noqa: S606 — thu muc da duoc soat o tren
            else:
                import subprocess
                lenh = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([lenh, thu_muc], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            return _ok({"dir": thu_muc})
        except Exception as e:
            return _fail(err("thu_muc_khong_mo_duoc", detail=str(e)))

    # Đuôi tệp mà phần mềm tự xuất ra; chỉ những đuôi này `mo_tep` mới mở (không bao giờ .exe, .bat, .ps1, .lnk ...).
    _DUOI_TEP_XUAT = (".html", ".csv", ".xlsx", ".pdf", ".docx")

    def mo_tep(self, path: str):
        """GT4-L5: mở đúng TỆP vừa xuất bằng chương trình mặc định của máy (cạnh nút "Mở thư mục").

        AN TOÀN (gọi được từ JavaScript, nên là cửa chạy chương trình ngoài): chỉ mở TỆP có thật nằm trong chỗ phần
        mềm đặt tệp xuất (`_goc_xuat_hop_le`, so bằng `realpath` + `commonpath`) VÀ có đuôi trong `_DUOI_TEP_XUAT`.
        Thư mục, tệp lạ, tệp chạy được: `tep_khong_hop_le`. Không chạy qua shell.
        """
        try:
            p = os.path.realpath((path or "").strip()) if (path or "").strip() else ""
            if (not p or not os.path.isfile(p) or not p.lower().endswith(self._DUOI_TEP_XUAT)
                    or not any(self._nam_trong(os.path.dirname(p), g) for g in self._goc_xuat_hop_le())):
                return _fail(err("tep_khong_hop_le", path=path))
            if sys.platform == "win32":
                os.startfile(p)  # noqa: S606 — tep da duoc soat o tren (trong cho xuat, duoi an toan)
            else:
                import subprocess
                lenh = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.Popen([lenh, p], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return _ok({"path": p})
        except Exception as e:
            return _fail(err("tep_khong_mo_duoc", detail=str(e)))

    # -----------------------------------------------------------------
    # KẾT QUẢ CÓ CÒN KHỚP DỮ LIỆU KHÔNG — và đã đổi gì so với lần trước
    # -----------------------------------------------------------------
    @staticmethod
    def _dau_van_tay_du_lieu(cur, rules=None) -> str:
        """Xem `rbda_priority_pipeline.dau_van_tay_du_lieu` — MỘT định nghĩa
        "dữ liệu quyết định kết quả" cho cả lần chạy lẫn phép so sau đó."""
        return dau_van_tay_du_lieu(cur, rules)
    def get_trang_thai_ket_qua(self):
        """Kết quả đang lưu có còn khớp dữ liệu hiện tại không.

        `ket_qua_cu` = đã có kết quả VÀ dữ liệu đã sửa sau lần chạy tạo ra
        nó (hoặc CSDL cũ chưa từng ghi dấu vân tay). Dùng cho dải cảnh báo ở
        thẻ Kết quả, cho mọi lần xuất tệp, và cho tệp tổng hợp.
        """
        try:
            rules = self._luat_nghiem()
            with self._ket_noi_doc() as cur:
                co_ket_qua = cur.execute(
                    "SELECT COUNT(*) FROM match_results").fetchone()[0] > 0
                dvt = cur.execute(
                    "SELECT dau_van_tay, luc FROM dau_van_tay_chay WHERE id = 1"
                ).fetchone()
                meta = cur.execute(
                    "SELECT run_at FROM run_meta WHERE id = 1").fetchone()
                hien_tai = self._dau_van_tay_du_lieu(cur, rules) if co_ket_qua else None
            ket_qua_cu = bool(co_ket_qua and (dvt is None or dvt[0] != hien_tai))
            return _ok({
                "co_ket_qua": co_ket_qua,
                "ket_qua_cu": ket_qua_cu,
                "luc_chay": meta[0] if meta else None,
            })
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
    # Thứ tự cố định để tệp và màn hình liệt kê giống nhau.
    _LOAI_THAY_DOI = ("moi_duoc_xep", "mat_cho", "doi_clb", "doi_dien",
                      "hoc_sinh_moi", "bi_bo")
    def get_thay_doi_ket_qua(self):
        """So bảng kết quả hiện tại với bản chụp NGAY TRƯỚC lần chạy gần nhất.

        So theo cặp (học sinh, buổi). Chỉ trả những cặp KHÁC nhau:
          * `moi_duoc_xep` — trước không có CLB, nay có
          * `mat_cho`      — trước có CLB, nay không
          * `doi_clb`      — CLB khác
          * `doi_dien`     — cùng CLB, đổi diện (dự trữ ↔ thường)
          * `hoc_sinh_moi` — trước chưa có dòng nào của cặp này
          * `bi_bo`        — nay không còn dòng nào của cặp này
        Lần chạy đầu tiên thì bản chụp rỗng -> `co_lan_truoc` = False.
        """
        try:
            with self._ket_noi_doc() as cur:
                meta = cur.execute(
                    "SELECT run_at FROM run_meta WHERE id = 1").fetchone()
                truoc = {
                    (r["student_id"], r["buoi"]): r for r in cur.execute(
                        "SELECT * FROM ket_qua_truoc")
                }
                nay = {
                    (r["student_id"], r["buoi"]): r for r in cur.execute(
                        "SELECT * FROM match_results")
                }
                ten_hs = dict(cur.execute(
                    "SELECT student_id, name FROM students").fetchall())
                ten_clb = dict(cur.execute(
                    "SELECT club_id, name FROM clubs").fetchall())
                run_at_truoc = next(
                    (r["run_at"] for r in truoc.values() if r["run_at"]), None)
                ds_buoi = self._ds_buoi(cur)

            dong = []
            for khoa in sorted(set(truoc) | set(nay)):
                a, b = truoc.get(khoa), nay.get(khoa)
                clb_a = a["club_id"] if a else None
                clb_b = b["club_id"] if b else None
                dien_a = a["matched_tier"] if a else None
                dien_b = b["matched_tier"] if b else None
                if a is None:
                    loai = "hoc_sinh_moi"
                elif b is None:
                    loai = "bi_bo"
                elif clb_a == clb_b:
                    if clb_a is None or dien_a == dien_b:
                        continue
                    loai = "doi_dien"
                elif clb_a is None:
                    loai = "moi_duoc_xep"
                elif clb_b is None:
                    loai = "mat_cho"
                else:
                    loai = "doi_clb"
                sid, buoi = khoa
                dong.append({
                    "student_id": sid, "name": ten_hs.get(sid) or "",
                    "buoi": buoi,
                    "club_cu": clb_a, "ten_club_cu": ten_clb.get(clb_a) if clb_a else None,
                    "dien_cu": dien_a,
                    "club_moi": clb_b, "ten_club_moi": ten_clb.get(clb_b) if clb_b else None,
                    "dien_moi": dien_b,
                    "loai": loai,
                })
            return _ok({
                "co_lan_truoc": bool(truoc),
                "run_at_truoc": run_at_truoc,
                "run_at_moi": meta[0] if meta else None,
                "nhieu_buoi": len(ds_buoi) > 1,
                "dong": dong,
                "dem": {k: sum(1 for d in dong if d["loai"] == k)
                        for k in self._LOAI_THAY_DOI},
            })
        except Exception as e:
            return _fail(err("error_reading_results", detail=str(e)))
    _NHAN_LOAI_THAY_DOI = {
        "moi_duoc_xep": "Mới được xếp",
        "mat_cho": "Mất chỗ",
        "doi_clb": "Đổi {slot_sl}",
        "doi_dien": "Đổi diện",
        "hoc_sinh_moi": "{person} mới",
        "bi_bo": "Không còn trong kết quả",
    }
    @staticmethod
    def _nhan_dien(tier):
        # 'reserve'/'general' la ma noi bo — giao vien khong phai doan.
        return {"reserve": "Dự trữ", "general": "Thường"}.get(tier or "", "")
    def export_thay_doi_ket_qua(self, output_path: str = ""):
        """Tệp `thay_doi_ket_qua.csv`: những em có kết quả khác lần chạy trước."""
        try:
            kq = self.get_thay_doi_ket_qua()
            if not kq["ok"]:
                return kq
            d = kq["data"]
            if not d["co_lan_truoc"]:
                return _fail(err("chua_co_lan_chay_truoc"))
            path = self._duong_xuat(output_path, "thay_doi_ket_qua.csv")
            nb = d["nhieu_buoi"]
            nhan = self._nhan_xuat()
            header = [dien_nhan(c, nhan) for c in (
                ["Mã {person_l}", "Họ tên"] + (["{session}"] if nb else [])
                + ["{slot_s} cũ", "Diện cũ", "{slot_s} mới", "Diện mới", "Loại thay đổi"])]
            dong = [
                [x["student_id"], x["name"]] + ([x["buoi"]] if nb else [])
                + [x["ten_club_cu"] or x["club_cu"] or "(không có)",
                   self._nhan_dien(x["dien_cu"]),
                   x["ten_club_moi"] or x["club_moi"] or "(không có)",
                   self._nhan_dien(x["dien_moi"]),
                   dien_nhan(self._NHAN_LOAI_THAY_DOI[x["loai"]], nhan)]
                for x in d["dong"]
            ]
            tt = self.get_trang_thai_ket_qua()
            ket_qua_cu = bool(tt["ok"] and tt["data"]["ket_qua_cu"])
            # Dong dau noi RO so voi lan nao — thieu no thi tep "thay doi"
            # khong noi duoc la thay doi tu dau.
            dau = [["So sánh kết quả lúc", d["run_at_truoc"] or "",
                    "với kết quả lúc", d["run_at_moi"] or ""]]
            if ket_qua_cu:
                dau.append(["CẢNH BÁO: dữ liệu đã sửa sau lần chạy gần nhất: "
                            "kết quả có thể đã cũ, hãy chạy lại."])
            _ghi_csv(path, [], dau + [[]] + [header] + dong)
            return _ok({"path": path, "n_thay_doi": len(dong),
                        "dem": d["dem"], "ket_qua_cu": ket_qua_cu})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    # -----------------------------------------------------------------
    # DỮ LIỆU ĐẦU VÀO HIỆN TẠI — một Sổ nhập CLB NẠP LẠI ĐƯỢC
    # -----------------------------------------------------------------
    def _du_lieu_so_nhap(self, cur):
        """(clubs, students, n_thi_ngoai_nv, n_ten_doi) đúng dạng `so_nhap.ghi_so_nhap`.

        Sổ đòi mỗi CLB một TÊN riêng (ô NV chọn theo tên), còn CSDL thì không
        (form CLB và CSV cũ cho phép "Toán" lẫn "toán"). Tên đụng nhau thì CLB
        sau được thêm buổi hoặc mã CLB (`so_nhap.ten_khong_trung`) — không
        thế thì sổ vừa xuất ra không nạp lại được. `n_ten_doi` đếm số tên đã thêm để giao diện nói ra.
        """
        clubs = [{
            "club_id": r[0], "name": (r[1] or "").strip() or r[0], "capacity": r[2],
            "reserve_capacity": r[3], "reserve_group": r[4],
            "buoi": "" if (r[5] or BUOI_MAC_DINH) == BUOI_MAC_DINH else r[5],
        } for r in cur.execute(
            "SELECT club_id, name, capacity, reserve_capacity, "
            "COALESCE(reserve_group, ''), buoi FROM clubs ORDER BY club_id")]
        # SG-6: giờ / địa điểm đi cùng sổ khi có CLB nào đã khai; không thì sổ y như cũ.
        gd = {r[0]: (r[1], r[2]) for r in cur.execute("SELECT club_id, gio, dia_diem FROM clubs")}
        if any(g or d for g, d in gd.values()):
            for c in clubs:
                c["gio"], c["dia_diem"] = gd.get(c["club_id"], (None, None))
        n_ten_doi = so_nhap.ten_khong_trung(clubs)
        hs = {r[0]: {"student_id": r[0], "name": r[1] or "", "reserve_group": r[2],
                     "class_id": r[3], "nv": []}
              for r in cur.execute(
                  "SELECT student_id, name, COALESCE(reserve_group, ''), class_id "
                  "FROM students ORDER BY student_id")}
        # Workspace chấm điểm theo NGƯỜI: điểm chung của mỗi người đi vào cột "Điểm" của sổ.
        if self._cfg_ws(nghiem=True)["rules"]["score_scope"] == "per_person":
            for sid, diem in cur.execute(
                    "SELECT student_id, diem_ca_nhan FROM students "
                    "WHERE diem_ca_nhan IS NOT NULL"):
                hs[sid]["diem_ca_nhan"] = diem
        for sid, cid in cur.execute(
                "SELECT student_id, club_id FROM preferences ORDER BY student_id, rank"):
            if sid in hs:
                hs[sid]["nv"].append({"club_id": cid, "thi": False, "diem": ""})
        # Workspace bật điểm Wharton: điểm đã chia của mỗi nguyện vọng đi vào cột "Điểm W k".
        # Tắt thì không đọc bảng wharton_bids và sổ y hệt trước vòng 2.
        if dung_wharton(self._cfg_ws(nghiem=True)["rules"]):
            for sid, cid, diem_w in cur.execute(
                    "SELECT student_id, club_id, points FROM wharton_bids "
                    "ORDER BY student_id, club_id"):
                o = next((x for x in hs.get(sid, {"nv": []})["nv"] if x["club_id"] == cid), None)
                if o is not None:
                    o["diem_w"] = diem_w
        n_ngoai = 0
        for sid, cid, diem in cur.execute("""
                SELECT t.student_id, t.club_id, sc.score
                FROM club_test_selection t
                LEFT JOIN club_scores sc
                       ON sc.student_id = t.student_id AND sc.club_id = t.club_id"""):
            o = next((x for x in hs.get(sid, {"nv": []})["nv"] if x["club_id"] == cid), None)
            if o is None:
                # Sổ chỉ ghi điểm CẠNH một nguyện vọng; thi CLB không xếp
                # nguyện vọng thì sổ không chứa được — đếm để nói ra.
                n_ngoai += 1
                continue
            o["thi"], o["diem"] = True, ("" if diem is None else diem)
        return clubs, list(hs.values()), n_ngoai, n_ten_doi

    def export_du_lieu_dau_vao(self, output_path: str = ""):
        """Xuất dữ liệu đầu vào ĐANG CÓ (kể cả sửa sau lần chạy) thành MỘT
        Sổ nhập CLB. Kéo sổ này vào ô nạp của một CSDL trống là dựng lại y
        nguyên — test `test_xuat_du_lieu.py` canh điều đó.

        Lượt thi một CLB mà em KHÔNG xếp nguyện vọng thì sổ không chứa được
        (điểm luôn nằm cạnh một NV) — đếm vào `n_thi_ngoai_nv` để giao diện
        nói ra. Thuật toán không bao giờ xếp em vào CLB em không chọn, nên
        lượt thi đó không đổi kết quả.
        """
        try:
            ten = "SO_NHAP_CLB_" + datetime.datetime.now().strftime("%Y%m%d_%H%M") + ".xlsx"
            path = self._duong_xuat(output_path, ten)
            with self._ket_noi_doc() as cur:
                clubs, students, n_ngoai, n_ten_doi = self._du_lieu_so_nhap(cur)
            so_nhap.ghi_so_nhap(path, clubs, students, cfg=self._cfg_ws(nghiem=True),
                                co_lop=any(x.get("class_id") for x in students))   # A14
            return _ok({
                "path": path,
                "dir": os.path.dirname(path),
                "n_clubs": len(clubs),
                "n_hoc_sinh": len(students),
                "n_preferences": sum(len(s["nv"]) for s in students),
                "n_tick": sum(1 for s in students for x in s["nv"] if x["thi"]),
                "n_scores": sum(1 for s in students for x in s["nv"]
                                if x["diem"] not in ("", None)),
                "n_thi_ngoai_nv": n_ngoai,
                "n_ten_doi": n_ten_doi,
            })
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def export_wharton_can_sua(self, output_path: str = ""):
        """Danh sách hồ sơ điểm quyết tâm cần sửa (A13.5) thành MỘT tệp Excel. KHÔNG đổi điểm nào.

        Mỗi lỗi một dòng: mã, họ tên, buổi, quỹ, tổng hiện tại, thiếu hoặc thừa bao nhiêu, và câu lỗi
        đã dịch. Cùng nguồn với `list_wharton_canh_bao` (`_ho_so_wharton_tat_ca`). Chỗ đặt tệp theo
        luật của `_duong_xuat`.
        """
        try:
            luat = self._luat_nghiem()
            if not dung_wharton(luat):
                return _fail(err("wharton_chua_bat"))
            from openpyxl import Workbook

            from i18n_errors import format_message
            from rbda_priority_pipeline import WHARTON_NGAN_SACH
            from so_excel import Trang

            path = self._duong_xuat(output_path, "diem_quyet_tam_can_sua.xlsx")
            nhan = self._nhan_xuat()
            with self._ket_noi_doc() as cur:
                ho_so = self._ho_so_wharton_tat_ca(cur, luat)
                ten = {r[0]: r[1] for r in cur.execute("SELECT student_id, name FROM students")}
            dong = []
            for sid in sorted(ho_so["loi"]):
                tong = self._dong_wharton_cua_em(sid, ho_so)["tong"]
                for e in ho_so["loi"][sid]:
                    p = e["params"]
                    buoi, quy = p.get("buoi"), p.get("quy")
                    hien_tai = (tong.get(buoi, {}).get(str(quy))
                                if buoi is not None and quy is not None else None)
                    thieu = p.get("thieu") if e["code"] == "wharton_chua_dung_het" else None
                    thua = (hien_tai - WHARTON_NGAN_SACH
                            if e["code"] == "wharton_vuot_ngan_sach" and hien_tai is not None
                            else None)
                    dong.append([sid, ten.get(sid, sid),
                                 "" if buoi in (None, BUOI_MAC_DINH) else buoi,
                                 quy if quy is not None else "",
                                 hien_tai if hien_tai is not None else "",
                                 thieu if thieu is not None else "",
                                 thua if thua is not None else "",
                                 format_message(e["code"], p, "vi", nhan)])
            wb = Workbook()
            ws = wb.active
            ws.title = "Cần sửa"
            t = Trang(ws, nhan)
            t.tieu_de("ĐIỂM QUYẾT TÂM CẦN SỬA",
                      "Hồ sơ chưa hợp lệ khiến lần chạy xếp bị chặn. Tệp này chỉ để xem, phần mềm "
                      "không đổi điểm nào khi tạo nó.")
            dau, _ = t.bang(["Mã {person_l}", "Họ tên", "{session}", "Quỹ", "Tổng hiện tại",
                             "Thiếu", "Thừa", "Lỗi"], dong, khoa=True, loc=True,
                            rong="Không có hồ sơ nào cần sửa.")
            t.xong(lap_hang=dau)
            wb.save(path)
            return _ok({"path": path, "dir": os.path.dirname(path),
                        "n_hoc_sinh": len({d[0] for d in dong}), "n_dong": len(dong)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def tao_so_nhap_mau(self, output_path: str = "", kieu: str = "thuong"):
        """Tạo Sổ nhập CLB để điền, đặt vào thư mục Tải xuống.

        Phần mềm đã có CLB thì sheet "1. CLB" điền sẵn chúng: người vận
        hành chỉ còn điền học sinh. Chưa có thì sổ trống.

        UX1A-L5: `kieu` = "thuong" (như cũ: có cột Huy chương chỉ khi chế độ huy chương đang bật) hoặc
        "huy_chuong" (luôn là sổ mẫu có cột Loại và Huy chương; dùng khi chế độ đó bật).
        """
        try:
            if kieu not in ("thuong", "huy_chuong"):
                kieu = "thuong"
            path = self._duong_xuat(output_path, "SO_NHAP_CLB.xlsx")
            with self._ket_noi_doc() as cur:
                clubs, _, _, n_ten_doi = self._du_lieu_so_nhap(cur)
            so_nhap.ghi_so_nhap(path, clubs, [], cfg=self._cfg_ws(nghiem=True),
                                 luon_co_cot_w=True,       # sổ mẫu luôn có cột Điểm quyết tâm (A13.7)
                                 co_lop=True,              # và cột Lớp (A14, đã duyệt)
                                 che_do_fa=(kieu == "huy_chuong" or dung_fa_daa(self._luat_nghiem())))   # FG-2 (D3); UX1A-L5: kieu
            return _ok({"path": path, "dir": os.path.dirname(path),
                        "n_clubs": len(clubs), "n_ten_doi": n_ten_doi})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("so_nhap_mau_loi", detail=self._chi_tiet_loi_xuat(e)))

    # -----------------------------------------------------------------
    # HỒ SƠ HỌC SINH — một em hoặc nhiều em được chọn
    # -----------------------------------------------------------------
    def export_hoc_sinh_csv(self, student_ids: list, output_path: str = ""):
        """Toàn bộ dữ liệu của các em được chọn, mỗi dòng một cặp (em, CLB).

        Một cặp có mặt khi em tick thi, xếp nguyện vọng, HOẶC được xếp vào
        CLB đó. Em chưa có gì vẫn có MỘT dòng — chọn em nào thì tệp phải có
        em đó, thiếu im lặng là người nhận tưởng em không tồn tại.

        Điểm: chỉ điểm còn tick, đúng tập lần chạy dùng — trừ workspace chấm điểm theo
        NGƯỜI, nơi mỗi em có MỘT điểm (`students.diem_ca_nhan`) áp cho mọi dòng của em, đúng
        thứ thuật toán đã dùng (không có tick hay điểm từng CLB để mà đọc). Số bốc thăm: trường
        nhiều buổi dùng số TỪNG BUỔI (cùng nguồn với bảng số bốc thăm), một
        buổi dùng số đã khoá. Nguyện vọng thứ: thứ hạng TRONG BUỔI, như cột
        cùng tên ở bảng kết quả.
        """
        try:
            if not isinstance(student_ids, list) or not student_ids:
                return _fail(err("chua_chon_hoc_sinh"))
            ids = list(dict.fromkeys(str(s) for s in student_ids))
            # Luật và nhãn đọc MỘT lần, TRƯỚC khi mở giao dịch đọc dữ liệu.
            cau_hinh = self._cfg_ws(nghiem=True)
            theo_nguoi = diem_theo_nguoi(cau_hinh["rules"])
            nhan = cau_hinh["labels"]

            with self._ket_noi_doc() as cur:
                hs = {r["student_id"]: r for r in cur.execute(
                    "SELECT student_id, name, reserve_group, stb_number FROM students "
                    "WHERE student_id IN (%s)" % ",".join("?" * len(ids)), ids)}
                thieu = [s for s in ids if s not in hs]
                if thieu:
                    return _fail(err("student_not_found", student_id=", ".join(thieu)))
                clb = {r["club_id"]: r for r in cur.execute(
                    "SELECT club_id, name, COALESCE(NULLIF(buoi, ''), ?) AS buoi "
                    "FROM clubs", (BUOI_MAC_DINH,))}
                ds_buoi = self._ds_buoi(cur)
                dau = ",".join("?" * len(ids))
                tick = {(r[0], r[1]) for r in cur.execute(
                    "SELECT student_id, club_id FROM club_test_selection "
                    "WHERE student_id IN (%s)" % dau, ids)}
                diem = {(r[0], r[1]): r[2] for r in cur.execute(
                    "SELECT student_id, club_id, score FROM club_scores "
                    "WHERE student_id IN (%s)" % dau, ids)}
                diem_nguoi = {r[0]: r[1] for r in cur.execute(
                    "SELECT student_id, diem_ca_nhan FROM students "
                    "WHERE diem_ca_nhan IS NOT NULL AND student_id IN (%s)" % dau, ids)
                } if theo_nguoi else {}
                nv: dict = {}
                for r in cur.execute(
                        "SELECT student_id, club_id FROM preferences "
                        "WHERE student_id IN (%s) ORDER BY student_id, rank" % dau, ids):
                    nv.setdefault(r[0], []).append(r[1])
                kq = {(r["student_id"], r["club_id"]): r for r in cur.execute(
                    "SELECT student_id, club_id, matched_tier FROM match_results "
                    "WHERE club_id IS NOT NULL AND student_id IN (%s)" % dau, ids)}

            nhieu_buoi = len(ds_buoi) > 1
            so_buoi: dict = {}
            if nhieu_buoi:
                tham = self.get_so_boc_tham_theo_buoi()
                if tham["ok"]:
                    so_buoi = {e["student_id"]: e["so"]
                               for e in tham["data"]["hoc_sinh"]}

            def buoi_cua(cid):
                return clb[cid]["buoi"] if cid in clb else BUOI_MAC_DINH

            header = (["Mã {person_l}", "Họ tên", "Nhóm dự trữ"]
                      + (["{session}"] if nhieu_buoi else [])
                      + ["Số bốc thăm", "Mã {slot_sl}", "Tên {slot_sl}", "Đăng ký thi",
                         "{score}", "Nguyện vọng thứ", "Kết quả", "Diện"])
            dong = []
            for sid in ids:
                h = hs[sid]
                # Thu hang trong buoi: dem theo thu tu nguyen vong cua em.
                hang: dict = {}
                dem_buoi: dict = {}
                for cid in nv.get(sid, []):
                    b = buoi_cua(cid)
                    dem_buoi[b] = dem_buoi.get(b, 0) + 1
                    hang[cid] = dem_buoi[b]
                cac_clb = list(dict.fromkeys(
                    nv.get(sid, [])
                    + sorted(c for (s, c) in tick if s == sid)
                    + sorted(c for (s, c) in kq if s == sid)))
                # Sap theo buoi (thu tu ngay), roi theo thu tu tren.
                cac_clb.sort(key=lambda c: (ds_buoi.index(buoi_cua(c))
                                            if buoi_cua(c) in ds_buoi else 99))

                def so_tham(b, sid=sid, h=h):
                    if nhieu_buoi:
                        v = so_buoi.get(sid, {}).get(b)
                        return "" if v is None else v
                    return "" if h["stb_number"] is None else h["stb_number"]

                goc = [sid, h["name"] or "", h["reserve_group"] or ""]
                if not cac_clb:
                    dong.append(goc + ([""] if nhieu_buoi else [])
                                + [so_tham(None) if not nhieu_buoi else "",
                                   "", "(chưa nhập gì)", "", "", "", "", ""])
                    continue
                for cid in cac_clb:
                    b = buoi_cua(cid)
                    co_tick = (sid, cid) in tick
                    if theo_nguoi:
                        d = diem_nguoi.get(sid)
                    else:
                        d = diem.get((sid, cid)) if co_tick else None
                    x = kq.get((sid, cid))
                    dong.append(
                        goc + ([b] if nhieu_buoi else [])
                        + [so_tham(b), cid,
                           clb[cid]["name"] if cid in clb else "",
                           "Có" if co_tick else "—",
                           "" if d is None else ("%g" % d),
                           hang.get(cid, ""),
                           "Được xếp" if x else "—",
                           self._nhan_dien(x["matched_tier"]) if x else ""])

            ten = ("hoc_sinh_%s.csv" % self._ten_file_an_toan(ids[0], "hoc_sinh")
                   if len(ids) == 1 else "hoc_sinh_da_chon_%d_em.csv" % len(ids))
            path = self._duong_xuat(output_path, ten)
            _ghi_csv(path, [dien_nhan(c, nhan) for c in header], dong)
            tt = self.get_trang_thai_ket_qua()
            return _ok({
                "path": path,
                "n_hoc_sinh": len(ids),
                "n_dong": len(dong),
                "ket_qua_cu": bool(tt["ok"] and tt["data"]["ket_qua_cu"]),
            })
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def _khoa_xuat(self, ham, *args):
        """Giữ khoá ghi + bật bộ nhớ báo cáo suốt một lần xuất.

        Khoá ghi: không lời gọi ghi nào chen vào giữa, nên mọi tệp (và mọi
        trang) của một lần xuất cùng chụp MỘT trạng thái dữ liệu. Bộ nhớ:
        xem _nho_trong_luc_xuat.
        """
        with self._khoa_ghi:
            self._bo_nho_xuat = {}
            try:
                return ham(*args)
            finally:
                self._bo_nho_xuat = None

    def export_ket_qua(self, output_path: str = "", kem_csv: bool = False):
        """Xuất kết quả thành MỘT tệp Excel — đường xuất của nút trên giao diện.

        VÌ SAO. Ban giám khảo nhận xét phần xuất quá rối: một lần bấm từng
        đẻ ra tới sáu tệp rời và hai thư mục, tệp `.xlsx` có nhưng thông báo
        không nhắc tới, còn danh sách từng CLB lại không nằm trong sổ. Giờ
        mặc định chỉ ra một tệp `ket_qua_phan_bo.xlsx` sáu trang (xem
        `_ghi_so_excel`). Hỏng sổ Excel là hỏng cả lần xuất — sổ là sản phẩm
        chính, không được lặng lẽ biến mất như trước.

        `kem_csv=True`: ghi thêm bộ `.csv` rời cũ (xem `export_csv`) cạnh sổ,
        cùng tên gốc — cho ai cần đổ số liệu vào phần mềm khác.

        Chỗ đặt tệp theo đúng luật của `_duong_xuat`: rỗng/tương đối thì vào
        thư mục Tải xuống và không ghi đè tệp cũ.
        """
        return self._khoa_xuat(self._export_ket_qua_da_khoa, output_path, kem_csv)

    def _chua_co_ket_qua(self) -> bool:
        """Chưa có kết quả xếp nào (cùng phép đo với `get_trang_thai_ket_qua`: bảng match_results
        rỗng). Hai đường xuất kết quả từ chối TRƯỚC khi tạo tệp, để không có tệp rỗng mà vẫn
        báo "Đã xuất" (A13.5)."""
        with self._ket_noi_doc() as cur:
            return cur.execute("SELECT COUNT(*) FROM match_results").fetchone()[0] == 0

    def _export_ket_qua_da_khoa(self, output_path: str, kem_csv: bool):
        path = None
        try:
            if self._chua_co_ket_qua():
                return _fail(err("xuat_chua_co_ket_qua"))
            # Kem CSV thi ten goc phai con trong cho CA HAI duoi, khong thi tep
            # .csv di kem ghi de mot tep cu trung ten.
            path = self._duong_xuat(output_path, "ket_qua_phan_bo.xlsx",
                                    kem_duoi=(".csv",) if kem_csv else ())
            du = self._du_lieu_xuat()
            try:
                trang = self._luu_so_excel(path, du)
            except Exception as e:
                return _fail(err("error_exporting_excel", detail=self._chi_tiet_loi_xuat(e)))

            ra = {
                "path": path, "excel_path": path, "trang": trang,
                "n_rows": len(du["rows"]),
                "n_hoc_sinh": len({r["student_id"] for r in du["rows"]}),
                "nhieu_buoi": du["nhieu_buoi"],
                "ket_qua_cu": self._ket_qua_cu(),
                "csv_path": None, "per_club_dir": None, "n_club_files": 0,
                "tong_hop_path": None, "thoi_khoa_bieu_path": None,
                "so_boc_tham_path": None,
                "canh_bao": du.get("canh_bao", []),
            }
            if kem_csv:
                # So Excel da ghi xong. CSV hong (vd tep CSV cu dang mo trong
                # Excel tren Windows) khong duoc xoa cong do: van tra ve duong
                # dan so, kem loi rieng cho phan CSV.
                try:
                    bo = self._ghi_bo_csv(os.path.splitext(path)[0] + ".csv", du)
                    bo["csv_path"] = bo.pop("path")
                    ra.update(bo)
                except Exception as e:
                    ra["loi_csv"] = err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e))
            return _ok(ra)
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def export_csv(self, output_path: str = ""):
        """Bộ tệp `.csv` rời (kèm sổ Excel cùng tên) — đường xuất cho phần
        mềm khác và kịch bản đo đạc. Giao diện gọi `export_ket_qua`."""
        return self._khoa_xuat(self._export_csv_da_khoa, output_path)

    def _export_csv_da_khoa(self, output_path: str = ""):
        """
        Xuất kết quả phân bổ ra CSV:

          1. MỘT FILE TỔNG — mọi học sinh, đủ tên và diện trúng tuyển.
          2. MỘT THƯ MỤC theo CLB — mỗi CLB một file, kèm file
             `_chua_duoc_xep.csv` liệt kê các em chưa vào CLB nào.
          3. Tệp tổng hợp, và (nhiều buổi) thời khoá biểu, từng buổi, số
             bốc thăm.
          4. Sổ Excel cùng tên gốc. Hỏng sổ KHÔNG làm hỏng lần xuất này —
             các tệp `.csv` đã ghi xong và vẫn dùng được, `excel_path` None.

        output_path rỗng hoặc TƯƠNG ĐỐI -> tệp rơi vào **thư mục Tải
        xuống** của người dùng (lùi về cạnh app.db nếu không ghi được). Đường
        dẫn TUYỆT ĐỐI thì đặt đúng chỗ bên gọi chỉ định. Cả hai đều không
        ghi đè tệp cũ (trùng tên thì `x (2).csv`). Luôn trả về đường dẫn
        ĐẦY ĐỦ đã dùng để giao diện hiện đúng chỗ tệp nằm.
        """
        try:
            if self._chua_co_ket_qua():
                return _fail(err("xuat_chua_co_ket_qua"))
            # So Excel cung ten goc di kem -> ten goc phai trong cho ca .xlsx,
            # khong thi ghi de so ma nut tren giao dien vua de o Tai xuong.
            output_path = self._duong_xuat(output_path, "ket_qua_phan_bo.csv",
                                           kem_duoi=(".xlsx",))
            du = self._du_lieu_xuat()
            ra = self._ghi_bo_csv(output_path, du)

            duong_excel = os.path.splitext(output_path)[0] + ".xlsx"
            try:
                self._luu_so_excel(duong_excel, du)
            except Exception:
                duong_excel = None
            ra["excel_path"] = duong_excel
            return _ok(ra)
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def export_ly_do_csv(self, output_path: str = ""):
        """FA-DAA (FA-6): `ket_qua_ly_do.csv` — lý do của LẦN CHẠY MỚI NHẤT, mỗi dòng một học sinh một
        CLB: mã học sinh, buổi, CLB, nhóm phòng, mã lý do, câu giải thích (`fa_ly_do.cau_ly_do`),
        số bốc thăm CỦA CHÍNH EM, vị trí chờ. Câu không chứa mã học sinh khác. Chưa có lý do (FA tắt,
        hay chưa chạy) thì `fa_chua_co_ly_do`."""
        return self._khoa_xuat(self._export_ly_do_da_khoa, output_path)

    @staticmethod
    def _doc_ly_do_moi_nhat(cur):
        """(run_id, các dòng lý do, các buổi thiếu lý do) — FA-S7 + FA-N1.

        MỖI buổi lấy lý do của lần chạy MỚI NHẤT có chạy buổi đó (chạy riêng một buổi không làm mất
        lý do các buổi khác). Lần đó không phải FA (không có `fa_ly_do` cho buổi ấy) -> buổi đó
        không có lý do và được liệt kê ở phần thứ ba. `run_id` trả về = lần FA mới nhất được dùng;
        không buổi nào có lý do -> (None, [], buổi...)."""
        runs = cur.execute(
            "SELECT run_id, buoi_da_chay FROM run_history WHERE %s ORDER BY run_id DESC"
            % loc_chinh_thuc(cur)).fetchall()      # GT2: bỏ lần chạy thử
        buoi_ket_qua = {r[0] for r in cur.execute(
            "SELECT DISTINCT buoi FROM match_results").fetchall()}
        buoi_ly_do = {(r[0], r[1]) for r in cur.execute(
            "SELECT DISTINCT run_id, buoi FROM fa_ly_do").fetchall()}
        # FA-P6: thứ tự NGÀY (`chu_nhat` sau `thu_7`), nên cảnh báo / `thieu_buoi` cũng theo ngày
        tat_ca_buoi = sorted(buoi_ket_qua | {b for _, b in buoi_ly_do}, key=khoa_sap_buoi)
        chon, thieu = {}, []                      # buổi -> run_id dùng
        for buoi in tat_ca_buoi:
            for run_id, da_chay in runs:
                ds = [x for x in (da_chay or "").split(",") if x]
                if ds and buoi not in ds:
                    continue
                if (run_id, buoi) in buoi_ly_do:
                    chon[buoi] = run_id
                else:
                    thieu.append(buoi)
                break
        if not chon:
            return None, [], thieu
        dong = []
        for buoi, run_id in chon.items():
            dong += cur.execute(
                "SELECT l.student_id, l.buoi, l.club_id, COALESCE(c.name, l.club_id), "
                " l.outcome, l.reason, l.rank_in_list, l.cut_score, l.diem_em, l.n_hoa, "
                " l.k_cho, l.waitlist_pos, l.cut_medal, s.stb_number, n.group_no "
                "FROM fa_ly_do l LEFT JOIN clubs c ON c.club_id = l.club_id "
                "LEFT JOIN students s ON s.student_id = l.student_id "
                "LEFT JOIN fa_nhom n ON n.run_id = l.run_id AND n.buoi = l.buoi "
                " AND n.student_id = l.student_id AND n.club_id = l.club_id "
                "WHERE l.run_id = ? AND l.buoi = ?", (run_id, buoi)).fetchall()
        # FA-O1: buổi theo THỨ TỰ NGÀY (như COLLATE THU_TU_BUOI), không theo vần chữ cái
        dong.sort(key=lambda r: (r[0], khoa_sap_buoi(r[1]), r[6] if r[6] is not None else 999, r[2]))
        return max(chon.values()), dong, thieu

    @staticmethod
    def _cau_cua_dong(r):
        return fa_ly_do.cau_ly_do(
            {"outcome": r[4], "reason": r[5], "rank_in_list": r[6], "cut_score": r[7],
             "diem_em": r[8], "n_hoa": r[9], "k_cho": r[10], "waitlist_pos": r[11],
             "cut_medal": r[12]}, r[3])

    def get_ly_do_ket_qua(self):
        """FA-UI-4: câu giải thích của lần chạy mới nhất cho thẻ kết quả: {fa_bat, run_id, cau: {mã HS:
        {buổi: [câu theo thứ tự nguyện vọng]}}, thieu_buoi: [buổi không có lý do, theo thứ tự ngày]} (FA-P3).
        FA tắt -> fa_bat False, không đọc gì thêm."""
        try:
            try:
                fa_bat = dung_fa_daa(self._luat_nghiem())
            except Exception:
                fa_bat = False
            if not fa_bat:
                return _ok({"fa_bat": False, "run_id": None, "cau": {}})
            with self._ket_noi_doc() as cur:
                run_id, dong, thieu = self._doc_ly_do_moi_nhat(cur)
            cau = {}
            for r in dong:
                cau.setdefault(r[0], {}).setdefault(r[1], []).append(self._cau_cua_dong(r))
            # FA-P3: buổi không có lý do (lần chạy mới nhất của buổi đó không FA) -> màn hình báo, không im lặng
            return _ok({"fa_bat": True, "run_id": run_id, "cau": cau, "thieu_buoi": thieu})
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    # ===== GT1-L1: giải trình một học sinh (chỉ ĐỌC) =====
    def get_giai_trinh_hoc_sinh(self, student_id, run_id=None):
        """GT1-L1: vì sao MỘT học sinh có (hoặc không có) từng CLB, cho lần chạy mới nhất (hay `run_id`).

        Trả {ok, data, errors}; `data` xem `giai_trinh.giai_trinh_mot_hoc_sinh`. FA bật: dùng lại dòng
        `fa_ly_do` đã lưu; FA tắt: dựng lại lần chạy trong bộ nhớ bằng bộ số bốc thăm đã khoá. Không ghi gì.
        Dữ liệu đã đổi sau lần chạy (dấu vân tay khác, hay dựng lại ra khác kết quả đã lưu) -> `du_lieu_da_doi`
        True. Lỗi: `gt1_chua_chay`, `gt1_khong_co_hoc_sinh`, `gt1_lan_chay_cu` (chỉ lần mới nhất có kết quả
        lưu), `gt1_khong_tim_thay_lan_chay`."""
        try:
            return self._giai_trinh_hoc_sinh(student_id, run_id, "giao_vien")   # GT4-L4: khung tra cứu = giọng trung tính
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def _giai_trinh_hoc_sinh(self, student_id, run_id, giong="hoc_sinh"):
        import giai_trinh
        r = self._giai_trinh_dung_lai(run_id)
        if isinstance(r, dict):
            return r
        du_lieu, thong_tin_hs = r
        if student_id not in thong_tin_hs:
            return _fail(err("gt1_khong_co_hoc_sinh"))
        return _ok(self._giai_trinh_them_ten(giai_trinh.giai_trinh_mot_hoc_sinh(du_lieu, student_id, giong),
                                             thong_tin_hs[student_id]))

    def export_phieu_giai_trinh(self, output_path: str = "", student_ids=None, lop=None):
        """GT1-L3: MỘT tệp HTML tự đủ để in, mỗi học sinh một trang (mã, tên, lớp, nguyện vọng, điểm của chính em,
        câu giải thích; chỗ trống cho mã tra cứu). `student_ids` (danh sách mã) hoặc `lop` chọn em; không chọn gì
        = mọi em. Dựng lại lần chạy MỘT lần rồi lặp. Chỗ đặt như mọi lần xuất (`_duong_xuat`, không ghi đè).
        Lỗi: `gt1_chua_chay`, `gt1_khong_co_hoc_sinh` (không em nào khớp), `gt1_lan_chay_cu`. Trả {path, n_trang}."""
        return self._khoa_xuat(self._export_phieu_giai_trinh_da_khoa, output_path, student_ids, lop)

    def _phieu_chuan_bi(self, student_ids, lop):
        """Chọn các em cần phiếu (HTML hoặc PDF dùng chung): trả `(du_lieu, thong_tin_hs, chon, so_ngay, ma_cua)`
        hoặc một phản hồi lỗi `_fail(...)` (kiểu dict). Chỉ ĐỌC."""
        r = self._giai_trinh_dung_lai(None)
        if isinstance(r, dict):
            return r
        du_lieu, thong_tin_hs = r
        if student_ids is not None:
            chon = [sid for sid in dict.fromkeys(str(x) for x in student_ids) if sid in thong_tin_hs]
        else:
            chon = list(thong_tin_hs)
        if lop is not None and str(lop).strip():
            lop_chuan = chuan_hoa_lop(lop)
            chon = [sid for sid in chon if (thong_tin_hs[sid][1] or None) == lop_chuan]
        chon.sort(key=lambda sid: (self._khoa_lop_tu_nhien(thong_tin_hs[sid][1]), sid))
        if not chon:
            return _fail(err("gt1_khong_co_hoc_sinh"))
        bat_kn, so_ngay_kn = self._co_khieu_nai()      # luật của workspace; chỉ in số ngày khi khiếu nại BẬT
        so_ngay = so_ngay_kn if bat_kn else None
        with self._ket_noi_doc() as cur:
            ma_cua = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))   # GT1-L4: mã của CHÍNH em
        return du_lieu, thong_tin_hs, chon, so_ngay, ma_cua

    @staticmethod
    def _phieu_cac_em(du_lieu, thong_tin_hs, chon, ma_cua):
        import giai_trinh
        return [(giai_trinh.giai_trinh_mot_hoc_sinh(du_lieu, sid),
                 (sid, thong_tin_hs[sid][0], thong_tin_hs[sid][1]), ma_cua.get(sid)) for sid in chon]

    def _export_phieu_giai_trinh_da_khoa(self, output_path, student_ids, lop):
        import phieu_giai_trinh
        try:
            r = self._phieu_chuan_bi(student_ids, lop)
            if isinstance(r, dict):
                return r
            du_lieu, thong_tin_hs, chon, so_ngay, ma_cua = r
            html = phieu_giai_trinh.dung_phieu_html(self._phieu_cac_em(du_lieu, thong_tin_hs, chon, ma_cua), so_ngay)
            duong = self._duong_xuat(output_path, "phieu_giai_trinh.html")
            with open(duong, "w", encoding="utf-8") as f:
                f.write(html)
            return _ok({"path": duong, "n_trang": len(chon)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def export_phieu_giai_trinh_pdf(self, output_path: str = "", lop=None, theo_lop: bool = False,
                                    student_ids=None):
        """XP1-L2: phiếu giải trình dạng PDF (A4 dọc, mỗi học sinh bắt đầu một trang; mỗi dòng nguyện vọng có
        loại CLB). `theo_lop=False`: MỘT tệp (mọi em, hoặc chỉ `lop`). `theo_lop=True`: MỘT THƯ MỤC
        `phieu_giai_trinh_theo_lop`, mỗi lớp một tệp PDF + `_chua_co_lop.pdf` (có `lop` thì chỉ lớp đó).
        `student_ids` (danh sách mã): chỉ các em đó (MỘT mã = một tệp `phieu_giai_trinh_<mã>.pdf` cho khung tra cứu).
        Cùng dữ liệu với phiếu HTML; chỗ đặt như mọi lần xuất (`_duong_xuat`, không ghi đè); chỉ ĐỌC dữ liệu.
        Lỗi: `gt1_chua_chay`, `gt1_khong_co_hoc_sinh`, `gt1_lan_chay_cu`, `xp1_thieu_thu_vien_pdf`.
        Trả {path, n_trang} hoặc {thu_muc, n_tep, n_trang}."""
        return self._khoa_xuat(self._export_phieu_giai_trinh_pdf_da_khoa, output_path, lop, theo_lop, student_ids)

    def _export_phieu_giai_trinh_pdf_da_khoa(self, output_path, lop, theo_lop, student_ids=None):
        import phieu_giai_trinh
        import xuat_pdf
        thu_muc, da_tao = None, False
        try:
            xuat_pdf.san_sang()
            r = self._phieu_chuan_bi(student_ids, lop)
            if isinstance(r, dict):
                return r
            du_lieu, thong_tin_hs, chon, so_ngay, ma_cua = r
            if not theo_lop:
                ten_mac_dinh = "phieu_giai_trinh.pdf"
                if student_ids is not None and len(chon) == 1:
                    ten_mac_dinh = "phieu_giai_trinh_%s.pdf" % self._cat_ten_tep(
                        self._ten_file_an_toan(chon[0], "hs"), 60)
                duong = self._duong_xuat(output_path, ten_mac_dinh)
                duong = phieu_giai_trinh.dung_phieu_pdf(
                    self._phieu_cac_em(du_lieu, thong_tin_hs, chon, ma_cua), duong, so_ngay)
                return _ok({"path": duong, "n_trang": xuat_pdf.dem_trang(duong)})
            nhom: dict = {}
            for sid in chon:                      # `chon` đã xếp theo lớp tự nhiên
                nhom.setdefault(thong_tin_hs[sid][1] or None, []).append(sid)
            thu_muc = self._thu_muc_xuat_moi(output_path, "phieu_giai_trinh_theo_lop")
            os.makedirs(thu_muc)
            da_tao = True                         # từ đây thư mục là CỦA lần xuất này
            da_dung: set = {"_chua_co_lop"}       # giữ chỗ trước: lớp tên "_chua_co_lop" không đè
            n_trang = 0
            for lop_nay, cac_sid in nhom.items():
                ten = "_chua_co_lop" if lop_nay is None else self._ten_chua_dung(
                    self._cat_ten_tep(self._ten_file_an_toan(str(lop_nay), "lop")), da_dung)
                duong = phieu_giai_trinh.dung_phieu_pdf(
                    self._phieu_cac_em(du_lieu, thong_tin_hs, cac_sid, ma_cua),
                    os.path.join(thu_muc, ten + ".pdf"), so_ngay)
                n_trang += xuat_pdf.dem_trang(duong)
            return _ok({"thu_muc": thu_muc, "n_tep": len(nhom), "n_trang": n_trang})
        except xuat_pdf.ThieuThuVienPdf:
            if da_tao and thu_muc:
                shutil.rmtree(thu_muc, ignore_errors=True)
            return _fail(err("xp1_thieu_thu_vien_pdf"))
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            if da_tao and thu_muc:                # không để lại thư mục thiếu lớp trông như đã xuất đủ
                shutil.rmtree(thu_muc, ignore_errors=True)
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    # ===== GT1-L4: mã tra cứu + em tự tra cứu =====
    # Đồng hồ cho khoá tạm: bài kiểm thay `self._gt1_dong_ho` để khỏi phải chờ thật.
    _gt1_dong_ho = staticmethod(time.monotonic)

    def tao_ma_tra_cuu(self, chi_hs_chua_co=True):
        """GT1-L4: tạo mã tra cứu (8 ký tự, `secrets`). `chi_hs_chua_co` True: chỉ em chưa có mã (mã cũ giữ nguyên,
        nên in lại phiếu vẫn đúng mã); False: tạo lại cho MỌI em. Trả {n_tao, n_co_san, n_hoc_sinh}; KHÔNG trả mã
        (xuất qua `export_ma_tra_cuu_csv`). Không đụng kết quả xếp, số khoá bốc thăm hay lịch sử chạy."""
        import ma_tra_cuu
        try:
            with self._ket_noi_ghi() as cur:
                hs = [r[0] for r in cur.execute("SELECT student_id FROM students ORDER BY student_id")]
                if not hs:
                    return _fail(err("gt1_khong_co_hoc_sinh"))
                co = dict(cur.execute("SELECT student_id, ma FROM ma_tra_cuu"))
                if not chi_hs_chua_co:
                    co = {}
                da_dung = set(co.values())
                n_tao = 0
                gio = datetime.datetime.now().isoformat(timespec="seconds")
                for sid in hs:
                    if sid in co:
                        continue
                    m = ma_tra_cuu.sinh_ma_moi(da_dung)
                    da_dung.add(m)
                    cur.execute("INSERT OR REPLACE INTO ma_tra_cuu (student_id, ma, tao_luc) VALUES (?, ?, ?)",
                                (sid, m, gio))
                    n_tao += 1
            return _ok({"n_tao": n_tao, "n_co_san": len(hs) - n_tao, "n_hoc_sinh": len(hs)})
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def tao_lai_ma_tra_cuu(self, student_id):
        """GT1-L4: cấp mã mới cho MỘT em (mất phiếu). Trả {student_id, ma}: người quản trị cần mã để in lại."""
        import ma_tra_cuu
        try:
            with self._ket_noi_ghi() as cur:
                if cur.execute("SELECT 1 FROM students WHERE student_id = ?", (student_id,)).fetchone() is None:
                    return _fail(err("gt1_khong_co_hoc_sinh"))
                da_dung = {r[0] for r in cur.execute("SELECT ma FROM ma_tra_cuu WHERE student_id != ?",
                                                     (student_id,))}
                m = ma_tra_cuu.sinh_ma_moi(da_dung)
                cur.execute("INSERT OR REPLACE INTO ma_tra_cuu (student_id, ma, tao_luc) VALUES (?, ?, ?)",
                            (student_id, m, datetime.datetime.now().isoformat(timespec="seconds")))
            return _ok({"student_id": student_id, "ma": m})
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def export_ma_tra_cuu_csv(self, output_path: str = "", lop=None):
        """GT1-L4: tệp CSV (student_id, name, class, code) để trộn thư in phiếu. `lop` chọn một lớp. Chỗ đặt như
        mọi lần xuất (không ghi đè). Lỗi: `gt1_chua_co_ma`, `gt1_khong_co_hoc_sinh` (không em nào khớp)."""
        return self._khoa_xuat(self._export_ma_tra_cuu_csv_da_khoa, output_path, lop)

    def _export_ma_tra_cuu_csv_da_khoa(self, output_path, lop):
        try:
            with self._ket_noi_doc() as cur:
                if cur.execute("SELECT COUNT(*) FROM ma_tra_cuu").fetchone()[0] == 0:
                    return _fail(err("gt1_chua_co_ma"))
                dong = cur.execute(
                    "SELECT s.student_id, s.name, s.class_id, m.ma FROM ma_tra_cuu m "
                    "JOIN students s ON s.student_id = m.student_id").fetchall()
            if lop is not None and str(lop).strip():
                lop_chuan = chuan_hoa_lop(lop)
                dong = [r for r in dong if (r[2] or None) == lop_chuan]
            if not dong:
                return _fail(err("gt1_khong_co_hoc_sinh"))
            dong.sort(key=lambda r: (self._khoa_lop_tu_nhien(r[2]), r[0]))
            duong = self._duong_xuat(output_path, "ma_tra_cuu.csv")
            _ghi_csv(duong, ["student_id", "name", "class", "code"],
                     [[r[0], r[1] or "", r[2] or "", r[3]] for r in dong])
            return _ok({"path": duong, "n_dong": len(dong)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def tra_cuu_hoc_sinh(self, student_id, ma):
        """GT1-L4: MỘT em tự xem lời giải thích của chính mình bằng mã học sinh + mã tra cứu. Trả đúng dữ liệu của
        `get_giai_trinh_hoc_sinh` cho em đó và KHÔNG gì khác. Mã sai, mã học sinh lạ, em chưa có mã: cùng lỗi
        `gt1_ma_sai` (không để dò ra mã nào có thật). Sai 5 lần cho một mã học sinh -> `gt1_tam_khoa` 60 giây
        (trong bộ nhớ). So mã bằng `hmac.compare_digest`."""
        import hmac

        import ma_tra_cuu
        try:
            sid = str(student_id).strip() if student_id is not None else ""
            thu = self._gt1_luot_sai.setdefault(sid[:64], [0, 0.0])
            bay_gio = self._gt1_dong_ho()
            if thu[1] and bay_gio < thu[1]:
                return _fail(err("gt1_tam_khoa", giay=max(1, int(thu[1] - bay_gio + 0.999))))   # GT4-L5: đếm ngược
            if thu[1]:                                    # hết hạn khoá: đếm lại từ đầu
                thu[0], thu[1] = 0, 0.0
            with self._ket_noi_doc() as cur:
                r = cur.execute("SELECT ma FROM ma_tra_cuu WHERE student_id = ?", (sid,)).fetchone()
            that = r[0] if r else "-" * ma_tra_cuu.DO_DAI           # em lạ: vẫn so một chuỗi cùng độ dài
            dung = hmac.compare_digest(ma_tra_cuu.chuan_hoa(ma).encode("utf-8"), that.encode("utf-8"))
            if not (dung and r):
                thu[0] += 1
                if thu[0] >= ma_tra_cuu.SO_LAN_SAI_TOI_DA:
                    thu[1] = bay_gio + ma_tra_cuu.GIAY_KHOA
                if len(self._gt1_luot_sai) > 5000:        # chặn bộ nhớ khi bị dò bằng nhiều mã lạ
                    self._gt1_luot_sai = {k: v for k, v in self._gt1_luot_sai.items() if v[1] > bay_gio}
                return _fail(err("gt1_ma_sai"))
            thu[0], thu[1] = 0, 0.0
            return self._giai_trinh_hoc_sinh(sid, None)
        except CauHinhHong as e:
            return _fail(loi_cau_hinh(e))
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    @property
    def _gt1_luot_sai(self):
        if "_gt1_luot_sai_d" not in self.__dict__:
            self.__dict__["_gt1_luot_sai_d"] = {}
        return self.__dict__["_gt1_luot_sai_d"]

    @_gt1_luot_sai.setter
    def _gt1_luot_sai(self, v):
        self.__dict__["_gt1_luot_sai_d"] = v

    @staticmethod
    def _giai_trinh_them_ten(ra, ten_lop):
        ra["ten"], ra["lop"] = ten_lop[0] or "", ten_lop[1] or ""     # chỉ tên và lớp của chính em
        return ra

    def _giai_trinh_dung_lai(self, run_id):
        """Dựng lại MỘT LẦN dữ liệu giải trình của lần chạy mới nhất (chỉ ĐỌC). Trả `(du_lieu,
        {mã: (tên, lớp)})` hoặc một phản hồi lỗi `_fail(...)` (kiểu dict)."""
        import json

        import giai_trinh
        from rbda_priority_pipeline import (
            _doc_du_lieu, cat_du_lieu_theo_buoi, default_reserve_eligible_fn, diem_wharton_hieu_luc,
            doc_du_lieu_wharton, doc_stb_buoi, nhom_theo_buoi, sap_buoi, tham_so_luat,
            tu_dien_wharton_mot_clb)

        with self._ket_noi_doc() as cur:
            lan = cur.execute(
                "SELECT run_id, seed, run_at, luat_xep, buoi_da_chay FROM run_history "
                "WHERE %s ORDER BY run_id DESC" % loc_chinh_thuc(cur)).fetchall()   # GT4-L0: bỏ lần chạy thử
            co_kq = cur.execute("SELECT COUNT(*) FROM match_results").fetchone()[0] > 0
            if not lan or not co_kq:
                return _fail(err("gt1_chua_chay"))
            moi_nhat = lan[0]["run_id"]
            chon = next((r for r in lan if run_id is None or r["run_id"] == run_id), None)
            if chon is None:
                return _fail(err("gt1_khong_tim_thay_lan_chay"))
            if chon["run_id"] != moi_nhat:   # chỉ lưu kết quả của lần mới nhất
                return _fail(err("gt1_lan_chay_cu"))
            thong_tin_hs = {r[0]: (r[1], r[2]) for r in cur.execute(
                "SELECT student_id, name, class_id FROM students")}
            luat = json.loads(chon["luat_xep"]) if chon["luat_xep"] else None
            fa_bat = bool(luat and luat.get("fa_daa"))
            students, clubs, scores, applicants, prefs, stb_goc = _doc_du_lieu(cur, luat)
            ten_clb = {r[0]: (r[1] or r[0]) for r in cur.execute("SELECT club_id, name FROM clubs")}
            # XP1-L2: loại CLB (`clubs.loai`) chỉ để HIỂN THỊ trên phiếu; thuật toán xếp không đọc khoá này.
            co_loai = any(r[1] == "loai" for r in cur.execute("PRAGMA table_info(clubs)"))
            loai_clb = dict(cur.execute("SELECT club_id, loai FROM clubs")) if co_loai else {}
            clubs = {cid: dict(c, ten=ten_clb.get(cid, cid), loai=loai_clb.get(cid))
                     for cid, c in clubs.items()}
            luu = cur.execute("SELECT dau_van_tay FROM dau_van_tay_chay WHERE id = 1").fetchone()
            hien_tai = dau_van_tay_du_lieu(cur, luat)
            da_doi = luu is None or luu[0] != hien_tai
            luu_kq = {}
            for sid, buoi, cid in cur.execute(
                    "SELECT student_id, buoi, club_id FROM match_results"):
                luu_kq.setdefault(buoi, {})[sid] = cid
            stb_buoi = doc_stb_buoi(cur) or None
            fa_dong, wharton = {}, None
            if fa_bat:
                _, dong, _ = self._doc_ly_do_moi_nhat(cur)
                for r in dong:
                    fa_dong.setdefault(r[1], {}).setdefault(r[0], []).append({
                        "club_id": r[2], "outcome": r[4], "reason": r[5], "rank_in_list": r[6],
                        "cut_score": r[7], "diem_em": r[8], "n_hoa": r[9], "k_cho": r[10],
                        "waitlist_pos": r[11], "cut_medal": r[12]})
            elif dung_wharton(luat):
                wharton = doc_du_lieu_wharton(cur)

        thong_tin = {"run_id": chon["run_id"], "seed": chon["seed"], "run_at": chon["run_at"],
                     "luat_xep": luat, "buoi_da_chay": chon["buoi_da_chay"]}
        if fa_bat:
            nhom = nhom_theo_buoi(clubs)
            ds_buoi = sap_buoi(set(nhom))
            theo_buoi = {}
            for buoi in ds_buoi:
                clubs_b, scores_b, _, prefs_b = cat_du_lieu_theo_buoi(
                    buoi, nhom[buoi], clubs, scores, applicants, prefs)
                stb_b = (stb_buoi or {}).get(buoi) or stb_goc
                theo_buoi[buoi] = {
                    "clubs": {cid: {"ten": c["ten"], "capacity": c["capacity"],
                                    "reserve_capacity": c["reserve_capacity"],
                                    "chon_loc": bool(scores_b.get(cid)), "loai": c.get("loai")}
                              for cid, c in clubs_b.items()},
                    "prefs": prefs_b, "scores": scores_b, "stb": stb_b,
                    "assign": {sid: cid for sid, cid in luu_kq.get(buoi, {}).items()},
                    "base_rank": {}, "fa_rows": fa_dong.get(buoi, {})}
        else:
            reserve_fn = default_reserve_eligible_fn(students, clubs)
            tham_so = tham_so_luat(luat, students)
            diem_w = None
            if wharton is not None:
                w1, w2 = tu_dien_wharton_mot_clb(
                    prefs, wharton["clb_thi"], wharton["w1"], wharton["w2"], clubs)
                diem_w, _ = diem_wharton_hieu_luc(prefs, w1, w2, scores)
            ket, theo_buoi = giai_trinh.dung_du_lieu_run(
                students, clubs, scores, applicants, prefs, reserve_fn, tham_so["tier_rank"],
                tham_so["bo_qua_du_tru"], diem_w, stb_goc, chon["seed"] or 0, stb_buoi)
            ds_buoi = ket.ds_buoi
            for buoi in ds_buoi:      # dựng lại ra KHÁC kết quả đã lưu = dữ liệu/ luật đã đổi
                lai = {s: c for s, c in theo_buoi[buoi]["assign"].items() if c is not None}
                luu_b = {s: c for s, c in luu_kq.get(buoi, {}).items() if c is not None}
                if lai != luu_b:
                    da_doi = True
        du_lieu = {"fa_bat": fa_bat, "du_lieu_da_doi": da_doi, "run": thong_tin,
                   "ds_buoi": ds_buoi, "buoi": theo_buoi}
        return du_lieu, thong_tin_hs

    def _export_ly_do_da_khoa(self, output_path: str = ""):
        import csv
        try:
            with self._ket_noi_doc() as cur:
                run_id, dong, thieu = self._doc_ly_do_moi_nhat(cur)
            if run_id is None:
                return _fail(err("fa_chua_co_ly_do"))
            duong = self._duong_xuat(output_path, "ket_qua_ly_do.csv")
            with open(duong, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["student_id", "buoi", "club", "group", "reason", "sentence", "stb",
                            "waitlist_pos"])
                for r in dong:
                    cau = self._cau_cua_dong(r)
                    w.writerow([r[0], r[1], r[3], r[14] or "", r[5], cau, r[13], r[11] or ""])
            ra = {"path": duong, "run_id": run_id, "n_rows": len(dong)}
            if thieu:
                ra["canh_bao"] = [err("fa_ly_do_thieu_buoi", buoi=b) for b in thieu]
            return _ok(ra)
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def export_bien_ban_boc_tham(self, output_path: str = ""):
        """FA-9 (D5): `bien_ban_boc_tham.html` — biên bản bốc thăm có người chứng kiến (một trang để in và ký):
        kỳ, thời điểm, dấu vân tay dữ liệu của lần chạy, hạt giống đã khoá, SHA-256 của danh sách (mã học sinh,
        số bốc thăm) đã sắp xếp, số liệu từng buổi, dòng ký. KHÔNG có tên hay mã học sinh. Chưa bốc thăm (chưa
        chạy xếp, chưa khoá hạt giống) thì `bien_ban_chua_boc_tham`. Chỉ ĐỌC dữ liệu."""
        return self._khoa_xuat(self._export_bien_ban_da_khoa, output_path)

    def _export_bien_ban_da_khoa(self, output_path: str = ""):
        try:
            rules = self._luat_nghiem()
            with self._ket_noi_doc() as cur:
                khoa = cur.execute("SELECT is_locked, seed FROM stb_lock WHERE id = 1").fetchone()
                cap = [(r[0], r[1]) for r in cur.execute(
                    "SELECT student_id, stb_number FROM students WHERE stb_number IS NOT NULL")]
                dvt = cur.execute("SELECT dau_van_tay FROM dau_van_tay_chay WHERE id = 1").fetchone()
                dem = {r[0]: {"n_hoc_sinh": r[1], "n_xep": r[2]} for r in cur.execute(
                    "SELECT buoi, COUNT(DISTINCT student_id), COUNT(*) FROM match_results GROUP BY buoi")}
                hien_tai = self._dau_van_tay_du_lieu(cur, rules) if dem else None
            if not khoa or not khoa[0] or khoa[1] is None or not cap or not dvt or not dem:
                return _fail(err("bien_ban_chua_boc_tham"))
            ban_ghi = fa_bien_ban.tao_ban_ghi(
                doc_cau_hinh(self.db_path).get("name", ""),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), dvt[0], khoa[1], cap, dem,
                ket_qua_con_khop=(dvt[0] == hien_tai), fa_daa=dung_fa_daa(rules))
            # FA-9b + FA-P5: bản Excel cạnh bản HTML, MỘT tên gốc cho cả cặp (tên chỉ coi là trống khi trống cho
            # cả .html lẫn .xlsx), không ghi đè tệp cũ
            duong = self._duong_xuat(output_path, "bien_ban_boc_tham.html", kem_duoi=(".xlsx",))
            duong_x = os.path.splitext(duong)[0] + ".xlsx"
            with open(duong, "w", encoding="utf-8") as f:
                f.write(fa_bien_ban.html_bien_ban(ban_ghi))
            fa_bien_ban.ghi_xlsx(ban_ghi, duong_x)
            return _ok({"path": duong, "path_xlsx": duong_x, "sha256_stb": ban_ghi["sha256_stb"],
                        "hat_giong": ban_ghi["hat_giong"],
                        "ket_qua_con_khop": ban_ghi["ket_qua_con_khop"], "n_hoc_sinh": len(cap)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def export_bang_nhu_cau(self, output_path: str = "", buoi: str = ""):
        """FA-DAA (FA-7): `bang_nhu_cau.csv` cho giáo viên xét chỉ tiêu — mỗi CLB: số em xếp đầu
        tiên, số em có trong nguyện vọng, số đạt điểm sàn, chỉ tiêu, số giữ chỗ. KHÔNG có mã hay tên
        học sinh. Cần `rules.fa_daa` bật (`fa_chua_bat`)."""
        return self._khoa_xuat(self._export_bang_nhu_cau_da_khoa, output_path, buoi)

    @staticmethod
    def _bang_nhu_cau_goi_y(cur, buoi=None) -> list:
        """Bảng nhu cầu (FA-7) kèm gợi ý chỉ tiêu kỳ sau (GAP-7, `fa_daa.goi_y_chi_tieu`). Chỉ đọc."""
        import fa_daa
        clubs, _hs, prefs = fa_daa.doc_clubs_va_nguyen_vong(cur)
        _, cap, _ = fa_daa.doc_du_lieu_fa(cur)
        diem: dict = {}
        for cid, sid, d in cur.execute(
                "SELECT sc.club_id, sc.student_id, sc.score FROM club_scores sc "
                "JOIN club_test_selection t ON t.student_id = sc.student_id "
                "AND t.club_id = sc.club_id"):
            diem.setdefault(cid, {})[sid] = d
        ten = {r[0]: r[1] or r[0] for r in cur.execute("SELECT club_id, name FROM clubs")}
        gioi_han = dict(cur.execute("SELECT club_id, gioi_han FROM fa_gioi_han_gv").fetchall())
        rows = fa_daa.bang_nhu_cau(clubs, prefs, diem, clubs, cap, buoi=buoi, ten_clb=ten)
        return fa_daa.goi_y_chi_tieu(rows, gioi_han)

    def _export_bang_nhu_cau_da_khoa(self, output_path: str = "", buoi: str = ""):
        import csv
        try:
            if not dung_fa_daa(self._luat_nghiem()):
                return _fail(err("fa_chua_bat"))
            with self._ket_noi_doc() as cur:
                rows = self._bang_nhu_cau_goi_y(cur, buoi or None)
            duong = self._duong_xuat(output_path, "bang_nhu_cau.csv")
            with open(duong, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["buoi", "club_id", "ten", "loai", "capacity", "nv1", "so_ghi",
                            "so_dat_san", "so_giu_cho", "goi_y_ky_sau"])
                for r in rows:
                    w.writerow([r["buoi"], r["club_id"], r["ten"], r["loai"] or "", r["capacity"],
                                r["nv1"], r["so_ghi"],
                                "" if r["so_dat_san"] is None else r["so_dat_san"],
                                r["so_giu_cho"], r["goi_y_ky_sau"]])
            return _ok({"path": duong, "n_rows": len(rows)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    def export_goi_y_chi_tieu(self, output_path: str = ""):
        """GAP-7 (V§10): `goi_y_chi_tieu.csv` — gợi ý chỉ tiêu kỳ sau = NV1 kỳ này, chặn trên bởi giới hạn giáo viên
        khai (`luu_gioi_han_gv`). KHÔNG có dữ liệu học sinh. Cần `rules.fa_daa` (`fa_chua_bat`)."""
        return self._khoa_xuat(self._export_goi_y_chi_tieu_da_khoa, output_path)

    def _export_goi_y_chi_tieu_da_khoa(self, output_path: str = ""):
        import csv
        try:
            if not dung_fa_daa(self._luat_nghiem()):
                return _fail(err("fa_chua_bat"))
            with self._ket_noi_doc() as cur:
                rows = self._bang_nhu_cau_goi_y(cur)
            duong = self._duong_xuat(output_path, "goi_y_chi_tieu.csv")
            with open(duong, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f)
                w.writerow(["buoi", "club_id", "ten", "loai", "capacity", "nv1", "gioi_han", "goi_y_ky_sau",
                            "ghi_chu"])
                for r in rows:
                    w.writerow([r["buoi"], r["club_id"], r["ten"], r["loai"] or "", r["capacity"], r["nv1"],
                                "" if r["gioi_han"] is None else r["gioi_han"], r["goi_y_ky_sau"], r["ghi_chu"]])
            return _ok({"path": duong, "n_rows": len(rows)})
        except LoiDuongXuat as e:
            return _fail(e.loi)
        except Exception as e:
            return _fail(err("error_exporting_csv", detail=self._chi_tiet_loi_xuat(e)))

    @staticmethod
    def _so_nguyen_duong(x) -> bool:
        return isinstance(x, int) and not isinstance(x, bool) and x > 0

    def luu_gioi_han_gv(self, club_id: str, gioi_han):
        """GAP-7: giới hạn chỉ tiêu giáo viên khai cho MỘT CLB (số nguyên > 0; None = xoá). Chỉ dùng cho gợi ý kỳ sau,
        không đổi chỉ tiêu hiện tại, không vào khoá ưu tiên."""
        try:
            if not dung_fa_daa(self._luat_nghiem()):
                return _fail(err("fa_chua_bat"))
            if gioi_han is not None and not self._so_nguyen_duong(gioi_han):
                return _fail(err("gioi_han_gv_sai", value=repr(gioi_han)))
            with self._ket_noi_ghi() as cur:
                if not cur.execute("SELECT 1 FROM clubs WHERE club_id = ?", (club_id,)).fetchone():
                    return _fail(err("club_not_found", club_id=club_id))
                if gioi_han is None:
                    cur.execute("DELETE FROM fa_gioi_han_gv WHERE club_id = ?", (club_id,))
                else:
                    cur.execute("INSERT INTO fa_gioi_han_gv (club_id, gioi_han) VALUES (?, ?) "
                                "ON CONFLICT(club_id) DO UPDATE SET gioi_han = excluded.gioi_han", (club_id, gioi_han))
            return _ok({"club_id": club_id, "gioi_han": gioi_han})
        except Exception as e:
            return _fail(err("loi_luu_sau_xep", detail=str(e)))

    def kiem_chi_tieu_ky_sau(self, khai: dict):
        """GAP-7: so chỉ tiêu giáo viên khai cho kỳ sau ({club_id: n}) với gợi ý: chỉ được tăng (vi phạm
        `GIAM_SUC_CHUA`). Chỉ đọc."""
        import fa_daa
        try:
            if not dung_fa_daa(self._luat_nghiem()):
                return _fail(err("fa_chua_bat"))
            if not isinstance(khai, dict) or not all(
                    isinstance(n, int) and not isinstance(n, bool) and n >= 0 for n in khai.values()):
                return _fail(err("gioi_han_gv_sai", value=repr(khai)))
            with self._ket_noi_doc() as cur:
                goi_y = {r["club_id"]: r["goi_y_ky_sau"] for r in self._bang_nhu_cau_goi_y(cur)}
            return _ok({"vi_pham": fa_daa.kiem_tang_tu_goi_y(goi_y, khai)})
        except Exception as e:
            return _fail(err("error_reading_last_run", detail=str(e)))

    def _ket_qua_cu(self) -> bool:
        tt = self.get_trang_thai_ket_qua()
        return bool(tt.get("ok") and tt["data"]["ket_qua_cu"])

    def _du_lieu_xuat(self) -> dict:
        """Mọi bảng của một lần xuất, đọc MỘT lần cho cả sổ Excel lẫn bộ CSV.

        Hai định dạng đi ra từ cùng một nguồn — không có hai đường tính song
        song để rồi trôi khỏi nhau.
        """
        with self._ket_noi_doc() as cur:
            rows = cur.execute("""
                SELECT m.student_id, s.name AS ho_ten, m.buoi, m.club_id,
                       c.name AS ten_club, m.rank_in_student_pref, m.matched_tier,
                       s.reserve_group, s.class_id AS lop, c.gio, c.dia_diem
                FROM match_results m
                LEFT JOIN students s ON s.student_id = m.student_id
                LEFT JOIN clubs   c ON c.club_id   = m.club_id
                ORDER BY m.student_id, m.buoi COLLATE THU_TU_BUOI
            """).fetchall()
            ds_buoi = self._ds_buoi(cur)
        nhieu_buoi = len(ds_buoi) > 1
        dien = self._nhan_dien

        # Cot "Buoi" chi xuat hien khi truong THAT SU dung nhieu buoi.
        # Mot buoi ma van co cot day gia tri "__mac_dinh__" thi giao vien
        # phai doan xem no nghia la gi.
        cot_tong = (["Mã {person_l}", "Họ tên", "{cohort}"]
                    + (["{session}"] if nhieu_buoi else [])
                    + ["Mã {slot_sl}", "Tên {slot_sl}", "Nguyện vọng thứ",
                       "Diện trúng tuyển", "Nhóm dự trữ"])
        dong_tong = [
            [r["student_id"], r["ho_ten"] or "", r["lop"] or ""]
            + ([r["buoi"]] if nhieu_buoi else [])
            + [
                r["club_id"] or "",
                r["ten_club"] or ("" if r["club_id"] else "(chưa được xếp)"),
                r["rank_in_student_pref"] if r["rank_in_student_pref"] else "",
                dien(r["matched_tier"]), r["reserve_group"] or "",
            ]
            for r in rows
        ]

        # ---- Thoi khoa bieu tuan: SAN PHAM CHINH cua ban nhieu buoi ----
        # Moi em MOT dong, moi buoi MOT cot — dan bang duoc, phat cho hoc
        # sinh duoc.
        tkb = None
        tkb_xlsx = None
        tham = None
        if nhieu_buoi:
            theo_em: dict = {}
            for r in rows:
                em = theo_em.setdefault(
                    r["student_id"], {"ho_ten": r["ho_ten"] or "", "lop": r["lop"] or "", "o": {}})
                em["o"][r["buoi"]] = (
                    r["ten_club"] or r["club_id"] or "") if r["club_id"] else ""
            tkb = (["Mã {person_l}", "Họ tên"] + list(ds_buoi) + ["Số {slot_sl}"], [
                [sid, em["ho_ten"]]
                + [em["o"].get(b, "") for b in ds_buoi]
                + [sum(1 for b in ds_buoi if em["o"].get(b))]
                for sid, em in sorted(theo_em.items())
            ])
            # Cột Lớp chỉ ở bản Excel; CSV thời khoá biểu giữ nguyên (hợp đồng cột CSV).
            # SG-6: bản Excel (phát cho học sinh) kèm giờ / địa điểm trong ô; CSV giữ nguyên.
            o_xlsx = {}
            for r in rows:
                o_xlsx.setdefault(r["student_id"], {})[r["buoi"]] = (
                    self._o_clb_kem_gio(r) if r["club_id"] else "")
            tkb_xlsx = (["Mã {person_l}", "Họ tên", "{cohort}"] + list(ds_buoi) + ["Số {slot_sl}"], [
                [sid, em["ho_ten"], em["lop"]]
                + [o_xlsx[sid].get(b, "") for b in ds_buoi]
                + [sum(1 for b in ds_buoi if em["o"].get(b))]
                for sid, em in sorted(theo_em.items())
            ])

            # ---- So boc tham tung buoi ----
            # Phan mem xao lai thu tu o moi buoi, nen se co phu huynh hoi
            # "vi sao con toi thu Ba dung thu 30 ma thu Sau dung thu 120".
            # Truong van chi cong bo MOT thu: bo so da khoa cong hat giong.
            # Bang nay la ham TAT DINH cua hai thu do, ai cung tinh lai duoc.
            kq_tham = self.get_so_boc_tham_theo_buoi()
            if kq_tham["ok"] and kq_tham["data"]["da_chay"]:
                tham = (["Mã {person_l}", "Họ tên"] + list(ds_buoi), [
                    [e["student_id"], e["name"] or ""]
                    + [e["so"].get(b, "") for b in ds_buoi]
                    for e in kq_tham["data"]["hoc_sinh"]
                ])

        return {"rows": rows, "ds_buoi": ds_buoi, "nhieu_buoi": nhieu_buoi,
                "cot_tong": cot_tong, "dong_tong": dong_tong,
                "tkb": tkb, "tkb_xlsx": tkb_xlsx, "tham": tham,
                "theo_lop": self._du_lieu_theo_lop(rows, ds_buoi, nhieu_buoi),
                "nhan": self._nhan_xuat()}

    def _ghi_bo_csv(self, output_path: str, du: dict) -> dict:
        """Ghi bộ `.csv` rời từ `_du_lieu_xuat`. Trả về các đường dẫn đã ghi."""
        import csv

        ghi_tho = _ghi_csv   # UTF-8 co BOM + chan cong thuc Excel
        rows = du["rows"]
        dien = self._nhan_dien
        nhan = du.get("nhan")

        def ghi(duong, cot, dong):
            """Ghi một CSV; chỉ DÒNG TIÊU ĐỀ được điền nhãn, dữ liệu để nguyên."""
            ghi_tho(duong, [dien_nhan(c, nhan) for c in cot], dong)

        ghi(output_path, du["cot_tong"], du["dong_tong"])

        goc, _ = os.path.splitext(output_path)
        per_club_dir = goc + "_theo_club"
        os.makedirs(per_club_dir, exist_ok=True)

        # Xoa tep .csv cua lan xuat TRUOC trong dung thu muc nay.
        # Khong xoa thi mot CLB da bi go khoi he thong van con nguyen
        # tep cua no, nam canh cac tep moi va trong y het nhu that.
        # Chi dung .csv, chi trong thu muc do phan mem tu tao ra.
        for cu_ten in os.listdir(per_club_dir):
            if cu_ten.lower().endswith(".csv"):
                try:
                    os.remove(os.path.join(per_club_dir, cu_ten))
                except OSError:
                    pass

        theo_club: dict = {}
        for r in rows:
            theo_club.setdefault(r["club_id"] or None, []).append(r)

        n_file = 0
        # Giu cho "_chua_duoc_xep" truoc, de mot CLB trung ten do khong
        # ghi de danh sach em chua co cho.
        ten_da_dung: set = {"_chua_duoc_xep"}
        for club_id, ds in theo_club.items():
            if club_id is None:
                ten = "_chua_duoc_xep"
            else:
                # Hai club_id khac nhau co the ra cung ten sau khi lam
                # sach ("a/b" va "a\b"), hoac chi khac hoa/thuong.
                ten = self._ten_chua_dung(
                    self._ten_file_an_toan(club_id), ten_da_dung)
            ghi(
                os.path.join(per_club_dir, ten + ".csv"),
                ["Mã {person_l}", "Họ tên", "{cohort}", "Nguyện vọng thứ",
                 "Diện trúng tuyển", "Nhóm dự trữ"],
                [[r["student_id"], r["ho_ten"] or "", r["lop"] or "",
                  r["rank_in_student_pref"] if r["rank_in_student_pref"] else "",
                  dien(r["matched_tier"]), r["reserve_group"] or ""] for r in ds],
            )
            n_file += 1

        duong_tkb = None
        n_tkb = 0
        duong_tham = None
        n_tham = 0
        if du["tkb"]:
            duong_tkb = goc + "_thoi_khoa_bieu.csv"
            ghi(duong_tkb, *du["tkb"])
            n_tkb = len(du["tkb"][1])

            # ---- Mot tep moi buoi, cho giao vien truc ngay do ----
            per_buoi_dir = goc + "_theo_buoi"
            os.makedirs(per_buoi_dir, exist_ok=True)
            for cu_ten in os.listdir(per_buoi_dir):
                if cu_ten.lower().endswith(".csv"):
                    try:
                        os.remove(os.path.join(per_buoi_dir, cu_ten))
                    except OSError:
                        pass
            for b in du["ds_buoi"]:
                ghi(
                    os.path.join(per_buoi_dir, self._ten_file_an_toan(b, "buoi") + ".csv"),
                    ["Mã {person_l}", "Họ tên", "Mã {slot_sl}", "Tên {slot_sl}",
                     "Nguyện vọng thứ", "Diện trúng tuyển"],
                    [
                        [r["student_id"], r["ho_ten"] or "", r["club_id"] or "",
                         r["ten_club"] or "",
                         r["rank_in_student_pref"] if r["rank_in_student_pref"] else "",
                         dien(r["matched_tier"])]
                        for r in rows
                        if r["buoi"] == b and r["club_id"]
                    ],
                )

        if du["tham"]:
            duong_tham = goc + "_so_boc_tham_theo_buoi.csv"
            ghi(duong_tham, *du["tham"])
            n_tham = len(du["tham"][1])

        # ---- Tep TONG HOP: ket qua nay den tu dau, va con gi phai lam ----
        duong_tong_hop = goc + "_tong_hop.csv"
        with open(duong_tong_hop, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerows([_an_toan_cho_excel(o) for o in d]
                        for d in self._bang_tong_hop())

        return {
            "path": output_path,
            "tong_hop_path": duong_tong_hop,
            "n_rows": len(rows),
            "per_club_dir": per_club_dir,
            "n_club_files": n_file,
            "nhieu_buoi": du["nhieu_buoi"],
            "thoi_khoa_bieu_path": duong_tkb,
            "n_thoi_khoa_bieu_rows": n_tkb,
            "so_boc_tham_path": duong_tham,
            "n_so_boc_tham_rows": n_tham,
        }
