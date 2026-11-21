"""Chia các tệp tests/test_*.py thành N phần cân bằng THỜI GIAN để CI chạy song song.

Dùng: python .github/chia_test.py <phan> <so_phan> [--windows] [--song-song | --tuan-tu]   (phan tính từ 1)
      -> in danh sách tệp của phần đó, cách nhau dấu cách.
      --song-song: chỉ tệp chạy được với pytest-xdist (-n auto);
      --tuan-tu:   chỉ tệp NHẠY THỜI GIAN (giao diện Chromium có timeout, test đo tốc độ có ngưỡng giây),
                   phải chạy một tiến trình — chạy song song thì tranh CPU làm chúng hỏng giả.
      Không cờ nào: cả hai nhóm (như trước).

Trọng số mỗi tệp (giây ước tính):
- Có trong `.github/thoi_gian_test.json` (đo thật, tổng thời gian các test của tệp) -> dùng số đó.
- Tệp mới chưa đo -> ước theo kích thước (byte / HE_SO_BYTE), giao diện x4.
- `--windows`: tệp gọi `pytest.importorskip("playwright")` ở đầu tệp bị BỎ QUA cả tệp trên Windows
  (không cài playwright) -> trọng số gần 0, để không chiếm chỗ của tệp chạy thật.
Chia tất định (tham lam theo trọng số giảm dần): cùng bộ tệp + cùng số đo luôn ra cùng cách chia.
Mọi tệp đều thuộc đúng một phần. Không cần thư viện ngoài.
"""
import glob
import json
import os
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
TEP_THOI_GIAN = os.path.join(THU_MUC, "thoi_gian_test.json")
TEP_THOI_GIAN_WINDOWS = os.path.join(THU_MUC, "thoi_gian_test_windows.json")
HE_SO_BYTE = 2000.0  # ~2 KB mã test ~ 1 giây (chỉ dùng khi tệp chưa có số đo)
HE_SO_SONG_SONG = 3.0  # 4 nhân CI, trừ hao phí khởi động tiến trình


def _doc_thoi_gian(windows=False):
    """Số đo đúng máy: Windows dùng số đo Windows nếu có (máy Windows chậm hơn và lệch tỉ lệ)."""
    for duong in ([TEP_THOI_GIAN_WINDOWS] if windows else []) + [TEP_THOI_GIAN]:
        try:
            with open(duong, encoding="utf-8") as f:
                return json.load(f), duong == TEP_THOI_GIAN_WINDOWS
        except (OSError, ValueError):
            continue
    return {}, False


def _bo_qua_tren_windows(t):
    try:
        with open(t, encoding="utf-8") as f:
            return any(d.startswith('pytest.importorskip("playwright"') for d in f)
    except OSError:
        return False


# Tệp đo tốc độ có ngưỡng giây: chạy song song thì tranh CPU, hỏng giả (đo thật trên CI 2026-11-21).
TUAN_TU_THEO_TEN = {
    "tests/test_hieu_nang.py",
    "tests/test_xp1_hieu_nang.py",
    "tests/test_a13_11_stress.py",
    "tests/test_wharton_quan_ly.py",
}


def nhay_thoi_gian(t):
    """True nếu tệp phải chạy tuần tự: dùng Chromium (playwright) hoặc đo tốc độ có ngưỡng."""
    if t.replace("\\", "/") in TUAN_TU_THEO_TEN:
        return True
    try:
        with open(t, encoding="utf-8") as f:
            return "playwright" in f.read()
    except OSError:
        return False


def chia(so_phan, windows=False):
    tep = sorted(t.replace("\\", "/") for t in glob.glob(os.path.join("tests", "test_*.py")))
    do, _ = _doc_thoi_gian(windows)

    def nang(t):
        if windows and _bo_qua_tren_windows(t):
            return 0.01
        g = float(do[t]) if t in do else (
            os.path.getsize(t) / HE_SO_BYTE * (4 if "giao_dien" in os.path.basename(t) else 1))
        # Tệp thường chạy -n auto (4 tiến trình cùng lúc): thời gian thực của cả bước ~ tổng thời gian
        # từng test / số tiến trình, nên trọng số chia HE_SO_SONG_SONG. Tệp tuần tự giữ nguyên.
        return g if nhay_thoi_gian(t) else g / HE_SO_SONG_SONG

    phan = [[] for _ in range(so_phan)]
    tong = [0.0] * so_phan
    for t in sorted(tep, key=lambda t: (-nang(t), t)):
        i = tong.index(min(tong))
        phan[i].append(t)
        tong[i] += nang(t)
    return [sorted(p) for p in phan]


if __name__ == "__main__":
    k, n = int(sys.argv[1]), int(sys.argv[2])
    co = sys.argv[3:]
    ds = chia(n, windows="--windows" in co)[k - 1]
    if "--song-song" in co:
        ds = [t for t in ds if not nhay_thoi_gian(t)]
    elif "--tuan-tu" in co:
        ds = [t for t in ds if nhay_thoi_gian(t)]
    print(" ".join(ds))
