# PA05 — Tạo 5 màn hình và khung co giãn

⏱ 20 phút · [← PA04](PA04_cong_thuc_app.md) · Tiếp: [PA06](PA06_man_khong_co_ten.md)

## Phần 1 — Tạo và đặt tên màn hình
1. Cây: chuột phải **Screen1** → **Rename** → gõ `scrKhongCoTen` → Enter.
2. Thanh trên: **+ New screen** → **Blank**.
3. Chuột phải màn mới → **Rename** → `scrDangKy`.
4. Lặp 2–3 với tên `scrXacNhan`.
5. Lặp 2–3 với tên `scrQuanTri`.
6. Có thi tuyển: lặp 2–3 với tên `scrChonThi`.
   👀 Cây có 4 (hoặc 5) màn hình đúng tên.

## Phần 2 — Khung co giãn cho `scrDangKy`
7. Cây: bấm `scrDangKy`.
8. Thanh trên: **+ Insert** → gõ `vertical` → bấm **Vertical container**.
9. Chuột phải container mới → **Rename** → `conKhung_DangKy`.
10. Đặt từng thuộc tính (chọn tên ở ô thả xuống, dán vào fx):

| Thuộc tính | Dán |
|---|---|
| `X` | `(Parent.Width - Self.Width) / 2` |
| `Y` | `0` |
| `Width` | `Min(Parent.Width - 32, 760)` |
| `Height` | `Parent.Height` |
| `LayoutGap` | `12` |
| `PaddingTop` | `16` |
| `PaddingBottom` | `16` |
| `LayoutOverflowY` | `LayoutOverflow.Scroll` |

   (Một số thuộc tính dễ đặt hơn ở khung **Properties** bên phải: *Gap*, *Padding*, *Vertical overflow = Scroll*.)

## Phần 3 — Làm khung cho các màn còn lại
11. Cây: chuột phải `conKhung_DangKy` → **Copy**.
12. Bấm màn `scrXacNhan` → **Ctrl+V**.
13. Đổi tên container vừa dán → `conKhung_XacNhan`.
14. Lặp 12–13 cho `scrKhongCoTen` (`conKhung_KhongCoTen`), `scrChonThi` (`conKhung_ChonThi`), `scrQuanTri` (`conKhung_QuanTri`).
15. Riêng `conKhung_QuanTri`: sửa `Width` thành `Min(Parent.Width - 32, 1200)`.
16. **Ctrl+S**.

## Quy tắc cho mọi control đặt trong khung (dùng ở PA06–PA12)
- **Chèn vào trong khung:** chọn container ở cây **trước**, rồi **+ Insert**. Kiểm ở cây: control nằm **thụt vào dưới** container.
- `Width`: `Parent.Width`.
- Chữ thường: `Size` = `If(LaPhone, 16, 14)`. Tiêu đề: `If(LaPhone, 22, 26)`.
- Nút: `Height` = `48`.
- Label nhiều dòng: bật **Auto height** (thuộc tính `AutoHeight` = `true`).

- [ ] Đủ màn hình, mỗi màn có khung.
