from flask import Blueprint, render_template, url_for, redirect, session, request, flash
from sqlalchemy import asc, desc
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks, generate_note_slug
from static.js.functions import get_user
import datetime

current_date = datetime.datetime.now()

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
        Notes.user_id == user).order_by(Notes.created_on)

    note_count = notes.count()

    return render_template("notes/note_index.html", notes=notes, count=note_count)


# get form to create a new note
@note.route("/new", methods=["GET", "POST"], endpoint='new')
@check_login
def new_route():

    # create a new note
    if request.method == "POST":
        user = session['user_id']

        title = request.form.get("note-title")
        subject = request.form.get("note-subject")

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
        try:
            db.session.add(new_note)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        flash(f"{title} note created", "info")
        return redirect("/notes")

    else:
        return render_template("notes/notes.html")


# create a new page on a current note
@note.route("/<string:title>/create_page", methods=["GET", "POST"])
def create_page(title):

    if request.method == "POST":
        user = session['user_id']

        page_title = request.form.get("title")

        get_note = db.session.query(Notes).filter(
            Notes.note_title == title).first()

        # create new page for current note
        create_new_page = Page(
            page_id=get_note.id,
            page_title=page_title,
            created_on=current_date,
            page_slug=page_title
        )

        try:
            db.session.add(create_new_page)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        flash(f"{page_title} note created", "info")
        return redirect(f"/notes/{title}")
    else:
        return render_template('pages/_pageForm.html', title=title)


@note.route("/<string:title>/")
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
    flash(f"{ note_delete.note_title.capitalize() } successfully deleted")
    return redirect("/notes")
