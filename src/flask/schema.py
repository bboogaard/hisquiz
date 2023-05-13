import json
import os
from typing import Dict

import colander

import settings


IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'dist/images')


def valid_answers(node, value):
    if len(value) != 3 or any([x.strip() == '' for x in value]):
        raise colander.Invalid(node, "Three answers required")


class ColanderQuestionSchema(colander.Schema):
    chapter = colander.SchemaNode(colander.String(), validator=colander.OneOf(settings.CHAPTERS))
    route = colander.SchemaNode(colander.String(), validator=colander.OneOf(settings.ROUTES))
    image = colander.SchemaNode(colander.String(), validator=colander.OneOf(
        list(filter(lambda x: x.endswith('png'), os.listdir(IMAGES_DIR)))))
    question_number = colander.SchemaNode(colander.Int(), validator=colander.Range(1, None))
    title = colander.SchemaNode(colander.String())
    answers = colander.SchemaNode(colander.List(), validator=valid_answers)
    answer = colander.SchemaNode(colander.Int(), validator=colander.OneOf([0, 1, 2]))


class QuestionSchema:

    def __init__(self, data: Dict):
        self.data = data
        self._schema = ColanderQuestionSchema()
        self._deserialized = {}
        self._errors = {}

    @property
    def deserialized(self):
        return self._deserialized

    @property
    def errors(self):
        return self._errors

    def deserialize(self):
        try:
            self._deserialized = self._schema.deserialize(self.data)
            return True
        except colander.Invalid as exc:
            self._errors = exc.asdict()
        except Exception as exc:
            self._errors = {
                'non_field_error': str(exc)
            }

        return False

    @classmethod
    def from_json(cls, json_str: str):
        try:
            return cls(json.loads(json_str))
        except ValueError:
            return None
