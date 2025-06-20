from flask import Flask, render_template, request, Response
from typing import Optional, Union, Any

from app.modules.sitemap.sitemap import extract_internal_links, format_sitemap_for_jstree
from app.modules.page_titles.page_titles_request import get_page_titles_request
from app.modules.page_titles.page_titles_selenium import get_page_titles_selenium

app = Flask(__name__)


@app.route("/", methods=["GET"])
def sitemap() -> Union[str, Response]:
    url: Optional[str] = request.args.get("url")
    depth: int = request.args.get("depth", type=int, default=100)
    sitemap: Optional[Union[list[dict], str]] = None  # type: ignore

    if url:
        try:
            sitemap_data: dict[str, Any] = extract_internal_links(url, max_depth=depth)
            sitemap = format_sitemap_for_jstree(sitemap_data)
        except Exception as e:
            sitemap = f"An error occurred: {e}"
        return render_template("pages/sitemap.html", url=url, depth=depth, sitemap=sitemap)

    return render_template("pages/sitemap.html")


@app.route("/page-titles", methods=["GET", "POST"])
def page_titles() -> Union[str, Response]:
    titles: Optional[dict[str, str]] = None
    urls: Optional[list[str]] = request.form.get("urls")
    enable_selenium: bool = "enable-selenium" in request.form
    if urls:
        urls = [url for url in urls.replace("\r", "").replace(" ", "").split("\n") if url]
        get_page_titles = get_page_titles_selenium if enable_selenium else get_page_titles_request
        titles = get_page_titles(urls)
    
    return render_template("pages/page_titles.html", urls=urls, titles=titles)
