from os import path
import pytest


API_URL = "http://backend-service"
IMAGEPROXY_URL = "http://imageproxy"


def domain_responses(image_path, respx_mock, **response_data):
    image_filename = path.basename(image_path)
    domain, extension = path.splitext(image_filename)

    metadata_uri = f"{API_URL}/domains/{domain}"
    proxy_uri = f"{IMAGEPROXY_URL}/https://{domain}/favicon.ico"

    data = b"not_an_image"
    mime_type = "image/x-icon"

    response = {"image_src": None}
    response.update(response_data)

    respx_mock.get(metadata_uri).respond(json=response)
    respx_mock.get(proxy_uri).respond(content=data, headers={"Content-Type": mime_type})


@pytest.fixture
@pytest.mark.respx
def domain_responses_enabled(image_path, respx_mock):
    return domain_responses(image_path, respx_mock, enabled=True)


@pytest.mark.parametrize("image_path", ["example.com.ico"])
def test_domain_request(client, image_path, domain_responses_enabled):
    response = client.get(f"/domains/{image_path}")

    assert response.status_code == 200
    assert response.data is not None
    assert response.headers["Content-Type"] == "image/x-icon"


def recipe_responses(image_path, respx_mock, **response_data):
    image_filename = path.basename(image_path)
    recipe_id, extension = path.splitext(image_filename)

    metadata_uri = f"{API_URL}/recipes/{recipe_id}"
    image_uri = "http://example.org/image.png"
    proxy_uri = f"{IMAGEPROXY_URL}/192,png/{image_uri}"

    data = b"not_an_image"
    mime_type = "image/png"

    response = {"image_src": image_uri}
    response.update(response_data)

    respx_mock.get(metadata_uri).respond(json=response)
    respx_mock.get(proxy_uri).respond(content=data, headers={"Content-Type": mime_type})


@pytest.fixture
@pytest.mark.respx
def recipe_responses_enabled(image_path, respx_mock):
    return recipe_responses(image_path, respx_mock, enabled=True)


@pytest.mark.parametrize("image_path", ["image.png"])
def test_recipe_request(client, image_path, recipe_responses_enabled):
    response = client.get(f"/recipes/{image_path}")

    assert response.status_code == 200
    assert response.data is not None
    assert response.headers["Content-Type"] == "image/png"
