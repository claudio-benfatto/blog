import functools
from blog.models.entry import Entry
from blog.app import app
from blog.app import database
from flask import (flash, redirect, render_template, request,
                   Response, session, url_for)
from markdown.extensions.codehilite import CodeHiliteExtension


def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
    print("Logging in")
    print("Password")
    print(request.method)
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        # TODO: If using a one-way hash, you would also hash the user-submitted
        # password and do the comparison on the hashed versions.
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')

@app.route('/')
def index():
    published = database.session.query(Entry).filter(Entry.published==True)
    return render_template('index.html', object_list=published)

@app.route('/create/', methods=['GET', 'POST'])
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
                return redirect(url_for('detail', slug=entry.slug))
            else:
                return redirect(url_for('edit', slug=entry.slug))
        else:
            flash('Title and Content are required.', 'danger')
    return render_template('create.html')

@app.route('/drafts/')
@login_required
def drafts():
    drafts = database.session.query(Entry).filter(Entry.published==False).order_by(Entry.timestamp.desc())
    return render_template('index.html', object_list=drafts, check_bounds=False)

@app.route('/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = database.session.query(Entry).filter(Entry.slug == slug)
    else:
        query = database.session.query(Entry).filter(Entry.published==True).filter(Entry.slug == slug)
    return render_template('detail.html', entry=query.first())

@app.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = get_object_or_404(Entry, Entry.slug == slug)
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry.title = request.form['title']
            entry.content = request.form['content']
            entry.published = request.form.get('published') or False
            entry.save()

            flash('Entry saved successfully.', 'success')
            if entry.published:
                return redirect(url_for('detail', slug=entry.slug))
            else:
                return redirect(url_for('edit', slug=entry.slug))
        else:
            flash('Title and Content are required.', 'danger')

    return render_template('edit.html', entry=entry)

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Sorry Not found</h3>'), 404
