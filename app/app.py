import json
from flask import Flask, render_template, request, Response
from typing import Optional, Union, Any

from app.modules.sitemap.sitemap import Sitemap
from app.modules.sitemap.jstree_formatter import sitemap_to_jstree_formatter
from app.modules.page_titles.page_titles_request import get_page_titles_request
from app.modules.page_titles.page_titles_selenium import get_page_titles_selenium

app: Flask = Flask(__name__)


@app.context_processor
def inject_defaults():
    return {
        "site_name": "QA-Tools"
    }


@app.route("/", methods=["GET"])
def sitemap() -> Union[str, Response]:
    meta_title: str = "Sitemap"
    url: Optional[str] = request.args.get("url")
    depth: int = request.args.get("depth", type=int, default=0)

    if url:
        sitemap = Sitemap("https://normafahotel.hu/", max_depth=depth)
        sitemap.collect()
        sitemap_data: dict[str, Any] = sitemap.get()
        sitemap_jstree = sitemap_to_jstree_formatter(sitemap_data)

        return render_template(
            "pages/sitemap.html",
            meta_title=meta_title,
            url=url,
            depth=depth,
            sitemap=sitemap_jstree,
            metadata_json=json.dumps(sitemap_data.get("metadata", {})),
            incoming_links=json.dumps(sitemap_data.get("incoming", {})),
        )

    return render_template("pages/sitemap.html", meta_title=meta_title, depth=depth)


@app.route("/page-titles", methods=["GET", "POST"])
def page_titles() -> Union[str, Response]:
    meta_title: str = "Titles"
    titles: Optional[dict[str, str]] = None
    urls: Optional[list[str]] = request.form.get("urls")
    enable_selenium: bool = "enable-selenium" in request.form
    if urls:
        urls = [url for url in urls.replace("\r", "").replace(" ", "").split("\n") if url]
        get_page_titles = get_page_titles_selenium if enable_selenium else get_page_titles_request
        titles = get_page_titles(urls)
    
    return render_template("pages/page_titles.html", meta_title=meta_title, urls=urls, titles=titles)
