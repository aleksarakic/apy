from os import environ, path
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config(object):

	# app config
    FLASK_ENV = environ.get('FLASK_ENV', default='development')
    TESTING = False
    DEBUG = True
    FLASK_APP = 'wsgi.py'
    FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
    SECRET_KEY = environ.get('SECRET_KEY')

    # db config
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True