"""DK3-L1: bảng dk_* — di trú hai lần = một lần; dữ liệu cũ còn nguyên."""
import sqlite3

import dang_ky_schema as ds
from rbda_priority_pipeline import di_tru_schema


def _bang(p):
    c = sqlite3.connect(p)
    try:
        return {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    finally:
        c.close()


def test_tao_du_tam_bang_va_chay_lai_khong_doi(api):
    assert set(ds.TEN_BANG_DK3) <= _bang(api.db_path)
    assert "dk3" not in di_tru_schema(api.db_path)
    assert "dk3" not in di_tru_schema(api.db_path)


def test_csdl_cu_duoc_nang_cap_va_giu_du_lieu(tmp_path):
    p = str(tmp_path / "cu.db")
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT)")
    c.execute("INSERT INTO students VALUES ('S1','An')")
    c.commit()
    c.close()
    assert "dk3" in di_tru_schema(p)
    assert "dk3" not in di_tru_schema(p)
    c = sqlite3.connect(p)
    assert c.execute("SELECT name FROM students").fetchall() == [("An",)]
    c.close()
    assert set(ds.TEN_BANG_DK3) <= _bang(p)
