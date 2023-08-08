from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, comment_form_data,
                                            detail_url):
    comments_count_before = Comment.objects.count()
    response = client.post(detail_url, data=comment_form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count_before


def test_user_can_create_comment(author_client, author,
                                 detail_url, comment_form_data):
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=comment_form_data)
    expected_url = f'{detail_url}#comments'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count_before + 1
    new_comment = Comment.objects.get()
    assert new_comment.text == comment_form_data['text']
    assert new_comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(admin_client, detail_url):
    comments_count_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {choice(BAD_WORDS)},'
                      'еще текст'}
    response = admin_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before


def test_author_can_delete_comment(author_client,
                                   detail_url, delete_comment_url):
    comments_count_before = Comment.objects.count()
    url_to_comments = f'{detail_url}#comments'
    response = author_client.delete(delete_comment_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before - 1


def test_author_can_edit_comment(author_client, comment,
                                 comment_form_data, detail_url,
                                 edit_comment_url):
    url_to_comments = f'{detail_url}#comments'
    response = author_client.post(edit_comment_url, data=comment_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']
    assert comment.author == comment_form_data['author']
    assert comment.news == comment_form_data['news']


def test_user_cant_edit_comment_of_another_user(admin_client,
                                                comment_form_data, comment,
                                                edit_comment_url):
    response = admin_client.post(edit_comment_url, comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_user_cant_delete_comment_of_another_user(admin_client, comment,
                                                  delete_comment_url):
    comments_count_before = Comment.objects.count()
    response = admin_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count_before
