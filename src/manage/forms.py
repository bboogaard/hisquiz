import os

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from wtforms import fields

import settings


IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'dist/images')


class QuestionForm(FlaskForm):
    chapter = fields.SelectField('Chapter')
    route = fields.SelectField('Route')
    image = fields.SelectField('Image')
    question_number = fields.IntegerField('Question number', validators=[DataRequired(), NumberRange(min=1)])
    title = fields.StringField('Title', validators=[DataRequired(), Length(1, 100)])
    answers = fields.TextAreaField('Answers', validators=[DataRequired()])
    answer = fields.SelectField('Answer', choices=[0, 1, 2], coerce=int)
    submit = fields.SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chapter.choices = settings.CHAPTERS
        self.route.choices = settings.ROUTES
        self.image.choices = list(filter(lambda x: x.endswith('png'), os.listdir(IMAGES_DIR)))

    def validate_answers(self, field):
        if len(field.data.split('\n')) != 3:
            raise ValidationError("There should be three answers")
