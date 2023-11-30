from http import HTTPStatus

from .constants_and_parent_test_class import (
    ParentTestClass, EDIT_URL, DELETE_URL, DETAIL_URL,
    URL_ADD_NOTE, URL_HOME_PAGE, URL_NOTES_LIST, URL_SUCCESS,
    URL_USER_LOGIN, URL_USER_LOGOUT, URL_USER_SIGNUP,
    REDIRECT_URL_FOR_AFTER_EDIT, REDIRECT_URL_FOR_AFTER_DELETE,
    REDIRECT_URL_FOR_DETAIL_URL
)


class TestPagesAvaibility(ParentTestClass):

    def test_pages_availability_for_all_users(self):
        cases = [
            [URL_ADD_NOTE, self.auth_client, HTTPStatus.OK],
            [URL_NOTES_LIST, self.auth_client, HTTPStatus.OK],
            [URL_SUCCESS, self.auth_client, HTTPStatus.OK],
            [EDIT_URL, self.auth_client, HTTPStatus.OK],
            [DELETE_URL, self.auth_client, HTTPStatus.OK],
            [DETAIL_URL, self.auth_client, HTTPStatus.OK],
            [EDIT_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [DELETE_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [DETAIL_URL, self.auth_reader, HTTPStatus.NOT_FOUND],
            [URL_HOME_PAGE, self.anonymous, HTTPStatus.OK],
            [URL_USER_LOGIN, self.anonymous, HTTPStatus.OK],
            [URL_USER_LOGOUT, self.anonymous, HTTPStatus.OK],
            [URL_USER_SIGNUP, self.anonymous, HTTPStatus.OK]
        ]
        for url, some_user, expected_status in cases:
            with self.subTest(
                some_user=some_user, url=url, expected_status=expected_status
            ):
                self.assertEqual(
                    some_user.get(url).status_code, expected_status
                )

    def test_redirect_for_anonymous_client(self):
        url_redirects = {
            DETAIL_URL: REDIRECT_URL_FOR_DETAIL_URL,
            DELETE_URL: REDIRECT_URL_FOR_AFTER_DELETE,
            EDIT_URL: REDIRECT_URL_FOR_AFTER_EDIT
        }
        for url, redirect_url in url_redirects.items():
            with self.subTest(url=url, redirect_url=redirect_url):
                self.assertRedirects(self.client.get(url), redirect_url)
