from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
import datetime

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, username, password, created_on):
        self.username = username
        self.password = password
        self.created_on = created_on


class Notes(db.Model):
    __tablename__ = 'user_notes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    note_title = db.Column(db.String, nullable=False)
    note_subject = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, note_title, note_subject, created_on):
        self.note_title = note_title
        self.note_subject = note_subject
        self.created_on = created_on

    # Define the relationship with Blocks
    blocks = db.relationship('Blocks', backref='blocks')

    # Define the relationship with BookMarks
    bookmarks = db.relationship('BookMarks', backref='bookmarks')

    # Define the relationship with SideNotes
    sidenotes = db.relationship('SideNotes', backref='sidenotes')

    page = db.relationship('Page', backref='pagess')


class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, ForeignKey(
        'user_notes.id'), nullable=False)
    page_title = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, page_title, created_on):
        self.page_title = page_title
        self.created_on = created_on


class Blocks(db.Model):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True)
    block_notes = db.Column(db.Text(), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, user_id, block_notes, created_on):
        self.user_id = user_id
        self.block_notes = block_notes
        self.created_on = created_on


class BookMarks(db.Model):
    __tablename__ = 'bookmarks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    bookmark = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, user_id, bookmark, created_on):
        self.user_id = user_id
        self.bookmark = bookmark
        self.created_on = created_on


class SideNotes(db.Model):
    __tablename__ = 'sidenotes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    sidenotes = db.Column(db.String(255), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.now())

    def __init__(self, user_id, sidenotes, created_on):
        self.user_id = user_id
        self.sidenotes = sidenotes
        self.created_on = created_on
