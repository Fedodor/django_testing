from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

URL_NOTES_LIST = reverse('notes:list')
URL_ADD_NOTE = reverse('notes:add')

NOTE_SLUG = 'bulka'
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,)),

User = get_user_model()


class ParentTestClass(TestCase):
    @classmethod
    def setUpTestData(cls, note, auth_client, auth_reader, anonymous):
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
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.anonymous = Client()


class TestContent(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData(
            note=True, auth_client=True,
            auth_reader=True, anonymous=True
        )

    def test_notes_list_for_different_users(self):
        users_bools = (
            (self.auth_client, True),
            (self.auth_reader, False)
        )
        for user, bools in users_bools:
            with self.subTest(user=user, bools=bools):
                notes = user.get(URL_NOTES_LIST).context['object_list']
                if user == self.auth_client:
                    self.assertIn(self.note, notes)
                    self.assertEqual(len(notes), 1)
                note = notes.get(pk=self.note.pk)
                self.assertEqual((note in notes), bools)
                self.assertEqual((note.title in self.note.title), bools)
                self.assertEqual((note.text in self.note.text), bools)
                self.assertEqual((note.slug in self.note.slug), bools)
                self.assertEqual((note.author in self.note.author), bools)

    def test_pages_contains_form(self):
        urls = (
            URL_ADD_NOTE,
            EDIT_URL
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertIn('form', self.auth_client.get(url).context)
                self.assertIsInstance(
                    self.auth_client.get(url).context.get('form'), NoteForm
                )
