import pathlib
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[3]
HYPERMATH = ROOT / "fields" / "hypermath"


def pytest_configure(config):
    config.addinivalue_line("markers", "real: needs the pinned hypermath checkout under fields/")
    config.addinivalue_line("markers", "lean: needs a Lean 4 toolchain on PATH")
    config.addinivalue_line("markers", "metamath: needs mmverify.py (HM_MMVERIFY or ./mmverify.py)")
