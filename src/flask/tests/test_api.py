import base64
import json
import os.path
import shutil
from unittest import mock, TestCase
from werkzeug.security import generate_password_hash

from flask import url_for
from flask_webtest import TestApp

import questions
import schema
import settings
from app import create_app
from blueprints.api import routes


@mock.patch.object(settings, 'CHAPTERS', ["Opstand en oorlog", "De Gouden Eeuw"])
@mock.patch.object(settings, 'ROUTES', ["opstand-en-oorlog", "de-gouden-eeuw"])
@mock.patch.object(schema, 'IMAGES_DIR', os.path.join(os.path.dirname(__file__), 'images'))
@mock.patch.object(questions, 'QUESTIONS_FILE', os.path.join(os.path.dirname(__file__), 'data/test_questions.json'))
@mock.patch.object(routes, 'users', {'tester': generate_password_hash('foobar')})
class TestApiRoutes(TestCase):

    def setUp(self):
        self.app = create_app()
        self.w = TestApp(self.app)
        shutil.copy(
            os.path.join(os.path.dirname(__file__), 'data/questions.json'),
            os.path.join(os.path.dirname(__file__), 'data/test_questions.json')
        )

    def tearDown(self):
        os.unlink(os.path.join(os.path.dirname(__file__), 'data/test_questions.json'))

    def test_chapters(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('api_routes.api_chapter_list'), status=200)
            response.mustcontain('Opstand en oorlog', 'De Gouden Eeuw')

    def test_routes(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('api_routes.api_route_list'), status=200)
            response.mustcontain('opstand-en-oorlog', 'de-gouden-eeuw')

    def test_images(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('api_routes.api_image_list'), status=200)
            response.mustcontain('beeldenstorm.png', 'nachtwacht.png')

    def test_list(self):
        with self.app.test_request_context():
            response = self._make_request('get', url_for('api_routes.api_question_list'), status=200)
            response.mustcontain('Tachtigjare Oorlog', 'Johannes Vermeer')

    def test_add(self):
        with self.app.test_request_context():
            data = {
                'chapter': "Opstand en oorlog",
                'route': "opstand-en-oorlog",
                'image': "beeldenstorm.png",
                'question_number': 2,
                'title': "Wat is de tegenhanger van de Unie van Utrecht?",
                'answers': [
                    "De Unie van Atrecht",
                    "De Pacificatie van Gent",
                    "De Raad van Beroerten"
                ],
                'answer': 0
            }
            self._make_request('post_json', url_for('api_routes.api_question_add'), params=json.dumps(data), status=201)

            data = questions.Questions.data().list()
            self.assertEqual(len(data), 3)

            question_id = data[1].question_id
            question = questions.Questions.data().get(question_id)
            self.assertEqual(question.chapter, "Opstand en oorlog")
            self.assertEqual(question.route, "opstand-en-oorlog")
            self.assertEqual(question.title, "Wat is de tegenhanger van de Unie van Utrecht?")
            self.assertEqual(question.question_number, 2)

    def test_add_with_error(self):
        with self.app.test_request_context():
            data = {
                'chapter': "Opstand en oorlog",
                'route': "opstand-en-oorlog",
                'image': "beeldenstorm.png",
                'question_number': 2,
                'title': "Wat is de tegenhanger van de Unie van Utrecht?",
                'answers': [
                    "De Pacificatie van Gent",
                    "De Raad van Beroerten"
                ],
                'answer': 0
            }
            self._make_request('post_json', url_for('api_routes.api_question_add'), params=json.dumps(data), status=400)

    def test_edit(self):
        with self.app.test_request_context():
            data = {
                "chapter": "Opstand en oorlog",
                "route": "opstand-en-oorlog",
                "image": "beeldenstorm.png",
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
                    'api_routes.api_question_edit',
                    question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'
                ),
                params=json.dumps(data),
                status=200
            )

            data = questions.Questions.data().list()
            self.assertEqual(len(data), 2)

            question = questions.Questions.data().get('c1401fa4-23e3-4e73-aa1b-a4ac29b8db51')
            self.assertEqual(question.title, "Wat wordt beschouwd als het begin van de Tachtigjare Oorlog?")

    def test_edit_with_error(self):
        with self.app.test_request_context():
            data = {
                "chapter": "Opstand en oorlog",
                "route": "opstand-en-oorlog",
                "image": "beeldenstorm.png",
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
                    'api_routes.api_question_edit',
                    question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'
                ),
                params=json.dumps(data),
                status=400
            )

    def test_delete(self):
        with self.app.test_request_context():
            self._make_request(
                'delete_json',
                url_for(
                    'api_routes.api_question_edit',
                    question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'
                ),
                status=204
            )

            data = questions.Questions.data().list()
            self.assertEqual(len(data), 1)

            with self.assertRaises(questions.QuestionNotFound):
                questions.Questions.data().get('c1401fa4-23e3-4e73-aa1b-a4ac29b8db51')

    def _make_request(self, method, path, **kwargs):
        func = getattr(self.w, method)
        return func(
            path,
            headers={
                'Authorization': 'Basic: {}'.format(base64.b64encode(b'tester:foobar').decode()),
                'Content-Type': 'application/json'
            },
            **kwargs
        )
