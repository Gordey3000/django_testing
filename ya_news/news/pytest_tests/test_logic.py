from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        'form',
        'text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client,
                                 form_data,
                                 comment,
                                 news,
                                 author
                                 ):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response, f'{url}#comments')
    news.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.delete(url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = admin_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_other_user_cant_delete_note(admin_client, form_data, slug_for_args):
    url = reverse('news:delete', args=slug_for_args)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
