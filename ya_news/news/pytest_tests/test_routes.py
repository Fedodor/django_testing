import pytest
from pytest_django.asserts import assertRedirects

from http import HTTPStatus

pytestmark = pytest.mark.django_db

CLIENT = pytest.lazy_fixture('client')
AUTHOR = pytest.lazy_fixture('author_client')
ADMIN = pytest.lazy_fixture('admin_client')

URL_HOME_PAGE = pytest.lazy_fixture('url_home_page')
URL_USER_LOGIN = pytest.lazy_fixture('url_user_login')
URL_USER_LOGOUT = pytest.lazy_fixture('url_user_logout')
URL_USER_SIGNUP = pytest.lazy_fixture('url_user_signup')
URL_EDIT_COMMENT = pytest.lazy_fixture('url_edit_comment')
URL_DELETE_COMMENT = pytest.lazy_fixture('url_delete_comment')

EXPECTED_EDIT_URL = pytest.lazy_fixture('expected_edit_url')
EXPECTED_DELETE_URL = pytest.lazy_fixture('expected_delete_url')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (URL_HOME_PAGE, CLIENT, HTTPStatus.OK),
        (URL_USER_LOGIN, CLIENT, HTTPStatus.OK),
        (URL_USER_LOGOUT, CLIENT, HTTPStatus.OK),
        (URL_USER_SIGNUP, CLIENT, HTTPStatus.OK),
        (URL_EDIT_COMMENT, AUTHOR, HTTPStatus.OK),
        (URL_DELETE_COMMENT, AUTHOR, HTTPStatus.OK),
        (URL_EDIT_COMMENT, ADMIN, HTTPStatus.NOT_FOUND),
        (URL_DELETE_COMMENT, ADMIN, HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability_for_all_users(
        url, parametrized_client, expected_status
):
    assert parametrized_client.get(url).status_code == expected_status


@pytest.mark.parametrize(
    'url, expected_url',
    (
        (URL_EDIT_COMMENT, EXPECTED_EDIT_URL),
        (URL_DELETE_COMMENT, EXPECTED_DELETE_URL),
    )
)
def test_redirect_for_anonymous_client(
    client, url, expected_url
):
    assertRedirects(client.get(url), expected_url)
