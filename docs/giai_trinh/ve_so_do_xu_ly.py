"""Dựng `so_do_xu_ly.svg`: sơ đồ luồng XỬ LÝ của một lần chạy xếp (thuật toán, điểm quyết định, nhánh không đủ chỗ).

Chạy: python docs/giai_trinh/ve_so_do_xu_ly.py   (ghi đè so_do_xu_ly.svg cạnh tệp này; chỉ dùng thư viện chuẩn)
Khác `ve_so_do.py` (đường đi của DỮ LIỆU qua 12 bước): sơ đồ này vẽ các QUYẾT ĐỊNH bên trong một lần chạy.
Tên hàm trong sơ đồ là tên thật trong `rbda_priority_pipeline.py` và `api.py` (đối chiếu: `LICH_SU_THAY_DOI.md`).
Nền trắng, chữ tối: đọc được ở cả giao diện sáng và tối. Dữ liệu minh hoạ là dữ liệu mô phỏng.
"""

import os
from xml.sax.saxutils import escape

THU_MUC = os.path.dirname(os.path.abspath(__file__))
MAU = {"nhap": "#dbeafe", "kiem": "#fef3c7", "chay": "#dcfce7", "ra": "#ede9fe", "loi": "#fee2e2", "thieu": "#ffedd5",
       "ghi": "#f1f5f9"}
VIEN, CHU, NET = "#334155", "#0f172a", "#475569"
CX, RONG, CX_PHAI, RONG_PHAI = 470, 420, 940, 300
W, LE_TRAI = 1200, 190


class Ve:
    def __init__(self):
        self.ra = []
        self.nut = {}

    # ---- hình
    def chu(self, x, y, dong, co=13, dam=False, canh="middle"):
        for i, d in enumerate(dong):
            self.ra.append(f'<text x="{x}" y="{y + i * (co + 5)}" text-anchor="{canh}" font-family="sans-serif" '
                           f'font-size="{co}" font-weight="{700 if (dam and i == 0) else 400}" fill="{CHU}">{escape(d)}</text>')

    def hop(self, ten, cx, y, rong, dong, loai, cao=None):
        cao = cao or 24 + 18 * len(dong)
        x = cx - rong // 2
        self.ra.append(f'<rect x="{x}" y="{y}" width="{rong}" height="{cao}" rx="9" fill="{MAU[loai]}" stroke="{VIEN}" stroke-width="1.5"/>')
        self.chu(cx, y + 22, dong, dam=True)
        self.nut[ten] = (cx, y, rong, cao)
        return y + cao

    def thoi(self, ten, cx, y, rong, dong, loai="kiem"):
        cao = 46 + 18 * len(dong)
        self.ra.append(f'<polygon points="{cx},{y} {cx + rong // 2},{y + cao // 2} {cx},{y + cao} {cx - rong // 2},{y + cao // 2}" '
                       f'fill="{MAU[loai]}" stroke="{VIEN}" stroke-width="1.5"/>')
        self.chu(cx, y + cao // 2 - 9 * (len(dong) - 1) + 4, dong, dam=True)
        self.nut[ten] = (cx, y, rong, cao)
        return y + cao

    # ---- mũi tên (điểm gấp khúc)
    def mui(self, diem, nhan=None, nhan_vi_tri=None, net=False):
        d = " ".join(f"{x},{y}" for x, y in diem)
        kieu = ' stroke-dasharray="6 4"' if net else ""
        self.ra.append(f'<polyline points="{d}" fill="none" stroke="{VIEN}" stroke-width="1.6"{kieu} marker-end="url(#mui)"/>')
        if nhan:
            x, y = nhan_vi_tri or diem[0]
            self.ra.append(f'<text x="{x + 6}" y="{y - 6}" font-family="sans-serif" font-size="12" font-weight="700" fill="{NET}">{escape(nhan)}</text>')

    def duoi(self, ten):
        cx, y, _, cao = self.nut[ten]
        return (cx, y + cao)

    def tren(self, ten):
        cx, y, _, _ = self.nut[ten]
        return (cx, y)

    def phai(self, ten):
        cx, y, r, cao = self.nut[ten]
        return (cx + r // 2, y + cao // 2)

    def trai(self, ten):
        cx, y, r, cao = self.nut[ten]
        return (cx - r // 2, y + cao // 2)


def dung() -> str:
    v = Ve()
    y = 70
    # ---- cột chính, phần trước vòng lặp
    y = v.hop("n1", CX, y, RONG, ["Đầu vào", "Sổ nhập CLB (Excel) hoặc CSV nội bộ", "CLB + chỉ tiêu; học sinh + nguyện vọng + điểm thi"], "nhap") + 34
    y0 = y
    y = v.thoi("n2", CX, y, 300, ["Mỗi dòng hợp lệ?", "(xem_truoc_so_nhap)"]) + 34
    v.hop("s2", CX_PHAI, y0 + 4, RONG_PHAI, ["Báo lỗi theo dòng", "Không nạp gì cả; sửa tệp rồi nạp lại"], "loi")
    y = v.hop("n3", CX, y, RONG, ["Sao lưu app.db (_backup_db)", "CSDL đang bận hoặc không sao lưu được: dừng ngay"], "chay") + 34
    y2 = y
    y = v.thoi("n4", CX, y, 340, ["Dữ liệu đủ và nhất quán?", "(validate_data_integrity)"]) + 34
    v.hop("s4", CX_PHAI, y2 + 4, RONG_PHAI, ["Dừng, nêu rõ học sinh nào", "Dữ liệu không đổi"], "loi")
    y = v.hop("n5", CX, y, RONG, ["Khoá bốc thăm STB (generate_stb_lottery)", "Một số cho mỗi học sinh, dùng chung mọi CLB",
                                   "Lần đầu bốc; sau đó khoá và dùng lại đúng số cũ",
                                   "Em đến muộn: chèn ngẫu nhiên, giữ thứ tự cũ", "(chen_stb_cho_hoc_sinh_moi)"], "chay") + 34
    y = v.hop("n6", CX, y, RONG, ["Thứ tự ưu tiên của từng CLB (compute_club_priority)",
                                   "Tầng 1 đã thi: điểm giảm dần, hoà thì theo số bốc thăm",
                                   "Tầng 2 không thi: chỉ theo số bốc thăm",
                                   "Không đọc thứ hạng nguyện vọng của học sinh"], "chay") + 40
    # mũi tên dọc cột chính
    for a, b in (("n1", "n2"), ("n2", "n3"), ("n3", "n4"), ("n4", "n5"), ("n5", "n6")):
        (ax, ay), (bx, by) = v.duoi(a), v.tren(b)
        v.mui([(ax, ay), (bx, by)], nhan="Có" if a in ("n2", "n4") else None, nhan_vi_tri=(ax, ay + 18))
    for t, s in (("n2", "s2"), ("n4", "s4")):
        v.mui([v.phai(t), (v.nut[s][0] - v.nut[s][2] // 2, v.phai(t)[1])], nhan="Không", nhan_vi_tri=v.phai(t))

    # ---- vòng lặp Deferred Acceptance
    vl_tren = y
    v.chu(W - 60, vl_tren + 22, ["Vòng lặp Deferred Acceptance (run_rbda): học sinh đề xuất, CLB giữ tạm"], co=14, dam=True, canh="end")
    y = vl_tren + 42
    y = v.hop("l1", CX, y, RONG, ["Mỗi học sinh chưa có chỗ", "đề xuất vào nguyện vọng kế tiếp của mình"], "chay") + 30
    y = v.hop("l2", CX, y, RONG, ["Mỗi CLB có người mới nộp: gộp", "người đang giữ tạm + người mới"], "chay") + 30
    y = v.hop("l3", CX, y, RONG, ["Hàm lựa chọn của CLB (club_choice_function)", "Lượt dự trữ mềm, rồi lượt chung",
                                   "Giữ tối đa bằng chỉ tiêu (capacity)"], "chay") + 30
    y_l4 = y
    y = v.thoi("l4", CX, y, 320, ["Em nằm trong số được giữ?"], "kiem") + 34
    y_l5 = y
    y = v.hop("l5", CX, y, RONG, ["CLB giữ tạm em này", "(chưa chốt: vòng sau có thể bị người khác đẩy ra)"], "chay") + 30
    y = v.thoi("l6", CX, y, 400, ["Còn em chưa có chỗ", "mà còn nguyện vọng chưa thử?"], "kiem") + 30
    vl_duoi = y
    v.hop("r1", CX_PHAI, y_l4 - 6, RONG_PHAI, ["NHÁNH KHÔNG ĐỦ CHỖ", "CLB đã đủ chỉ tiêu: em xếp sau bị từ chối",
                                                 "Em thử nguyện vọng kế tiếp ở vòng sau"], "thieu")
    v.hop("r3", CX_PHAI, y_l5 + 10, RONG_PHAI, ["Hết nguyện vọng vẫn bị từ chối", "Kết quả: Chưa có chỗ",
                                                  "Có trang riêng trong tệp Excel kết quả"], "loi")
    # khung vòng lặp
    v.ra.insert(0, f'<rect x="{LE_TRAI}" y="{vl_tren}" width="{W - LE_TRAI - 40}" height="{vl_duoi - vl_tren}" rx="14" fill="none" '
                   f'stroke="{VIEN}" stroke-width="1.5" stroke-dasharray="8 5"/>')
    for a, b in (("l1", "l2"), ("l2", "l3"), ("l3", "l4"), ("l5", "l6")):
        (ax, ay), (bx, by) = v.duoi(a), v.tren(b)
        v.mui([(ax, ay), (bx, by)])
    (ax, ay), (bx, by) = v.duoi("l4"), v.tren("l5")
    v.mui([(ax, ay), (bx, by)], nhan="Có", nhan_vi_tri=(ax, ay + 18))
    v.mui([v.phai("l4"), (v.nut["r1"][0] - RONG_PHAI // 2, v.phai("l4")[1])], nhan="Không", nhan_vi_tri=v.phai("l4"))
    v.mui([(CX_PHAI, v.nut["r1"][1] + v.nut["r1"][3]), (CX_PHAI, v.nut["r3"][1])], nhan="hết nguyện vọng", nhan_vi_tri=(CX_PHAI, v.nut["r3"][1] - 4), net=True)
    # từ nhánh bị từ chối quay về điều kiện lặp l6 (đường dọc bên phải rồi vào l6 từ phải)
    x_lui = CX_PHAI - RONG_PHAI // 2 - 26
    v.mui([(CX_PHAI - RONG_PHAI // 2, v.nut["r1"][1] + 30), (x_lui, v.nut["r1"][1] + 30), (x_lui, v.phai("l6")[1]), v.phai("l6")],
          nhan="vòng sau", nhan_vi_tri=(x_lui, v.phai("l6")[1] - 22), net=True)
    # quay lại đầu vòng (đường bên trái)
    x_trai = LE_TRAI + 34
    v.mui([v.trai("l6"), (x_trai, v.trai("l6")[1]), (x_trai, v.nut["l1"][1] + v.nut["l1"][3] // 2), v.trai("l1")],
          nhan="Có: vòng kế", nhan_vi_tri=(x_trai, v.trai("l6")[1] - 4))
    (ax, ay), (bx, by) = v.duoi("n6"), (CX, v.nut["l1"][1])
    v.mui([(ax, ay), (bx, by)])

    # ---- sau vòng lặp
    y = vl_duoi + 36
    y_n7 = y
    y = v.thoi("n7", CX, y, 380, ["Không có cặp học sinh–CLB phá vỡ?", "(verify_stability, dùng chính hàm lựa chọn)"]) + 34
    v.hop("s7", CX_PHAI, y_n7 + 6, RONG_PHAI, ["Dừng, không ghi kết quả", "Báo cặp phá vỡ"], "loi")
    y = v.hop("n8", CX, y, RONG, ["Ghi match_results và run_history", "trong MỘT giao dịch; lỗi thì quay về như trước",
                                   "run_history chỉ thêm dòng, không sửa, không xoá"], "chay") + 34
    y = v.hop("n9", CX, y, RONG, ["Xuất CSV và Excel; tra cứu từng học sinh", "Giải thích kết quả, phiếu in, khiếu nại"], "ra") + 34
    (ax, ay), (bx, by) = (CX, vl_duoi), v.tren("n7")
    v.mui([(ax, ay), (bx, by)], nhan="Không còn ai", nhan_vi_tri=(ax, ay + 20))
    (ax, ay), (bx, by) = v.duoi("n7"), v.tren("n8")
    v.mui([(ax, ay), (bx, by)], nhan="Có", nhan_vi_tri=(ax, ay + 18))
    v.mui([v.duoi("n8"), v.tren("n9")])
    v.mui([v.phai("n7"), (v.nut["s7"][0] - RONG_PHAI // 2, v.phai("n7")[1])], nhan="Không", nhan_vi_tri=v.phai("n7"))

    # ---- chú giải
    y += 16
    v.ra.append(f'<rect x="40" y="{y}" width="{W - 80}" height="150" rx="10" fill="#f8fafc" stroke="{VIEN}" stroke-width="1.2"/>')
    v.chu(60, y + 28, ["Khi không đủ chỗ: phần mềm làm gì",
                       "1. CLB đủ chỉ tiêu: các em được giữ theo thứ tự ưu tiên của CLB đó; em còn lại thử nguyện vọng kế tiếp.",
                       "2. Hết danh sách nguyện vọng mà vẫn bị từ chối: ghi 'Chưa có chỗ' và liệt kê riêng, không xếp ngẫu nhiên vào CLB khác.",
                       "3. Suất dự trữ mềm không khoá cứng: không đủ em thuộc diện thì suất thừa chuyển sang lượt chung, CLB vẫn tuyển đủ.",
                       "4. Chế độ FA-DAA (tuỳ chọn theo workspace): đóng CLB thiếu thành viên tối thiểu, danh sách chờ khi có suất nhả ra,",
                       "    vòng 2 cho em chưa có CLB chọn vào chỗ còn trống, CLB Tự do không giới hạn chỉ tiêu.",
                       "Toàn bộ là thuật toán xác định: cùng dữ liệu và cùng hạt giống thì cùng kết quả. Không có mô hình học máy ở bước nào."],
          co=13, dam=True, canh="start")
    y += 150 + 20
    h = y
    kieu = {"nhap": "Đầu vào", "kiem": "Kiểm tra / quyết định", "chay": "Xử lý", "thieu": "Nhánh không đủ chỗ", "loi": "Dừng hoặc báo lỗi", "ra": "Đầu ra"}
    x = 40
    for k, ten in kieu.items():
        v.ra.append(f'<rect x="{x}" y="{h - 8}" width="18" height="18" rx="4" fill="{MAU[k]}" stroke="{VIEN}"/>')
        v.chu(x + 26, h + 6, [ten], co=12, canh="start")
        x += 26 + 9 * len(ten) + 24
    h += 36

    dau = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" '
           f'aria-label="Sơ đồ luồng xử lý một lần chạy xếp câu lạc bộ, gồm các điểm quyết định và nhánh không đủ chỗ (dữ liệu mô phỏng)">',
           '<defs><marker id="mui" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto">'
           f'<path d="M0,0 L10,5 L0,10 z" fill="{VIEN}"/></marker></defs>',
           f'<rect x="0" y="0" width="{W}" height="{h}" fill="#ffffff"/>',
           f'<text x="40" y="40" font-family="sans-serif" font-size="20" font-weight="700" fill="{CHU}">'
           'Luồng xử lý của một lần chạy xếp (dữ liệu mô phỏng)</text>']
    return "\n".join(dau + v.ra + ["</svg>"]) + "\n"


def main() -> None:
    duong = os.path.join(THU_MUC, "so_do_xu_ly.svg")
    with open(duong, "w", encoding="utf-8", newline="\n") as f:
        f.write(dung())
    print("Đã ghi", duong)


if __name__ == "__main__":
    main()
