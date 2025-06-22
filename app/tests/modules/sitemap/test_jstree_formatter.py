from typing import Any, Dict, List
from app.modules.sitemap.jstree_formatter import sitemap_to_jstree_formatter


def test_empty_root_returns_empty_list() -> None:
    sitemap: Dict[str, Any] = {
        "root": None,
        "internal": {},
        "external": [],
        "response": {},
    }
    assert sitemap_to_jstree_formatter(sitemap) == []


def test_root_with_no_children() -> None:
    sitemap: Dict[str, Any] = {
        "root": "https://example.com",
        "internal": {"https://example.com": []},
        "external": [],
        "response": {},
    }
    result: List[Dict[str, Any]] = sitemap_to_jstree_formatter(sitemap)
    assert len(result) == 1
    assert result[0]["id"] == "https://example.com"
    assert result[0]["parent"] == "#"
    assert result[0]["icon"] == "fa-regular fa-file"


def test_internal_links_hierarchy() -> None:
    sitemap: Dict[str, Any] = {
        "root": "https://example.com",
        "internal": {
            "https://example.com": ["https://example.com/about"],
            "https://example.com/about": ["https://example.com/team"],
            "https://example.com/team": [],
        },
        "external": [],
        "response": {},
    }
    result: List[Dict[str, Any]] = sitemap_to_jstree_formatter(sitemap)
    ids = [node["id"] for node in result]
    assert "https://example.com" in ids
    assert "https://example.com>https://example.com/about" in ids
    assert (
        "https://example.com>https://example.com/about>https://example.com/team" in ids
    )
    assert all("status" not in node for node in result)


def test_response_status_included() -> None:
    sitemap: Dict[str, Any] = {
        "root": "https://example.com",
        "internal": {
            "https://example.com": [],
        },
        "external": [],
        "response": {"https://example.com": {"status": 404}},
    }
    result: List[Dict[str, Any]] = sitemap_to_jstree_formatter(sitemap)
    assert result[0]["status"] == 404


def test_external_links_added() -> None:
    sitemap: Dict[str, Any] = {
        "root": "https://example.com",
        "internal": {"https://example.com": []},
        "external": ["https://external.com", "https://z.com"],
        "response": {},
    }
    result: List[Dict[str, Any]] = sitemap_to_jstree_formatter(sitemap)
    external_ids = [node["id"] for node in result if node["parent"] == "__external__"]
    assert "__external__" in [node["id"] for node in result]
    assert sorted(external_ids) == [
        "__external__>https://external.com",
        "__external__>https://z.com",
    ]
