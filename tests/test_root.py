from os import path
import pytest
import responses


API_URL = 'http://backend-service'
IMAGEPROXY_URL = 'http://imageproxy'


@pytest.fixture
def recipe_responses(image_path):
    image_filename = path.basename(image_path)
    recipe_id, extension = path.splitext(image_filename)

    metadata_uri = f'{API_URL}/recipes/{recipe_id}'
    image_uri = 'http://example.org/image.png'
    proxy_uri = f'{IMAGEPROXY_URL}/192,png/{image_uri}'

    data = b'not_an_image'
    mime_type = 'image/png'

    responses.add(responses.GET, metadata_uri, json={'image_src': image_uri})
    responses.add(responses.GET, proxy_uri, body=data, content_type=mime_type)


@responses.activate
@pytest.mark.parametrize('image_path', ['image.png'])
def test_recipe_request(client, image_path, recipe_responses):
    response = client.get(f'/recipes/{image_path}')

    assert response.status_code == 200
    assert response.data is not None
    assert response.headers['Content-Type'] == 'image/png'
