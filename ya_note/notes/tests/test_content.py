from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

URL_NOTES_LIST = reverse('notes:list')
URL_ADD_NOTE = reverse('notes:add')

NOTE_SLUG = 'note-slug'
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))

User = get_user_model()


class ParentTestClass(TestCase):
    @classmethod
    def setUpTestData(
        cls, note=False, auth_client=True, new_note_form_data=False,
        auth_reader=False, anonymous=False, auth_second_reader=False,
        form_data=False
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


class TestContent(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData(
            note=True, auth_client=True, new_note_form_data=False,
            auth_reader=True, anonymous=False, auth_second_reader=False,
            form_data=False
        )

    def test_notes_list_for_different_users(self):
        notes = self.auth_client.get(
            URL_NOTES_LIST
        ).context['object_list']
        self.assertIn(self.note, notes)
        self.assertEqual(len(notes), 1)
        note = notes[0]
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_list_of_notes_for_other_author(self):
        self.assertNotIn(
            self.note, self.auth_reader.get(
                URL_NOTES_LIST
            ).context['object_list']
        )

    def test_pages_contains_form(self):
        urls = (
            URL_ADD_NOTE,
            EDIT_URL
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
