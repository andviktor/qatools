from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
from requests import RequestException
from requests.models import Response
from typing import Set
from app.modules.sitemap.sitemap import Sitemap


HTML_PAGE: str = """
<html>
  <head>
    <title>Example Title</title>
    <meta name="description" content="Test description.">
    <link rel="canonical" href="https://example.com/home" />
  </head>
  <body>
    <a href="https://example.com/about">About</a>
    <a href="https://external.com">External</a>
  </body>
</html>
"""


@patch("app.modules.sitemap.sitemap.get")
def test_extract_links_with_depth(mock_get: MagicMock) -> None:
    response_mock: MagicMock = MagicMock()
    response_mock.status_code = 200
    response_mock.text = HTML_PAGE
    response_mock.raise_for_status.return_value = None
    mock_get.return_value = response_mock

    sitemap: Sitemap = Sitemap("https://example.com", max_depth=1)
    sitemap.collect()

    data = sitemap.get()
    assert data["root"] == "https://example.com"
    assert "https://example.com/about" in data["internal"]["https://example.com"]
    assert "https://external.com" in data["external"]
    assert data["metadata"]["https://example.com"]["title"] == "Example Title"
    assert data["metadata"]["https://example.com"]["description"] == "Test description."
    assert (
        data["metadata"]["https://example.com"]["canonical"]
        == "https://example.com/home"
    )
    assert "https://example.com" in data["incoming"]["https://example.com/about"]
    assert "https://example.com" in data["incoming"]["https://external.com"]


@patch("app.modules.sitemap.sitemap.get")
def test_extract_links_with_request_exception(mock_get: MagicMock) -> None:
    response_mock: Response = Response()
    response_mock.status_code = 404

    exc: RequestException = RequestException("Request failed")
    exc.response = response_mock
    mock_get.side_effect = exc

    sitemap: Sitemap = Sitemap("https://fail.com", max_depth=1)
    sitemap.collect()

    data = sitemap.get()
    assert data["internal"] == {}
    assert data["metadata"] == {}
    assert data["response"]["https://fail.com"]["status"] == 404


def test_normalize_url() -> None:
    assert Sitemap._normalize_url("https://example.com/") == "https://example.com"
    assert Sitemap._normalize_url("/") == "/"


def test_extract_tags_with_missing_elements() -> None:
    soup: BeautifulSoup = BeautifulSoup(
        "<html><head></head><body></body></html>", "html.parser"
    )
    title, desc, canon = Sitemap._extract_tags(soup)
    assert title == ""
    assert desc == ""
    assert canon == ""


def test_extract_tags_with_empty_title() -> None:
    soup: BeautifulSoup = BeautifulSoup(
        "<html><head><title></title></head><body></body></html>", "html.parser"
    )
    title, desc, canon = Sitemap._extract_tags(soup)
    assert title == ""
    assert desc == ""
    assert canon == ""


def test_process_incoming_links_builds_reverse_map() -> None:
    sitemap: Sitemap = Sitemap("https://example.com", max_depth=0)
    sitemap.internal_links = {
        "https://example.com": ["https://example.com/page1"],
        "https://example.com/page1": ["https://example.com/page2"],
        "https://example.com/page2": [],
    }
    sitemap._process_incoming_links()

    incoming = sitemap.incoming_links
    assert incoming["https://example.com/page1"] == ["https://example.com"]
    assert incoming["https://example.com/page2"] == ["https://example.com/page1"]
    assert incoming["https://example.com"] == []


def test_extract_links_skips_already_visited() -> None:
    sitemap: Sitemap = Sitemap("https://example.com", max_depth=1)
    visited: Set[str] = {"https://example.com"}
    sitemap._extract_links("https://example.com", visited=visited)


def test_process_page_a_tags_skips_non_tag() -> None:
    soup: BeautifulSoup = BeautifulSoup(
        "<html><body><!-- comment --></body></html>", "html.parser"
    )
    sitemap: Sitemap = Sitemap("https://example.com", max_depth=1)
    sitemap._process_page_a_tags("https://example.com", soup)
    assert sitemap.internal_links["https://example.com"] == []


def test_process_page_a_tags_skips_non_tag_instance() -> None:
    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    sitemap = Sitemap("https://example.com", max_depth=1)

    with patch.object(soup, "find_all", return_value=["not-a-tag"]):
        sitemap._process_page_a_tags("https://example.com", soup)

    assert sitemap.internal_links["https://example.com"] == []
