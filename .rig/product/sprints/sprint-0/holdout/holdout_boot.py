"""Shared boot code for the sprint 0 holdout tests: a fresh app (and so a fresh cart) per test."""

import importlib
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def fresh_client() -> TestClient:
    src = str(Path.cwd() / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    for name in [m for m in sys.modules if m == "cart" or m.startswith("cart.")]:
        del sys.modules[name]
    main = importlib.import_module("cart.main")
    return TestClient(main.app)
