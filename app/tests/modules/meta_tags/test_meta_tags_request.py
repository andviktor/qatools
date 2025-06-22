from unittest.mock import patch, Mock
from app.modules.meta_tags.meta_tags_request import get_meta_tags_request


def test_empty_url_list() -> None:
    assert get_meta_tags_request([]) is None


@patch("app.modules.meta_tags.meta_tags_request.requests.get")
def test_valid_title_and_description(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = (
        "<html><head>"
        "<title>Test Page</title>"
        "<meta name='description' content='Test description.'>"
        "</head><body></body></html>"
    )
    mock_get.return_value = mock_response

    result = get_meta_tags_request(["http://example.com"])
    assert result == {
        "http://example.com": {"title": "Test Page", "description": "Test description."}
    }


@patch("app.modules.meta_tags.meta_tags_request.requests.get")
def test_missing_title_and_description(mock_get: Mock) -> None:
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><head></head><body></body></html>"
    mock_get.return_value = mock_response

    result = get_meta_tags_request(["http://no-title.com"])
    assert result == {"http://no-title.com": {"title": "", "description": ""}}


@patch("app.modules.meta_tags.meta_tags_request.requests.get")
def test_request_exception(mock_get: Mock) -> None:
    mock_get.side_effect = Exception("Connection failed")

    result = get_meta_tags_request(["http://fail.com"])
    assert result == {
        "http://fail.com": {
            "title": "Error: Connection failed",
            "description": "Error: Connection failed",
        }
    }
