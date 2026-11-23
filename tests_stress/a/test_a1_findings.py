"""ST-A1 findings: importing the shared Sổ while the mode drops columns. SIMULATED data."""
import pytest

import sthelp
from sthelp import b64_file, rows, switch


def _import_in(tmp_path, mode, tag):
    api = sthelp.new_ws_api(tmp_path, tag)
    switch(api, mode, False)
    r = api.import_so_nhap(b64_file(sthelp.SO_150))
    assert r["ok"], r
    return api, [w["code"] for w in r["data"]["warnings"]]


@pytest.mark.parametrize("rep", [1, 2])
@pytest.mark.parametrize("mode,codes", [("chia_100", {"fa_cot_bo_qua"}),
                                         ("chi_xep", {"fa_cot_bo_qua", "csv_wp_bo_qua"})])
def test_import_warns_at_import_time(tmp_path, mode, codes, rep):
    """Documented behaviour: the import itself warns (so not a bug)."""
    api, got = _import_in(tmp_path, mode, "w%d" % rep)
    assert codes <= set(got)
    assert rows(api.db_path, "SELECT COUNT(*) FROM clubs WHERE loai IS NOT NULL")[0][0] == 0


@pytest.mark.parametrize("rep", [1, 2])
@pytest.mark.parametrize("mode", ["chia_100", "chi_xep"])
def test_switch_after_lossy_import_gives_notice_or_stays_runnable(tmp_path, mode, rep):
    """After a lossy import, switching to Huy chương must either keep working or tell the admin at switch time
    (response carries a warning / needs-reimport flag). Today: ok:true, no notice, run blocked later."""
    api, _ = _import_in(tmp_path, mode, "s%d" % rep)
    r = switch(api, "huy_chuong", False)
    assert r["ok"]
    blob = repr(r["data"]).lower()
    notice = any(k in blob for k in ("warning", "canh_bao", "reimport", "nap_lai", "can_nap"))
    h = api.get_data_health_report()["data"]
    assert notice or h["n_high"] == 0
