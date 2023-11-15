import pytest

from django.utils import timezone
from django.urls import reverse


from news.models import Comment, News


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=timezone.now()
    )


@pytest.fixture
def form_data_news():
    return {
        'title': 'Заголовок',
        'text': 'Текст новости',
    }


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )


@pytest.fixture
def form_data_comment():
    return {
        'text': 'Текст комментария',
    }


@pytest.fixture
def pk_for_comment(comment):
    return comment.pk,


@pytest.fixture
def pk_for_news(news):
    return news.pk,


@pytest.fixture
def pages_for_anonymous():
    return [
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ]


@pytest.fixture
def pages_for_author():
    return [
        reverse('news:edit', args=(pk_for_comment,)),
        reverse('news:delete', args=(pk_for_comment,))
    ]


@pytest.fixture
def pages_for_user():
    return [
        reverse('news:detail', args=(pk_for_news,))
    ]
