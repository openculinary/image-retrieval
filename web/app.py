from os import path
import ssl

from flask import Flask, abort
import httpx


def get_tls_context():
    context = ssl.create_default_context(cafile="/etc/ssl/k8s/proxy-cert/ca.crt")
    while True:
        yield context


def request_patch(self, *args, **kwargs):
    kwargs["proxy"] = kwargs.pop("proxy", "http://proxy:3128")
    kwargs["timeout"] = kwargs.pop("timeout", 5)
    kwargs["verify"] = kwargs.pop("verify", get_tls_context())
    return self.request_orig(*args, **kwargs)


setattr(httpx, "request_orig", httpx.request)
httpx.request = request_patch


app = Flask(__name__)

with open("web/data/empty.ico", "rb") as f:
    empty_icon = f.read()


@app.route("/domains/<image_filename>")
def domain(image_filename):
    domain, extension = path.splitext(image_filename)
    try:
        response = httpx.get(f"http://backend-service/domains/{domain}", proxy=None)
        response.raise_for_status()
    except Exception:
        return abort(404)

    domain_info = response.json()
    if not domain_info.get("image_enabled"):
        return empty_icon, 200, {"Content-Type": "image/x-icon"}

    image_src = domain_info.get("image_src")
    image_src = image_src or f"https://{domain}/favicon.ico"
    try:
        image = httpx.get(url=f"http://imageproxy/{image_src}", proxy=None)
        image.raise_for_status()
    except Exception:
        return empty_icon, 200, {"Content-Type": "image/x-icon"}

    return image.content, 200, {"Content-Type": image.headers["Content-Type"]}


with open("web/data/empty.png", "rb") as f:
    empty_image = f.read()


@app.route("/recipes/<image_filename>")
def recipe(image_filename):
    recipe_id, extension = path.splitext(image_filename)
    try:
        response = httpx.get(f"http://backend-service/recipes/{recipe_id}", proxy=None)
        response.raise_for_status()
    except Exception:
        return abort(404)

    recipe = response.json()
    if not recipe.get("image_enabled"):
        return empty_image, 200, {"Content-Type": "image/png"}

    image_src = recipe.get("image_src")
    try:
        image = httpx.get(f"http://imageproxy/192,png/{image_src}", proxy=None)
        image.raise_for_status()
    except Exception:
        return abort(404)

    return image.content, 200, {"Content-Type": image.headers["Content-Type"]}
