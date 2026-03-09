from unittest.mock import patch

from config import Config
from quizby.core import create_app


def test_create_app_loads_root_config(app):
    assert app.config["OR_MODEL"] == Config.OR_MODEL
    assert app.config["SECRET_KEY"]


def test_index_route_returns_ok(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Quizby" in response.data


def test_default_source_asset_is_served(client):
    response = client.get("/static/assets/dmbok-sample.txt")

    assert response.status_code == 200
    assert b"DMBOK" in response.data


def test_generate_quiz_rejects_missing_custom_textbook_content(client):
    response = client.post("/generate-quiz", json={"useCustomTextbook": True})

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Custom textbook content is required when useCustomTextbook is true."
    }


def test_generate_quiz_returns_mocked_content(client):
    with patch("quizby.core.quizby", return_value="## Mock Quiz"):
        response = client.post("/generate-quiz", json={"customPrompt": "Custom prompt"})

    payload = response.get_json()

    assert response.status_code == 200
    assert payload["quiz"] == "## Mock Quiz"
    assert "executionTime" in payload


def test_generate_quiz_hides_internal_errors_outside_test_mode(tmp_path):
    app = create_app(
        {
            "TESTING": False,
            "DEBUG": False,
            "RATELIMIT_ENABLED": False,
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )
    client = app.test_client()

    with patch("quizby.core.quizby", side_effect=RuntimeError("backend details")):
        response = client.post("/generate-quiz", json={})

    assert response.status_code == 500
    assert response.get_json() == {
        "error": "Unable to generate quiz right now. Please try again later."
    }
