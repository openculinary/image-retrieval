from os import path

from flask import Flask, abort
import requests


def request_patch(self, *args, **kwargs):
    kwargs['proxies'] = {
        'http': 'http://proxy:3128',
        'https': 'http://proxy:3443',
    }
    kwargs['timeout'] = kwargs.pop('timeout', 5)
    kwargs['verify'] = '/etc/ssl/k8s/proxy-cert/ca.crt'
    return self.request_orig(*args, **kwargs)


setattr(
    requests.sessions.Session, 'request_orig',
    requests.sessions.Session.request
)
requests.sessions.Session.request = request_patch


app = Flask(__name__)


@app.route('/<path:recipe_path>')
def root(recipe_path):
    recipe_id = path.basename(recipe_path)
    recipe = requests.get(f'http://api-service/api/recipes/{recipe_id}/view')

    try:
        recipe.raise_for_status()
    except Exception:
        return abort(404)

    image_src = recipe.json().get('image_src')
    image = requests.get(image_src)

    try:
        image.raise_for_status()
    except Exception:
        return abort(404)

    return image.content
