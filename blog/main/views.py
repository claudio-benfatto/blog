import functools
from blog.config import config as config
from blog.main import main, main_config
from blog import database
from blog.models.entry import Entry
from flask import (flash, redirect, render_template, request,
                   Response, session, url_for)
from markdown.extensions.codehilite import CodeHiliteExtension
from sqlalchemy.orm import exc
from werkzeug.exceptions import abort


def get_object_or_404(model, *criterion):
    try:
        return database.session.query(model).filter(*criterion).one()
    except (exc.NoResultFound, exc.MultipleResultsFound):
        abort(404)

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('main.login', next=request.path))
    return inner

@main.route('/login/', methods=['GET', 'POST'])
def login():

    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        # TODO: If using a one-way hash, you would also hash the user-submitted
        # password and do the comparison on the hashed versions.
        if password == main_config.APP_ADMIN_PASSWORD:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('main.index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

@main.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('main.login'))
    return render_template('logout.html')

@main.route('/')
def index():
    published = database.session.query(Entry).filter(Entry.published==True)
    return render_template('index.html', object_list=published)

@main.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry = Entry(
                title=request.form['title'],
                content=request.form['content'],
                published=request.form.get('published') or False)
            database.session.add(entry)
            database.session.commit()
            flash('Entry created successfully.', 'success')
            if entry.published:
                return redirect(url_for('main.detail', slug=entry.slug))
            else:
                return redirect(url_for('main.edit', slug=entry.slug))
        else:
            flash('Title and Content are required.', 'danger')
    return render_template('create.html')

@main.route('/drafts/')
@login_required
def drafts():
    drafts = database.session.query(Entry).filter(Entry.published==False).order_by(Entry.timestamp.desc())
    return render_template('index.html', object_list=drafts, check_bounds=False)

@main.route('/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = database.session.query(Entry).filter(Entry.slug == slug)
    else:
        query = database.session.query(Entry).filter(Entry.published==True).filter(Entry.slug == slug)

    entry = get_object_or_404(Entry, Entry.slug == slug)
    return render_template('detail.html', entry=entry)

@main.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = database.session.query(Entry).filter(Entry.slug == slug)
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry.title = request.form['title']
            entry.content = request.form['content']
            entry.published = request.form.get('published') or False
            entry.save()

            flash('Entry saved successfully.', 'success')
            if entry.published:
                return redirect(url_for('main.detail', slug=entry.slug))
            else:
                return redirect(url_for('main.edit', slug=entry.slug))
        else:
            flash('Title and Content are required.', 'danger')

    return render_template('edit.html', entry=entry)

