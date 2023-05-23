import os
import base64
from unittest import mock
from werkzeug.security import generate_password_hash

from flask import url_for

import data as app_data
import settings
from blueprints.api import manage
from tests.base import RoutesTestCase
from tests.utils import generate_image


@mock.patch.object(app_data, 'CHAPTERS_FILE', os.path.join(os.path.dirname(__file__), 'json/chapters.json'))
@mock.patch.object(app_data, 'QUESTIONS_FILE', os.path.join(os.path.dirname(__file__), 'json/questions.json'))
@mock.patch.object(settings, 'IMAGES_DIR', os.path.join(os.path.dirname(__file__), 'images'))
@mock.patch.object(manage, 'users', {'tester': generate_password_hash('foobar')})
class TestManageRoutes(RoutesTestCase):

    def test_chapters_list(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('manage_routes.api_chapters_list'), status=200)
            response.mustcontain(
                'Opstand en oorlog', 'opstand-en-oorlog', 'beeldenstorm.png',
                'De Gouden Eeuw', 'de-gouden-eeuw', 'nachtwacht.png'
            )

    def test_chapters_edit(self):
        with self.app.test_request_context():
            data = {
                "chapters": [
                    {
                        "chapter": "Opstand en oorlog",
                        "route": "opstand-en-oorlog",
                        "image": "beeldenstorm.png"
                    },
                    {
                        "chapter": "De Gouden Eeuw",
                        "route": "de-gouden-eeuw",
                        "image": "nachtwacht.png"
                    },
                    {
                        "chapter": "Patriciërs en patriotten",
                        "route": "patriciers-en-patriotten",
                        "image": "nachtwacht.png"
                    }
                ]
            }
            self._make_request('put_json', url_for('manage_routes.api_chapters_edit'), params=data, status=200)

            data = app_data.Chapters.data().chapters()
            self.assertEqual(len(data), 3)

            data = app_data.Chapters.data().routes()
            self.assertEqual(len(data), 3)

    def test_chapters_edit_with_error(self):
        with self.app.test_request_context():
            data = {
                "chapters": [
                    {
                        "chapter": "Opstand en oorlog",
                        "route": "opstand-en-oorlog",
                        "image": "beeldenstorm.png"
                    },
                    {
                        "chapter": "De Gouden Eeuw",
                        "route": "de-gouden-eeuw",
                        "image": "nachtwacht.png"
                    },
                    {
                        "chapter": "Patriciërs en patriotten",
                        "route": "",
                        "image": "nachtwacht.png"
                    }
                ]
            }
            self._make_request('put_json', url_for('manage_routes.api_chapters_edit'), params=data, status=400)

    def test_images_list(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('manage_routes.api_images_list'), status=200)
            response.mustcontain('beeldenstorm.png', 'nachtwacht.png')

    def test_images_edit(self):
        with self.app.test_request_context():
            image = generate_image(1, 1)
            data = {
                'images': [
                    'beeldenstorm.png',
                    'nachtwacht.png'
                ]
            }
            self._make_request('put', url_for('manage_routes.api_images_edit'), params=data,
                               upload_files=[('images', 'patriotten.png', image.read())],
                               status=200)
            images = app_data.Images.list()
            self.assertEqual(len(images), 3)

    def test_images_edit_with_delete(self):
        with self.app.test_request_context():
            image = generate_image(1, 1)
            data = {
                'images': [
                    'beeldenstorm.png'
                ]
            }
            self._make_request('put', url_for('manage_routes.api_images_edit'), params=data,
                               upload_files=[('images', 'patriotten.png', image.read())],
                               status=200)
            images = app_data.Images.list()
            self.assertEqual(len(images), 2)

    def test_images_edit_with_error(self):
        with self.app.test_request_context():
            image = generate_image(1, 1, format='JPEG')
            data = {
                'images': [
                    'beeldenstorm.png',
                    'nachtwacht.png'
                ]
            }
            self._make_request('put', url_for('manage_routes.api_images_edit'), params=data,
                               upload_files=[('images', 'patriotten.jpg', image.read())],
                               status=400)

    def test_list(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('manage_routes.api_question_list'), status=200)
            response.mustcontain('Tachtigjare Oorlog', 'Johannes Vermeer')

    def test_add(self):
        with self.app.test_request_context():
            data = {
                'chapter': "Opstand en oorlog",
                'question_number': 2,
                'title': "Wat is de tegenhanger van de Unie van Utrecht?",
                'answers': [
                    "De Unie van Atrecht",
                    "De Pacificatie van Gent",
                    "De Raad van Beroerten"
                ],
                'answer': 0
            }
            self._make_request('post_json', url_for('manage_routes.api_question_add'), params=data, status=201)

            data = app_data.Questions.data().list()
            self.assertEqual(len(data), 3)

            question_id = data[1].question_id
            question = app_data.Questions.data().get(question_id=question_id)
            self.assertEqual(question.chapter, "Opstand en oorlog")
            self.assertEqual(question.title, "Wat is de tegenhanger van de Unie van Utrecht?")
            self.assertEqual(question.question_number, 2)

    def test_add_with_error(self):
        with self.app.test_request_context():
            data = {
                'chapter': "Opstand en oorlog",
                'question_number': 2,
                'title': "Wat is de tegenhanger van de Unie van Utrecht?",
                'answers': [
                    "De Pacificatie van Gent",
                    "De Raad van Beroerten"
                ],
                'answer': 0
            }
            self._make_request('post_json', url_for('manage_routes.api_question_add'), params=data, status=400)

    def test_edit(self):
        with self.app.test_request_context():
            data = {
                "chapter": "Opstand en oorlog",
                "question_number": 1,
                "title": "Wat wordt beschouwd als het begin van de Tachtigjare Oorlog?",
                "answers": [
                    "Aanbieding van het Smeekschrift der Edelen",
                    "De Slag bij Heiligerlee",
                    "Het Banedict van Filips II"
                ],
                "answer": 1
            }
            self._make_request(
                'put_json',
                url_for(
                    'manage_routes.api_question_edit',
                    question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'
                ),
                params=data,
                status=200
            )

            data = app_data.Questions.data().list()
            self.assertEqual(len(data), 2)

            question = app_data.Questions.data().get(question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51')
            self.assertEqual(question.title, "Wat wordt beschouwd als het begin van de Tachtigjare Oorlog?")

    def test_edit_with_error(self):
        with self.app.test_request_context():
            data = {
                "chapter": "Opstand en oorlog",
                "question_number": 1,
                "title": "",
                "answers": [
                    "Aanbieding van het Smeekschrift der Edelen",
                    "De Slag bij Heiligerlee",
                    "Het Banedict van Filips II"
                ],
                "answer": 1
            }
            self._make_request(
                'put_json',
                url_for(
                    'manage_routes.api_question_edit',
                    question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'
                ),
                params=data,
                status=400
            )

    def test_delete(self):
        with self.app.test_request_context():
            self._make_request(
                'delete_json',
                url_for(
                    'manage_routes.api_question_delete',
                    question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'
                ),
                status=204
            )

            data = app_data.Questions.data().list()
            self.assertEqual(len(data), 1)

            with self.assertRaises(app_data.QuestionNotFound):
                app_data.Questions.data().get(question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51')

    def _make_request(self, method, path, **kwargs):
        func = getattr(self.w, method)
        headers = {
            'Authorization': 'Basic: {}'.format(base64.b64encode(b'tester:foobar').decode()),
        }
        headers.update(kwargs.pop('headers', {}))
        return func(
            path,
            headers=headers,
            **kwargs
        )
