from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from slugify import slugify
import datetime

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True,
                   primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False, unique=True)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())
    email = db.Column(db.String(50), nullable=False, unique=True)

    users = db.relationship('Notes', back_populates='notes', cascade='delete')

    def __init__(self, username, password, created_on, email):
        self.username = username
        self.password = password
        self.created_on = created_on
        self.email = email


class Notes(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    note_title = db.Column(db.String(150), nullable=False)
    note_subject = db.Column(db.String(150))
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())
    note_slug = db.Column(db.String(150))

    # Define the relationship with Blocks
    notes = db.relationship('Users', back_populates='users')
    pages = db.relationship('Page', back_populates='note', cascade='delete')


@db.event.listens_for(Notes, 'before_insert')
@db.event.listens_for(Notes, 'before_update')
def generate_note_slug(mapper, connection, target):
    target.note_slug = slugify(str(target.note_title))

    def __init__(self, user_id, note_title, note_subject, created_on, note_slug):
        self.user_id = user_id
        self.note_title = note_title
        self.note_subject = note_subject
        self.created_on = created_on
        self.note_slug = note_slug


class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    page_id = db.Column(db.Integer, ForeignKey(
        'notes.id'), nullable=False)
    page_title = db.Column(db.String(150), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now)
    page_slug = db.Column(db.String(150))

    # relationship wit notes
    note = db.relationship('Notes', back_populates='pages')
    # All have relationship with the page
    block = db.relationship(
        'Blocks', back_populates='blocks', cascade='delete')
    bookmark = db.relationship(
        'BookMarks', back_populates='bookmarks', cascade='delete')
    sidenotes = db.relationship(
        'SideNotes', back_populates='sidenote', cascade='delete')


@db.event.listens_for(Page, 'before_insert')
@db.event.listens_for(Page, 'before_update')
def generate_page_slug(mapper, connection, target):
    target.page_slug = slugify(str(target.page_title))

    def __init__(self, page_id, page_title, created_on, page_slug):
        self.page_id = page_id
        self.page_title = page_title
        self.created_on = created_on
        self.page_slug = page_slug


class Blocks(db.Model):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    block_notes = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())
    block_title = db.Column(db.String(100), nullable=False)
    page_id = db.Column(db.Integer, ForeignKey(
        'pages.id'), nullable=False)

    blocks = db.relationship('Page', back_populates='block')

    def __init__(self, block_notes, created_on,  block_title, page_id):
        self.block_notes = block_notes
        self.created_on = created_on
        self.block_title = block_title
        self.page_id = page_id


class BookMarks(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    bookmark_url = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())
    page_id = db.Column(db.Integer, ForeignKey('pages.id'), nullable=False)
    bookmark_title = db.Column(db.String(100), nullable=False)

    bookmarks = db.relationship('Page', back_populates='bookmark')

    def __init__(self, bookmark_url, created_on, page_id, bookmark_title):
        self.bookmark_url = bookmark_url
        self.created_on = created_on
        self.page_id = page_id
        self.bookmark_title = bookmark_title


class SideNotes(db.Model):
    __tablename__ = 'sidenotes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True,)
    sidenotes = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())
    page_id = db.Column(db.Integer, ForeignKey('pages.id'), nullable=False)

    sidenote = db.relationship('Page', back_populates='sidenotes')

    def __init__(self, sidenotes, created_on, page_id):
        self.sidenotes = sidenotes
        self.created_on = created_on
        self.page_id = page_id
