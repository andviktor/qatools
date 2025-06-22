import pytest
from unittest.mock import patch, MagicMock
from typing import Generator
from flask.testing import FlaskClient
from app.app import app


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_root_get_without_url(client: FlaskClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"Sitemap" in response.data


@patch("app.app.Sitemap")
@patch("app.app.sitemap_to_jstree_formatter")
def test_root_get_with_url(
    mock_formatter: MagicMock, mock_sitemap: MagicMock, client: FlaskClient
) -> None:
    mock_instance = MagicMock()
    mock_instance.get.return_value = {
        "metadata": {"https://example.com": {"title": "Example"}},
        "incoming": {"https://example.com": []},
        "internal": {},
        "external": [],
        "root": "https://example.com",
    }
    mock_sitemap.return_value = mock_instance
    mock_formatter.return_value = [{"id": "1", "text": "example"}]

    response = client.get("/?url=https://example.com&depth=2")
    assert response.status_code == 200
    assert b"example" in response.data


def test_meta_tags_get(client: FlaskClient) -> None:
    response = client.get("/meta-tags")
    assert response.status_code == 200
    assert b"Meta tags" in response.data


@patch("app.app.get_meta_tags_request")
def test_meta_tags_post_request(mock_tags: MagicMock, client: FlaskClient) -> None:
    mock_tags.return_value = {
        "https://example.com": {
            "title": "Example Title",
            "description": "Example Description",
        }
    }
    response = client.post("/meta-tags", data={"urls": "https://example.com"})
    assert response.status_code == 200
    assert b"Example Title" in response.data
    assert b"Example Description" in response.data


@patch("app.app.get_meta_tags_selenium")
def test_meta_tags_post_selenium(mock_tags: MagicMock, client: FlaskClient) -> None:
    mock_tags.return_value = {
        "https://example.com": {
            "title": "Selenium Title",
            "description": "Selenium Description",
        }
    }
    response = client.post(
        "/meta-tags", data={"urls": "https://example.com", "enable-selenium": "on"}
    )
    assert response.status_code == 200
    assert b"Selenium Title" in response.data
    assert b"Selenium Description" in response.data
