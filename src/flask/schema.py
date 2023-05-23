import re
from typing import Dict

import colander
from dacite import from_dict
from flask.wrappers import Request


re_route = re.compile(r'^[a-z0-9-]+$')


class WrappedSchema:

    _schema: colander.Schema

    def __init__(self, data: Dict):
        self.data = data
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
    def from_request(cls, request: Request):
        return cls(request.get_json())


def valid_image(node: colander.SchemaNode, value: str):
    from data import Images

    if value not in Images.list():
        raise colander.Invalid(node, "Invalid image")


class ColanderChapterSchema(colander.Schema):
    chapter = colander.SchemaNode(colander.String())
    route = colander.SchemaNode(colander.String(), validator=colander.Regex(re_route))
    image = colander.SchemaNode(colander.String(), validator=valid_image)


class ColanderChapterSequenceSchema(colander.SequenceSchema):
    chapter = ColanderChapterSchema()


class ColanderChaptersSchema(colander.MappingSchema):
    chapters = ColanderChapterSequenceSchema()


class ChapterSchema(WrappedSchema):

    _schema = ColanderChaptersSchema()


def valid_chapter(node: colander.SchemaNode, value: str):
    from data import Chapters

    if value not in Chapters.data().chapters():
        raise colander.Invalid(node, "Invalid chapter")


def valid_answers(node: colander.SchemaNode, value: str):
    if len(value) != 3 or any([x.strip() == '' for x in value]):
        raise colander.Invalid(node, "Three answers required")


class ColanderQuestionSchema(colander.Schema):
    chapter = colander.SchemaNode(colander.String(), validator=valid_chapter)
    question_number = colander.SchemaNode(colander.Int(), validator=colander.Range(1, None))
    title = colander.SchemaNode(colander.String())
    answers = colander.SchemaNode(colander.List(), validator=valid_answers)
    answer = colander.SchemaNode(colander.Int(), validator=colander.OneOf([0, 1, 2]))


class QuestionSchema(WrappedSchema):

    _schema = ColanderQuestionSchema()
