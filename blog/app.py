
import os

from blog import config
from flask import Flask
from micawber import bootstrap_basic
from micawber.cache import Cache as OEmbedCache
from playhouse.flask_utils import FlaskDB

# Blog configuration values.

# use the hash again in the login view to perform the comparison. This is just
# for simplicity.
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
APP_DIR = os.path.dirname(os.path.realpath(__file__))

# This is used by micawber, which will attempt to generate rich media
# embedded objects with maxwidth=800.
SITE_WIDTH = 800

# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE='sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db'),
    DEBUG=True,
    SECRET_KEY='shhh, secret!',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_object(__name__)

# FlaskDB is a wrapper for a peewee database that sets up pre/post-request
# hooks for managing database connections.
flask_db = FlaskDB(app)

# The `database` is the actual peewee database, as opposed to flask_db which is
# the wrapper.
database = flask_db.database

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())
