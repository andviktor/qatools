from unittest.mock import patch, MagicMock
from app.modules.meta_tags.meta_tags_selenium import get_meta_tags_selenium


def test_empty_url_list_returns_none() -> None:
    assert get_meta_tags_selenium([]) is None


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.ChromeDriverManager")
def test_valid_url(mock_driver_manager: MagicMock, mock_webdriver: MagicMock) -> None:
    mock_driver_instance = MagicMock()
    mock_driver_instance.title = "Mock Title"

    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "Mock Description"
    mock_driver_instance.find_element.return_value = mock_element

    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_meta_tags_selenium(["http://example.com"])
    assert result == {
        "http://example.com": {"title": "Mock Title", "description": "Mock Description"}
    }
    mock_driver_instance.get.assert_called_once_with("http://example.com")
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.ChromeDriverManager")
def test_invalid_url_format(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_meta_tags_selenium(["ftp://example.com", "not-a-url"])
    expected = {
        "ftp://example.com": {
            "title": "Error: URL must start with http or https",
            "description": "Error: URL must start with http or https",
        },
        "not-a-url": {
            "title": "Error: URL must start with http or https",
            "description": "Error: URL must start with http or https",
        },
    }
    assert result == expected
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.ChromeDriverManager")
def test_selenium_exception(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_driver_instance.get.side_effect = Exception("Selenium crash")

    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_meta_tags_selenium(["http://bad-url.com"])
    assert result is not None
    assert result["http://bad-url.com"]["title"].startswith("Error:")
    assert result["http://bad-url.com"]["description"].startswith("Error:")
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.ChromeDriverManager")
def test_empty_url_skipped(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_meta_tags_selenium(["", "http://example.com"])
    assert result is not None
    assert "" not in result
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.ChromeDriverManager")
def test_title_and_missing_description(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_driver_instance.title = "Title Only"
    mock_driver_instance.find_element.side_effect = Exception("not found")

    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_meta_tags_selenium(["http://empty-desc.com"])
    assert result == {
        "http://empty-desc.com": {"title": "Title Only", "description": ""}
    }
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.meta_tags.meta_tags_selenium.webdriver.Chrome")
@patch("app.modules.meta_tags.meta_tags_selenium.ChromeDriverManager")
def test_empty_title_and_description(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_driver_instance.title = ""
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = ""

    mock_driver_instance.find_element.return_value = mock_element
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_meta_tags_selenium(["http://empty-tags.com"])
    assert result == {"http://empty-tags.com": {"title": "", "description": ""}}
    mock_driver_instance.quit.assert_called_once()
