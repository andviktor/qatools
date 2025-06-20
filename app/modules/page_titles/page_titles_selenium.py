from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict

def get_page_titles_selenium(urls: List[str]) -> Dict[str, str] | None:
    if not urls:
        return None

    titles: Dict[str, str] = {}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    for url in urls:
        if not url:
            continue

        if not url.startswith("http"):
            titles[url] = "Error: URL must start with http or https"
            continue

        try:
            driver.get(url)
            titles[url] = driver.title or "No title found"
        except Exception as e:
            titles[url] = f"Error: {str(e)}"

    driver.quit()
    return titles