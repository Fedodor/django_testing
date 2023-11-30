import pytest

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_count_news_on_home_page(
    client, url_home_page, news_list, news
):
    assert len(
        client.get(url_home_page).context['object_list']
    ) == settings.NEWS_COUNT_ON_HOME_PAGE


def test_order_news_on_home_page(
    client, url_home_page
):
    dates = [
        news.date for news in client.get(url_home_page).context['object_list']
    ]
    assert dates == sorted(dates, reverse=True)


def test_order_comments_on_detail_page(
    author_client, comments_list, news, url_detail_page
):
    created_dates = [
        comment.created for comment in author_client.get(
            url_detail_page).context['news'].comment_set.all()
    ]
    assert created_dates == sorted(created_dates, reverse=False)


def test_detail_page_for_author_has_form(author_client, url_detail_page):
    assert 'form' in author_client.get(url_detail_page).context
    assert isinstance(
        author_client.get(url_detail_page).context.get('form'), CommentForm
    )


def test_detail_page_for_anonymous_user_has_no_form(client, url_detail_page):
    assert 'form' not in client.get(url_detail_page).context
