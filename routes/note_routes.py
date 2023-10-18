from flask import Blueprint, render_template, url_for, redirect, session, request, flash
from sqlalchemy import asc, desc
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks
import datetime
current_date = datetime.datetime.now()

note = Blueprint('Notes', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


@note.route("/", methods=["GET", "POST"])
@check_login
def notes():

    user = session['user_id']

    notes = db.session.query(
        Notes).filter(Notes.user_id == user).order_by(Notes.created_on).all()

    note_count = db.session.query(Notes).filter(
        Notes.user_id == user).count()

    return render_template("note_index.html", notes=notes, count=note_count, count_message="Currently No Notes")


# get form to create a new note
@note.route("/new", methods=["GET", "POST"], endpoint='new_note')
@check_login
def new_route():

    # create a new note
    if request.method == "POST":
        user = session['user_id']
        # form data

        title = request.form.get("note-title")
        subject = request.form.get("note-subject")

        title_msg = ""
        subject_msg = ""

        # add the new note object to database
        new_note = Notes(
            user_id=user,
            note_title=title,
            note_subject=subject,
            created_on=current_date
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
        return render_template("notes.html")


# create a new page on a current note
@note.route("/<string:title>/create_page", methods=["GET", "POST"])
def create_page(title):

    if request.method == "POST":
        user = session['user_id']

        page_title = request.form.get("title")

        note_id = db.session.query(Notes.id).filter(
            Notes.note_title == title)

        # create new page for current note
        create_new_page = Page(
            page_id=note_id,
            page_title=page_title,
            created_on=current_date,
        )

        try:
            db.session.add(create_new_page)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        flash(f"{page_title} note created", "info")
        return redirect(f"/note/{title}")
    else:
        return render_template('_pageForm.html', title=title)


@note.route("/<string:title>/", methods=['GET', 'POST'])
def note_page(title):

    user = session['user_id']

    note_id = db.session.query(Notes.id).filter(
        Notes.note_title == title)

    pages = db.session.query(Page).filter(Page.page_id == note_id)

    page_count = pages.count()

    page_length = db.session.query(Page).filter(
        Page.page_id == user).count()

    return render_template("pages_index.html", title=title, page_length=page_length, pages=pages, count=page_count)


@note.route("/<string:title>/edit", methods=["GET", "POST"])
def edit_note(title):

    if request.method == "GET":
        user = session['user_id']

        notes = db.session.query(
            Notes).filter(Notes.user_id == user, Notes.note_title == title).first()

        return render_template("editMainNote.html", notes=notes)
    else:
        note_title = request.form.get("title")
        note_subject = request.form.get("note-subject")

        note_query_update = db.session.query(
            Notes).filter(Notes.note_title == title)

        note_query_update.update(
            {"note_title": note_title, "note_subject": note_subject})

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
