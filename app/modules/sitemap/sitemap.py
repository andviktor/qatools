from requests import get, Response, RequestException
from bs4 import BeautifulSoup, Tag
from urllib.parse import urlparse, urljoin, ParseResult
from typing import List, Set, Dict, Any
from typing import Optional
from logging import getLogger, Logger

logger: Logger = getLogger(__name__)


class Sitemap:
    def __init__(self, root: str, max_depth: int) -> None:
        self.root: str = Sitemap._normalize_url(root)
        self.max_depth: int = max_depth
        self.internal_links: Dict[str, List[str]] = {}
        self.external_links: Set[str] = set()
        self.metadata: Dict[str, Dict[str, str]] = {}
        self.incoming_links: Dict[str, List[str]] = {}
        self.response_data: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _normalize_url(url: str) -> str:
        return url.rstrip("/") if url != "/" else url

    def _request_get(self, url: str) -> Optional[Response]:
        try:
            response: Response = get(url, timeout=10)
            response.raise_for_status()
        except RequestException as e:
            status = getattr(e.response, "status_code", None)
            self.response_data[url] = {
                "status": status,
            }
            return None
        return response

    @staticmethod
    def _extract_tags(soup: BeautifulSoup) -> tuple[str, str, str]:
        title: str = (
            soup.title.string.strip() if soup.title and soup.title.string else ""
        )
        description_tag: Any = soup.find("meta", attrs={"name": "description"})
        description: str = (
            description_tag["content"].strip()
            if description_tag and "content" in description_tag.attrs
            else ""
        )
        canonical_tag: Any = soup.find("link", rel="canonical")
        canonical: str = (
            canonical_tag["href"].strip()
            if canonical_tag and "href" in canonical_tag.attrs
            else ""
        )
        return title, description, canonical

    def _process_page_a_tags(self, url: str, soup: BeautifulSoup) -> None:
        normalized_url: str = Sitemap._normalize_url(url)
        parsed_url: ParseResult = urlparse(url)
        base_url: str = f"{parsed_url.scheme}://{parsed_url.netloc}"
        page_links: List[str] = []

        for a_tag in soup.find_all("a", href=True):
            if not isinstance(a_tag, Tag):
                continue

            href: str = str(a_tag["href"])
            full_url: str = urljoin(base_url, href)
            clean_url: str = Sitemap._normalize_url(full_url.split("#")[0])
            parsed_href = urlparse(clean_url)

            if parsed_href.netloc == parsed_url.netloc:
                if clean_url != normalized_url and clean_url not in page_links:
                    page_links.append(clean_url)
            else:
                self.external_links.add(clean_url)

                if clean_url not in self.incoming_links:
                    self.incoming_links[clean_url] = []

                if normalized_url not in self.incoming_links[clean_url]:
                    self.incoming_links[clean_url].append(normalized_url)

        self.internal_links[normalized_url] = page_links

    def _extract_links(
        self,
        url: str,
        visited: Optional[Set[str]] = None,
        current_depth: int = 0,
    ) -> None:
        if visited is None:
            visited = set()

        normalized_url: str = Sitemap._normalize_url(url)
        if normalized_url in visited:
            return

        visited.add(normalized_url)

        response: Optional[Response] = self._request_get(url)
        if not response:
            return

        soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

        self._process_page_a_tags(url, soup)

        title, description, canonical = Sitemap._extract_tags(soup)

        self.metadata[normalized_url] = {
            "title": title,
            "description": description,
            "canonical": canonical,
        }

        if current_depth < self.max_depth:
            for link in self.internal_links[normalized_url]:
                self._extract_links(
                    link,
                    visited=visited,
                    current_depth=current_depth + 1,
                )

    def _process_incoming_links(self) -> None:
        for parent_url, children in self.internal_links.items():
            for child_url in children:
                if child_url not in self.incoming_links:
                    self.incoming_links[child_url] = []
                self.incoming_links[child_url].append(parent_url)

        for url in self.internal_links:
            if url not in self.incoming_links:
                self.incoming_links[url] = []

    def collect(self) -> None:
        self._extract_links(self.root)
        self._process_incoming_links()

    def get(self) -> Dict[str, Any]:
        return {
            "root": self.root,
            "internal": self.internal_links,
            "external": self.external_links,
            "metadata": self.metadata,
            "incoming": self.incoming_links,
            "response": self.response_data,
        }
