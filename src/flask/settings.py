import environ
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

SECRET_KEY = env.str('SECRET_KEY', 'dev')

CHAPTERS = env.list('CHAPTERS', [])
ROUTES = env.list('ROUTES', [])

IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'dist/images')
IMAGES = list(filter(lambda x: x.endswith('png'), os.listdir(IMAGES_DIR)))

API_USERNAME = env.str('API_USERNAME')
API_PASSWORD = env.str('API_PASSWORD')

API_ORIGINS = env.list('API_ORIGINS', default=[]) or '*'
