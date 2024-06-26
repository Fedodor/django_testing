from datetime import datetime, timedelta

from django.conf import settings
from django.test import Client
from django.utils import timezone
from django.urls import reverse
import pytest

from news.models import Comment, News

LOGIN_URL = reverse('users:login')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def author_client(author):
    author_client = Client()
    author_client.force_login(author)
    return author_client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def news_list():
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        text='Текст комментария',
        author=author,
        news=news,
    )


@pytest.fixture
def comments_list(author, news):
    for index in range(444):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}'
        )
        comment.created = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def url_home_page():
    return reverse('news:home')


@pytest.fixture
def url_user_login():
    return reverse('users:login')


@pytest.fixture
def url_user_logout():
    return reverse('users:logout')


@pytest.fixture
def url_user_signup():
    return reverse('users:signup')


@pytest.fixture
def url_detail_page(news):
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def url_delete_comment(comment):
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def url_edit_comment(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def expected_edit_url(
    url_edit_comment
):
    return f'{LOGIN_URL}?next={url_edit_comment}'


@pytest.fixture
def expected_delete_url(
    url_delete_comment
):
    return f'{LOGIN_URL}?next={url_delete_comment}'
