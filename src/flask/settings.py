import environ
import os

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

SECRET_KEY = env.str('SECRET_KEY', 'dev')

DATA_DIR = env.str('DATA_DIR', '/data')
JSON_DIR = os.path.join(DATA_DIR, 'json')
IMAGES_DIR = os.path.join(DATA_DIR, 'images')
IMAGES_URL = env.str('IMAGES_URL', '/images/')

API_USERNAME = env.str('API_USERNAME')
API_PASSWORD = env.str('API_PASSWORD')

API_ORIGINS = env.list('API_ORIGINS', default=[]) or '*'


