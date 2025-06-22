import requests
from bs4 import BeautifulSoup
from typing import Any, List, Dict, Optional


def get_meta_tags_request(urls: List[str]) -> Optional[Dict[str, Dict[str, str]]]:
    if not urls:
        return None

    meta_data: Dict[str, Dict[str, str]] = {}

    headers: Dict[str, str] = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    for url in urls:
        try:
            response: requests.Response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup: BeautifulSoup = BeautifulSoup(response.text, "html.parser")

            title_tag: Any = soup.find("title")
            description_tag: Any = soup.find("meta", attrs={"name": "description"})

            title: str = (
                title_tag.string.strip() if title_tag and title_tag.string else ""
            )
            description: str = (
                description_tag["content"].strip()
                if description_tag and "content" in description_tag.attrs
                else ""
            )

            meta_data[url] = {"title": title, "description": description}

        except Exception as e:
            error: str = f"Error: {str(e)}"
            meta_data[url] = {"title": error, "description": error}

    return meta_data
