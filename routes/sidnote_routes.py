

from flask import Blueprint, render_template, url_for, redirect, session, request
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks
import bleach
import datetime
current_date = datetime.datetime.now()

sidenotes = Blueprint('Sidenotes', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect("/login")
        return view_func(*args, **kwargs)
    return wrapped_view


@sidenotes.route("/new", methods=["GET", "POST"])
@check_login
def page_sidenote(sidenote_title, sidenote_page):

    if request.method == "POST":
        user = session['user_id']
        sidenote = request.form.get("sidenote")

        page_id = db.session.query(Page.id).filter(
            Page.page_title == sidenote_page)

        new_sidenote = SideNotes(
            sidenotes=sidenote,
            created_on=current_date,
            page_id=page_id
        )

        db.session.add(new_sidenote)
        db.session.commit()

        db.session.close()

        return redirect(f"/note/{sidenote_title}/page/{sidenote_page}")
    else:
        return render_template("sidenotes/sidenote.html", title=sidenote_title, page=sidenote_page)


@sidenotes.route("/<int:id>/edit", methods=["GET", "POST"])
def note_edit(sidenote_title, sidenote_page, id):

    if request.method == "GET":
        user = session['user_id']

        notes = db.session.query(SideNotes).filter(
            Page.page_title == sidenote_page, SideNotes.id == id).first()

        return render_template("sidenotes/editNote.html", title=sidenote_title, page=sidenote_page, notes=notes, id=id)

    else:

        update_sidenote = request.form.get("sidenote")

        # Use update() on the query object to update the block's title.
        sidenote_update_query = db.session.query(
            SideNotes).filter(SideNotes.id == id)

        sidenote_update_query.update(
            {"sidenotes": update_sidenote})

        db.session.commit()
        db.session.close()

        return redirect(f"/note/{sidenote_title}/page/{sidenote_page}")


@sidenotes.route("/<int:id>/", methods=["GET", "DELETE"])
def delete_sidenote(sidenote_title, sidenote_page, id):

    # Use update() on the query object to update the block's title.
    sidenote_delete = db.session.query(
        SideNotes).filter(SideNotes.id == id).first()

    db.session.delete(sidenote_delete)
    db.session.commit()
    db.session.close()

    return redirect(f"/note/{sidenote_title}/page/{sidenote_page}")
