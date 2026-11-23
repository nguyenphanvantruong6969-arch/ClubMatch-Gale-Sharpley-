"""ST-A4 helper: build a prepared workspace DB once and fuzz every public PipelineAPI method."""
import inspect
import signal


SKIP = {"mo_tep", "mo_thu_muc"}     # launch OS programs: monkeypatched / covered separately

VALUES = {
    "None": None, "zero": 0, "neg": -1, "huge_int": 10 ** 30, "float": 3.14, "nan": float("nan"), "true": True,
    "empty": "", "space": "   ", "long": "x" * 200000, "sql": "'; DROP TABLE students;--", "traversal": "../../etc/passwd",
    "nul": "a\0b", "unicode": "é😀‮​", "list0": [], "dict0": {}, "list_none": [None],
    "dict_junk": {"a": 1, "__proto__": 2}, "list_big": ["x"] * 3000, "bytes": b"bytes",
}


def public_methods(api):
    out = []
    for n in sorted(dir(api)):
        if n.startswith("_"):
            continue
        f = getattr(api, n)
        if callable(f):
            out.append(n)
    return out


def n_required(f):
    try:
        sig = inspect.signature(f)
    except (TypeError, ValueError):
        return 0
    return sum(1 for p in sig.parameters.values()
               if p.default is p.empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD))


class Timeout(Exception):
    pass


def call_limited(fn, args, sec=60):
    def h(*a):
        raise Timeout("hang > %ds" % sec)
    old = signal.signal(signal.SIGALRM, h)
    signal.alarm(sec)
    try:
        return fn(*args)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)
