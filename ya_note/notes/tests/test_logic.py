from http import HTTPStatus

from pytils.translit import slugify

from .constants_and_parent_test_class import (
    ParentTestClass, DELETE_URL, EDIT_URL,
    URL_ADD_NOTE, URL_SUCCESS
)
from notes.models import Note


class TestNoteCreationEdit(ParentTestClass):

    def auth_client_can_create_note(self, slug):
        notes_befor = set(Note.objects.all())
        response = self.auth_client.post(
            URL_ADD_NOTE, data=self.second_new_note_form_data
        )
        self.assertRedirects(response, URL_SUCCESS)
        created_notes = set(Note.objects.all()).difference(
            notes_befor
        )
        self.assertEqual(len(created_notes), 1)
        new_note = Note.objects.get(id=created_notes.pop().id)
        self.assertEqual(
            new_note.title, self.second_new_note_form_data['title']
        )
        self.assertEqual(new_note.text, self.second_new_note_form_data['text'])
        self.assertEqual(new_note.slug, slug)
        self.assertEqual(new_note.author, self.author)

    def test_user_can_create_note(self):
        self.auth_client_can_create_note(
            self.second_new_note_form_data['slug']
        )

    def test_anonymous_user_cant_create_note(self):
        notes = Note.objects.all()
        self.anonymous.post(URL_ADD_NOTE, data=self.form_data)
        self.assertEqual(
            set(notes), set(Note.objects.all())
        )

    def test_empty_slug(self):
        self.second_new_note_form_data.pop('slug')
        self.auth_client_can_create_note(
            slugify(self.second_new_note_form_data['title'])
        )

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
        response = self.auth_reader.delete(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        last_note = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, last_note.title)
        self.assertEqual(self.note.text, last_note.text)
        self.assertEqual(self.note.slug, last_note.slug)
        self.assertEqual(self.note.author, last_note.author)

    def test_author_can_delete_note(self):
        response = self.auth_client.delete(
            DELETE_URL
        )
        self.assertRedirects(response, URL_SUCCESS)
        self.assertFalse(Note.objects.filter(
            id=self.note.id).exists()
        )
