import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture

from http import HTTPStatus

from django.urls import reverse

pytestmark = pytest.mark.django_db

CLIENT = lazy_fixture('client')
AUTHOR = lazy_fixture('author_client')
ADMIN = lazy_fixture('admin_client')


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('url_home_page'), CLIENT, HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_login'), CLIENT, HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_logout'), CLIENT, HTTPStatus.OK),
        (pytest.lazy_fixture('url_user_signup'), CLIENT, HTTPStatus.OK),
        (pytest.lazy_fixture('url_edit_comment'), AUTHOR, HTTPStatus.OK),
        (pytest.lazy_fixture('url_delete_comment'), AUTHOR, HTTPStatus.OK),
        (pytest.lazy_fixture('url_edit_comment'), ADMIN, HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('url_delete_comment'), ADMIN,
         HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability_for_all_users(
        url, parametrized_client, expected_status
):
    assert parametrized_client.get(url).status_code == expected_status, (
        f'Проверьте, что код ответа страницы "{url}" соответствует ожидаемому.'
    )


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_edit_comment')),
        (pytest.lazy_fixture('url_delete_comment')),
    )
)
def test_redirect_for_anonymous_client(
    client, url
):
    expected_url = f'{reverse("users:login")}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
