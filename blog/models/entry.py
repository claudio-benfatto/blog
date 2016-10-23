import datetime
import re
from flask import Markup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from blog import database

oembed_providers = bootstrap_basic(OEmbedCache())


Base = declarative_base()

class Entry(database.Model):

    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    slug = Column(String(128), unique=True)
    content = Column(Text)
    published = Column(Boolean)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, title=title, content=content, published=published):
        self.title = title
        self.slug = self.create_slug()
        self.content = content
        self.published = published
        self.timestamp = datetime.datetime.now()

    def __repr__(self):
        return "<Entry(title='%s', slug='%s', published='%r', timestamp='%s'>" % (
            self.title, self.slug, self.published, str(self.timestamp))

    @property
    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog entry,
        and also convert any media URLs into rich media objects such as video
        players or images.
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=800)
        return Markup(oembed_content)

    def create_slug(self):
        # Generate a URL-friendly representation of the entry's title.
        if not self.slug:
            return re.sub(r'[^\w]+', '-', self.title.lower()).strip('-')
        return self.slug
