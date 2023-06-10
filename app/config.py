import pathlib
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api

BASE_DIR = pathlib.Path(__file__).parent

UPLOAD_FOLDER = pathlib.Path.joinpath(BASE_DIR, 'media')

ALLOWED_FORMATS = ['wav', ]


class Config:
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY', '68f3acbf-2f87-4e5c-a7d6-f1f09526440f')
    SQLALCHEMY_DATABASE_URI = "sqlite:///my.db"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


app = Flask(__name__)

app.config.from_object(DevelopmentConfig)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
