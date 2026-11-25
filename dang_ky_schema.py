"""DK3-L1: các bảng MỚI của cổng đăng ký thật (phòng, giáo viên, giai đoạn, CLB đăng ký, học sinh, nguyện vọng).

Toàn bộ là bảng mới (`CREATE TABLE IF NOT EXISTS`), tiền tố `dk_`, KHÔNG khoá ngoại sang bảng của bộ xếp, nên
chạy lại bao nhiêu lần cũng như nhau và không đụng dữ liệu cũ. `di_tru_schema` gọi `dam_bao_bang` (sao lưu trước
khi tạo lần đầu nếu CSDL đã có dữ liệu). Huy chương chỉ được LƯU ở đây; `compute_club_priority` không đọc bảng này
(bất biến 2, ngoại lệ D2 đường A).
"""

SCHEMA_DK3 = """
CREATE TABLE IF NOT EXISTS dk_cai_dat (
    khoa TEXT PRIMARY KEY,
    gia_tri TEXT
);
CREATE TABLE IF NOT EXISTS dk_giai_doan (
    ten TEXT PRIMARY KEY,
    mo_luc TEXT,
    han_chot TEXT,
    trang_thai TEXT NOT NULL DEFAULT 'cho' CHECK (trang_thai IN ('cho', 'mo', 'dong'))
);
CREATE TABLE IF NOT EXISTS dk_phong (
    phong_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL UNIQUE,
    suc_chua INTEGER NOT NULL CHECK (suc_chua > 0)
);
CREATE TABLE IF NOT EXISTS dk_giao_vien (
    gv_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL UNIQUE,
    pin_bam BLOB NOT NULL,
    pin_muoi BLOB NOT NULL,
    cach_tao TEXT NOT NULL CHECK (cach_tao IN ('tu_dang_ky', 'quan_tri'))
);
CREATE TABLE IF NOT EXISTS dk_clb (
    clb_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ten TEXT NOT NULL UNIQUE,
    buoi TEXT NOT NULL,
    loai TEXT NOT NULL CHECK (loai IN ('Tự do', 'Giới hạn', 'Tuyển chọn')),
    phong_id INTEGER,
    gv_id INTEGER,
    chi_tieu_gv INTEGER,
    chi_tieu INTEGER,
    khoi_tu INTEGER NOT NULL,
    khoi_den INTEGER NOT NULL,
    diem_san INTEGER,
    link_forms TEXT,
    mo_ta TEXT,
    yeu_cau TEXT,
    trang_thai TEXT NOT NULL DEFAULT 'cho_duyet' CHECK (trang_thai IN ('cho_duyet', 'duyet', 'tu_choi')),
    ly_do_tu_choi TEXT
);
CREATE TABLE IF NOT EXISTS dk_hoc_sinh (
    student_id TEXT PRIMARY KEY,
    ho_ten TEXT NOT NULL,
    lop TEXT NOT NULL,
    khoi INTEGER NOT NULL,
    pin_bam BLOB NOT NULL,
    pin_muoi BLOB NOT NULL,
    nop_luc TEXT
);
CREATE TABLE IF NOT EXISTS dk_nguyen_vong (
    student_id TEXT NOT NULL,
    buoi TEXT NOT NULL,
    hang INTEGER NOT NULL CHECK (hang >= 1),
    clb_id INTEGER NOT NULL,
    thi INTEGER NOT NULL DEFAULT 0 CHECK (thi IN (0, 1)),
    diem REAL,
    huy_chuong TEXT CHECK (huy_chuong IS NULL OR huy_chuong IN ('Vàng', 'Bạc', 'Đồng')),
    PRIMARY KEY (student_id, clb_id),
    UNIQUE (student_id, buoi, hang)
);
CREATE TABLE IF NOT EXISTS dk_nhat_ky (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    luc TEXT NOT NULL,
    vai TEXT NOT NULL,
    hanh_dong TEXT NOT NULL,
    chi_tiet TEXT
);
"""

TEN_BANG_DK3 = ("dk_cai_dat", "dk_giai_doan", "dk_phong", "dk_giao_vien", "dk_clb",
                "dk_hoc_sinh", "dk_nguyen_vong", "dk_nhat_ky")


def dam_bao_bang(conn) -> bool:
    """Tạo các bảng còn thiếu trên `conn` (một kết nối đang mở). True nếu vừa tạo ít nhất một bảng."""
    co = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    thieu = [t for t in TEN_BANG_DK3 if t not in co]
    if thieu:
        conn.executescript(SCHEMA_DK3)
    return bool(thieu)
