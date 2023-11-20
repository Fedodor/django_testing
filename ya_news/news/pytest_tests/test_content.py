import pytest

from django.conf import settings

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_home_page')),
    )
)
def test_count_news_on_home_page(
    client, news_list, url
):
    news_list = news_list
    response = client.get(url)
    news_list = response.context['object_list']
    assert len(news_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_home_page')),
    )
)
def test_order_news_on_home_page(
    client, news_list, url
):
    news_list = news_list
    response = client.get(url)
    news_list = response.context['object_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_detail_page')),
    )
)
def test_order_comments_on_detail_page(
    author_client, comments_list, news, url
):
    response = author_client.get(url)
    news = response.context['news']
    comment = news.comment_set.all()
    assert comment[0].created < comment[1].created
    assert comment[0].created < comment[2].created
    assert comment[0].created < comment[3].created
    assert comment[1].created < comment[2].created
    assert comment[1].created < comment[3].created
    assert comment[2].created < comment[3].created


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_detail_page')),
    )
)
def test_detail_page_for_author_has_form(author_client, url):
    assert 'form' in author_client.get(url).context
    form = author_client.get(url).context.get('form')
    assert isinstance(form, CommentForm)


@pytest.mark.parametrize(
    'url',
    (
        (pytest.lazy_fixture('url_detail_page')),
    )
)
def test_detail_page_for_anonymous_user_has_no_form(client, url):
    assert 'form' not in client.get(url).context
