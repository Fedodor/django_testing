from constants import (
    EDIT_URL, ParentTestClass, URL_ADD_NOTE, URL_NOTES_LIST
)
from notes.forms import NoteForm


class TestContent(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData(
            note=True, auth_client=True, auth_reader=True
        )

    def test_notes_list_for_different_users(self):
        users_bools = (
            (self.auth_client, True),
            (self.auth_reader, False),
        )
        for user, bools in users_bools:
            with self.subTest(user=user, bools=bools):
                response = self.client.get(URL_NOTES_LIST)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), bools)
                self.assertEqual((self.note.title in object_list), bools)
                self.assertEqual((self.note.text in object_list), bools)
                self.assertEqual((self.note.slug in object_list), bools)
                self.assertEqual((self.note.author in object_list), bools)

    def test_pages_contains_form(self):
        urls = (
            URL_ADD_NOTE,
            EDIT_URL
        )
        for url in urls:
            self.auth_client = self.auth_client
            with self.subTest(url=url):
                self.assertIn('form', self.auth_client.get(url).context)
                self.assertIsInstance(
                    self.auth_client.get(url).context.get('form'), NoteForm
                )
