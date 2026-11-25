# Từ cổng đăng ký (bản mẫu) sang phần mềm xếp CLB

> Bản mẫu `docs/phien/DK1_BAN_MAU_V8.html` dùng **dữ liệu giả**, chỉ lưu trong trình duyệt đang mở.
> Công cụ này chỉ để thử trọn quy trình nhập liệu, chưa dùng cho đăng ký thật.

## Các bước
1. Mở `DK1_BAN_MAU_V8.html` bằng Edge hoặc Chrome. Đi hết 6 giai đoạn tới **Xuất**.
2. Ở Xuất, bấm **Chép dữ liệu xuất**. Dán vào một tệp mới tên `vao.json` (Notepad, lưu kiểu UTF-8).
3. Trong thư mục mã nguồn, chạy:
   ```
   python dk2_so_nhap.py vao.json SO_NHAP_CLB.xlsx
   ```
   Thành công: "Đã ghi SO_NHAP_CLB.xlsx: … CLB, … học sinh." Có lỗi: danh sách lỗi bằng tiếng Việt,
   không tệp nào được ghi.
4. Mở phần mềm xếp CLB, bật chế độ huy chương (FA-DAA), rồi nhập `SO_NHAP_CLB.xlsx` như mọi sổ nhập.

## Dữ liệu đi đâu
| Bản mẫu | Sổ nhập |
|---|---|
| Tên, buổi, loại, chỉ tiêu, điểm sàn, mã CLB | cột cùng tên ở sheet "1. CLB" |
| Phòng / sức chứa phòng | "Địa điểm" / "Sức chứa phòng" |
| Lớp | cột "Lớp" (khối suy từ tên lớp) |
| Nguyện vọng từng buổi | một dãy Nguyện vọng 1…k, buổi đầu trước, trong buổi giữ thứ tự em xếp |
| Bài thi, điểm, huy chương | "Điểm thi", "Huy chương (60/30/10)" trong từng nguyện vọng |

Không vào sổ: link bài thi, giáo viên, mô tả CLB (việc xếp không cần).

## Luật cần biết
- Điểm sàn là số nguyên 0–10 (như phần mềm). CLB Tự do: phần mềm luôn có chỗ, chỉ tiêu trong sổ
  là sức chứa phòng cho đủ cột.
- Mỗi buổi tối đa 10 nguyện vọng và 5 bài thi; mỗi buổi một Vàng, một Bạc, một Đồng; Tự do không
  nhận huy chương.
