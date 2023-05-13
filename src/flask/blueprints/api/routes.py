from flask import Blueprint, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash

import settings
from questions import Question, QuestionNotFound, Questions
from response import json_response
from schema import QuestionSchema


api_routes = Blueprint('api_routes', __name__, url_prefix='/api/v1')

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


@api_routes.route('/chapters', methods=['GET'])
@auth.login_required
def api_chapter_list():
    return json_response(settings.CHAPTERS)


@api_routes.route('/routes', methods=['GET'])
@auth.login_required
def api_route_list():
    return json_response(settings.ROUTES)


@api_routes.route('/images', methods=['GET'])
@auth.login_required
def api_image_list():
    return json_response(settings.IMAGES)


@api_routes.route('/questions', methods=['GET'])
@auth.login_required
def api_question_list():
    questions = Questions.data().list()
    return json_response(questions)


@api_routes.route('/questions', methods=['POST'])
@auth.login_required
def api_question_add():
    if (schema := QuestionSchema.from_json(request.get_json())) and schema.deserialize():
        question = Question.add_from_schema(schema)
        Questions.data().save(question, add=True)
        return json_response(question, status=201)
    return json_response(schema.errors, status=400)


@api_routes.route('/questions/<question_id>', methods=['GET'])
@auth.login_required
def api_question_detail(question_id):
    try:
        question = Questions.data().get(question_id)
        return json_response(question)
    except QuestionNotFound:
        return json_response({}, status=404)


@api_routes.route('/questions/<question_id>', methods=['PUT'])
@auth.login_required
def api_question_edit(question_id):
    try:
        question = Questions.data().get(question_id)
        if (schema := QuestionSchema.from_json(request.get_json())) and schema.deserialize():
            question = question.save_from_schema(schema)
            Questions.data().save(question)
            return json_response(question)
        return json_response(schema.errors, status=400)
    except QuestionNotFound:
        return json_response({}, 404)


@api_routes.route('/questions/<question_id>', methods=['DELETE'])
@auth.login_required
def api_question_delete(question_id):
    try:
        question = Questions.data().get(question_id)
        Questions.data().delete(question)
        return json_response({}, status=204)
    except QuestionNotFound:
        return json_response({}, 404)
