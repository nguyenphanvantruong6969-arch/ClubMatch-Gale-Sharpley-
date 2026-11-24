"""XP1-L3: danh sách thành viên dạng PDF (theo CLB, theo lớp). Hàm thuần dựng khối cho `xuat_pdf`.

Mọi chữ hiển thị do bên gọi truyền vào (đã điền nhãn của workspace); module này chỉ xếp bố cục. Không điểm,
không số bốc thăm, không diện trúng tuyển: bên gọi không đưa những cột đó vào.
"""

import xuat_pdf

CUOT_STT_MM = 13      # đủ cho chữ "STT" (in đậm) và số tới 4 chữ số trên MỘT dòng, kể cả khi bảng có nhiều cột buổi


def hoa_dau(chu):
    """Viết hoa chữ cái đầu (nhãn như "học sinh", "câu lạc bộ" đi vào đầu tiêu đề); phần còn lại giữ nguyên."""
    chu = str(chu)
    return chu[:1].upper() + chu[1:]


def bang_danh_sach(cot, hang):
    """Bảng có cột đầu là STT (rộng cố định), các cột còn lại chia đều."""
    return xuat_pdf.bang(cot, hang, [1] * len(cot), cot_dau_mm=CUOT_STT_MM)


def _canh_bao(canh_bao):
    return [xuat_pdf.dong_khoa_gia_tri("Chú ý", canh_bao)] if canh_bao else []


def _thong_tin(thong_tin):
    return [xuat_pdf.dong_khoa_gia_tri(hoa_dau(k), v) for k, v in thong_tin if v not in (None, "")]


def dung_pdf_clb(duong, tieu_de, thong_tin, cot, hang, canh_bao=None) -> str:
    """MỘT tệp cho MỘT CLB (một buổi): tiêu đề, các dòng `thong_tin` [(khoá, giá trị)], bảng `cot`/`hang`
    (bên gọi đã thêm số thứ tự). Trả đường dẫn thật đã ghi."""
    khoi = [xuat_pdf.tieu_de(hoa_dau(tieu_de))] + _thong_tin(thong_tin) + _canh_bao(canh_bao)
    khoi.append(bang_danh_sach(cot, hang))
    return xuat_pdf.dung_pdf(duong, khoi)


def dung_pdf_lop(duong, tieu_de, thong_tin, cot, hang, tieu_chua, cot_chua, hang_chua, canh_bao=None) -> str:
    """MỘT tệp cho MỘT lớp: bảng các em đã có chỗ, rồi (nếu có) mục `tieu_chua` cho em chưa có chỗ."""
    khoi = [xuat_pdf.tieu_de(hoa_dau(tieu_de))] + _thong_tin(thong_tin) + _canh_bao(canh_bao)
    if hang:
        khoi.append(bang_danh_sach(cot, hang))
    if hang_chua:
        khoi.append(xuat_pdf.tieu_de(hoa_dau(tieu_chua)))
        khoi.append(bang_danh_sach(cot_chua, hang_chua))
    return xuat_pdf.dung_pdf(duong, khoi)
