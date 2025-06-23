from unittest.mock import patch, MagicMock
from typing import Dict
from selenium.webdriver.remote.webelement import WebElement
from app.modules.meta_tags.meta_tags_selenium import get_meta_tags_selenium


def test_empty_url_list_returns_none() -> None:
    assert get_meta_tags_selenium([]) is None


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.Service")
def test_valid_title_and_description(
    mock_service: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver: MagicMock = MagicMock()
    mock_driver.title = "Test Title"

    mock_element: MagicMock = MagicMock(spec=WebElement)
    mock_element.get_attribute.return_value = "Test Description"
    mock_driver.find_element.return_value = mock_element

    mock_webdriver.return_value = mock_driver

    result: Dict[str, Dict[str, str]] | None = get_meta_tags_selenium(
        ["http://example.com"]
    )
    assert result == {
        "http://example.com": {"title": "Test Title", "description": "Test Description"}
    }
    mock_driver.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.Service")
def test_missing_description_tag(
    mock_service: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver: MagicMock = MagicMock()
    mock_driver.title = "Title without description"
    mock_driver.find_element.side_effect = Exception("not found")
    mock_webdriver.return_value = mock_driver

    result: Dict[str, Dict[str, str]] | None = get_meta_tags_selenium(
        ["http://nodec.com"]
    )
    assert result == {
        "http://nodec.com": {"title": "Title without description", "description": ""}
    }
    mock_driver.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.Service")
def test_invalid_url_format_skipped(
    mock_service: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver: MagicMock = MagicMock()
    mock_webdriver.return_value = mock_driver

    result: Dict[str, Dict[str, str]] | None = get_meta_tags_selenium(
        ["", "ftp://bad", "not-a-url"]
    )
    assert result == {
        "": {
            "title": "Error: URL must start with http or https",
            "description": "Error: URL must start with http or https",
        },
        "ftp://bad": {
            "title": "Error: URL must start with http or https",
            "description": "Error: URL must start with http or https",
        },
        "not-a-url": {
            "title": "Error: URL must start with http or https",
            "description": "Error: URL must start with http or https",
        },
    }
    mock_driver.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.Service")
def test_selenium_driver_exception(
    mock_service: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver: MagicMock = MagicMock()
    mock_driver.get.side_effect = Exception("crash")
    mock_webdriver.return_value = mock_driver

    result: Dict[str, Dict[str, str]] | None = get_meta_tags_selenium(
        ["http://crash.com"]
    )
    assert result == {
        "http://crash.com": {"title": "Error: crash", "description": "Error: crash"}
    }
    mock_driver.quit.assert_called_once()
