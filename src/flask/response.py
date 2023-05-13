from typing import Any

from flask import jsonify


def json_response(data: Any, status: int = 200):
    response = jsonify(data)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, Origin'
    response.status = status
    return response
