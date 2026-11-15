# PA08 — Màn đăng ký: 10 ô chọn CLB

⏱ 30 phút · [← PA07](PA07_dang_ky_phan_tren.md) · Tiếp: [PA09](PA09_dang_ky_nut_nop.md)

Làm **ô 1 thật kỹ**, chạy đúng, rồi mới nhân bản ra 9 ô còn lại.

## Phần 1 — Lưới chứa các ô
1. Cây: bấm `conKhung_DangKy`.
2. **+ Insert → Horizontal container**.
3. Đổi tên → `conLuoi`.
4. Thuộc tính:

| Thuộc tính | Dán |
|---|---|
| `Width` | `Parent.Width` |
| `LayoutWrap` (khung Properties: *Wrap*) | `true` |
| `LayoutGap` | `12` |
| `Height` | `If(LaPhone, 90 * SoNguyenVongToiDa, 90 * RoundUp(SoNguyenVongToiDa / 2, 0))` |

## Phần 2 — Ô 1
5. Cây: bấm `conLuoi` → **+ Insert → Vertical container** → đổi tên `conNV1`.

| Thuộc tính | Dán |
|---|---|
| `Width` | `If(LaPhone, Parent.Width, (Parent.Width - 12) / 2)` |
| `Height` | `80` |
| `Visible` | `1 <= SoNguyenVongToiDa` |

6. Cây: bấm `conNV1` → **+ Insert → Text label** → đổi tên `lblNV1`.

| Thuộc tính | Dán |
|---|---|
| `Text` | `"Nguyện vọng 1"` |
| `Width` | `Parent.Width` |
| `Height` | `30` |

7. Cây: bấm `conNV1` → **+ Insert** → gõ `drop` → **Drop down** (bản cổ điển) → đổi tên `ddNV1`.

| Thuộc tính | Dán |
|---|---|
| `Items` | `colCLB` |
| `Value` | `name` *(chọn trong khung Properties ô "Value")* |
| `AllowEmptySelection` | `true` |
| `Default` | `LookUp(colCLB, club_id = varNV.pref_1).name` |
| `DisplayMode` | `If(HetHan, DisplayMode.View, DisplayMode.Edit)` |
| `Width` | `Parent.Width` |
| `Height` | `44` |

> **Nếu bạn chèn phải Dropdown "Modern"** (thuộc tính tên *ItemDisplayText*, *DefaultSelectedItems*): dùng
> `Items` = `colCLB`; `ItemDisplayText` = `ThisItem.name`; `DefaultSelectedItems` = `Filter(colCLB, club_id = varNV.pref_1)`. Phần còn lại giữ nguyên. Ở PA09 công thức `ddNV1.Selected.club_id` vẫn dùng được.

8. **Ctrl+S**. Bấm **▶** (Preview, góc trên phải) → mở ô 1 → 👀 thấy danh sách tên CLB. **Esc** để thoát.

## Phần 3 — Nhân bản ô 2 → 10
9. Cây: chuột phải `conNV1` → **Copy**.
10. Bấm `conLuoi` → **Ctrl+V**. 👀 Xuất hiện `conNV1_1` chứa `lblNV1_1`, `ddNV1_1`.
11. Đổi tên 3 đối tượng mới: `conNV2`, `lblNV2`, `ddNV2`.
12. Sửa **4 chỗ** (đổi số 1 → 2):

| Đối tượng | Thuộc tính | Giá trị mới |
|---|---|---|
| `conNV2` | `Visible` | `2 <= SoNguyenVongToiDa` |
| `lblNV2` | `Text` | `"Nguyện vọng 2"` |
| `ddNV2` | `Default` | `LookUp(colCLB, club_id = varNV.pref_2).name` |

13. Lặp 9–12 cho ô 3, 4, … 10 (thay số tương ứng; `pref_3`, `pref_4`…).
14. **Ctrl+S** sau mỗi 2–3 ô.

## Kiểm tra xong
- [ ] Cây có `conNV1` … `conNV10`, mỗi cái có `lblNVk`, `ddNVk` **đúng số**.
- [ ] Preview cửa sổ rộng: 2 cột. Thu hẹp cửa sổ (< 600 px): 1 cột.
- [ ] Đặt tạm `SoNguyenVongToiDa = 3` (PA04) → chỉ còn 3 ô. Đặt lại giá trị thật.
