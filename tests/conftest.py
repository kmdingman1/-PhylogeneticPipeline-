import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir():
    return FIXTURES


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(scope="session")
def muscle_available():
    return shutil.which("muscle") is not None or shutil.which("muscle.exe") is not None


@pytest.fixture
def workdir(tmp_path):
    return tmp_path
