from flask import Flask, render_template, request, Response
from typing import Optional, Union, Any

from modules.sitemap.sitemap import extract_internal_links, format_sitemap_for_jstree

app: Flask = Flask(__name__)


@app.route("/", methods=["GET"])
def index() -> Union[str, Response]:
    url: Optional[str] = request.args.get("url")
    depth: int = request.args.get("depth", type=int, default=100)
    sitemap: Optional[Union[list[dict], str]] = None  # type: ignore

    if url:
        try:
            sitemap_data: dict[str, Any] = extract_internal_links(url, max_depth=depth)
            sitemap = format_sitemap_for_jstree(sitemap_data)
        except Exception as e:
            sitemap = f"An error occurred: {e}"
        return render_template("index.html", url=url, depth=depth, sitemap=sitemap)

    return render_template("index.html")
