"""Chia các tệp tests/test_*.py thành N phần cân bằng THỜI GIAN để CI chạy song song.

Dùng: python .github/chia_test.py <phan> <so_phan> [--windows]   (phan tính từ 1)
      -> in danh sách tệp, cách nhau dấu cách.

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
HE_SO_BYTE = 2000.0  # ~2 KB mã test ~ 1 giây (chỉ dùng khi tệp chưa có số đo)


def _doc_thoi_gian():
    try:
        with open(TEP_THOI_GIAN, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _bo_qua_tren_windows(t):
    try:
        with open(t, encoding="utf-8") as f:
            return any(d.startswith('pytest.importorskip("playwright"') for d in f)
    except OSError:
        return False


def chia(so_phan, windows=False):
    tep = sorted(t.replace("\\", "/") for t in glob.glob(os.path.join("tests", "test_*.py")))
    do = _doc_thoi_gian()

    def nang(t):
        if windows and _bo_qua_tren_windows(t):
            return 0.01
        if t in do:
            return float(do[t])
        return os.path.getsize(t) / HE_SO_BYTE * (4 if "giao_dien" in os.path.basename(t) else 1)

    phan = [[] for _ in range(so_phan)]
    tong = [0.0] * so_phan
    for t in sorted(tep, key=lambda t: (-nang(t), t)):
        i = tong.index(min(tong))
        phan[i].append(t)
        tong[i] += nang(t)
    return [sorted(p) for p in phan]


if __name__ == "__main__":
    k, n = int(sys.argv[1]), int(sys.argv[2])
    print(" ".join(chia(n, windows="--windows" in sys.argv[3:])[k - 1]))
