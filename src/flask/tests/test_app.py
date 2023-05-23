import os
from unittest import mock

from flask import url_for

import data as app_data
import settings
from tests.base import RoutesTestCase


@mock.patch.object(app_data, 'CHAPTERS_FILE', os.path.join(os.path.dirname(__file__), 'json/chapters.json'))
@mock.patch.object(app_data, 'QUESTIONS_FILE', os.path.join(os.path.dirname(__file__), 'json/questions.json'))
@mock.patch.object(settings, 'IMAGES_DIR', os.path.join(os.path.dirname(__file__), 'images'))
class TestAppRoutes(RoutesTestCase):

    def test_chapters_list(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('app_routes.api_chapters_list'), status=200)
            response.mustcontain(
                'Opstand en oorlog', 'opstand-en-oorlog',
                'De Gouden Eeuw', 'de-gouden-eeuw',
                no=['beeldenstorm.png', 'nachtwacht.png']
            )

    def test_question_list(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('app_routes.api_question_list'), status=200)
            response.mustcontain(
                'c1401fa4-23e3-4e73-aa1b-a4ac29b8db51',
                '70582011-083a-4de6-aa1d-c325a884084f'
            )

    def test_question_search(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('app_routes.api_question_search') + '?questionNumber=2',
                                          status=200)
            response.mustcontain('70582011-083a-4de6-aa1d-c325a884084f', 'nachtwacht.png', 'de-gouden-eeuw')

    def test_question_search_not_found(self):
        with self.app.test_request_context():
            self._make_request('get', url_for('app_routes.api_question_search') + '?questionNumber=3', status=404)

    def test_question_search_missing_arguments(self):
        with self.app.test_request_context():
            self._make_request('get', url_for('app_routes.api_question_search'), status=400)

    def test_image(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('app_routes.api_image', image='nachtwacht.png'),
                                          status=200)

    def _make_request(self, method, path, **kwargs):
        func = getattr(self.w, method)
        return func(
            path,
            **kwargs
        )
