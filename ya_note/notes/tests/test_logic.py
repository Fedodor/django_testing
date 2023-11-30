from http import HTTPStatus

from pytils.translit import slugify

from .constants_and_parent_test_class import (
    ParentTestClass, DELETE_URL, EDIT_URL,
    URL_ADD_NOTE, URL_SUCCESS
)
from notes.models import Note


class TestNoteCreationEdit(ParentTestClass):

    def base_tests(self):
        notes_objects_before_add = Note.objects.all()
        notes_count_in_db_before_add = Note.objects.count()
        response = self.auth_client.post(
            URL_ADD_NOTE, data=self.second_new_note_form_data
        )
        self.assertRedirects(response, URL_SUCCESS)
        notes_count_in_db_after_add = Note.objects.count()
        notes_objects_after_add = Note.objects.all()
        self.assertEqual(
            notes_count_in_db_after_add - notes_count_in_db_before_add, 1
        )
        note_diff = set(notes_objects_after_add).difference(
            set(notes_objects_before_add)
        )
        self.assertNotIn(
            note_diff, notes_objects_before_add
        )
        new_note, status = Note.objects.get_or_create(
            author=self.note.author, slug='note-slug-second',
            text='Текст заметки 2', title='Заголовок 2'
        )
        self.assertEqual(status, False)
        self.assertEqual(
            new_note.title, self.second_new_note_form_data['title']
        )
        self.assertEqual(new_note.text, self.second_new_note_form_data['text'])
        self.assertEqual(new_note.slug, self.second_new_note_form_data['slug'])
        self.assertEqual(new_note.author, self.note.author)

    def test_user_can_create_note(self):
        self.base_tests()

    def test_anonymous_user_cant_create_note(self):
        notes_count_in_db_before_add = Note.objects.all()
        self.anonymous.post(URL_ADD_NOTE, data=self.form_data)
        notes_count_in_db_after_add = Note.objects.all()
        self.assertSetEqual(
            set(notes_count_in_db_before_add), set(notes_count_in_db_after_add)
        )

    def test_empty_slug(self):
        del self.form_data['slug']
        self.base_tests()
        new_note, status = Note.objects.get_or_create(
            author=self.note.author, slug='note-slug-second',
            text='Текст заметки 2', title='Заголовок 2'
        )
        expected_slug = slugify(new_note.title)
        self.assertEqual(status, False)
        self.assertEqual(slugify(new_note.title), expected_slug)

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
        new_note, status = Note.objects.get_or_create(
            author=self.note.author, slug='note-slug-second',
            text='Текст заметки 2', title='Заголовок 2'
        )
        self.assertEqual(status, True)
        response = self.auth_reader.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        last_note, expected_status = Note.objects.get_or_create(
            author=self.note.author, slug='note-slug-second',
            text='Текст заметки 2', title='Заголовок 2'
        )
        self.assertEqual(expected_status, False)
        self.assertEqual(new_note.title, last_note.title)
        self.assertEqual(new_note.text, last_note.text)
        self.assertEqual(new_note.slug, last_note.slug)
        self.assertEqual(new_note.author, last_note.author)

    def test_author_can_delete_note(self):
        notes_count_in_db_before_delete = Note.objects.count()
        notes_objects_before_delete = Note.objects.all()
        response = self.auth_client.delete(
            DELETE_URL
        )
        notes_count_in_db_after_delete = Note.objects.count()
        notes_objects_after_delete = Note.objects.all()
        self.assertRedirects(response, URL_SUCCESS)
        self.assertEqual(
            notes_count_in_db_before_delete,
            (notes_count_in_db_after_delete + 1)
        )
        note_diff = set(notes_objects_before_delete).difference(
            set(notes_objects_after_delete)
        )
        self.assertNotIn(
            note_diff, set(notes_objects_after_delete)
        )
