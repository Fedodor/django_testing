from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING


URL_NOTES_LIST = reverse('notes:list')
URL_ADD_NOTE = reverse('notes:add')
URL_SUCCESS = reverse('notes:success')

NOTE_SLUG = 'bulka'
EDIT_URL = reverse('notes:edit', args=(NOTE_SLUG,)),
DELETE_URL = reverse('notes:delete', args=(NOTE_SLUG,)),

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


class TestNoteCreationEdit(ParentTestClass):

    @classmethod
    def setUpTestData(
        cls, note=True, auth_client=True, new_note_form_data=True,
            auth_reader=False, anonymous=True, auth_second_reader=True,
            form_data=True
    ):
        super().setUpTestData()

    def base_tests(self):
        notes_count_in_db_before_add = list(Note.objects.all())
        response = self.auth_second_reader.post(
            URL_ADD_NOTE, data=self.form_data
        )
        self.assertRedirects(response, URL_SUCCESS)
        notes_count_in_db_after_add = list(Note.objects.all())
        note_diff = set(notes_count_in_db_after_add).difference(
            set(notes_count_in_db_before_add)
        )
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(
            len(note_diff),
            1
        )
        self.assertIn(
            note_from_db,
            Note.objects.all().filter(pk=self.note.pk)
        )

    def test_user_can_create_note(self):
        self.base_tests()
        new_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.auth_second_reader)

    def test_anonymous_user_cant_create_note(self):
        notes_count_in_db_before_add = list(Note.objects.all())
        self.anonymous.post(URL_ADD_NOTE, data=self.form_data)
        notes_count_in_db_after_add = list(Note.objects.all())
        note_diff = set(notes_count_in_db_before_add).difference(
            set(notes_count_in_db_after_add)
        )
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(
            len(note_diff),
            0
        )
        self.assertIn(
            note_from_db,
            Note.objects.all().filter(pk=self.note.pk)
        )

    def test_unique_slug(self):
        notes_count_in_db_before_add = list(Note.objects.all())
        response = self.auth_second_reader.post(
            URL_ADD_NOTE, data=self.form_data
        )
        notes_count_in_db_after_add = list(Note.objects.all())
        self.assertFormError(response, form='form', field='slug',
                             errors=(self.form_data['slug'] + WARNING))
        self.assertListEqual(
            notes_count_in_db_before_add,
            notes_count_in_db_after_add
        )

    def test_empty_slug(self):
        del self.form_data['slug']
        self.base_tests()
        expected_slug = slugify(self.form_data['title'])
        last_note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(slugify(last_note.title), expected_slug)

    def test_author_can_edit_note(self):
        response = self.auth_client.post(EDIT_URL, self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.auth_client)

    def test_other_user_cant_edit_note(self):
        response = self.auth_user.post(EDIT_URL, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(pk=self.note.pk)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        notes_count_in_db_before_delete = Note.objects.count()
        response = self.auth_client.delete(DELETE_URL)
        self.assertRedirects(response, URL_SUCCESS)
        notes_count_in_db_after_delete = Note.objects.count()
        self.assertEqual(
            notes_count_in_db_before_delete,
            (notes_count_in_db_after_delete + 1)
        )

    def test_other_user_cant_delete_note(self):
        notes_count_in_db_before_delete = Note.objects.count()
        response = self.auth_second_reader.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_in_db_after_delete = Note.objects.count()
        self.assertEqual(
            notes_count_in_db_before_delete,
            notes_count_in_db_after_delete
        )
