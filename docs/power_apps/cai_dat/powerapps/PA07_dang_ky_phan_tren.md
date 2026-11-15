# PA07 — Màn đăng ký: lời chào, hạn chót, hướng dẫn

⏱ 10 phút · [← PA06](PA06_man_khong_co_ten.md) · Tiếp: [PA08](PA08_dang_ky_o_chon.md)

Mỗi label: chọn `conKhung_DangKy` ở cây → **+ Insert → Text label** → đổi tên → đặt thuộc tính. Mọi label: `Width` = `Parent.Width`, `AutoHeight` = `true`.

## Label 1 — `lblChao`
| Thuộc tính | Dán |
|---|---|
| `Text` | `"Chào " & varHS.name & " (" & varHS.student_id & " – " & varHS.class_id & ")"` |
| `Size` | `If(LaPhone, 22, 26)` |
| `FontWeight` | `FontWeight.Semibold` |

## Label 2 — `lblHan`
| Thuộc tính | Dán |
|---|---|
| `Text` | xem khối dưới |
| `Color` | `If(HetHan, Color.Red, Color.DarkGreen)` |
| `Size` | `If(LaPhone, 16, 14)` |

```
If(HetHan, "Đã hết hạn nộp nguyện vọng.",
  "Hạn chót: " & Text(HanChot, "dd/mm/yyyy hh:mm") &
  If(IsBlank(varNV), "  •  Em chưa nộp.", "  •  Đã nộp lúc " & Text(varNV.nop_luc, "dd/mm hh:mm")))
```

## Label 3 — `lblHuongDan`
| Thuộc tính | Dán |
|---|---|
| `Text` | xem khối dưới |
| `Size` | `If(LaPhone, 16, 14)` |

```
"Chọn tối đa " & SoNguyenVongToiDa & " CLB, CLB em thích nhất ở ô 1. Không chọn trùng. Hãy xếp đúng thứ tự em thật sự muốn: cách xếp của trường (Gale–Shapley) bảo đảm khai thật luôn có lợi nhất cho em."
```

**Ctrl+S.**

## Kiểm tra xong
- 👀 Ở chế độ soạn, `lblChao` có thể chỉ hiện "Chào  ( – )" vì bạn không có trong `HocSinh`. Bình thường.
- Thứ tự ở cây (trên xuống): `lblChao`, `lblHan`, `lblHuongDan`. Sai thứ tự → chuột phải → **Reorder → Move up/down**.

- [ ] Xong 3 label.
