import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


HOME_URL = reverse('news:home')


@pytest.mark.django_db
def test_news_count(client, news_list):
    response = client.get(HOME_URL)
    news = response.context['object_list']
    assert news.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(HOME_URL)
    news = response.context['object_list']
    all_dates = [news.date for news in news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comments, detail_url):
    response = client.get(detail_url)
    assert "news" in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    sorted_comments = sorted(all_comments,
                             key=lambda comment: comment.created)
    assert sorted_comments == comments


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, form_in_page',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('author_client'), True)
    ),
)
def test_form_availability_for_different_users(
        parametrized_client, form_in_page, detail_url, author
):
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) == form_in_page
    if parametrized_client == author:
        assert isinstance(response.context['form'], CommentForm)
