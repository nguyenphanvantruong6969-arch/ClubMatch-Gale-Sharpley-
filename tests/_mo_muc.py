"""UX5B-L3: ba bước của thẻ Nhập nguyện vọng là ba mục gập (chỉ một mục mở). Test cũ thao tác thẳng trên Bước 1/2/3
gọi `mo_muc(page, "thi" | "nv" | "b3")` trước khi chạm vào ô của bước đó; đã mở rồi thì không làm gì."""


def mo_muc(page, muc):
    page.evaluate("(k) => ux5bMoMuc(k)", muc)
