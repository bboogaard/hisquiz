import dataclasses
from typing import Any, Union

from camel_converter import dict_to_camel, dict_to_snake
from flask import Flask
from flask_cors import CORS
from flask.json.provider import _default, DefaultJSONProvider

import settings
from blueprints.api.app import app_routes
from blueprints.api.manage import manage_routes


def json_default(o: Any) -> Any:
    if dataclasses.is_dataclass(o):
        return dict_to_camel(dataclasses.asdict(o))

    return _default(o)


def to_snake_keys(data: Any) -> Any:
    if isinstance(data, list):
        return list(map(to_snake_keys, data))
    elif isinstance(data, dict):
        return dict_to_snake(data)
    else:
        return data


class JSONProvider(DefaultJSONProvider):

    ensure_ascii = False

    def dumps(self, obj: Any, **kwargs: Any) -> str:
        kwargs.setdefault('default', json_default)
        return super().dumps(obj, **kwargs)

    def loads(self, s: Union[str, bytes], **kwargs: Any) -> Any:
        return to_snake_keys(super().loads(s, **kwargs))


def create_app():
    flask_app = Flask(__name__)
    flask_app.secret_key = settings.SECRET_KEY
    flask_app.json = JSONProvider(flask_app)

    CORS(flask_app, resources={r"/api/*": {"origins": settings.API_ORIGINS}})

    flask_app.register_blueprint(app_routes)
    flask_app.register_blueprint(manage_routes)

    return flask_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
