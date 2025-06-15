import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse, urljoin
from typing import List, Set, Dict, Any, Tuple, Deque
from collections import deque, defaultdict

import requests
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse, urljoin
from typing import List, Set, Dict, Any, Optional

def normalize_url(url: str) -> str:
    return url.rstrip("/") if url != "/" else url

def extract_internal_links(
    url: str,
    visited: Set[str] | None = None,
    max_depth: int = 100,
    current_depth: int = 0,
    external_links: Set[str] | None = None,
    links_per_page: Dict[str, List[str]] | None = None,
    metadata: Optional[Dict[str, Dict[str, str]]] = None,
) -> Dict[str, Any]:
    if visited is None:
        visited = set()
    if external_links is None:
        external_links = set()
    if links_per_page is None:
        links_per_page = {}
    if metadata is None:
        metadata = {}

    normalized_url: str = normalize_url(url)
    if normalized_url in visited or current_depth > max_depth:
        return {}

    visited.add(normalized_url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return {}

    soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")
    parsed_root = urlparse(url)
    base_url: str = f"{parsed_root.scheme}://{parsed_root.netloc}"

    internal_links: List[str] = []
    for a_tag in soup.find_all("a", href=True):
        if not isinstance(a_tag, Tag):
            continue

        href: str = a_tag["href"]  # type: ignore
        full_url: str = urljoin(base_url, href)
        clean_url: str = normalize_url(full_url.split("#")[0])
        parsed_href = urlparse(clean_url)

        if parsed_href.netloc == parsed_root.netloc:
            if clean_url not in visited and clean_url not in internal_links:
                internal_links.append(clean_url)
        else:
            external_links.add(clean_url)

    links_per_page[normalized_url] = internal_links

    title: str = soup.title.string.strip() if soup.title and soup.title.string else ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    description: str = description_tag["content"].strip() if description_tag and "content" in description_tag.attrs else ""

    metadata[normalized_url] = {
        "title": title,
        "description": description
    }

    for link in internal_links:
        extract_internal_links(
            link,
            visited=visited,
            max_depth=max_depth,
            current_depth=current_depth + 1,
            external_links=external_links,
            links_per_page=links_per_page,
            metadata=metadata,
        )

    if current_depth == 0:
        return {
            "internal": links_per_page,
            "external": sorted(external_links),
            "metadata": metadata
        }

    return {}


def format_sitemap_for_jstree(sitemap: Dict[str, Any]) -> List[Dict[str, Any]]:
    links_per_page: Dict[str, List[str]] = sitemap.get("internal", {})
    external_links: List[str] = sitemap.get("external", [])

    nodes: List[Dict[str, Any]] = []
    seen_node_ids: Set[str] = set()
    url_min_depth: Dict[str, int] = defaultdict(lambda: float("inf"))  # type: ignore

    all_children: Set[str] = {
        child for children in links_per_page.values() for child in children
    }
    root_nodes: List[str] = [url for url in links_per_page if url not in all_children]

    queue: Deque[Tuple[str, int]] = deque([(root, 0) for root in root_nodes])
    while queue:
        current, depth = queue.popleft()
        if depth < url_min_depth[current]:
            url_min_depth[current] = depth
            for child in links_per_page.get(current, []):
                queue.append((child, depth + 1))

    seen_urls: Set[str] = set()

    def add_node(node_id: str, parent_id: str, text: str, icon: str) -> str:
        unique_id: str = f"{parent_id}>{node_id}" if parent_id != "#" else node_id
        if unique_id not in seen_node_ids:
            seen_node_ids.add(unique_id)
            nodes.append(
                {"id": unique_id, "parent": parent_id, "text": text, "icon": icon}
            )
        return unique_id

    def recurse(current_url: str, parent_id: str = "#", depth: int = 0) -> None:
        if depth > url_min_depth[current_url] or current_url in seen_urls:
            return
        seen_urls.add(current_url)

        raw_children: List[str] = links_per_page.get(current_url, [])
        visible_children: List[str] = [
            child
            for child in raw_children
            if url_min_depth[child] == depth + 1 and child not in seen_urls
        ]

        visible_children.sort(key=lambda u: u.lower())

        icon: str = "fa fa-folder" if visible_children else "fa-regular fa-file"
        node_uid: str = add_node(current_url, parent_id, current_url, icon)

        for child in visible_children:
            recurse(child, node_uid, depth + 1)

    for root in sorted(root_nodes, key=lambda u: u.lower()):
        recurse(root)

    if external_links:
        external_root: str = "__external__"
        add_node(external_root, "#", "External Links", "fa fa-folder")
        for ext in sorted(external_links, key=lambda x: x.lower()):
            add_node(ext, external_root, ext, "fa fa-link")

    return nodes
