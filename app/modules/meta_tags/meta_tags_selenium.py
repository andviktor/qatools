from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import List, Dict, Optional


def get_meta_tags_selenium(urls: List[str]) -> Optional[Dict[str, Dict[str, str]]]:
    if not urls:
        return None

    meta_data: Dict[str, Dict[str, str]] = {}

    options: Options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service: Service = Service(executable_path="/usr/bin/chromedriver")
    driver: WebDriver = webdriver.Chrome(service=service, options=options)

    for url in urls:
        if not url or not url.startswith("http"):
            meta_data[url] = {
                "title": "Error: URL must start with http or https",
                "description": "Error: URL must start with http or https",
            }
            continue

        try:
            driver.get(url)
            title: str = driver.title or ""

            try:
                description_element: WebElement = driver.find_element(
                    By.XPATH, "//meta[@name='description']"
                )
                description: str = description_element.get_attribute("content") or ""
                description = description.strip()
            except Exception:
                description = ""

            meta_data[url] = {"title": title, "description": description}

        except Exception as e:
            error_message: str = f"Error: {str(e)}"
            meta_data[url] = {"title": error_message, "description": error_message}

    driver.quit()
    return meta_data
