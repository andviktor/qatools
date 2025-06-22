import json
from flask import Flask, render_template, request, Response
from typing import Optional, Union, Any

from modules.sitemap.sitemap import Sitemap
from modules.sitemap.jstree_formatter import sitemap_to_jstree_formatter

app: Flask = Flask(__name__)


@app.route("/", methods=["GET"])
def index() -> Union[str, Response]:
    url: Optional[str] = request.args.get("url")
    depth: int = request.args.get("depth", type=int, default=0)

    if url:
        sitemap = Sitemap("https://normafahotel.hu/", max_depth=depth)
        sitemap.collect()
        sitemap_data: dict[str, Any] = sitemap.get()
        sitemap_jstree = sitemap_to_jstree_formatter(sitemap_data)

        return render_template(
            "index.html",
            url=url,
            depth=depth,
            sitemap=sitemap_jstree,
            metadata_json=json.dumps(sitemap_data.get("metadata", {})),
            incoming_links=json.dumps(sitemap_data.get("incoming", {})),
        )

    return render_template("index.html", depth=depth)
