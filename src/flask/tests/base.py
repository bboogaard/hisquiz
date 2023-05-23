import os.path
import shutil
from unittest import TestCase

from flask_webtest import TestApp

from app import create_app


class RoutesTestCase(TestCase):

    def setUp(self):
        self.app = create_app()
        self.w = TestApp(self.app)
        shutil.copytree(
            os.path.join(os.path.dirname(__file__), 'data/json'),
            os.path.join(os.path.dirname(__file__), 'json')
        )
        shutil.copytree(
            os.path.join(os.path.dirname(__file__), 'data/images'),
            os.path.join(os.path.dirname(__file__), 'images')
        )

    def tearDown(self):
        shutil.rmtree(os.path.join(os.path.dirname(__file__), 'json'))
        shutil.rmtree(os.path.join(os.path.dirname(__file__), 'images'))
