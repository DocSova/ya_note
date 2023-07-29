from http import HTTPStatus

from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestPagesAvailability(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability_for_anonymous_user(self):
        urls = ['notes:home', 'users:login', 'users:logout', 'users:signup']
        for url_name in urls:
            url = reverse(url_name)
            response = self.client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = ['notes:list', 'notes:add', 'notes:success']
        for url_name in urls:
            url = reverse(url_name)
            response = self.reader_client.get(url)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        test_data = [
            (self.reader_client, 'notes:detail', HTTPStatus.NOT_FOUND),
            (self.author_client, 'notes:detail', HTTPStatus.OK),
            (self.reader_client, 'notes:edit', HTTPStatus.NOT_FOUND),
            (self.author_client, 'notes:edit', HTTPStatus.OK),
            (self.reader_client, 'notes:delete', HTTPStatus.NOT_FOUND),
            (self.author_client, 'notes:delete', HTTPStatus.OK),
        ]
        for client, url_name, expected_status in test_data:
            url = reverse(url_name, args=(self.note.slug,))
            response = client.get(url)
            self.assertEqual(response.status_code, expected_status)

    def test_redirects(self):
        test_data = [
            ('notes:detail', [self.note.slug]),
            ('notes:edit', [self.note.slug]),
            ('notes:delete', [self.note.slug]),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        ]
        for url_name, args in test_data:
            url = reverse(url_name, args=args)
            login_url = reverse('users:login')
            expected_url = f'{login_url}?next={url}'
            response = self.client.get(url)
            self.assertRedirects(response, expected_url)