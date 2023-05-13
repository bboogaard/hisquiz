from flask import Flask
from flask_cors import CORS

import settings
from blueprints.api.routes import api_routes


def create_app():
    flask_app = Flask(__name__)
    flask_app.secret_key = settings.SECRET_KEY

    print(settings.API_ORIGINS)

    CORS(flask_app, resources={r"/api/*": {"origins": settings.API_ORIGINS}})

    flask_app.register_blueprint(api_routes)

    return flask_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
