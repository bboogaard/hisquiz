import environ
env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
# reading .env file
environ.Env.read_env()

SECRET_KEY = env.str('SECRET_KEY', 'dev')

CHAPTERS = env.list('CHAPTERS', [])
ROUTES = env.list('ROUTES', [])
