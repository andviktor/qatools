import json
from flask import Flask, render_template, request, Response
from typing import Optional, Union, Any

from app.modules.sitemap.sitemap import Sitemap
from app.modules.sitemap.jstree_formatter import sitemap_to_jstree_formatter
from app.modules.meta_tags.meta_tags_request import get_meta_tags_request
from app.modules.meta_tags.meta_tags_selenium import get_meta_tags_selenium

app: Flask = Flask(__name__)


@app.context_processor
def inject_defaults() -> dict[str, str]:
    return {"site_name": "QA-Tools"}


@app.route("/", methods=["GET"])
def sitemap() -> Union[str, Response]:
    page_meta_title: str = "Sitemap"

    url: Optional[str] = request.args.get("url")
    exclude_substrings_raw: Optional[str] = request.args.get("exclude_substrings")
    exclude_substrings: list[str] = (
        [
            substring
            for substring in exclude_substrings_raw.replace("\r", "")
            .replace(" ", "")
            .split("\n")
            if substring
        ]
        if exclude_substrings_raw
        else []
    )
    depth: int = request.args.get("depth", type=int, default=0)

    if url:
        sitemap: Sitemap = Sitemap(
            url, max_depth=depth, exclude_substrings=exclude_substrings
        )
        sitemap.collect()
        sitemap_data: dict[str, Any] = sitemap.get()
        sitemap_jstree = sitemap_to_jstree_formatter(sitemap_data)

        return render_template(
            "pages/sitemap.html",
            page_meta_title=page_meta_title,
            url=url,
            depth=depth,
            sitemap=sitemap_jstree,
            metadata_json=json.dumps(sitemap_data.get("metadata", {})),
            incoming_links=json.dumps(sitemap_data.get("incoming", {})),
            exclude_substrings=exclude_substrings,
        )

    return render_template(
        "pages/sitemap.html",
        page_meta_title=page_meta_title,
        depth=depth,
        exclude_substrings=exclude_substrings,
    )


@app.route("/meta-tags", methods=["GET", "POST"])
def meta_tags() -> Union[str, Response]:
    page_meta_title: str = "Meta tags"

    meta_tags: Optional[dict[str, dict[str, str]]] = None
    urls_raw: Optional[str] = request.form.get("urls")
    urls: list[str] = (
        [url for url in urls_raw.replace("\r", "").replace(" ", "").split("\n") if url]
        if urls_raw
        else []
    )
    enable_selenium: bool = "enable-selenium" in request.form
    if urls:
        get_page_meta_tags = (
            get_meta_tags_selenium if enable_selenium else get_meta_tags_request
        )
        meta_tags = get_page_meta_tags(urls)

    return render_template(
        "pages/meta_tags.html",
        page_meta_title=page_meta_title,
        urls=urls,
        meta_tags=meta_tags,
    )
