import json
import operator
import os
import uuid
from dataclasses import asdict, dataclass, replace
from typing import List, Optional, TextIO

from camel_converter import dict_to_snake, dict_to_camel
from dacite import from_dict

import settings
from forms import QuestionForm


class QuestionNotFound(Exception):
    ...


@dataclass
class Question:
    chapter: str
    route: str
    image: str
    question_number: int
    title: str
    answers: List[str]
    answer: int
    answered: Optional[int] = None
    question_id: Optional[str] = None

    def __str__(self):
        return f'{self.question_number}. {self.title}'

    @property
    def chapter_num(self):
        return settings.CHAPTERS.index(self.chapter) + 1

    @classmethod
    def add_from_form(cls, form: QuestionForm):
        return Question(**cls._kwargs_from_form(form))

    def save_from_form(self, form: QuestionForm):
        return replace(self, **self._kwargs_from_form(form, question_id=self.question_id))

    @staticmethod
    def _kwargs_from_form(form: QuestionForm, question_id: str = None):
        return dict(
            chapter=form.chapter.data,
            route=form.route.data,
            image=form.image.data,
            question_number=form.question_number.data,
            title=form.title.data,
            answers=list(map(lambda x: x.strip(), form.answers.data.split('\n')))[:3],
            answer=form.answer.data,
            question_id=question_id if question_id else str(uuid.uuid4())
        )


QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), 'dist/data/questions.json')


class Questions:

    _questions: List[Question]

    def __init__(self, source: TextIO):
        self._questions = list(map(lambda x: from_dict(Question, dict_to_snake(x)), json.loads(source.read())))

    @classmethod
    def data(cls) -> 'Questions':
        return cls(open(QUESTIONS_FILE, 'r'))

    def list(self):
        return self._questions

    def get(self, question_id: str):
        question = next(filter(lambda x: x.question_id == question_id, self._questions), None)
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
