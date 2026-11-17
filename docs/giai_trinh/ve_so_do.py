"""Dựng `so_do_luong.svg` từ danh sách bước dưới đây (chỉ dùng thư viện chuẩn).

Chạy: python docs/giai_trinh/ve_so_do.py   (ghi đè so_do_luong.svg cạnh tệp này)
Nền trắng và chữ tối để đọc được ở cả giao diện sáng và tối. Dữ liệu minh hoạ là dữ liệu mô phỏng.
"""

import os
from xml.sax.saxutils import escape

CAC_BUOC = [
    ("1. Biểu mẫu", "Học sinh đăng ký", "Google / Microsoft Forms", "nhap"),
    ("2. Sổ nhập CLB", "Một tệp Excel", "CLB, chỉ tiêu, nguyện vọng, điểm", "nhap"),
    ("3. Kiểm khi nhập", "Báo lỗi theo dòng", "Sai thì không nạp gì", "kiem"),
    ("4. Sao lưu", "Chép app.db", "Trước mọi lần chạy", "chay"),
    ("5. Kiểm dữ liệu", "validate", "Thiếu / mâu thuẫn thì dừng", "kiem"),
    ("6. Khoá bốc thăm", "stb_lottery", "Một lần, dùng lại sau đó", "chay"),
    ("7. Xếp chỗ", "rbda_cascade", "Học sinh đề xuất + dự trữ mềm", "chay"),
    ("8. Soát ổn định", "verify", "Không có cặp phá vỡ", "kiem"),
    ("9. Lưu kết quả", "Một giao dịch", "Lỗi thì quay về như cũ", "chay"),
    ("10. Xuất tệp", "Excel / CSV", "match_results.csv", "ra"),
    ("11. Tra cứu và khiếu nại", "Quản trị / giáo viên", "Phiếu, khiếu nại, lý do", "ra"),
    ("12. Lịch sử chạy", "run_history", "Chỉ thêm, không sửa, không xoá", "ra"),
]
MAU = {"nhap": "#dbeafe", "kiem": "#fef3c7", "chay": "#dcfce7", "ra": "#ede9fe"}
VIEN = "#334155"
CHU = "#0f172a"
COT, RONG, CAO, KHE_X, KHE_Y, LE = 4, 250, 96, 50, 56, 30


def ve() -> str:
    hang = (len(CAC_BUOC) + COT - 1) // COT
    w = LE * 2 + COT * RONG + (COT - 1) * KHE_X
    h = LE + 56 + hang * CAO + (hang - 1) * KHE_Y + 70
    ra = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
          f'role="img" aria-label="Sơ đồ luồng dữ liệu của phần mềm xếp câu lạc bộ (dữ liệu mô phỏng)">',
          '<defs><marker id="mui" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{VIEN}"/></marker></defs>',
          f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>',
          f'<text x="{LE}" y="34" font-family="sans-serif" font-size="20" font-weight="700" fill="{CHU}">'
          'Luồng dữ liệu: từ biểu mẫu đến kết quả (dữ liệu mô phỏng)</text>']
    vi_tri = []
    for i, (tieu_de, dong1, dong2, loai) in enumerate(CAC_BUOC):
        r, c = divmod(i, COT)
        x = LE + c * (RONG + KHE_X)
        y = LE + 56 + r * (CAO + KHE_Y)
        vi_tri.append((x, y))
        ra.append(f'<rect x="{x}" y="{y}" width="{RONG}" height="{CAO}" rx="10" fill="{MAU[loai]}" '
                  f'stroke="{VIEN}" stroke-width="1.5"/>')
        for k, (chu, co, dam) in enumerate(((tieu_de, 16, 700), (dong1, 14, 400), (dong2, 13, 400))):
            ra.append(f'<text x="{x + 14}" y="{y + 28 + k * 24}" font-family="sans-serif" font-size="{co}" '
                      f'font-weight="{dam}" fill="{CHU}">{escape(chu)}</text>')
    for i in range(len(CAC_BUOC) - 1):
        (x1, y1), (x2, y2) = vi_tri[i], vi_tri[i + 1]
        if y1 == y2:
            ra.append(f'<line x1="{x1 + RONG}" y1="{y1 + CAO // 2}" x2="{x2 - 2}" y2="{y2 + CAO // 2}" '
                      f'stroke="{VIEN}" stroke-width="2" marker-end="url(#mui)"/>')
        else:                                   # xuống hàng: đi xuống, sang trái, rồi xuống ô đầu hàng sau
            giua = y1 + CAO + KHE_Y // 2
            ra.append(f'<polyline points="{x1 + RONG // 2},{y1 + CAO} {x1 + RONG // 2},{giua} '
                      f'{x2 + RONG // 2},{giua} {x2 + RONG // 2},{y2 - 2}" fill="none" stroke="{VIEN}" '
                      f'stroke-width="2" marker-end="url(#mui)"/>')
    ghi_chu_y = h - 30
    for k, (loai, ten) in enumerate((("nhap", "Dữ liệu vào"), ("kiem", "Kiểm tra"), ("chay", "Chạy xếp"),
                                     ("ra", "Kết quả và tra cứu"))):
        x = LE + k * 210
        ra.append(f'<rect x="{x}" y="{ghi_chu_y - 14}" width="18" height="18" rx="4" fill="{MAU[loai]}" '
                  f'stroke="{VIEN}"/>')
        ra.append(f'<text x="{x + 26}" y="{ghi_chu_y + 1}" font-family="sans-serif" font-size="13" '
                  f'fill="{CHU}">{escape(ten)}</text>')
    ra.append("</svg>")
    return "\n".join(ra) + "\n"


if __name__ == "__main__":
    duong = os.path.join(os.path.dirname(os.path.abspath(__file__)), "so_do_luong.svg")
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(ve())
    print("Da ghi", duong)
