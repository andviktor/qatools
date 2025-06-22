from unittest.mock import patch, MagicMock
from app.modules.page_titles.page_titles_selenium import get_page_titles_selenium


def test_empty_url_list_returns_none() -> None:
    assert get_page_titles_selenium([]) is None


@patch("app.modules.page_titles.page_titles_selenium.webdriver.Chrome")
@patch("app.modules.page_titles.page_titles_selenium.ChromeDriverManager")
def test_valid_url(mock_driver_manager: MagicMock, mock_webdriver: MagicMock) -> None:
    mock_driver_instance = MagicMock()
    mock_driver_instance.title = "Mock Title"
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_page_titles_selenium(["http://example.com"])
    assert result == {"http://example.com": "Mock Title"}
    mock_driver_instance.get.assert_called_once_with("http://example.com")
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.page_titles.page_titles_selenium.webdriver.Chrome")
@patch("app.modules.page_titles.page_titles_selenium.ChromeDriverManager")
def test_invalid_url_format(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_page_titles_selenium(["ftp://example.com", "not-a-url"])
    expected = {
        "ftp://example.com": "Error: URL must start with http or https",
        "not-a-url": "Error: URL must start with http or https",
    }
    assert result == expected
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.page_titles.page_titles_selenium.webdriver.Chrome")
@patch("app.modules.page_titles.page_titles_selenium.ChromeDriverManager")
def test_selenium_exception(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_driver_instance.get.side_effect = Exception("Selenium crash")
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_page_titles_selenium(["http://bad-url.com"])
    assert result is not None
    assert "Error: Selenium crash" in result["http://bad-url.com"]
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.page_titles.page_titles_selenium.webdriver.Chrome")
@patch("app.modules.page_titles.page_titles_selenium.ChromeDriverManager")
def test_empty_url_skipped(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_page_titles_selenium(["", "http://example.com"])
    assert result is not None
    assert "http://example.com" in result
    assert "" not in result
    mock_driver_instance.quit.assert_called_once()


@patch("app.modules.page_titles.page_titles_selenium.webdriver.Chrome")
@patch("app.modules.page_titles.page_titles_selenium.ChromeDriverManager")
def test_title_missing(
    mock_driver_manager: MagicMock, mock_webdriver: MagicMock
) -> None:
    mock_driver_instance = MagicMock()
    mock_driver_instance.title = ""
    mock_webdriver.return_value = mock_driver_instance
    mock_driver_manager().install.return_value = "/path/to/chromedriver"

    result = get_page_titles_selenium(["http://empty-title.com"])
    assert result == {"http://empty-title.com": "No title found"}
    mock_driver_instance.quit.assert_called_once()
