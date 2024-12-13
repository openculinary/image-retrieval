import pytest
import respx

from web.app import app


@pytest.fixture
def client():
    return app.test_client()


@pytest.fixture()
def respx_mock(request):
    """Workaround: override the default plugin router"""
    with respx.mock(using="httpx", assert_all_called=False) as respx_mock:
        yield respx_mock
