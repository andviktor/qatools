from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Dict, Optional


def get_meta_tags_selenium(urls: List[str]) -> Optional[Dict[str, Dict[str, str]]]:
    if not urls:
        return None

    meta_data: Dict[str, Dict[str, str]] = {}

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
            meta_data[url] = {
                "title": "Error: URL must start with http or https",
                "description": "Error: URL must start with http or https",
            }
            continue

        try:
            driver.get(url)

            title = driver.title or ""
            try:
                description = driver.find_element(
                    By.XPATH, "//meta[@name='description']"
                ).get_attribute("content")
                description = description.strip() if description else ""
            except Exception:
                description = ""

            meta_data[url] = {"title": title, "description": description}

        except Exception as e:
            error_message = f"Error: {str(e)}"
            meta_data[url] = {"title": error_message, "description": error_message}

    driver.quit()
    return meta_data
