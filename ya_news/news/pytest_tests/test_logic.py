import pytest
from http import HTTPStatus

from news.forms import WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_detail_page')),
    )
)
def test_anonymous_client_cant_create_comment(client, form_data_comment, url):
    client.post(
        url,
        data=form_data_comment
    )
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_detail_page')),
    )
)
def test_authorized_client_can_create_comment(
    author_client, author, form_data_comment, news, url
):
    assert author_client.post(
        url, data=form_data_comment
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == form_data_comment.get('text')
    assert Comment.objects.get().news or Comment.objects.get(
    ).author in author and news


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_detail_page')),
    )
)
def test_user_cant_use_bad_words_in_comments(
    author_client, form_data_bad_comment, url
):
    assert author_client.post(
        url, data=form_data_bad_comment
    ).context['form'].errors['text'][0] == WARNING
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_delete_comment')),
    )
)
def test_author_can_delete_comment(author_client, url):
    assert author_client.delete(url).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_edit_comment')),
    )
)
def test_author_can_edit_comment(
    author_client, author, comment, form_data_updated_comment, news, url
):
    assert author_client.post(
        url, data=form_data_updated_comment
    ).status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == form_data_updated_comment.get('text')
    assert comment.author == form_data_updated_comment.get(author)
    assert comment.news == form_data_updated_comment.get(news)


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_edit_comment')),
    )
)
def test_user_cant_edit_comment_of_another_user(
    admin_client, author, comment, form_data_updated_comment, news, url
):
    assert admin_client.post(
        url, data=form_data_updated_comment
    ).status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
    assert comment.author == author
    assert comment.news == news
