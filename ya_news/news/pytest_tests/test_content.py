import pytest
from datetime import datetime, timedelta

from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from news.models import Comment, News


@pytest.mark.django_db
def test_count_news_on_home_page(
    client,
):
    today = datetime.today()
    News.objects.bulk_create(
        [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_order_news_on_home_page(
    client,
):
    today = datetime.today()
    News.objects.bulk_create(
        [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    )
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


@pytest.mark.django_db
def test_order_comments_on_detail_page(
    author_client, author, news,
):
    comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {index}',
            created=timezone.now() + timedelta(days=index)
        )
        comments.append(comment)
    response = author_client.get(reverse('news:detail', args=(news.pk,)))
    news = response.context['news']
    assert news.comment_set.all()[0].created < news.comment_set.all(
    )[1].created


@pytest.mark.django_db
def test_detail_page_for_author_has_form(author_client, news):
    detail_url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(detail_url)
    assert 'form' in response.context


@pytest.mark.django_db
def test_detail_page_for_anonymous_user_has_no_form(client, news):
    detail_url = reverse('news:detail', args=(news.pk,))
    response = client.get(detail_url)
    assert 'form' not in response.context
