import requests
from bs4 import BeautifulSoup
from typing import List, Dict


def get_page_titles_request(urls: List[str]) -> Dict[str, str] | None:
    if not urls:
        return None

    titles = {}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("title")
            titles[url] = (
                title_tag.string.strip()  # type: ignore
                if title_tag and title_tag.string  # type: ignore
                else "No title found"
            )
        except Exception as e:
            titles[url] = f"Error: {str(e)}"

    return titles
