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
    def setUpTestData(
        cls, note=True, auth_client=True, new_note_form_data=True,
        auth_reader=True, anonymous=True, auth_user=True, form_data=True
    ):
        if auth_client:
            cls.author = User.objects.create(username='Лев Толстой')
            cls.auth_client = Client()
            cls.auth_client.force_login(cls.author)
        if auth_reader:
            cls.reader = User.objects.create(username='Читатель простой')
            cls.auth_reader = Client()
            cls.auth_reader.force_login(cls.reader)
        if auth_user:
            cls.user = User.objects.create(username='Мимо Крокодил')
            cls.auth_user = Client()
            cls.auth_user.force_login(cls.user)
        if note:
            cls.note = Note.objects.create(
                title='Заголовок', text='Текст заметки',
                slug='note-slug', author=cls.author,
            )
        if new_note_form_data:
            cls.new_note_form_data = {
                'title': 'Новый заголовок',
                'text': 'Новый текст',
                'slug': 'note-slug-a'
            }
        if form_data:
            cls.form_data = {
                'title': 'Заголовок',
                'text': 'Текст заметки',
                'slug': 'note-slug'
            }
        if anonymous:
            cls.anonymous = Client()


class TestPagesAvaibility(ParentTestClass):

    @classmethod
    def setUpTestData(
        cls, note=True, auth_client=True, new_note_form_data=True,
        auth_reader=True, anonymous=True, auth_user=True, form_data=True
    ):
        super().setUpTestData(
            cls, note=False, auth_client=True, new_note_form_data=False,
            auth_reader=True, anonymous=True, auth_user=False, form_data=False
        )

    def test_pages_availability_for_all_users(self):
        data = (
            (URL_ADD_NOTE, self.auth_client, HTTPStatus.OK),
            (URL_NOTES_LIST, self.auth_client, HTTPStatus.OK),
            (URL_SUCCESS, self.auth_client, HTTPStatus.OK),
            (EDIT_URL, self.auth_client, HTTPStatus.OK),
            (DELETE_URL, self.auth_client, HTTPStatus.OK),
            (DETAIL_URL, self.auth_client, HTTPStatus.OK),
            (EDIT_URL, self.auth_reader, HTTPStatus.NOT_FOUND),
            (DELETE_URL, self.auth_reader, HTTPStatus.NOT_FOUND),
            (DETAIL_URL, self.auth_reader, HTTPStatus.NOT_FOUND),
            (URL_HOME_PAGE, self.anonymous, HTTPStatus.OK),
            (URL_USER_LOGIN, self.anonymous, HTTPStatus.OK),
            (URL_USER_LOGOUT, self.anonymous, HTTPStatus.OK),
            (URL_USER_SIGNUP, self.anonymous, HTTPStatus.OK),
        )
        for url, some_user, expected_status in data:
            with self.subTest(
                some_user=some_user, url=url, expected_status=expected_status
            ):
                self.assertEqual(
                    self.some_user.get(url).status_code, expected_status
                )


class TestRedirects(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData(
            cls, note=False, auth_client=False, new_note_form_data=False,
            auth_reader=False, anonymous=True, auth_user=False, form_data=False
        )

    def test_redirect_for_anonymous_client(self):
        for url in (
            DETAIL_URL, EDIT_URL, DELETE_URL,
        ):
            with self.subTest(url=url):
                redirect_url = f'{URL_USER_LOGIN}?next={url}'
                self.assertRedirects(self.anonymous.get(url), redirect_url)
