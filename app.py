"""
app.py — Dev Journal Flask Application
=======================================

A personal developer journal web application built with Flask and SQLite.
Supports CRUD operations for journal entries, tag management, and full-text search.

Modules:
    - Entry: SQLAlchemy model for journal entries
    - Tag: SQLAlchemy model for tags
    - Routes: Flask route handlers for dashboard, entries, tags, and search

Usage::

    python app.py

The application will be available at http://localhost:5001.
Interactive API docs are available at http://localhost:5001/apidocs.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-journal-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///journal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {
    'title': 'Dev Journal API',
    'uiversion': 3,
    'version': '1.0.0',
    'description': (
        'Interactive API documentation for the Dev Journal application. '
        'Manage journal entries, tags, and search functionality.'
    ),
    'termsOfService': '',
    'contact': {'name': 'Dev Journal'},
    'license': {'name': 'MIT'},
}

db = SQLAlchemy(app)
swagger = Swagger(app)

# ── Models ──────────────────────────────────────────────────────────────────

entry_tags = db.Table(
    'entry_tags',
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
    db.Column('tag_id',   db.Integer, db.ForeignKey('tag.id'),   primary_key=True),
)


class Entry(db.Model):
    """SQLAlchemy model representing a journal entry.

    Attributes:
        id (int): Primary key, auto-incremented.
        title (str): Title of the entry, max 200 characters.
        content (str): Full text content of the entry.
        created_at (datetime): UTC timestamp when the entry was created.
        updated_at (datetime): UTC timestamp of the last update.
        tags (list): List of associated :class:`Tag` objects (many-to-many).

    Example::

        entry = Entry(title="Today's work", content="Fixed the N+1 query bug.")
        db.session.add(entry)
        db.session.commit()
    """

    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags       = db.relationship('Tag', secondary=entry_tags, backref='entries')


class Tag(db.Model):
    """SQLAlchemy model representing a tag for categorizing entries.

    Attributes:
        id (int): Primary key, auto-incremented.
        name (str): Unique tag name, max 50 characters.

    Example::

        tag = Tag(name='python')
        db.session.add(tag)
        db.session.commit()
    """

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# ── Helpers ─────────────────────────────────────────────────────────────────

def _parse_entry_form():
    """Parse and validate title, content, and tag_ids from a POST form request.

    Reads ``title``, ``content``, and ``tags`` fields from ``request.form``.
    Both ``title`` and ``content`` are stripped of leading/trailing whitespace.

    Returns:
        tuple: A 4-tuple ``(title, content, tag_ids, error)`` where:

            - **title** (*str*): The submitted title.
            - **content** (*str*): The submitted content.
            - **tag_ids** (*list[int]*): List of selected tag IDs.
            - **error** (*str or None*): An error message if validation fails,
              or ``None`` if the data is valid.

    Example::

        title, content, tag_ids, error = _parse_entry_form()
        if error:
            flash(error, 'danger')
    """
    title   = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    tag_ids = request.form.getlist('tags', type=int)
    if not title or not content:
        return title, content, tag_ids, '제목과 내용을 모두 입력해주세요.'
    return title, content, tag_ids, None


def _assign_tags(tag_ids):
    """Retrieve Tag objects for a list of IDs using a single IN-query.

    Resolves the N+1 query problem by fetching all matching tags in one
    database round-trip instead of one query per ID.

    Args:
        tag_ids (list[int]): List of tag primary-key IDs to look up.

    Returns:
        list: List of :class:`Tag` objects matching the given IDs.
        Returns an empty list if ``tag_ids`` is falsy.

    Example::

        tags = _assign_tags([1, 2, 3])
        entry.tags = tags
    """
    if not tag_ids:
        return []
    return Tag.query.filter(Tag.id.in_(tag_ids)).all()

# ── Routes: Dashboard ────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Render the dashboard with summary statistics and recent entries.

    Displays the total number of entries, total number of tags, and the
    5 most recent journal entries.

    Returns:
        str: Rendered HTML of ``index.html``.
    ---
    tags:
      - Dashboard
    summary: Dashboard overview
    description: Returns the main dashboard with entry/tag counts and recent entries.
    responses:
      200:
        description: Dashboard page rendered successfully.
    """
    total     = Entry.query.count()
    all_tags  = Tag.query.count()
    recent    = Entry.query.order_by(Entry.created_at.desc()).limit(5).all()
    return render_template('index.html', total=total, all_tags=all_tags, recent=recent)

# ── Routes: Entries ──────────────────────────────────────────────────────────

@app.route('/entries')
def entries():
    """List all journal entries, optionally filtered by a tag.

    Accepts an optional ``tag`` query parameter (tag ID) to filter entries.
    Returns all entries ordered by creation date (newest first).

    Args:
        tag (int, optional): Tag ID as a query-string parameter.

    Returns:
        str: Rendered HTML of ``entries.html``.
    ---
    tags:
      - Entries
    summary: List journal entries
    description: Retrieves all journal entries, optionally filtered by tag ID.
    parameters:
      - name: tag
        in: query
        type: integer
        required: false
        description: Filter entries by this tag ID.
    responses:
      200:
        description: A list of journal entries.
      404:
        description: Tag not found.
    """
    tag_id  = request.args.get('tag', type=int)
    query   = Entry.query.order_by(Entry.created_at.desc())
    if tag_id:
        tag   = Tag.query.get_or_404(tag_id)
        query = tag.entries
    else:
        tag   = None
    all_entries = query if tag_id else query.all()
    all_tags    = Tag.query.order_by(Tag.name).all()
    return render_template('entries.html', entries=all_entries, tags=all_tags, active_tag=tag)


@app.route('/entries/new', methods=['GET', 'POST'])
def new_entry():
    """Display and handle the new journal entry creation form.

    **GET**: Renders an empty entry form.
    **POST**: Validates and saves a new entry to the database.
    Redirects to the entries list on success, or re-renders the form
    with an error message on validation failure.

    Returns:
        str: Rendered form HTML (GET/error), or redirect to entries list (success).
    ---
    tags:
      - Entries
    summary: Create a new journal entry
    description: |
      GET returns the entry creation form.
      POST creates a new journal entry with the provided title, content, and tags.
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: title
        in: formData
        type: string
        required: true
        description: Title of the new entry.
      - name: content
        in: formData
        type: string
        required: true
        description: Content body of the new entry.
      - name: tags
        in: formData
        type: array
        items:
          type: integer
        required: false
        description: List of tag IDs to associate with the entry.
    responses:
      200:
        description: Entry creation form (GET) or validation failure (POST).
      302:
        description: Redirect to entries list after successful creation.
    """
    all_tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        title, content, tag_ids, error = _parse_entry_form()
        if error:
            flash(error, 'danger')
            return render_template('entry_form.html', all_tags=all_tags, entry=None)
        entry = Entry(title=title, content=content)
        entry.tags = _assign_tags(tag_ids)
        db.session.add(entry)
        db.session.commit()
        flash('일지가 저장되었습니다.', 'success')
        return redirect(url_for('entries'))
    return render_template('entry_form.html', all_tags=all_tags, entry=None)


@app.route('/entries/<int:entry_id>')
def view_entry(entry_id):
    """Display the detail page for a single journal entry.

    Args:
        entry_id (int): The primary key of the entry to display.

    Returns:
        str: Rendered HTML of ``entry_detail.html``.

    Raises:
        werkzeug.exceptions.NotFound: If no entry with the given ID exists.
    ---
    tags:
      - Entries
    summary: View a journal entry
    description: Returns the detail page for a specific journal entry.
    parameters:
      - name: entry_id
        in: path
        type: integer
        required: true
        description: The ID of the journal entry.
    responses:
      200:
        description: Entry detail page.
      404:
        description: Entry not found.
    """
    entry = Entry.query.get_or_404(entry_id)
    return render_template('entry_detail.html', entry=entry)


@app.route('/entries/<int:entry_id>/edit', methods=['GET', 'POST'])
def edit_entry(entry_id):
    """Display and handle the edit form for an existing journal entry.

    **GET**: Renders the entry form pre-filled with existing data.
    **POST**: Validates and updates the entry in the database.
    Redirects to the entry detail page on success.

    Args:
        entry_id (int): The primary key of the entry to edit.

    Returns:
        str: Rendered form HTML, or redirect to ``view_entry`` on success.

    Raises:
        werkzeug.exceptions.NotFound: If no entry with the given ID exists.
    ---
    tags:
      - Entries
    summary: Edit a journal entry
    description: |
      GET returns the pre-filled edit form.
      POST updates the entry with the provided data.
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: entry_id
        in: path
        type: integer
        required: true
        description: The ID of the journal entry to edit.
      - name: title
        in: formData
        type: string
        required: true
        description: Updated title of the entry.
      - name: content
        in: formData
        type: string
        required: true
        description: Updated content of the entry.
      - name: tags
        in: formData
        type: array
        items:
          type: integer
        required: false
        description: Updated list of tag IDs.
    responses:
      200:
        description: Edit form (GET) or validation failure (POST).
      302:
        description: Redirect to entry detail page after successful update.
      404:
        description: Entry not found.
    """
    entry    = Entry.query.get_or_404(entry_id)
    all_tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        title, content, tag_ids, error = _parse_entry_form()
        if error:
            flash(error, 'danger')
            return render_template('entry_form.html', all_tags=all_tags, entry=entry)
        entry.title   = title
        entry.content = content
        entry.tags    = _assign_tags(tag_ids)
        db.session.commit()
        flash('일지가 수정되었습니다.', 'success')
        return redirect(url_for('view_entry', entry_id=entry.id))
    return render_template('entry_form.html', all_tags=all_tags, entry=entry)


@app.route('/entries/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    """Delete a journal entry and redirect to the entries list.

    Args:
        entry_id (int): The primary key of the entry to delete.

    Returns:
        Response: Redirect to the entries list page.

    Raises:
        werkzeug.exceptions.NotFound: If no entry with the given ID exists.
    ---
    tags:
      - Entries
    summary: Delete a journal entry
    description: Permanently deletes the specified journal entry.
    parameters:
      - name: entry_id
        in: path
        type: integer
        required: true
        description: The ID of the journal entry to delete.
    responses:
      302:
        description: Redirect to entries list after deletion.
      404:
        description: Entry not found.
    """
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('일지가 삭제되었습니다.', 'warning')
    return redirect(url_for('entries'))

# ── Routes: Tags ─────────────────────────────────────────────────────────────

@app.route('/tags')
def tags():
    """List all available tags sorted alphabetically.

    Returns:
        str: Rendered HTML of ``tags.html``.
    ---
    tags:
      - Tags
    summary: List all tags
    description: Returns a page listing all tags sorted alphabetically.
    responses:
      200:
        description: Tag list page.
    """
    all_tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags.html', tags=all_tags)


@app.route('/tags/new', methods=['POST'])
def new_tag():
    """Create a new tag from a POST form submission.

    Flashes an error if the name is empty or already exists;
    otherwise creates and persists the new tag.

    Returns:
        Response: Redirect to the tags page.
    ---
    tags:
      - Tags
    summary: Create a new tag
    description: Creates a new tag. Returns an error if the name is empty or duplicate.
    consumes:
      - application/x-www-form-urlencoded
    parameters:
      - name: name
        in: formData
        type: string
        required: true
        description: The name of the new tag.
    responses:
      302:
        description: Redirect to the tags page.
    """
    name = request.form.get('name', '').strip()
    if not name:
        flash('태그 이름을 입력해주세요.', 'danger')
    elif Tag.query.filter_by(name=name).first():
        flash('이미 존재하는 태그입니다.', 'warning')
    else:
        db.session.add(Tag(name=name))
        db.session.commit()
        flash(f'태그 "{name}"이 추가되었습니다.', 'success')
    return redirect(url_for('tags'))


@app.route('/tags/<int:tag_id>/delete', methods=['POST'])
def delete_tag(tag_id):
    """Delete a tag by its ID.

    Args:
        tag_id (int): The primary key of the tag to delete.

    Returns:
        Response: Redirect to the tags page.

    Raises:
        werkzeug.exceptions.NotFound: If no tag with the given ID exists.
    ---
    tags:
      - Tags
    summary: Delete a tag
    description: Permanently deletes the specified tag from the database.
    parameters:
      - name: tag_id
        in: path
        type: integer
        required: true
        description: The ID of the tag to delete.
    responses:
      302:
        description: Redirect to tags page after deletion.
      404:
        description: Tag not found.
    """
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f'태그 "{tag.name}"이 삭제되었습니다.', 'warning')
    return redirect(url_for('tags'))

# ── Routes: Search ───────────────────────────────────────────────────────────

@app.route('/search')
def search():
    """Search journal entries by title or content keyword.

    Performs a case-insensitive full-text search across both ``title``
    and ``content`` fields when a query is provided.

    Args:
        q (str): Search keyword passed as a query-string parameter.

    Returns:
        str: Rendered HTML of ``search.html`` with matching results.
    ---
    tags:
      - Search
    summary: Search journal entries
    description: |
      Case-insensitive full-text search over entry titles and content.
      Returns matching entries ordered by creation date (newest first).
    parameters:
      - name: q
        in: query
        type: string
        required: false
        description: Search keyword.
    responses:
      200:
        description: Search results page.
    """
    q       = request.args.get('q', '').strip()
    results = []
    if q:
        like    = f'%{q}%'
        results = Entry.query.filter(
            (Entry.title.ilike(like)) | (Entry.content.ilike(like))
        ).order_by(Entry.created_at.desc()).all()
    return render_template('search.html', q=q, results=results)

# ── Init ─────────────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
