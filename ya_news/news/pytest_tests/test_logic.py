import pytest

from http import HTTPStatus

from news.forms import WARNING, BAD_WORDS
from news.models import Comment


pytestmark = pytest.mark.django_db

FORM_DATA_COMMENT = {
    'text': 'Текст комментария'
}
FORM_DATA_UPDATED_COMMENT = {
    'text': 'Updated comment'
}
FORM_DATA_BAD_COMMENT = {
    'text': f'Text, {BAD_WORDS[0]}, text'
}


def test_anonymous_client_cant_create_comment(client, url_detail_page):
    client.post(
        url_detail_page,
        data=FORM_DATA_COMMENT
    )
    assert Comment.objects.count() == 0


def test_authorized_client_can_create_comment(
    author_client, author, news, url_detail_page
):
    assert author_client.post(
        url_detail_page, data=FORM_DATA_COMMENT
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == FORM_DATA_COMMENT.get('text')
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words_in_comments(
    author_client, url_detail_page
):
    assert author_client.post(
        url_detail_page, data=FORM_DATA_BAD_COMMENT
    ).context['form'].errors['text'][0] == WARNING
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, url_delete_comment):
    assert author_client.delete(
        url_delete_comment
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
    author_client, author, comment, news, url_edit_comment
):
    assert author_client.post(
        url_edit_comment, data=FORM_DATA_UPDATED_COMMENT
    ).status_code == HTTPStatus.FOUND
    comment_after_edit = Comment.objects.get()
    assert comment_after_edit.text == FORM_DATA_UPDATED_COMMENT['text']
    assert comment_after_edit.news == comment.news
    assert comment_after_edit.author == comment.author


def test_user_cant_edit_comment_of_another_user(
    admin_client, comment, url_edit_comment
):
    assert admin_client.post(
        url_edit_comment, data=FORM_DATA_UPDATED_COMMENT
    ).status_code == HTTPStatus.NOT_FOUND
    comment_after_edit = Comment.objects.get()
    assert comment_after_edit.text == comment.text
    assert comment_after_edit.author == comment.author
    assert comment_after_edit.news == comment.news
