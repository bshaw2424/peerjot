from flask import Blueprint, render_template, url_for, redirect, session, request, flash, jsonify
from sqlalchemy import asc, desc
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks, generate_note_slug
from static.js.functions import get_user
from datetime import datetime, timedelta

current_date = datetime.now()

note = Blueprint('Notes', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect("/login")
        return view_func(*args, **kwargs)
    return wrapped_view


@note.route("/", methods=["GET", "POST"])
@check_login
def notes():

    user = session['user_id']

    notes = db.session.query(Notes).filter(
        Notes.user_id == user).order_by(Notes.created_on.desc())

    note_message = "create a note"

    message = "New"
    getting_time = datetime.now()
    past_time = timedelta(hours=2)

    note_count = notes.count()

    return render_template("notes/note_index.html", notes=notes, count=note_count, note_message=note_message, elasped_time=past_time, time=getting_time, message=message)


# get form to create a new note
@note.route("/new", methods=["GET", "POST"], endpoint='new')
@check_login
def new_route():

    # create a new note
    if request.method == "POST":
        user = session['user_id']

        title = request.form.get("note-title").lower()
        subject = request.form.get("note-subject")

        get_logged_user = db.session.query(Users).filter(Users.id == user)
        note_title = db.session.query(Notes).filter(Users.id == user)

        title_list = []

        for notes in note_title:
            title_list.append(notes.note_title)

        if title in title_list:
            return 'title is already used'

        # add the new note object to database
        new_note = Notes(
            user_id=user,
            note_title=title,
            note_subject=subject,
            created_on=current_date,
            note_slug=title
        )

        if not title:
            title_msg = "Note title is required"
        if not subject:
            subject_msg = "Note Subject is required"

        if get_logged_user:
            db.session.add(new_note)
            db.session.commit()
            db.session.close()
        return redirect("/notes")

    else:
        return render_template("notes/notes.html")


# create a new page on a current note
@note.route("/<string:title>/create_page", methods=["GET", "POST"])
def create_page(title):

    if request.method == "POST":
        user = session['user_id']

        page_title = request.form.get("title").lower()

        get_note = db.session.query(Notes).filter(
            Notes.note_title == title).first()

        get_id = db.session.query(Notes).filter(
            Notes.note_title == title).first()

        get_note_pages = db.session.query(Page).filter(
            Users.id == user).join(Notes, Notes.id == Page.page_id).where(Page.page_id == get_id.id)

        page_list = []

        for pages in get_note_pages:
            page_list.append(pages.page_title)

        if page_title in page_list:
            return "that page title already exist"

        # create new page for current note
        create_new_page = Page(
            page_id=get_note.id,
            page_title=page_title,
            created_on=current_date,
            page_slug=page_title
        )

        db.session.add(create_new_page)

        db.session.commit()
        print(page_list)
        db.session.close()
        return redirect(f"/notes/{title}")
    else:
        return render_template('pages/_pageForm.html', title=title)


@note.route("/<string:title>/", methods=["GET"])
def note_page(title):

    user = session['user_id']

    note = db.session.query(Notes).filter(
        Notes.note_title == title, Users.id == user).first()

    pages = db.session.query(Page).filter(Page.page_id == note.id)

    page_count = pages.count()

    return render_template("pages/pages_index.html", title=title, pages=pages, count=page_count)


@note.route("/<string:title>/edit", methods=["GET", "POST"])
def edit_note(title):

    if request.method == "GET":
        user = session['user_id']

        notes = db.session.query(
            Notes).filter(Notes.user_id == user, Notes.note_title == title).first()

        return render_template("notes/editMainNote.html", notes=notes)
    else:
        note_title = request.form.get("title")
        note_subject = request.form.get("note-subject")

        note_update = db.session.query(
            Notes).filter(Notes.note_title == title).first()

        if note_update:
            note_update.note_title = note_title,
            note_update.note_subject = note_subject,
            generate_note_slug(None, None, note_update)

        db.session.commit()
        db.session.close()

        return redirect("/notes")


@note.route("/<int:id>/delete", methods=["GET", "DELETE"])
def delete_note(id):

    note_delete = db.session.query(Notes).filter(Notes.id == id).first()

    db.session.delete(note_delete)
    db.session.commit()
    db.session.close()
    return redirect("/notes")
