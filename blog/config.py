import os
basedir = os.path.abspath(os.path.abspath(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'just a secret key'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    APP_ADMIN_PASSWORD = os.environ.get('APP_ADMIN_PASSWORD') or 'admin'

    @staticmethod
    def init_app(app):
        pass



class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'blog-test.sqlite')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'blog-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'sqlite:///' + os.path.join(basedir, 'blog.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

def get_config():
    env = os.getenv('FLASK_CONFIG') or 'default'
    return config[env]
