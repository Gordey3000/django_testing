import pytest
from django.contrib.auth import get_user_model
from news.forms import CommentForm
User = get_user_model()

pytestmark = pytest.mark.django_db


def test_news_count(all_news, client, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    assert len(object_list) == len(all_news)


def test_news_order(all_news, client, url_home):
    response = client.get(url_home)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, created_comment, url_detail):
    response = client.get(url_detail)
    news = response.context['news']
    all_set_comments = [
        created_comment.created for created_comment in news.comment_set.all()
        ]
    news.comment_set.all()
    sorted_comments = sorted(all_set_comments, reverse=True)
    assert all_set_comments == sorted_comments


def test_anonymous_client_has_no_form(news, client, url_detail):
    response = client.get(url_detail)
    assert 'form' not in response.context


def test_authorized_client_has_form(news, author_client, url_detail):
    response = author_client.get(url_detail)
    assert isinstance('form', CommentForm) in response.context
