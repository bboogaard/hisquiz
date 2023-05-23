import os

from flask import Blueprint, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

import settings
from data import Chapters, Images, Question, QuestionNotFound, Questions
from response import json_response
from schema import ChapterSchema, QuestionSchema


manage_routes = Blueprint('manage_routes', __name__, url_prefix='/api/v1/manage')

auth = HTTPBasicAuth()

users = {
    settings.API_USERNAME: settings.API_PASSWORD
}


@auth.verify_password
def check_password(username, password):
    if username in users and \
            check_password_hash(users.get(username), password):
        return username


@auth.error_handler
def error_handler(status):
    return json_response({}, status)


@manage_routes.route('/chapters', methods=['GET'])
@auth.login_required
def api_chapters_list():
    chapters = Chapters.data().list()
    return json_response(chapters)


@manage_routes.route('/chapters', methods=['PUT'])
@auth.login_required
def api_chapters_edit():
    if (schema := ChapterSchema.from_request(request)) and schema.deserialize():
        chapters = Chapters.save_from_schema(schema)
        return json_response(chapters)
    return json_response(schema.errors, status=400)


@manage_routes.route('/images', methods=['GET'])
@auth.login_required
def api_images_list():
    return json_response(Images.list())


@manage_routes.route('/images', methods=['PUT', 'POST'])
@auth.login_required
def api_images_edit():
    existing = request.form.getlist('images')
    new = request.files.getlist('images')
    if any([os.path.splitext(file.filename)[1] != '.png' for file in new]):
        return json_response({'non_field_error': 'Extension not allowed'}, status=400)
    Images.save(existing, new)
    return json_response({})


@manage_routes.route('/questions', methods=['GET'])
@auth.login_required
def api_question_list():
    questions = Questions.data().list()
    return json_response(questions)


@manage_routes.route('/questions', methods=['POST'])
@auth.login_required
def api_question_add():
    if (schema := QuestionSchema.from_request(request)) and schema.deserialize():
        question = Question.add_from_schema(schema)
        Questions.data().save(question, add=True)
        return json_response(question, status=201)
    return json_response(schema.errors, status=400)


@manage_routes.route('/questions/<question_id>', methods=['GET'])
@auth.login_required
def api_question_detail(question_id):
    try:
        question = Questions.data().get(question_id=question_id)
        return json_response(question)
    except QuestionNotFound:
        return json_response({}, status=404)


@manage_routes.route('/questions/<question_id>', methods=['PUT'])
@auth.login_required
def api_question_edit(question_id):
    try:
        question = Questions.data().get(question_id=question_id)
        if (schema := QuestionSchema.from_request(request)) and schema.deserialize():
            question = question.save_from_schema(schema)
            Questions.data().save(question)
            return json_response(question)
        return json_response(schema.errors, status=400)
    except QuestionNotFound as exc:
        return json_response(str(exc), 404)


@manage_routes.route('/questions/<question_id>', methods=['DELETE'])
@auth.login_required
def api_question_delete(question_id):
    try:
        question = Questions.data().get(question_id=question_id)
        Questions.data().delete(question)
        return json_response({}, status=204)
    except QuestionNotFound:
        return json_response({}, 404)
