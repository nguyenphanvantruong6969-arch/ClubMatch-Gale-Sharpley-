# Giao việc: viết bộ hướng dẫn "Đường Forms"

> Người nhận: bạn của Truong, người sẽ viết bộ hướng dẫn.
> Người giao: Truong (chủ dự án). Có gì chưa rõ thì hỏi Truong **trước khi viết**, đừng tự đoán.

## 1. Bối cảnh trong 5 câu

1. Dự án xếp khoảng 800 học sinh vào khoảng 20 câu lạc bộ bằng phần mềm **rbda-kiosk** chạy trên Windows.
2. Phần mềm cần dữ liệu đầu vào gồm nguyện vọng của học sinh và điểm thi tuyển của những câu lạc bộ có thi.
3. Đường thứ nhất, **Power Apps + SharePoint**, đã có hướng dẫn trong `docs/power_apps/cai_dat/`. Tài khoản trường hiện **bị chặn tạo trang SharePoint**, nên đường này đang phải chờ bộ phận tin học.
4. Vì vậy cần **đường thứ hai, chỉ dùng Forms**: học sinh đăng ký nguyện vọng và làm bài thi trên một biểu mẫu, giáo viên tải kết quả về rồi đưa vào phần mềm. Không cần SharePoint, không cần Power Apps.
5. Đường này đã có sẵn công cụ và tài liệu kỹ thuật (mục 3). Việc của bạn là **biến chúng thành hướng dẫn từng bước cho người không rành máy tính**.

## 2. Việc cần làm

Viết một bộ hướng dẫn nằm ở thư mục mới `docs/forms/cai_dat/`, gồm:

| Tệp | Nội dung |
|---|---|
| `00_MUC_LUC.md` | Mục lục, cách đọc hướng dẫn, thứ tự bắt buộc, 4–5 thông tin cần ghi sổ tay |
| `FM01_…md` | Kiểm tra tài khoản: dùng được Microsoft Forms không, có giới hạn "chỉ người trong trường" không |
| `FM02_…md` | Chuẩn bị danh sách câu lạc bộ và đề thi theo mẫu `mau_forms_thi_clb/MAU_DE_THI.xlsx` |
| `FM03_…md` | Dựng biểu mẫu bằng **Quick Import** (nhập nhanh từ tệp `.docx`) |
| `FM04_…md` | Những phần Quick Import không mang theo: câu xếp hạng, rẽ nhánh theo câu lạc bộ, đáp án, điểm |
| `FM05_…md` | Cài đặt: chỉ người trong trường, ghi tên, mỗi người một lần, ẩn điểm và đáp án |
| `FM06_…md` | Làm thử bằng chế độ xem trước và 3 tài khoản thử |
| `FM07_…md` | Gửi cho học sinh: đường dẫn, mã QR, lời dặn |
| `FM08_…md` | Hết hạn: đóng biểu mẫu, tải Excel kết quả |
| `FM09_…md` | Chuyển Excel thành **Sổ nhập CLB** (`SO_NHAP_CLB.xlsx`) và đưa vào phần mềm |
| `FM10_…md` | Bảng xử lý sự cố |

Số tệp có thể thêm bớt, miễn **mỗi tệp chỉ làm một việc**.

**Phạm vi:** viết cho **Microsoft Forms** trước, vì trường dùng tài khoản Microsoft. Google Forms đã có hướng dẫn riêng (`mau_forms_thi_clb/HUONG_DAN_TUNG_BUOC.md`); chỉ cần một đoạn ngắn trong mục lục trỏ tới đó.

**Hai kiểu dùng**, mục lục phải cho người đọc chọn ngay từ đầu:
- **Kiểu A – Forms làm hết:** nguyện vọng và bài thi cùng nằm trong một biểu mẫu. Đây là kiểu mặc định.
- **Kiểu B – Forms chỉ có bài thi:** nguyện vọng nằm ở chỗ khác (ví dụ ứng dụng Power Apps). Xem "Chế độ chỉ thi" trong `mau_forms_thi_clb/README.md`, mục 0.

## 3. Đọc gì trước khi viết (theo thứ tự)

1. `docs/power_apps/cai_dat/00_MUC_LUC.md` và 2 tệp bất kỳ trong đó: **mẫu văn phong bắt buộc** (mục 4).
2. `mau_forms_thi_clb/README.md`: toàn bộ đường Forms, các tệp, cách chạy bộ chuyển đổi.
3. `mau_forms_thi_clb/CAI_DAT_FORMS.md`: bố cục từng phần, từng câu của biểu mẫu mẫu.
4. `mau_forms_thi_clb/HUONG_DAN_TUNG_BUOC.md`: hướng dẫn Google Forms đã có, để tham khảo cách chia bước.
5. `mau_forms_thi_clb/GHI_CHU_GIAO_VIEN.md`, `DINH_DANG_RAW.md`: điều giáo viên cần biết, dạng tệp Forms xuất ra.
6. `mau_csv/HUONG_DAN_SO_NHAP.md`: Sổ nhập CLB mà phần mềm nhận.
7. `mau_forms_thi_clb/MO_PHONG_FORMS.html`: mở bằng trình duyệt để **tự đi thử luồng** của học sinh trước khi viết.

## 4. Văn phong bắt buộc (giống bộ Power Apps)

1. **100% tiếng Việt dễ hiểu, không dùng từ chuyên môn.** Bắt buộc phải có từ lạ thì giải thích một lần ngay chỗ đó.
2. Chữ in trên màn hình của Microsoft giữ nguyên, đặt trong ngoặc «…», ví dụ «New Quiz», «Collect responses». Lần đầu xuất hiện thì kèm nghĩa tiếng Việt.
3. **Tối đa sao chép và dán:** mọi thứ người đọc phải gõ (tên biểu mẫu, câu hỏi, đường dẫn, lời dặn học sinh, lệnh chạy) đều nằm trong **ô xám riêng**, mỗi ô một giá trị.
4. **Mỗi bước đánh số chỉ một thao tác.** Không gộp kiểu "mở X rồi bấm Y và chọn Z".
5. Sau mỗi thao tác quan trọng có dòng **👀** (bạn sẽ thấy gì). Lỗi hay gặp ghi bằng **⚠️** kèm cách sửa.
6. **Không ước tính thời gian** ở bất cứ đâu.
7. **Không viết mơ hồ.** Cấm các câu kiểu "tìm nút tương tự", "nếu có", "tuỳ trường hợp", "góc trên" (phải nói rõ góc trên bên trái hay bên phải), "điền các thông tin cần thiết". Giao diện thật sự có nhiều bản thì ghi cụ thể **cả hai đường bấm**.
8. Mỗi tệp mở đầu bằng: đường dẫn về tệp trước và tệp sau, rồi mục **Cần có**. Cuối tệp có ô **[ ]** để đánh dấu đã xong.
9. Mọi ví dụ về học sinh, câu lạc bộ, điểm số đều là **dữ liệu giả** và phải ghi rõ là giả.

## 5. Những điều không được làm

- **Không sửa** mã nguồn (`.py`, `.js`, `.gs`, `.html`) hay tệp mẫu trong `mau_forms_thi_clb/`, `mau_csv/`. Thấy lỗi thì ghi lại, báo Truong.
- **Không đổi tên cột** mà phần mềm đọc (`student_id`, `club_id`, `pref_k`, `test_club_k`, `score_k`…). Hướng dẫn phải dẫn người đọc ra **đúng** Sổ nhập như `mau_csv/HUONG_DAN_SO_NHAP.md`.
- **Không đưa dữ liệu thật** của học sinh vào tài liệu hay ảnh chụp màn hình.
- Không dùng tính năng phải trả tiền thêm ngoài gói Microsoft 365 Education.
- Đây là đề tài nghiên cứu của học sinh: **không viết phần nhận xét, kết luận** cho báo cáo đề tài. Chỉ viết hướng dẫn thao tác.

## 6. Ba điểm phải viết thật kỹ (người làm dễ sai nhất)

1. **Rẽ nhánh theo câu lạc bộ** (học sinh chọn thi câu lạc bộ nào thì chỉ hiện đề câu lạc bộ đó). Microsoft Forms gọi là «Branching». Phải chỉ rõ từng câu rẽ đi đâu, đối chiếu với bảng bố cục trong `CAI_DAT_FORMS.md`.
2. **Câu xếp hạng nguyện vọng** («Ranking»). Quick Import không tạo được loại câu này, phải làm tay.
3. **Cài đặt chống gian lận:** chỉ người trong trường, ghi lại tên người làm, mỗi người chỉ nộp một lần, **không hiện điểm và đáp án** sau khi nộp.

## 7. Bước chuyển dữ liệu (FM09)

Đây là bước duy nhất phải chạy một lệnh trên máy tính. Viết sao cho người chưa từng mở cửa sổ lệnh vẫn làm được:
- Cài Python ở đâu, kiểm tra đã cài bằng cách nào (lệnh trong ô xám, kèm 👀 kết quả đúng).
- Mở cửa sổ lệnh ngay tại thư mục dự án bằng cách nào (trên Windows).
- Lệnh chạy bộ chuyển đổi lấy từ `mau_forms_thi_clb/README.md`, mỗi lệnh một ô xám, thay tên tệp ở đâu.
- Kết quả ra tệp nào, nằm ở đâu, đưa vào phần mềm rbda-kiosk ra sao.
- Nếu Truong có cách khác không cần cửa sổ lệnh (ví dụ skill `xu-li-raw-forms`, hay một nút trong phần mềm), hỏi Truong rồi viết thêm.

## 8. Tiêu chí nghiệm thu (Truong kiểm từng ô)

- [ ] Một người **chưa từng dùng Forms** làm theo từ FM01 đến FM09 với dữ liệu giả và ra được `SO_NHAP_CLB.xlsx` mà phần mềm nạp **không báo lỗi**.
- [ ] Tất cả đường dẫn giữa các tệp đều mở được.
- [ ] Không còn câu nào vi phạm mục 4 (Truong sẽ dò từ khoá "nếu có", "tương tự", "phút", "tuỳ").
- [ ] Mọi giá trị phải gõ đều nằm trong ô xám riêng.
- [ ] Ba điểm ở mục 6 có ảnh minh hoạ **hoặc** bảng đối chiếu từng câu.
- [ ] Có bảng sự cố với ít nhất 10 dòng: triệu chứng, nguyên nhân, cách sửa.
- [ ] Ghi rõ chỗ nào **chưa thử trên Forms thật**.

## 9. Cách nộp

1. Làm trên một nhánh riêng, đặt tên kiểu `forms-huong-dan-<tên bạn>`.
2. Mỗi lần xong vài tệp thì gửi Truong xem, đừng đợi xong hết.
3. Khi xong: tạo yêu cầu gộp (pull request) vào nhánh của Truong, kèm danh sách tệp và những chỗ còn chưa chắc.
4. Nếu có dùng AI hỗ trợ, ghi ngắn gọn vào phần mô tả của yêu cầu gộp để Truong ghi vào nhật ký dùng AI của đề tài.
