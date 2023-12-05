from notes.forms import NoteForm
from .constants_and_parent_test_class import (
    ParentTestClass, EDIT_URL, URL_ADD_NOTE, URL_NOTES_LIST
)


class TestContent(ParentTestClass):

    def test_visibility_note_on_list_page(self):
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

    def test_visibility_notes_other_author(self):
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
