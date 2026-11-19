"""XP1-L3: danh sách thành viên dạng PDF (theo CLB, theo lớp). Hàm thuần dựng khối cho `xuat_pdf`.

Mọi chữ hiển thị do bên gọi truyền vào (đã điền nhãn của workspace); module này chỉ xếp bố cục. Không điểm,
không số bốc thăm, không diện trúng tuyển: bên gọi không đưa những cột đó vào.
"""

import xuat_pdf


def _canh_bao(canh_bao):
    return [xuat_pdf.dong_khoa_gia_tri("Chú ý", canh_bao)] if canh_bao else []


def dung_pdf_clb(duong, tieu_de, thong_tin, cot, hang, canh_bao=None) -> str:
    """MỘT tệp cho MỘT CLB (một buổi): tiêu đề, các dòng `thong_tin` [(khoá, giá trị)], bảng `cot`/`hang`
    (bên gọi đã thêm số thứ tự). Trả đường dẫn thật đã ghi."""
    khoi = [xuat_pdf.tieu_de(tieu_de)]
    khoi += [xuat_pdf.dong_khoa_gia_tri(k, v) for k, v in thong_tin if v not in (None, "")]
    khoi += _canh_bao(canh_bao)
    khoi.append(xuat_pdf.bang(cot, hang, [0.5] + [2] * (len(cot) - 1)))
    return xuat_pdf.dung_pdf(duong, khoi)


def dung_pdf_lop(duong, tieu_de, thong_tin, cot, hang, tieu_chua, cot_chua, hang_chua, canh_bao=None) -> str:
    """MỘT tệp cho MỘT lớp: bảng các em đã có chỗ, rồi (nếu có) mục `tieu_chua` cho em chưa có chỗ."""
    khoi = [xuat_pdf.tieu_de(tieu_de)]
    khoi += [xuat_pdf.dong_khoa_gia_tri(k, v) for k, v in thong_tin if v not in (None, "")]
    khoi += _canh_bao(canh_bao)
    if hang:
        khoi.append(xuat_pdf.bang(cot, hang, [0.5] + [2] * (len(cot) - 1)))
    if hang_chua:
        khoi.append(xuat_pdf.tieu_de(tieu_chua))
        khoi.append(xuat_pdf.bang(cot_chua, hang_chua, [0.5] + [2] * (len(cot_chua) - 1)))
    return xuat_pdf.dung_pdf(duong, khoi)
