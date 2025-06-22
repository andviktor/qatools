from unittest.mock import patch, Mock
from app.modules.page_titles.page_titles_request import get_page_titles_request


def test_empty_url_list() -> None:
    assert get_page_titles_request([]) is None


@patch("app.modules.page_titles.page_titles_request.requests.get")
def test_valid_title(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = (
        "<html><head><title>Test Page</title></head><body></body></html>"
    )
    mock_get.return_value = mock_response

    result = get_page_titles_request(["http://example.com"])
    assert result == {"http://example.com": "Test Page"}


@patch("app.modules.page_titles.page_titles_request.requests.get")
def test_missing_title(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><head></head><body></body></html>"
    mock_get.return_value = mock_response

    result = get_page_titles_request(["http://no-title.com"])
    assert result == {"http://no-title.com": "No title found"}


@patch("app.modules.page_titles.page_titles_request.requests.get")
def test_request_exception(mock_get: Mock) -> None:
    mock_get.side_effect = Exception("Connection failed")

    result = get_page_titles_request(["http://fail.com"])
    assert result == {"http://fail.com": "Error: Connection failed"}
