from camel_converter import dict_to_snake
from flask import Blueprint, request, send_from_directory

import settings
from data import Chapter, ChapterNotFound, Chapters, Image, QuestionNotFound, Questions
from response import json_response


app_routes = Blueprint('app_routes', __name__, url_prefix='/api/v1/app')


@app_routes.route('/chapters', methods=['GET'])
def api_chapters_list():
    chapters = Chapters.data().only('chapter', 'route').list()
    return json_response(chapters)


@app_routes.route('/questions', methods=['GET'])
def api_question_list():
    answers = Questions.data().only('question_id', 'answer', 'answered').list()
    return json_response(answers)


@app_routes.route('/questions/find', methods=['GET'])
def api_question_search():
    try:
        question = Questions.data(meta_data=True).join('self', Chapter).join('chapter', Image).filter(
            **dict_to_snake(request.args)).get()
        return json_response(question)
    except (ChapterNotFound, QuestionNotFound) as exc:
        return json_response(str(exc), status=404)
    except ValueError as exc:
        return json_response(str(exc), status=400)


@app_routes.route('/images/<string:image>', methods=['GET'])
def api_image(image):
    return send_from_directory(settings.IMAGES_DIR, image)
