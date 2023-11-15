import pytest
from http import HTTPStatus

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_client_cant_create_comment(client, form_data_comment, news):
    url = reverse('news:detail', args=(news.pk,))
    client.post(
        url,
        data=form_data_comment
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_client_can_create_comment(
    author_client, author, form_data_comment, news
):
    url = reverse('news:detail', args=(news.pk,))
    assert author_client.post(
        url, data=form_data_comment
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    assert Comment.objects.get().text == 'Текст комментария'
    assert Comment.objects.get().news == news
    assert Comment.objects.get().author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words_in_comments(author_client, news):
    url = reverse('news:detail', args=(news.pk,))
    form_data = {'text': f'Text, {BAD_WORDS[0]}, text'}
    assert author_client.post(
        url, data=form_data
    ).context['form'].errors['text'][0] == WARNING
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    assert author_client.delete(
        reverse('news:delete', args=(comment.pk,))
    ).status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    form_data = {'text': 'Updated comment'}
    assert author_client.post(
        (reverse('news:edit', args=(comment.pk,))), data=form_data
    ).status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == 'Updated comment'


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(admin_client, comment):
    form_data = {'text': 'Updated comment'}
    assert admin_client.post(
        (reverse('news:edit', args=(comment.pk,))), data=form_data
    ).status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
