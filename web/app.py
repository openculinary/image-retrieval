from os import path

from flask import Flask, abort
import requests


def request_patch(self, *args, **kwargs):
    kwargs['proxies'] = kwargs.pop('proxies', {
        'http': 'http://proxy:3128',
        'https': 'http://proxy:3128',
    })
    kwargs['timeout'] = kwargs.pop('timeout', 5)
    kwargs['verify'] = kwargs.pop('verify', '/etc/ssl/k8s/proxy-cert/ca.crt')
    return self.request_orig(*args, **kwargs)


setattr(
    requests.sessions.Session, 'request_orig',
    requests.sessions.Session.request
)
requests.sessions.Session.request = request_patch


app = Flask(__name__)

with open('web/data/empty.ico', 'rb') as f:
    empty_icon = f.read()


@app.route('/domains/<image_filename>')
def domain(image_filename):
    domain, extension = path.splitext(image_filename)

    recipe = requests.get(
        url=f'http://backend-service/domains/{domain}',
        proxies={}
    )
    try:
        recipe.raise_for_status()
    except Exception:
        return abort(404)

    image_src = recipe.json().get('image_src')
    image_src = image_src or f'https://{domain}/favicon.ico'
    image = requests.get(
        url=f'http://imageproxy/{image_src}',
        proxies={}
    )

    try:
        image.raise_for_status()
    except Exception:
        return empty_icon, 200, {'Content-Type': 'image/x-icon'}

    return image.content, 200, {'Content-Type': image.headers['Content-Type']}


@app.route('/recipes/<image_filename>')
def recipe(image_filename):
    recipe_id, extension = path.splitext(image_filename)

    recipe = requests.get(
        url=f'http://backend-service/recipes/{recipe_id}',
        proxies={}
    )
    try:
        recipe.raise_for_status()
    except Exception:
        return abort(404)

    image_src = recipe.json().get('image_src')
    image = requests.get(
        url=f'http://imageproxy/192,png/{image_src}',
        proxies={}
    )

    try:
        image.raise_for_status()
    except Exception:
        return abort(404)

    return image.content, 200, {'Content-Type': image.headers['Content-Type']}
