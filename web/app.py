from os import path

from flask import Flask, abort
import requests


app = Flask(__name__)


@app.route('/recipes/<image_filename>')
def recipe(image_filename):
    recipe_id, extension = path.splitext(image_filename)

    recipe = requests.get(f'http://api-service/api/recipes/{recipe_id}')
    try:
        recipe.raise_for_status()
    except Exception:
        return abort(404)

    image_src = recipe.json().get('image_src')
    image = requests.get(f'http://imageproxy/192,png/{image_src}')
    try:
        image.raise_for_status()
    except Exception:
        return abort(404)

    return image.content, 200, {'Content-Type': image.headers['Content-Type']}
