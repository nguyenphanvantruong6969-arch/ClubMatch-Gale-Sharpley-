# PA06 — Màn hình "không có tên"

⏱ 5 phút · [← PA05](PA05_tao_man_hinh_va_khung.md) · Tiếp: [PA07](PA07_dang_ky_phan_tren.md)

Hiện khi email đăng nhập không có trong List `HocSinh`.

1. Cây: bấm `conKhung_KhongCoTen`.
2. **+ Insert → Text label**.
3. Đổi tên → `lblKhongCoTen`.
4. Đặt thuộc tính:

| Thuộc tính | Dán |
|---|---|
| `Text` | `"Email " & User().Email & " chưa có trong danh sách học sinh. Em liên hệ giáo viên chủ nhiệm."` |
| `Width` | `Parent.Width` |
| `AutoHeight` | `true` |
| `Size` | `If(LaPhone, 18, 16)` |
| `Color` | `Color.DarkRed` |

5. **Ctrl+S**.

- [ ] Xong.
