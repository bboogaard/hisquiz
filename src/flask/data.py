import json
import operator
import os
import uuid
from dataclasses import asdict, dataclass, make_dataclass, replace
from typing import Any, Dict, List, Optional, TextIO, Union

from camel_converter import dict_to_snake, dict_to_camel
from dacite import from_dict
from werkzeug.datastructures.file_storage import FileStorage
from werkzeug.utils import secure_filename

import settings
from schema import ChapterSchema, QuestionSchema
from utils import nested_getattr


CHAPTERS_FILE = os.path.join(settings.JSON_DIR, 'chapters.json')


class ORMDataClass:

    def join(self, data_class: dataclass):
        raise NotImplementedError()

    def only(self, *fields) -> dataclass:
        new_class = make_dataclass(self.__class__.__name__, fields)
        return new_class(**{
            field: getattr(self, field)
            for field in fields
        })


class ORMData:

    _item_attr: str

    @property
    def items(self):
        return getattr(self, self._item_attr)

    def join(self, field: str, data_class: dataclass):

        def _join(source: Any, attr: Optional[str]):
            target = nested_getattr(source, attr) if attr else source
            target.join(data_class)
            return source

        setattr(self, self._item_attr, list(map(lambda x: _join(x, field if field != 'self' else None), self.items)))
        return self

    def only(self, *fields):
        if not fields:
            return self
        setattr(self, self._item_attr, list(map(lambda x: x.only(*fields), self.items)))
        return self


class ImageNotFound(Exception):

    def __init__(self):
        super().__init__("Image not found")


class ChapterNotFound(Exception):

    def __init__(self):
        super().__init__("Chapter not found")


class QuestionNotFound(Exception):

    def __init__(self):
        super().__init__("Question not found")


@dataclass
class Image:
    url: str


@dataclass
class Chapter(ORMDataClass):
    chapter: str
    route: str
    image: Union[str, Image]

    def join(self, data_class: dataclass):
        if data_class == Image:
            self.image = Image(settings.IMAGES_URL + self.image)
            return

        raise NotImplementedError()


class Chapters(ORMData):

    _chapters: List[Chapter]

    _item_attr = '_chapters'

    def __init__(self, source: TextIO):
        self._chapters = list(map(lambda x: from_dict(Chapter, dict_to_snake(x)), json.loads(source.read())))

    @classmethod
    def data(cls) -> 'Chapters':
        return cls(open(CHAPTERS_FILE, 'r'))

    def list(self):
        return self._chapters

    def chapters(self):
        return [chapter.chapter for chapter in self._chapters]

    def routes(self):
        return [chapter.route for chapter in self._chapters]

    @classmethod
    def save_from_schema(cls, schema: ChapterSchema) -> List[Chapter]:
        chapters = [
            Chapter(**chapter)
            for chapter in schema.deserialized['chapters']
        ]
        with open(CHAPTERS_FILE, 'w') as fh:
            fh.write(json.dumps(list(map(lambda x: dict_to_camel(asdict(x)), chapters)), indent=2, ensure_ascii=False))
        return chapters


class Images:

    @classmethod
    def list(cls):
        return list(filter(lambda x: x.endswith('png'), os.listdir(settings.IMAGES_DIR)))

    @classmethod
    def save(cls, existing: List[str], new: List[FileStorage]):
        for image in cls.list():
            if image not in existing:
                os.unlink(os.path.join(settings.IMAGES_DIR, image))
        for file in new:
            filename = secure_filename(file.filename)
            file.save(os.path.join(settings.IMAGES_DIR, filename))


@dataclass
class Question(ORMDataClass):
    chapter: Union[str, Chapter]
    question_number: int
    title: str
    answers: List[str]
    answer: int
    answered: Optional[int] = None
    question_id: Optional[str] = None
    meta: Optional[Dict] = None

    def __str__(self):
        return f'{self.question_number}. {self.title}'

    @property
    def chapter_num(self):
        chapter = self.chapter if isinstance(self.chapter, str) else self.chapter.chapter
        try:
            return Chapters.data().chapters().index(chapter) + 1
        except ValueError:
            return 0

    @classmethod
    def add_from_schema(cls, schema: QuestionSchema):
        return Question(**cls._kwargs_from_schema(schema))

    def save_from_schema(self, schema: QuestionSchema):
        return replace(self, **self._kwargs_from_schema(schema, question_id=self.question_id))

    @staticmethod
    def _kwargs_from_schema(schema: QuestionSchema, question_id: str = None):
        return dict(
            chapter=schema.deserialized['chapter'],
            question_number=schema.deserialized['question_number'],
            title=schema.deserialized['title'],
            answers=schema.deserialized['answers'],
            answer=schema.deserialized['answer'],
            question_id=question_id if question_id else str(uuid.uuid4())
        )

    def join(self, data_class: dataclass):
        if data_class == Chapter:
            self.chapter = next(filter(lambda c: c.chapter == self.chapter, Chapters.data().list()), None)
            if self.chapter is None:
                raise ChapterNotFound()
            return

        raise NotImplementedError()


QUESTIONS_FILE = os.path.join(settings.JSON_DIR, 'questions.json')


class Questions(ORMData):

    _questions: List[Question]

    _item_attr = '_questions'

    def __init__(self, source: TextIO, meta_data: Optional[bool] = False):
        self._questions = list(map(lambda x: from_dict(Question, dict_to_snake(x)), json.loads(source.read())))
        if meta_data:
            self._questions = self._with_meta(self._questions)

    @classmethod
    def data(cls, meta_data: Optional[bool] = False) -> 'Questions':
        return cls(open(QUESTIONS_FILE, 'r'), meta_data)

    def filter(self, **kwargs):
        if not kwargs:
            raise ValueError("Missing arguments")
        self._questions = self._filter(self._questions, **kwargs)
        return self

    def list(self):
        return self._questions

    def get(self, **kwargs):
        if kwargs:
            self._questions = self._filter(self._questions, **kwargs)
        question = self._questions[0] if self._questions else None
        if question is None:
            raise QuestionNotFound()
        return question

    def save(self, question: Question, add: bool = False):
        if add:
            self._questions.append(question)
        self._questions = list(
            sorted(
                map(lambda x: question if question.question_id == x.question_id else x, self._questions),
                key=operator.attrgetter('question_number')
            )
        )
        self._write_file()

    def delete(self, question: Question):
        self._questions = list(
            sorted(
                filter(
                    None,
                    map(lambda x: None if question.question_id == x.question_id else x, self._questions)
                ),
                key=operator.attrgetter('question_number')
            )
        )
        self._write_file()

    @staticmethod
    def _with_meta(questions: List[Question]) -> List[Question]:
        question_count = len(questions)

        def get_meta(index: int) -> Dict:
            try:
                prev_question = questions[index - 1]
            except IndexError:
                prev_question = None
            try:
                next_question = questions[index + 1]
            except IndexError:
                next_question = None
            return dict(
                prev_question=prev_question.question_id if prev_question else None,
                next_question=next_question.question_id if next_question else None,
                question_count=question_count
            )

        return list(map(lambda x: replace(x[1], meta=get_meta(x[0])), enumerate(questions)))

    @staticmethod
    def _filter(questions: List[Question], **kwargs) -> List[Question]:
        return list(
            filter(lambda x: all(str(nested_getattr(x, key)) == val for key, val in kwargs.items()), questions)
        )

    def _write_file(self):
        self._questions = list(
            map(
                lambda x: replace(x[1], question_number=x[0]), enumerate(
                    sorted(self._questions, key=lambda x: (x.chapter_num, x.question_number)), start=1
                )
            )
        )
        with open(QUESTIONS_FILE, 'w') as fh:
            fh.write(
                json.dumps(
                    list(map(lambda x: dict_to_camel(asdict(x)), self._questions)), indent=2,
                    ensure_ascii=False
                )
            )
