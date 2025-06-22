from typing import List, Set, Dict, Any, Tuple, Deque
from collections import deque, defaultdict


def sitemap_to_jstree_formatter(sitemap: Dict[str, Any]) -> List[Dict[str, Any]]:
    links_per_page: Dict[str, List[str]] = sitemap.get("internal", {})
    response_status: Dict[str, Dict[str, Any]] = sitemap.get("response", {})
    external_links: List[str] = sitemap.get("external", [])
    root_url: str | None = sitemap.get("root")

    if not root_url:
        return []

    nodes: List[Dict[str, Any]] = []
    seen_node_ids: Set[str] = set()
    url_min_depth: Dict[str, int] = defaultdict(lambda: float("inf"))  # type: ignore

    queue: Deque[Tuple[str, int]] = deque([(root_url, 0)])
    while queue:
        current, depth = queue.popleft()
        if depth < url_min_depth[current]:
            url_min_depth[current] = depth
            for child in links_per_page.get(current, []):
                queue.append((child, depth + 1))

    def add_node(node_id: str, parent_id: str, text: str, icon: str) -> str:
        unique_id: str = f"{parent_id}>{node_id}" if parent_id != "#" else node_id
        if unique_id not in seen_node_ids:
            seen_node_ids.add(unique_id)
            node_data = {
                "id": unique_id,
                "parent": parent_id,
                "text": text,
                "icon": icon,
            }
            if node_id in response_status and "status" in response_status[node_id]:
                node_data["status"] = response_status[node_id]["status"]
            nodes.append(node_data)
        return unique_id

    def recurse(current_url: str, parent_id: str = "#", depth: int = 0) -> None:
        raw_children: List[str] = links_per_page.get(current_url, [])
        visible_children: List[str] = [
            child for child in raw_children if url_min_depth[child] == depth + 1
        ]

        visible_children.sort(key=lambda u: u.lower())

        icon: str = "fa fa-folder" if visible_children else "fa-regular fa-file"
        node_uid: str = add_node(current_url, parent_id, current_url, icon)

        for child in visible_children:
            recurse(child, node_uid, depth + 1)

    recurse(root_url)

    if external_links:
        external_root: str = "__external__"
        add_node(external_root, "#", "External Links", "fa fa-folder")
        for ext in sorted(external_links, key=lambda x: x.lower()):
            add_node(ext, external_root, ext, "fa fa-link")

    return nodes
