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
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст заметки',
            slug='note-slug', author=cls.author,
        )
        # cls.new_note_data = (title='Заголовок', text='Текст заметки',
        #    slug='note-slug', author=cls.author,)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'note-slug'
        }
        cls.auth_client = cls.client.force_login(cls.author)
        cls.auth_reader = cls.client.force_login(cls.reader)
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
