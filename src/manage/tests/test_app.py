import os.path
import shutil
from unittest import mock, TestCase

from flask import url_for
from flask_webtest import TestApp

import forms
import questions
import settings
from app import create_app


@mock.patch.object(settings, 'CHAPTERS', ["Opstand en oorlog", "De Gouden Eeuw"])
@mock.patch.object(settings, 'ROUTES', ["opstand-en-oorlog", "de-gouden-eeuw"])
@mock.patch.object(questions, 'QUESTIONS_FILE', os.path.join(os.path.dirname(__file__), 'data/test_questions.json'))
@mock.patch.object(forms, 'IMAGES_DIR', os.path.join(os.path.dirname(__file__), 'images'))
class TestManage(TestCase):
    def setUp(self):
        self.app = create_app()
        self.w = TestApp(self.app)
        shutil.copy(
            os.path.join(os.path.dirname(__file__), 'data/questions.json'),
            os.path.join(os.path.dirname(__file__), 'data/test_questions.json')
        )

    def tearDown(self):
        os.unlink(os.path.join(os.path.dirname(__file__), 'data/test_questions.json'))

    def test_list(self):
        with self.app.test_request_context():
            response = self.w.get(url_for('question_list'), status=200)
            response.mustcontain('Tachtigjare Oorlog', 'Johannes Vermeer')

    def test_add(self):
        with self.app.test_request_context():
            response = self.w.get(url_for('question_add'), status=200)
            form = response.form
            form['chapter'] = "Opstand en oorlog"
            form['route'] = "opstand-en-oorlog"
            form['image'] = "beeldenstorm.png"
            form['question_number'] = 2
            form['title'] = "Wat is de tegenhanger van de Unie van Utrecht?"
            form['answers'] = """De Unie van Atrecht
            De Pacificatie van Gent
            De Raad van Beroerten"""
            form['answer'] = 0

            form.submit(status=302)

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
            response = self.w.get(url_for('question_add'), status=200)
            form = response.form
            form['chapter'] = "Opstand en oorlog"
            form['route'] = "opstand-en-oorlog"
            form['image'] = "beeldenstorm.png"
            form['question_number'] = 2
            form['title'] = "Wat is de tegenhanger van de Unie van Utrecht?"
            form['answers'] = """De Pacificatie van Gent
            De Raad van Beroerten"""
            form['answer'] = 0

            form.submit(status=200)

    def test_edit(self):
        with self.app.test_request_context():
            response = self.w.get(url_for('question_edit', question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'),
                                  status=200)
            form = response.form
            self.assertEqual(
                form['title'].value, "Welke gebeurtenis wordt beschouwd als het begin van de Tachtigjare Oorlog?"
            )
            self.assertEqual(
                form['question_number'].value,
                '1'
            )
            form['title'] = "Wat wordt beschouwd als het begin van de Tachtigjare Oorlog?"

            form.submit(status=302)

            data = questions.Questions.data().list()
            self.assertEqual(len(data), 2)

            question = questions.Questions.data().get('c1401fa4-23e3-4e73-aa1b-a4ac29b8db51')
            self.assertEqual(question.title, "Wat wordt beschouwd als het begin van de Tachtigjare Oorlog?")

    def test_edit_with_error(self):
        with self.app.test_request_context():
            response = self.w.get(url_for('question_edit', question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'),
                                  status=200)
            form = response.form
            self.assertEqual(
                form['title'].value, "Welke gebeurtenis wordt beschouwd als het begin van de Tachtigjare Oorlog?"
            )
            self.assertEqual(
                form['question_number'].value,
                '1'
            )
            form['title'] = ""

            form.submit(status=200)

    def test_delete(self):
        with self.app.test_request_context():
            response = self.w.get(url_for('question_delete', question_id='c1401fa4-23e3-4e73-aa1b-a4ac29b8db51'),
                                  status=200)
            form = response.form

            form.submit(status=302)

            data = questions.Questions.data().list()
            self.assertEqual(len(data), 1)

            with self.assertRaises(questions.QuestionNotFound):
                questions.Questions.data().get('c1401fa4-23e3-4e73-aa1b-a4ac29b8db51')
