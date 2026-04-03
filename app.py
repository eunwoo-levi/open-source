import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-journal-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///journal.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Models ──────────────────────────────────────────────────────────────────

entry_tags = db.Table(
    'entry_tags',
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id'), primary_key=True),
    db.Column('tag_id',   db.Integer, db.ForeignKey('tag.id'),   primary_key=True),
)

class Entry(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(200), nullable=False)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags       = db.relationship('Tag', secondary=entry_tags, backref='entries')

class Tag(db.Model):
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

# ── Routes: Dashboard ────────────────────────────────────────────────────────

@app.route('/')
def index():
    total     = Entry.query.count()
    all_tags  = Tag.query.count()
    recent    = Entry.query.order_by(Entry.created_at.desc()).limit(5).all()
    return render_template('index.html', total=total, all_tags=all_tags, recent=recent)

# ── Routes: Entries ──────────────────────────────────────────────────────────

@app.route('/entries')
def entries():
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
    all_tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        title   = request.form['title'].strip()
        content = request.form['content'].strip()
        tag_ids = request.form.getlist('tags', type=int)
        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.', 'danger')
            return render_template('entry_form.html', all_tags=all_tags, entry=None)
        entry = Entry(title=title, content=content)
        for tid in tag_ids:
            t = Tag.query.get(tid)
            if t:
                entry.tags.append(t)
        db.session.add(entry)
        db.session.commit()
        flash('일지가 저장되었습니다.', 'success')
        return redirect(url_for('entries'))
    return render_template('entry_form.html', all_tags=all_tags, entry=None)

@app.route('/entries/<int:entry_id>')
def view_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    return render_template('entry_detail.html', entry=entry)

@app.route('/entries/<int:entry_id>/edit', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry    = Entry.query.get_or_404(entry_id)
    all_tags = Tag.query.order_by(Tag.name).all()
    if request.method == 'POST':
        title   = request.form['title'].strip()
        content = request.form['content'].strip()
        tag_ids = request.form.getlist('tags', type=int)
        if not title or not content:
            flash('제목과 내용을 모두 입력해주세요.', 'danger')
            return render_template('entry_form.html', all_tags=all_tags, entry=entry)
        entry.title   = title
        entry.content = content
        entry.tags    = [Tag.query.get(tid) for tid in tag_ids if Tag.query.get(tid)]
        db.session.commit()
        flash('일지가 수정되었습니다.', 'success')
        return redirect(url_for('view_entry', entry_id=entry.id))
    return render_template('entry_form.html', all_tags=all_tags, entry=entry)

@app.route('/entries/<int:entry_id>/delete', methods=['POST'])
def delete_entry(entry_id):
    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('일지가 삭제되었습니다.', 'warning')
    return redirect(url_for('entries'))

# ── Routes: Tags ─────────────────────────────────────────────────────────────

@app.route('/tags')
def tags():
    all_tags = Tag.query.order_by(Tag.name).all()
    return render_template('tags.html', tags=all_tags)

@app.route('/tags/new', methods=['POST'])
def new_tag():
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
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash(f'태그 "{tag.name}"이 삭제되었습니다.', 'warning')
    return redirect(url_for('tags'))

# ── Routes: Search ───────────────────────────────────────────────────────────

@app.route('/search')
def search():
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
