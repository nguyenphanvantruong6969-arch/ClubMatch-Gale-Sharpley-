"""ST-A: stress tests (backend). Outside `testpaths`; run explicitly. DỮ LIỆU MÔ PHỎNG."""
import os
import sys

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for p in (GOC, os.path.dirname(os.path.abspath(__file__))):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _khong_ghi_ra_ngoai(tmp_path, monkeypatch):
    cho = tmp_path / "TaiXuong_gia"
    cho.mkdir(exist_ok=True)
    monkeypatch.setenv("RBDA_THU_MUC_TAI_VE", str(cho))
