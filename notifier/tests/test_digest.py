# coding=utf-8

from unittest import skip
from django.test import TestCase
from mock import patch

from notifier.digest import Digest, DigestCourse, DigestItem, DigestThread, render_digest
from notifier.digest import _get_thread_url
from notifier.digest import render_digest_flagged
from notifier.tests.test_tasks import usern
from notifier.user import LANGUAGE_PREFERENCE_KEY

TEST_COURSE_ID = "test_org/test_num/test_course"
TEST_COMMENTABLE = "test_commentable"

@patch("notifier.digest.THREAD_ITEM_MAXLEN", 17)
class DigestItemTestCase(TestCase):
    def _test_unicode_data(self, input_text, expected_text):
        self.assertEqual(DigestItem(input_text, None, None).body, expected_text)

    def test_ascii(self):
        self._test_unicode_data(u"This post contains ASCII.", u"This post...")

    def test_latin_1(self):
        self._test_unicode_data(u"Thís pøst çòñtáins Lätin-1 tæxt", u"Thís pøst...")

    def test_CJK(self):
        self._test_unicode_data(u"ｲんﾉ丂 ｱo丂ｲ co刀ｲﾑﾉ刀丂 cﾌズ", u"ｲんﾉ丂 ｱo丂ｲ...")

    def test_non_BMP(self):
        self._test_unicode_data(u"𝕋𝕙𝕚𝕤 𝕡𝕠𝕤𝕥 𝕔𝕠𝕟𝕥𝕒𝕚𝕟𝕤 𝕔𝕙𝕒𝕣𝕒𝕔𝕥𝕖𝕣𝕤 𝕠𝕦𝕥𝕤𝕚𝕕𝕖 𝕥𝕙𝕖 𝔹𝕄ℙ", u"𝕋𝕙𝕚𝕤 𝕡𝕠𝕤𝕥...")

    def test_special_chars(self):
        self._test_unicode_data(u"\" This , post > contains < delimiter ] and [ other } special { characters ; that & may ' break things", u"\" This , post...")

    def test_string_interp(self):
        self._test_unicode_data(u"This post contains %s string interpolation #{syntax}", u"This post...")


@patch("notifier.digest.THREAD_TITLE_MAXLEN", 17)
class DigestThreadTestCase(TestCase):
    def _test_unicode_data(self, input_text, expected_text):
        self.assertEqual(DigestThread("0", TEST_COURSE_ID, TEST_COMMENTABLE, input_text, []).title, expected_text)

    def test_ascii(self):
        self._test_unicode_data(u"This post contains ASCII.", u"This post...")

    def test_latin_1(self):
        self._test_unicode_data(u"Thís pøst çòñtáins Lätin-1 tæxt", u"Thís pøst...")

    def test_CJK(self):
        self._test_unicode_data(u"ｲんﾉ丂 ｱo丂ｲ co刀ｲﾑﾉ刀丂 cﾌズ", u"ｲんﾉ丂 ｱo丂ｲ...")

    def test_non_BMP(self):
        self._test_unicode_data(u"𝕋𝕙𝕚𝕤 𝕡𝕠𝕤𝕥 𝕔𝕠𝕟𝕥𝕒𝕚𝕟𝕤 𝕔𝕙𝕒𝕣𝕒𝕔𝕥𝕖𝕣𝕤 𝕠𝕦𝕥𝕤𝕚𝕕𝕖 𝕥𝕙𝕖 𝔹𝕄ℙ", u"𝕋𝕙𝕚𝕤 𝕡𝕠𝕤𝕥...")

    def test_special_chars(self):
        self._test_unicode_data(u"\" This , post > contains < delimiter ] and [ other } special { characters ; that & may ' break things", u"\" This , post...")

    def test_string_interp(self):
        self._test_unicode_data(u"This post contains %s string interpolation #{syntax}", u"This post...")


class RenderDigestFlaggedTestCase(TestCase):
    """
    Test rendering of messages for digests of flagged posts
    """
    def test_posts(self):
        """
        Test that rendered messages contain the correct text
        """
        posts = [
            _get_thread_url(TEST_COURSE_ID, TEST_COMMENTABLE, i)
                for i in xrange(5)
        ]
        message = {
            "course_id": TEST_COURSE_ID,
            "recipient": usern(1),
            "posts": posts,
        }
        rendered_text = render_digest_flagged(message)
        for post in posts:
            self.assertIn(post, rendered_text)


@patch("notifier.digest.THREAD_TITLE_MAXLEN", 17)
class RenderDigestTestCase(TestCase):
    def set_digest(self, thread_title):
        self.digest = Digest([
            DigestCourse(
                TEST_COURSE_ID,
                [DigestThread(
                    "0",
                    TEST_COURSE_ID,
                    TEST_COMMENTABLE,
                    thread_title,
                    [DigestItem("test content", None, None)]
                )]
            )
        ])

    def setUp(self):
        self.user = {
            "id": "0",
            "username": "test_user",
            "preferences": {}
        }
        self.set_digest("test title")

    def _test_unicode_data(self, input_text, expected_text, expected_html=None):
        self.set_digest(input_text)
        (rendered_text, rendered_html) = render_digest(self.user, self.digest, "Test Title", "Test Description")
        self.assertIn(expected_text, rendered_text)
        self.assertIn(expected_html if expected_html else expected_text, rendered_html)

    def test_ascii(self):
        self._test_unicode_data(u"This post contains ASCII.", u"This post...")

    def test_latin_1(self):
        self._test_unicode_data(u"Thís pøst çòñtáins Lätin-1 tæxt", u"Thís pøst...")

    def test_CJK(self):
        self._test_unicode_data(u"ｲんﾉ丂 ｱo丂ｲ co刀ｲﾑﾉ刀丂 cﾌズ", u"ｲんﾉ丂 ｱo丂ｲ...")

    def test_non_BMP(self):
        self._test_unicode_data(u"𝕋𝕙𝕚𝕤 𝕡𝕠𝕤𝕥 𝕔𝕠𝕟𝕥𝕒𝕚𝕟𝕤 𝕔𝕙𝕒𝕣𝕒𝕔𝕥𝕖𝕣𝕤 𝕠𝕦𝕥𝕤𝕚𝕕𝕖 𝕥𝕙𝕖 𝔹𝕄ℙ", u"𝕋𝕙𝕚𝕤 𝕡𝕠𝕤𝕥...")

    def test_special_chars(self):
        self._test_unicode_data(
            u"\" This , post > contains < delimiter ] and [ other } special { characters ; that & may ' break things",
            u"\" This , post...",
            u"&quot; This , post..."
        )

    def test_string_interp(self):
        self._test_unicode_data(u"This post contains %s string interpolation #{syntax}", u"This post...")

    @patch("notifier.digest.deactivate")
    @patch("notifier.digest.activate")
    def test_user_lang_pref_supported(self, mock_activate, mock_deactivate):
        user_lang = "fr"
        self.user["preferences"][LANGUAGE_PREFERENCE_KEY] = user_lang
        render_digest(self.user, self.digest, "dummy", "dummy")
        mock_activate.assert_called_with(user_lang)
        mock_deactivate.assert_called()

    @patch("notifier.digest.activate")
    def test_user_lang_pref_unsupported(self, mock_activate):
        user_lang = "x-unsupported-lang"
        self.user["preferences"][LANGUAGE_PREFERENCE_KEY] = user_lang
        render_digest(self.user, self.digest, "dummy", "dummy")
        mock_activate.assert_not_called()

    @patch("notifier.digest.activate")
    def test_user_lang_pref_absent(self, mock_activate):
        if LANGUAGE_PREFERENCE_KEY in self.user["preferences"]:
            del self.user["preferences"][LANGUAGE_PREFERENCE_KEY]
        render_digest(self.user, self.digest, "dummy", "dummy")
        mock_activate.assert_not_called()
