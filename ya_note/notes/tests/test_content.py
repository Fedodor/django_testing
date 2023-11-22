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


class TestContent(ParentTestClass):

    @classmethod
    def setUpTestData(
        cls, note=True, auth_client=True, new_note_form_data=True,
        auth_reader=True, anonymous=True, auth_user=True, form_data=True
    ):
        super().setUpTestData(
            cls, note=True, auth_client=True, new_note_form_data=False,
            auth_reader=True, anonymous=False, auth_user=False, form_data=False
        )

    def test_notes_list_for_different_users(self):
        users_bools = (
            (self.auth_client, True),
            (self.auth_reader, False)
        )
        for user, bools in users_bools:
            with self.subTest(user=user, bools=bools):
                notes = user.get(URL_NOTES_LIST).context['object_list']
                if user is self.auth_client:
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
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    self.auth_client.get(url).context.get('form'), NoteForm
                )
