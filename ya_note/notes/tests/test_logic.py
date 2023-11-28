from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
# from notes.forms import WARNING


User = get_user_model()

URL_NOTES_LIST = reverse('notes:list')
URL_ADD_NOTE = reverse('notes:add')
URL_SUCCESS = reverse('notes:success')

NOTE_SLUG = 'note-slug'
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,))
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,))


class ParentTestClass(TestCase):
    @classmethod
    def setUpTestData(
        cls, note=False, auth_client=True, new_note_form_data=False,
        auth_reader=False, anonymous=False, auth_second_reader=False,
        form_data=False, second_new_note_form_data=False,
        third_note_form_data=False
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


class TestNoteCreationEdit(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData(
            note=True, auth_client=True, new_note_form_data=True,
            auth_reader=True, anonymous=True, auth_second_reader=True,
            form_data=True, second_new_note_form_data=True,
            third_note_form_data=True
        )

    def base_tests(self):
        notes_count_in_db_before_add = Note.objects.count()
        response = self.auth_client.post(
            URL_ADD_NOTE, data=self.second_new_note_form_data
        )
        self.assertRedirects(response, URL_SUCCESS)
        notes_count_in_db_after_add = Note.objects.count()
        self.assertEqual(
            notes_count_in_db_after_add - notes_count_in_db_before_add, 1
        )

    def test_user_can_create_note(self):
        self.base_tests()
        new_note = Note.objects.get(id=self.note.id + 1)
        self.assertEqual(
            new_note.title, self.second_new_note_form_data['title']
        )
        self.assertEqual(new_note.text, self.second_new_note_form_data['text'])
        self.assertEqual(new_note.slug, self.second_new_note_form_data['slug'])
        self.assertEqual(new_note.author, self.note.author)

    def test_anonymous_user_cant_create_note(self):
        notes_count_in_db_before_add = list(Note.objects.all())
        self.anonymous.post(URL_ADD_NOTE, data=self.form_data)
        notes_count_in_db_after_add = list(Note.objects.all())
        note_diff = set(notes_count_in_db_before_add).difference(
            set(notes_count_in_db_after_add)
        )
        self.assertEqual(
            len(note_diff),
            0
        )
        self.assertIn(
            Note.objects.get(id=self.note.id),
            Note.objects.all().filter(id=self.note.id)
        )

    def test_empty_slug(self):
        del self.form_data['slug']
        self.base_tests()
        expected_slug = slugify(self.note.title)
        last_note = Note.objects.get(id=self.note.id)
        self.assertEqual(slugify(last_note.title), expected_slug)

    def test_author_can_edit_note(self):
        response = self.auth_client.post(
            EDIT_URL, data=self.new_note_form_data
        )
        self.assertRedirects(response, URL_SUCCESS)
        note = Note.objects.get(id=self.note.id)
        self.assertEqual(note.title, self.new_note_form_data['title'])
        self.assertEqual(note.text, self.new_note_form_data['text'])
        self.assertEqual(note.slug, self.new_note_form_data['slug'])
        self.assertEqual(note.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        response = self.auth_reader.post(
            EDIT_URL, data=self.second_new_note_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        last_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, last_note.title)
        self.assertEqual(self.note.text, last_note.text)
        self.assertEqual(self.note.slug, last_note.slug)
        self.assertEqual(self.note.author, last_note.author)

    def test_other_user_cant_delete_note(self):
        notes_count_in_db_before_delete = Note.objects.count()
        response = self.auth_reader.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_in_db_after_delete = Note.objects.count()
        self.assertEqual(
            notes_count_in_db_before_delete,
            notes_count_in_db_after_delete
        )

    def test_author_can_delete_note(self):
        notes_count_in_db_before_delete = Note.objects.count()
        response = self.auth_client.delete(
            DELETE_URL
        )
        notes_count_in_db_after_delete = Note.objects.count()
        self.assertRedirects(response, URL_SUCCESS)
        self.assertEqual(
            notes_count_in_db_before_delete,
            (notes_count_in_db_after_delete + 1)
        )
