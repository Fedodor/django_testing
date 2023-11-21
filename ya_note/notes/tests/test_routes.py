from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

URL_HOME_PAGE = reverse('notes:home')
URL_USER_LOGIN = reverse('users:login')
URL_USER_LOGOUT = reverse('users:logout')
URL_USER_SIGNUP = reverse('users:signup')
URL_NOTES_LIST = reverse('notes:list')
URL_ADD_NOTE = reverse('notes:add')
URL_SUCCESS = reverse('notes:success')

NOTE_SLUG = 'bulka'
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,)),
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,)),
DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,)),

User = get_user_model()


class ParentTestClass(TestCase):
    @classmethod
    @classmethod
    def setUpTestData(
        cls, note, auth_client,
        author, reader, auth_reader
    ):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст заметки',
            slug='note-slug', author=cls.author,
        )
        cls.new_note_form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'note-slug-a'
        }
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст заметки',
            'slug': 'note-slug'
        }
        cls.auth_client = cls.client.force_login(cls.author)
        cls.auth_reader = cls.client.force_login(cls.reader)
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)


class TestPagesAvaibility(ParentTestClass):

    @classmethod
    def setUpTestData(
        cls, note, auth_client,
        author, reader, auth_reader
    ):
        super().setUpTestData(
            cls, note, author, reader,
            auth_client, auth_reader
        )

    def test_pages_availability_for_all_users(self):
        data = [
            [URL_ADD_NOTE, self.auth_client, HTTPStatus.OK],
            [URL_NOTES_LIST, self.auth_client, HTTPStatus.OK],
            [URL_SUCCESS, self.auth_client, HTTPStatus.OK],
            [EDIT_URL, self.auth_client, HTTPStatus.OK],
            [DELETE_URL, self.auth_client, HTTPStatus.OK],
            [DETAIL_URL, self.auth_client, HTTPStatus.OK],
            [EDIT_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [DELETE_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [DETAIL_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [URL_HOME_PAGE, self.reader, HTTPStatus.NOT_FOUND],
            [URL_USER_LOGIN, self.reader, HTTPStatus.NOT_FOUND],
            [URL_USER_LOGOUT, self.reader, HTTPStatus.NOT_FOUND],
            [URL_USER_SIGNUP, self.reader, HTTPStatus.NOT_FOUND],

        ]
        for url, user, expected_status in data:
            with self.subTest(client=user):
                self.assertEqual(
                    self.client.get(url).status_code, expected_status
                )


class TestRedirects(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def test_redirect_for_anonymous_client(self):
        for url in [
            DETAIL_URL, EDIT_URL, DELETE_URL
        ]:
            redirect_url = f'{URL_USER_LOGIN}?next={url}'
            self.assertRedirects(self.client.get(url), redirect_url)
