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

NOTE_SLUG = 'note-slug'
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,)),
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,)),
DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,)),

User = get_user_model()


class ParentTestClass(TestCase):
    @classmethod
    def setUpTestData(
        cls, note=True, auth_client=True, new_note_form_data=True,
        auth_reader=True, anonymous=True, auth_second_reader=True,
        form_data=True
    ):
        if auth_client:
            cls.author = User.objects.create(username='Лев Толстой')
            cls.auth_client = Client()
            cls.auth_client.force_login(cls.author)
        if auth_reader:
            cls.reader = User.objects.create(username='Читатель простой')
            cls.auth_reader = Client()
            cls.auth_reader.force_login(cls.reader)
        if auth_second_reader:
            cls.second_reader = User.objects.create(username='Мимо Крокодил')
            cls.auth_second_reader = Client()
            cls.auth_second_reader.force_login(cls.second_reader)
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
        cls, note=True, auth_client=True, new_note_form_data=False,
            auth_reader=True, anonymous=True, auth_second_reader=True,
            form_data=False
    ):
        super().setUpTestData()

    def test_pages_availability_for_all_users(self):
        data = {
            URL_HOME_PAGE: (
                (self.client, HTTPStatus.OK),
                (self.auth_second_reader, HTTPStatus.OK)
            ),
            URL_USER_LOGIN: (
                (self.client, HTTPStatus.OK),
                (self.auth_second_reader, HTTPStatus.OK)
            ),
            URL_USER_SIGNUP: (
                (self.client, HTTPStatus.OK),
                (self.auth_second_reader, HTTPStatus.OK)
            ),
            URL_NOTES_LIST: ((self.auth_client, HTTPStatus.OK),),
            URL_ADD_NOTE: ((self.auth_client, HTTPStatus.OK),),
            URL_SUCCESS: ((self.auth_client, HTTPStatus.OK),),
            EDIT_URL: (
                (self.client, HTTPStatus.NOT_FOUND),
                (self.auth_client, HTTPStatus.OK)
            ),
            DELETE_URL: (
                (self.client, HTTPStatus.NOT_FOUND),
                (self.auth_client, HTTPStatus.OK)
            ),
            DETAIL_URL: (
                (self.client, HTTPStatus.NOT_FOUND),
                (self.auth_client, HTTPStatus.OK)
            ),
            URL_USER_LOGOUT: (
                (self.client, HTTPStatus.OK),
                (self.auth_second_reader, HTTPStatus.OK)
            ),
        }
        for item in data.items():
            urls, user_statuses = item
            with self.subTest(urls=urls):
                for user_status in user_statuses:
                    user, status = user_status
                    with self.subTest(user_status=user_status):
                        self.assertEqual(
                            user.get(urls).status_code, status
                        )


class TestRedirects(ParentTestClass):

    @classmethod
    def setUpTestData(
        cls, note=True, auth_client=False, new_note_form_data=False,
        auth_reader=False, anonymous=True, auth_second_reader=False,
        form_data=False
    ):
        super().setUpTestData()

    def test_redirect_for_anonymous_client(self):
        self.auth_client.post(URL_ADD_NOTE, data=self.form_data)
        for url in (
            DETAIL_URL, EDIT_URL, DELETE_URL,
        ):
            with self.subTest(url=url):
                redirect_url = f'{URL_USER_LOGIN}?next={url}'
                self.assertRedirects(self.anonymous.get(url), redirect_url)
