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
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))
DETAIL_URL = reverse('notes:detail', args=(NOTE_SLUG,))

REDIRECT_URL_FOR_AFTER_EDIT = f'{URL_USER_LOGIN}?next={EDIT_URL}'
REDIRECT_URL_FOR_AFTER_DELETE = f'{URL_USER_LOGIN}?next={DELETE_URL}'
REDIRECT_URL_FOR_DETAIL_URL = f'{URL_USER_LOGIN}?next={DETAIL_URL}'

User = get_user_model()


class ParentTestClassFail(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст заметки',
            slug='note-slug', author=cls.author,
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'note-slug'
        }
        cls.auth_client = cls.client.force_login(cls.author)
        cls.auth_reader = cls.client.force_login(cls.reader)


class ParentTestClass(TestCase):
    @classmethod
    def setUpTestData(
        cls, note=True, auth_client=True, new_note_form_data=True,
        auth_reader=True, anonymous=True, auth_second_reader=True,
        form_data=True, second_new_note_form_data=True,
        third_note_form_data=True
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
                'slug': 'note-slug'
            }
        if second_new_note_form_data:
            cls.second_new_note_form_data = {
                'title': 'Заголовок 2',
                'text': 'Текст заметки 2',
                'slug': 'note-slug-second'
            }
        if third_note_form_data:
            cls.third_note_form_data = {
                'title': 'Заголовок 3',
                'text': 'Текст заметки 3',
                'slug': 'note-slug'
            }
        if form_data:
            cls.form_data = {
                'title': 'Заголовок 1',
                'text': 'Текст заметки 1',
                'slug': 'note-slug'
            }
        if anonymous:
            cls.anonymous = Client()
