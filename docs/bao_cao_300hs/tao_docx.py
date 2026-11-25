# -*- coding: utf-8 -*-
"""Dựng BAO_CAO_THU_NGHIEM_300HS.docx từ so_lieu.json và anh/*.png (do chay_bao_cao.py tạo).

    python docs/bao_cao_300hs/tao_docx.py

Báo cáo vận hành: chỉ mô tả cách chạy, số đo và thông báo của phần mềm. Phần nhận xét, diễn giải
và kết luận để trống cho học sinh tự viết (quy định liêm chính học thuật của dự án).
"""
import json
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

D = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, GOC)
from i18n_errors import format_message  # noqa: E402

with open(os.path.join(D, "so_lieu.json"), encoding="utf-8") as _f:
    SL = json.load(_f)
ANH = os.path.join(D, "anh")
RA = os.path.join(D, "BAO_CAO_THU_NGHIEM_300HS.docx")
BUOI = {"thu_3": "Thứ 3", "thu_6": "Thứ 6"}
MAU = RGBColor(0x1F, 0x4E, 0x3D)

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.font.size = Pt(12)
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(2.2)
    s.top_margin = s.bottom_margin = Cm(2)
for ten in ("Heading 1", "Heading 2", "Heading 3", "Title"):
    h = doc.styles[ten]
    h.font.name = "Times New Roman"
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    h.font.color.rgb = MAU
doc.styles["Heading 1"].paragraph_format.page_break_before = True   # mỗi mục lớn sang trang mới

SO_HINH = [0]
SO_BANG = [0]


def doan(text, dam=False, nghieng=False, co=None, canh=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold, r.italic = dam, nghieng
    if co:
        r.font.size = Pt(co)
    if canh:
        p.alignment = canh
    return p


def gach(text):
    return doc.add_paragraph(text, style="List Bullet")


def hinh(ten, chu_thich, rong=16.0):
    duong = os.path.join(ANH, ten)
    if not os.path.exists(duong):
        doan("[Thiếu ảnh %s]" % ten, nghieng=True)
        return
    doc.add_picture(duong, width=Cm(rong))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    SO_HINH[0] += 1
    p = doan("Hình %d. %s" % (SO_HINH[0], chu_thich), nghieng=True, co=10, canh=WD_ALIGN_PARAGRAPH.CENTER)
    p.paragraph_format.space_after = Pt(10)


def nen_o(o, mau="DDEBE4"):
    tc = o._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), mau)
    tc.append(sh)


def bang(tieu_de, dau, dong, co=10, rong=None):
    SO_BANG[0] += 1
    doan("Bảng %d. %s" % (SO_BANG[0], tieu_de), dam=True, co=11)
    t = doc.add_table(rows=1, cols=len(dau))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, x in enumerate(dau):
        o = t.rows[0].cells[i]
        o.text = ""
        r = o.paragraphs[0].add_run(str(x))
        r.bold = True
        r.font.size = Pt(co)
        nen_o(o)
    for d in dong:
        cs = t.add_row().cells
        for i, x in enumerate(d):
            cs[i].text = ""
            r = cs[i].paragraphs[0].add_run("" if x is None else str(x))
            r.font.size = Pt(co)
    if rong:
        t.autofit = False
        for i, w in enumerate(rong):           # LibreOffice đọc tblGrid, Word đọc độ rộng ô: đặt cả hai
            t.columns[i].width = Cm(w)
        for hang in t.rows:
            for i, w in enumerate(rong):
                hang.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def loi_vi(e):
    try:
        return format_message(e["code"], e.get("params") or {})
    except Exception:
        return e["code"]


# ------------------------------------------------------------------ Trang bìa
doc.add_paragraph()
doan("BÁO CÁO THỬ NGHIỆM", dam=True, co=22, canh=WD_ALIGN_PARAGRAPH.CENTER)
doan("Phần mềm phân bổ câu lạc bộ RB-DA trên bộ dữ liệu mô phỏng 300 học sinh", dam=True, co=15,
     canh=WD_ALIGN_PARAGRAPH.CENTER)
doan("Ca thành công / không đạt nguyện vọng có giải thích · Bảng số bốc thăm (seed) · "
     "Kết quả khi đổi cấu hình · Xử lý dữ liệu thiếu và tiêu chí xung đột", nghieng=True,
     canh=WD_ALIGN_PARAGRAPH.CENTER)
doc.add_paragraph()
p = doan("LƯU Ý: Mọi số liệu trong báo cáo là DỮ LIỆU MÔ PHỎNG do máy sinh (tên học sinh bịa ghép từ "
         "bảng họ/đệm/tên, seed cố định 20261122). Đây không phải khảo sát hay học sinh thật.", dam=True,
         canh=WD_ALIGN_PARAGRAPH.CENTER)
p.runs[0].font.color.rgb = RGBColor(0xA0, 0x30, 0x20)
doc.add_paragraph()
doan("Thuật toán: Deferred Acceptance (Gale–Shapley), học sinh đề nghị; dự trữ mềm hai lượt; "
     "bốc thăm một lần (STB) đã khoá; ưu tiên hai tầng.", canh=WD_ALIGN_PARAGRAPH.CENTER, co=11)
doan("Mọi ảnh chụp từ giao diện thật của phần mềm (trình duyệt Chromium, chế độ dự phòng browser_host).",
     canh=WD_ALIGN_PARAGRAPH.CENTER, co=11)

# ------------------------------------------------------------------ 1. Dữ liệu và cách chạy
doc.add_heading("1. Dữ liệu thử nghiệm và cách tái lập", level=1)
doan("Bộ dữ liệu gồm 300 học sinh, 2 buổi sinh hoạt (Thứ 3, Thứ 6), mỗi buổi 7 câu lạc bộ thuộc ba loại: "
     "1 CLB Tự do (nhận mọi em), 3 CLB Giới hạn (có chỉ tiêu, không thi), 3 CLB Tuyển chọn (có bài thi "
     "và điểm sàn). Sổ nhập được thiết kế để hợp lệ cùng lúc cho cả ba cách khai nguyện vọng (Chỉ xếp "
     "thứ tự, Chia 100 điểm, Huy chương 60/30/10) và cho công tắc “Chia CLB theo loại”, nên có thể đổi "
     "chế độ qua lại mà không phải nạp lại.")
dong = [(c["name"], BUOI.get(c["buoi"], c["buoi"]), c.get("loai") or "", c["capacity"], c.get("diem_san") or "–")
        for c in SL["clb"]]
bang("Danh sách 14 câu lạc bộ (sheet “1. CLB”)", ["Tên CLB", "Buổi", "Loại", "Chỉ tiêu", "Điểm sàn"], dong)
doan("Mỗi em, mỗi buổi, chọn ngẫu nhiên một trong ba kiểu khai: K1 không thi (xếp 3 CLB Giới hạn), "
     "K2 thi một CLB (3 CLB Giới hạn + 1 CLB Tuyển chọn), K3 thi ba CLB Tuyển chọn; 85 % em thêm CLB Tự do "
     "ở cuối danh sách. Huy chương Vàng/Bạc/Đồng (60/30/10) đặt trọn trong một quỹ 100 điểm.")
doan("Các tệp đi kèm (thư mục docs/bao_cao_300hs/):", dam=True)
for x in ("SO_NHAP_300HS_DOI_CHE_DO.xlsx — sổ nhập hợp lệ 300 em (sinh bằng sinh_300hs.py).",
          "SO_NHAP_300HS_LOI_CLB.xlsx, SO_NHAP_300HS_LOI_HS.xlsx, SO_NHAP_300HS_THIEU_XUNG_DOT.xlsx — ba sổ "
          "cố ý sai (sinh bằng sinh_so_co_loi.py).",
          "chay_bao_cao.py — điều khiển giao diện thật bằng Chromium, chụp ảnh, ghi so_lieu.json.",
          "tao_docx.py — dựng báo cáo này từ so_lieu.json và thư mục anh/."):
    gach(x)
doan("Chạy lại toàn bộ (cùng seed cho ra cùng số liệu):", dam=True)
for x in ("python docs/bao_cao_300hs/sinh_300hs.py", "python docs/bao_cao_300hs/sinh_so_co_loi.py",
          "python docs/bao_cao_300hs/chay_bao_cao.py", "python docs/bao_cao_300hs/tao_docx.py"):
    p = doc.add_paragraph(x)
    p.runs[0].font.name = "Consolas"
    p.runs[0].font.size = Pt(10)
hinh("01_trang_dau.png", "Màn hình “Xếp CLB” trước khi nạp sổ.")
hinh("02_nap_xong.png", "Nạp sổ 300 học sinh xong: 14 CLB, 300 học sinh, 0 dòng bỏ qua; bước “Xem cảnh báo” "
     "báo không có vấn đề.")
doan("Kiểm tra sức khoẻ dữ liệu sau khi nạp: %d cảnh báo." % len(SL["suc_khoe"]))

# ------------------------------------------------------------------ 2. Ca thành công / không đạt
doc.add_heading("2. Một số ca phân bổ thành công / không đạt nguyện vọng, có giải thích", level=1)
doan("Các ca dưới đây chạy ở chế độ Huy chương, seed %d. Lời giải thích lấy nguyên văn từ mục “Tra cứu "
     "một học sinh” ở thẻ Kết quả: gõ mã học sinh, phần mềm liệt kê từng nguyện vọng, CLB đó còn chỗ hay "
     "đã đầy, mức vào được (điểm chuẩn / huy chương / bốc thăm) và câu “Vì sao”. Cùng nội dung ấy có thể "
     "in phiếu hoặc lưu PDF để phát cho học sinh." % SL["seed"])
TEN_CA = {"thanh_cong": ("2.1. Ca thành công — %s", "05_ca_thanh_cong_%s.png"),
          "khong_dat_huy_chuong_boc_tham": ("2.2. Ca không đạt nguyện vọng đầu vì huy chương và bốc thăm — %s",
                                            "05_ca_khong_dat_huy_chuong_boc_tham_%s.png"),
          "khong_dat_diem": ("2.3. Ca không đạt vì chưa đủ điểm sàn — %s", "05_ca_khong_dat_diem_%s.png")}
for nhan, ca in SL["ca"].items():
    sid = ca["student_id"]
    tieu, anh = TEN_CA[nhan]
    doc.add_heading(tieu % sid, level=2)
    for b in ca["buoi"]:
        dong = [(x["hang"], x["clb"], x["huy_chuong"] or "–", x["diem"] if x["diem"] is not None else "–",
                 x["ma"], x["cau"]) for x in b["lua_chon"]]
        bang("%s — %s: kết quả %s" % (sid, BUOI[b["buoi"]], b["ket_qua"]),
             ["NV", "CLB", "Huy chương", "Điểm thi", "Mã lý do", "Câu giải thích của phần mềm"], dong, co=9,
             rong=[1.0, 2.8, 1.8, 1.4, 3.4, 6.2])
    hinh(anh % sid, "Thẻ Kết quả → Tra cứu một học sinh: %s." % sid)
doc.add_heading("2.4. Báo cáo tải về", level=2)
doan("Từ thẻ Kết quả có thể tải: phiếu giải trình từng em (HTML in được / PDF), phiếu cả lớp, báo cáo tổng "
     "hợp (PDF), và ở thẻ “Chi tiết và xuất tệp”: Excel kết quả, lý do kết quả (CSV), biên bản bốc thăm.")
hinh("07_menu_bao_cao.png", "Menu “Báo cáo và phiếu in” trên thẻ Kết quả.")
hinh("06_phieu_giai_trinh_tai_ve.png", "Phiếu giải trình tải về (HTML in được) — trang của DC002.", rong=13)
hinh("06b_phieu_pdf-1.png", "Phiếu giải trình dạng PDF (nút “Lưu PDF”) — DC034.", rong=13)
hinh("07b_chi_tiet_xuat.png", "Thẻ “Chi tiết và xuất tệp”: tóm tắt lần chạy và các nút tải.")

# ------------------------------------------------------------------ 3. Bảng trọng số / seed
doc.add_heading("3. Bảng thứ tự xét (trọng số) và số bốc thăm theo seed", level=1)
doan("Khi nhiều em cùng muốn một chỗ, phần mềm xét theo thứ tự tiêu chí cố định (bảng “Thứ tự đang dùng” ở "
     "Quản lý → Cách xếp → Tuỳ chỉnh thêm). Tiêu chí cuối cùng luôn là số bốc thăm (STB). Số bốc thăm được "
     "sinh tất định từ seed (“Mã bốc thăm”) bằng crc32, khoá sau lần chạy đầu; muốn đổi seed phải bấm "
     "“Bốc thăm lại…” và mọi lần chạy đều được ghi vào lịch sử.")
hinh("10_thu_tu_tieu_chi_huy_chuong.png", "Thứ tự tiêu chí ở chế độ Huy chương: điểm thi → nhóm ưu tiên → "
     "số bốc thăm. Theo chú thích trên phiếu giải trình, huy chương cao hơn được xét trước khi các em bằng "
     "nhau ở các bước trước, rồi mới tới bốc thăm.")
hinh("10_thu_tu_tieu_chi_chi_xep.png", "Thứ tự tiêu chí ở chế độ Chỉ xếp thứ tự.")
hinh("09b_o_ma_boc_tham.png", "Ô “Mã bốc thăm” (seed) và nút “Bốc thăm lại…”.", rong=12)
stb42 = {h["student_id"]: h for h in SL["stb_mau"]["42"]["hoc_sinh"]}
stb7 = {h["student_id"]: h for h in SL["stb_mau"]["7"]["hoc_sinh"]}
dong = [(sid, stb42[sid]["name"], stb42[sid]["so"]["thu_3"], stb42[sid]["so"]["thu_6"],
         stb7.get(sid, {}).get("so", {}).get("thu_3", ""), stb7.get(sid, {}).get("so", {}).get("thu_6", ""))
        for sid in sorted(stb42)[:10]]
bang("Số bốc thăm của 10 em đầu với seed 42 và seed 7 (số nhỏ được xét trước)",
     ["Mã HS", "Họ tên", "Seed 42 · Thứ 3", "Seed 42 · Thứ 6", "Seed 7 · Thứ 3", "Seed 7 · Thứ 6"], dong)
dong = [(s["seed"], s["nv"]["1"], s["ty_le_nv1"], s["ty_le_top3"], s["ngoai_nv"], s["khac_seed42"])
        for s in SL["seed_bang"]]
bang("Kết quả chế độ Chỉ xếp thứ tự với bốn seed (600 chỗ = 300 em × 2 buổi)",
     ["Seed", "Số chỗ NV1", "% NV1", "% trong 3 NV đầu", "Xếp ngoài danh sách NV", "Số chỗ khác so với seed 42"],
     dong)
hinh("08_so_boc_tham_seed_42.png", "Bảng “Số bốc thăm theo buổi” với seed 42 (lọc 9 em đầu).", rong=14)
hinh("08_so_boc_tham_seed_7.png", "Cùng bảng sau khi bốc thăm lại với seed 7.", rong=14)
hinh("09_lich_su_chay.png", "Lịch sử sắp xếp: mỗi lần chạy thêm một dòng (seed, số vòng, có bốc lại hay không); "
     "không dòng nào bị ghi đè.", rong=14)

# ------------------------------------------------------------------ 4. Đổi cấu hình
doc.add_heading("4. Kết quả thay đổi khi chỉnh cấu hình", level=1)
doan("Cùng một sổ nhập, cùng seed %d, chỉ đổi chế độ ở Quản lý → Cách xếp (và công tắc “Chia CLB theo loại” ở "
     "Danh sách CLB) rồi bấm “Chạy sắp xếp” lại. Số liệu đọc từ bảng kết quả sau mỗi lần chạy." % SL["seed"])
dong = [(c["ten"], "bật" if c["rules"]["wharton"] else "tắt", "bật" if c["rules"]["fa_daa"] else "tắt",
         "bật" if c["rules"]["chia_loai"] else "tắt", c["nv"]["1"], c["nv"]["2"], c["nv"]["3"],
         c["nv"]["4"] + c["nv"]["5"] + c["nv_6_tro_len"], c["ngoai_nv"], c["ty_le_nv1"], c["ty_le_top3"])
        for c in SL["che_do"]]
bang("Phân bố mức đáp ứng nguyện vọng theo chế độ (600 chỗ)",
     ["Chế độ", "Chia 100", "Huy chương", "Chia loại", "NV1", "NV2", "NV3", "NV4+", "Ngoài DS", "% NV1", "% top 3"],
     dong, co=9, rong=[3.4, 1.3, 1.6, 1.3, 1.1, 1.1, 1.1, 1.1, 1.3, 1.2, 1.3])
ten = {c["khoa"]: c["ten"] for c in SL["che_do"]}
dong = [(ten[k.split("|")[0]], ten[k.split("|")[1]], v) for k, v in SL["khac_nhau"].items()]
bang("Số chỗ (học sinh × buổi) đổi CLB giữa hai chế độ", ["Chế độ A", "Chế độ B", "Số chỗ khác nhau / 600"], dong)
dong = [(v["student_id"], v["ten"], BUOI[v["buoi"]], v["chi_xep"], v["chia100"], v["huy_chuong"])
        for v in SL["vi_du_doi_clb"]]
bang("Ví dụ học sinh đổi CLB khi đổi chế độ", ["Mã HS", "Họ tên", "Buổi", "Chỉ xếp thứ tự", "Chia 100 điểm",
                                               "Huy chương"], dong, co=9, rong=[1.6, 3.0, 1.4, 3.5, 3.5, 3.6])
doan("Ghi chú đọc bảng: biểu đồ trên giao diện tính phần trăm trên số chỗ nằm trong danh sách nguyện vọng, "
     "còn Bảng trên tính trên đủ 600 chỗ, nên hai con số lệch nhau một chút.", nghieng=True, co=10)
for c in SL["che_do"]:
    k = c["khoa"]
    doc.add_heading("Chế độ: %s" % c["ten"], level=3)
    hinh("03_%s_cach_xep.png" % k, "Chọn chế độ “%s” ở Quản lý → Cách xếp." % c["ten"], rong=13)
    if k == "chia100_loai":
        hinh("03_%s_cong_tac_loai.png" % k, "Bật công tắc “Chia CLB theo loại”: mỗi CLB có loại và điểm sàn.",
             rong=13)
    hinh("04_%s_muc_dap_ung.png" % k, "Mức đáp ứng nguyện vọng sau khi chạy ở chế độ “%s”." % c["ten"], rong=14)

# ------------------------------------------------------------------ 5. Dữ liệu thiếu / sai / xung đột
doc.add_heading("5. Xử lý dữ liệu thiếu và tiêu chí xung đột", level=1)
doan("Bốn tình huống được dựng từ chính sổ 300 em bằng cách sửa vài ô. Thông báo lỗi trong bảng là "
     "câu tiếng Việt phần mềm hiển thị (một nguồn duy nhất: i18n_errors.py).")
doc.add_heading("5.1. Sheet CLB sai — chặn nhập", level=2)
gach("CLB Bóng rổ bỏ trống Chỉ tiêu (thiếu dữ liệu bắt buộc).")
gach("CLB Cờ vua: Suất ưu tiên 80 > Chỉ tiêu 50 (hai cột mâu thuẫn).")
bang("Thông báo khi nhập SO_NHAP_300HS_LOI_CLB.xlsx", ["Mã lỗi", "Thông báo"],
     [(e["code"], loi_vi(e)) for e in SL["loi"]["loi_clb"]["import_errors"]], co=9, rong=[4.2, 12.4])
hinh("11_loi_clb_nhap.png", "Sổ có lỗi CLB: phần mềm liệt kê từng dòng sai và không nạp gì.")
doc.add_heading("5.2. Sheet học sinh sai — chặn nhập", level=2)
for x in ("DC003 đổi mã thành DC001 (trùng mã).", "DC004 bỏ trống mã học sinh (thiếu dữ liệu).",
          "DC005 ghi nguyện vọng “CLB Bơi lội” không có trong danh sách.", "DC006 ghi điểm thi bằng chữ “chín”."):
    gach(x)
bang("Thông báo khi nhập SO_NHAP_300HS_LOI_HS.xlsx", ["Mã lỗi", "Thông báo"],
     [(e["code"], loi_vi(e)) for e in SL["loi"]["loi_hs"]["import_errors"]], co=9, rong=[4.2, 12.4])
hinh("11_loi_hs_nhap.png", "Sổ có lỗi học sinh: bốn lỗi, mỗi lỗi chỉ đúng dòng và ô; chưa nạp gì.")
doc.add_heading("5.3. Thiếu nguyện vọng và huy chương xung đột — nạp được, chặn khi chạy", level=2)
gach("DC007 không khai nguyện vọng nào (thiếu dữ liệu): cảnh báo mức “Cần lưu ý”, không chặn.")
gach("DC009 đặt huy chương Vàng (60) cho hai CLB cùng buổi Thứ 3 (tiêu chí xung đột): cảnh báo “Nghiêm trọng”, "
     "chặn chạy cho đến khi sửa.")
x = SL["loi"]["thieu_xung_dot"]
bang("Cảnh báo sức khoẻ dữ liệu và lỗi khi chạy", ["Nơi báo", "Mức", "Mã", "Thông báo"],
     [("Xem cảnh báo", w.get("severity"), w["code"], loi_vi(w)) for w in x["health"]]
     + [("Chạy sắp xếp", "chặn", e["code"], loi_vi(e)) for e in x["run_errors"]], co=9, rong=[2.6, 1.6, 4.4, 8.0])
doan("Lần chạy bị chặn có ghi kết quả không? %s." % ("Có" if x["chay_duoc"] else
     "Không — không có dòng mới trong lịch sử chạy, dữ liệu giữ nguyên"))
hinh("12_thieu_xung_dot_canh_bao.png", "Bước “Xem cảnh báo”: 1 nghiêm trọng (huy chương trùng), 1 cần lưu ý "
     "(học sinh không có nguyện vọng).", rong=14)
hinh("12b_thieu_xung_dot_chay_bi_chan.png", "Bấm “Chạy sắp xếp”: bước Kiểm tra dữ liệu báo lỗi, các bước sau "
     "không chạy; mục “Các lỗi cần xử lý” chỉ ra DC009.", rong=14)
doc.add_heading("5.4. Xung đột giữa chế độ và dữ liệu đã nạp", level=2)
doan("Nạp sổ khi đang ở chế độ mặc định (Chia 100 điểm, không chia loại): phần mềm báo đã bỏ qua các cột "
     "Loại / Điểm sàn. Sau đó bật chế độ Huy chương: phần mềm cảnh báo ngay rằng dữ liệu còn thiếu thứ chế "
     "độ này cần, và lần chạy bị chặn với các lỗi dưới đây (cách sửa: chọn Loại cho từng CLB ở bảng hiện ra, "
     "hoặc nạp lại sổ khi đã bật chế độ).")
errs = SL["loi"]["xung_dot_che_do"]["run_errors"]
gop = {}
for e in errs:
    gop.setdefault(e["code"], []).append(e)
bang("Lỗi khi chạy ở chế độ Huy chương với dữ liệu nạp ở chế độ khác",
     ["Mã lỗi", "Số lần", "Ví dụ thông báo"], [(k, len(v), loi_vi(v[0])) for k, v in gop.items()], co=9, rong=[4.0, 1.4, 11.2])
hinh("13_xung_dot_che_do_nap.png", "Nạp ở chế độ mặc định: dòng vàng báo 14 CLB có cột bị bỏ qua.")
hinh("13b_xung_dot_che_do_bat_huy_chuong.png", "Bật Huy chương sau khi nạp: cảnh báo thiếu Loại / CLB Tự do và "
     "bảng chọn loại cho từng CLB.", rong=13)

# ------------------------------------------------------------------ 6. Phần học sinh tự viết
doc.add_heading("6. Nhận xét và kết luận (học sinh tự viết)", level=1)
doan("Theo quy định liêm chính học thuật của dự án, phần nhận xét, diễn giải số liệu và kết luận do học sinh tự "
     "viết. Các câu hỏi gợi ý:", nghieng=True)
for x in ("Vì sao tỷ lệ nguyện vọng 1 ở chế độ Chỉ xếp thứ tự khác các chế độ dùng điểm/huy chương?",
          "Đổi seed làm thay đổi bao nhiêu chỗ? Điều đó nói gì về vai trò của bốc thăm khi các em bằng nhau?",
          "Thông báo lỗi ở mục 5 có đủ rõ để người nhập tự sửa không?"):
    gach(x)
for _ in range(6):
    doc.add_paragraph("…" * 60)

doc.save(RA)
print(RA, "· hình:", SO_HINH[0], "· bảng:", SO_BANG[0])
