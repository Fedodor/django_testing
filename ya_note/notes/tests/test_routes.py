from http import HTTPStatus

from constants import (
    DELETE_URL, DETAIL_URL, EDIT_URL, ParentTestClass,
    URL_ADD_NOTE, URL_HOME_PAGE, URL_NOTES_LIST, URL_USER_LOGIN,
    URL_USER_LOGOUT, URL_USER_SIGNUP, URL_SUCCESS,
)

# REDIRECT_LOGIN_URL = f'{URL_USER_LOGIN}?next={url}'


class TestPagesAvaibility(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData(
            note=True, author=True, reader=True,
            auth_client=True, auth_reader=True
        )

    def test_pages_availability_for_all_users(self):
        data = [
            [URL_ADD_NOTE, self.auth_client, HTTPStatus.OK],
            [URL_NOTES_LIST, self.auth_client, HTTPStatus.OK],
            [URL_SUCCESS, self.auth_client, HTTPStatus.OK],
            [EDIT_URL, self.auth_client, HTTPStatus.OK],
            [DELETE_URL, self.auth_client, HTTPStatus.OK],
            [DETAIL_URL, self.auth_client, HTTPStatus.OK],
            [EDIT_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [DELETE_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [DETAIL_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [URL_HOME_PAGE, self.reader, HTTPStatus.NOT_FOUND],
            [URL_USER_LOGIN, self.reader, HTTPStatus.NOT_FOUND],
            [URL_USER_LOGOUT, self.reader, HTTPStatus.NOT_FOUND],
            [URL_USER_SIGNUP, self.reader, HTTPStatus.NOT_FOUND],

        ]
        for url, user, expected_status in data:
            with self.subTest(client=user):
                self.assertEqual(
                    self.client.get(url).status_code, expected_status
                )


class TestRedirects(ParentTestClass):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData(
            author=True, reader=True,
        )

    def test_redirect_for_anonymous_client(self):
        for url in [
            DETAIL_URL, EDIT_URL, DELETE_URL
        ]:
            redirect_url = f'{URL_USER_LOGIN}?next={url}'
            self.assertRedirects(self.client.get(url), redirect_url)
