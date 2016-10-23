from flask import Blueprint
from blog import config

main_config = config.get_config()

main = Blueprint('main', __name__)

from blog.main import views, errors
 