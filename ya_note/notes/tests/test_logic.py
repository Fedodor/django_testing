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
        cls, note, author, reader, auth_client, client,
        auth_user, auth_reader, form_data, new_note_form_data
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


class TestNoteCreationEdit(ParentTestClass):

    @classmethod
    def setUpTestData(
        cls
    ):
        super().setUpTestData(
            note=True, author=True, reader=True,
            auth_client=True, auth_reader=True, auth_user=True,
            form_data=True, new_note_form_data=True, client=True
        )

    def base_tests(self):
        notes_count_in_db_before_add = list(Note.objects.all())
        response = self.auth_user.post(URL_ADD_NOTE, data=self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        notes_count_in_db_after_add = list(Note.objects.all())
        note = set(notes_count_in_db_before_add).difference(
            set(notes_count_in_db_after_add)
        )
        self.assertEqual(
            len(note),
            1
        )
        self.assertEqual(
            note.id,
            Note.objects.all().last().id
        )

    def test_user_can_create_note(self):
        self.base_tests(self)
        new_note, created = Note.objects.get_or_create(
            title='Новый заголовок', text='Новый текст',
            slug='note-slug-a', author=self.auth_user
        )
        if created is True:
            self.assertEqual(new_note.title, self.new_note_form_data['title'])
            self.assertEqual(new_note.text, self.new_note_form_data['text'])
            self.assertEqual(new_note.slug, self.new_note_form_data['slug'])
            self.assertEqual(new_note.author, self.auth_user)

    def test_anonymous_user_cant_create_note(self):
        notes_count_in_db_before_add = list(Note.objects.all())
        self.client.post(URL_ADD_NOTE, data=self.form_data)
        notes_count_in_db_after_add = list(Note.objects.all())
        note = set(notes_count_in_db_before_add).difference(
            set(notes_count_in_db_after_add)
        )
        self.assertEqual(
            len(note),
            0
        )
        self.assertEqual(
            note.id,
            Note.objects.all().last().id
        )

    def test_unique_slug(self):
        notes_count_in_db_before_add = list(Note.objects.all())
        response = self.auth_user.post(URL_ADD_NOTE, data=self.form_data)
        notes_count_in_db_after_add = list(Note.objects.all())
        self.assertFormError(response, form='form', field='slug',
                             errors=(self.form_data['slug'] + WARNING))
        self.assertIn(
            notes_count_in_db_before_add,
            notes_count_in_db_after_add
        )

    def test_empty_slug(self):
        del self.form_data['slug']
        self.base_tests(self)
        expected_slug = slugify(self.form_data['title'])
        last_note = Note.objects.all().last().id
        self.assertEqual(last_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        response = self.auth_client.post(EDIT_URL, self.form_data)
        self.assertRedirects(response, URL_SUCCESS)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])
        self.assertEqual(self.note.author, self.auth_client)

    def test_other_user_cant_edit_note(self):
        response = self.auth_user.post(self.edit_url, self.form_data)
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
        response = self.auth_user.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_in_db_after_delete = Note.objects.count()
        self.assertEqual(
            notes_count_in_db_before_delete,
            notes_count_in_db_after_delete
        )
