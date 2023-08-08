from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

HOME_URL = reverse('news:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        (HOME_URL),
        (pytest.lazy_fixture('detail_url')),
        (LOGIN_URL),
        (LOGOUT_URL),
        (SIGNUP_URL),
    ),
)
def test_pages_availability_for_anonymous_user(client, name):
    response = client.get(name)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('edit_comment_url')),
        (pytest.lazy_fixture('delete_comment_url')),
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, expected_status
):
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('edit_comment_url')),
        (pytest.lazy_fixture('delete_comment_url')),
    ),
)
def test_redirects(client, name):
    expected_url = f'{LOGIN_URL}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
