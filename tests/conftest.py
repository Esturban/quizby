import pytest

from quizby.core import create_app


@pytest.fixture
def app(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "RATELIMIT_ENABLED": False,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()
