import os
from flask import Flask
from micawber import bootstrap_basic
from micawber.cache import Cache as OEmbedCache
from playhouse.flask_utils import FlaskDB
from flask_sqlalchemy import SQLAlchemy
from blog import config

database = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    database.init_app(app)

    app.config.from_object(config.get_config())
    config.get_config().init_app(app)

    from blog.main import main as main_blueprint

    app.register_blueprint(main_blueprint)
    context = app.app_context()
    with context:
        database.create_all()

    return app

from  blog.main import views

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
SITE_WIDTH = 800

