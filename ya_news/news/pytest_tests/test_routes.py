import pytest
from pytest_django.asserts import assertRedirects
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous_user(
        client, news, name, args
):
    url = reverse(name, args=args)
    assert client.get(url).status_code == HTTPStatus.OK, (
        f'Проверьте, что код ответа {HTTPStatus.OK} страницы '
        f'"{url}" соответствует ожидаемому.'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_comment',)),
        ('news:delete', pytest.lazy_fixture('pk_for_comment',)),
    )
)
def test_pages_availability_for_author_and_user(
        admin_client, author_client, name, args
):
    url = reverse(name, args=args)
    assert author_client.get(url).status_code == HTTPStatus.OK, (
        f'Проверьте, что код ответа {HTTPStatus.OK} страницы '
        f'"{url}" соответствует ожидаемому.'
    )
    assert admin_client.get(url).status_code == HTTPStatus.NOT_FOUND, (
        f'Проверьте, что код ответа {HTTPStatus.NOT_FOUND} страницы '
        f'"{url}" соответствует ожидаемому.'
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_comment',)),
        ('news:delete', pytest.lazy_fixture('pk_for_comment',)),
    )
)
def test_redirect_for_anonymous_client(
    client, name, args
):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
