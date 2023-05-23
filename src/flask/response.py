from typing import Any

from flask.json import current_app
from flask.wrappers import Response


def json_response(data: Any, status: int = 200):
    response = Response(current_app.json.dumps(data, indent=2, ensure_ascii=False), headers={
        'Access-Control-Allow-Headers': 'Authorization, Content-Type, Origin'
    }, status=status, content_type='application/json')
    return response
