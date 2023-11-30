import pytest
from pytest_django.asserts import assertRedirects
# from pytest_lazyfixture import lazy_fixture

from http import HTTPStatus

# from django.urls import reverse

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


def test_pages_availability_for_all_users(
        url_home_page, url_user_login, url_user_logout,
        url_user_signup, url_edit_comment, url_delete_comment,
        client, author_client, admin_client
):
    cases = (
        (url_home_page, client, HTTPStatus.OK),
        (url_user_login, client, HTTPStatus.OK),
        (url_user_logout, client, HTTPStatus.OK),
        (url_user_signup, client, HTTPStatus.OK),
        (url_edit_comment, author_client, HTTPStatus.OK),
        (url_delete_comment, author_client, HTTPStatus.OK),
        (url_edit_comment, admin_client, HTTPStatus.NOT_FOUND),
        (url_delete_comment, admin_client, HTTPStatus.NOT_FOUND),
    )
    for url, some_user, expected_status in cases:
        assert some_user.get(url).status_code == expected_status


def test_redirect_for_anonymous_client(
    client, url_delete_comment, url_edit_comment,
    expected_edit_url, expected_delete_url
):
    urls = (
        (url_edit_comment, expected_edit_url),
        (url_delete_comment, expected_delete_url),
    )
    for url, expected_url in urls:
        assertRedirects(client.get(url), expected_url)
