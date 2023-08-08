from datetime import timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def new():
    new = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return new


@pytest.fixture
def comment(new, author):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def detail_url(new):
    detail_url = reverse('news:detail', args=(new.id,))
    return detail_url


@pytest.fixture
def edit_comment_url(comment):
    edit_comment_url = reverse('news:edit', args=(comment.id,))
    return edit_comment_url


@pytest.fixture
def delete_comment_url(comment):
    delete_comment_url = reverse('news:delete', args=(comment.id,))
    return delete_comment_url


@pytest.fixture
def comment_form_data(new, author):
    return {
        'text': 'Новый текст',
        'news': new,
        'author': author
    }


@pytest.fixture
def news_list():
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News.objects.create(title=f'Новость {index}',
                                   text='Просто текст.')
        news.save()
    return index


@pytest.fixture
def comments(author, new):
    now = timezone.now()
    comments = []
    for index in range(2):
        comment = Comment.objects.create(
            news=new,
            author=author,
            text=f"Текст {index}",
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments
