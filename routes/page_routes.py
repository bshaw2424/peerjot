from flask import Blueprint, render_template, url_for, redirect, session, request
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks, generate_page_slug
import bleach
import datetime
from static.js.functions import get_user
current_date = datetime.datetime.now()

pages = Blueprint('Pages', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


# main page associated to note
@pages.route("/", methods=["GET"])
def note(page_title, page_name):

    user = session['user_id']

    note_id = db.session.query(Page).filter(Page.page_title == page_name)

    username = get_user(db, Users, user).first()

    get_page = db.session.query(Page).filter(
        Page.page_title == page_name, Users.id == user).first()

    get_bookmark_id = db.session.query(
        BookMarks).filter(Page.page_title == page_name, BookMarks.page_id == Page.id).all()

    id = db.session.query(Blocks).filter(
        Page.page_title == page_name, Blocks.page_id == Page.id).first()

    get_sidenote_id = db.session.query(
        SideNotes).filter(Page.page_title == page_name, SideNotes.page_id == Page.id).all()

    bookmark_total = db.session.query(Page).filter(
        Page.page_title == page_name, BookMarks.page_id == Page.id).count()

    sidenote_total = db.session.query(SideNotes).filter(
        Page.page_title == page_name, SideNotes.page_id == Page.id).count()

    blocks = db.session.query(Blocks).filter(
        Users.id == user, get_page.id == Blocks.page_id)

    block_count = blocks.count()

    get_page_title = db.session.query(Page).filter(
        Page.page_title == page_name).first()

    notes = db.session.query(SideNotes).filter(
        SideNotes.page_id == Page.id)

    return render_template("pages/page.html", title=page_title, page=get_page_title, id=id, blocks=blocks, block_count=block_count, username=username, bookmark_total=bookmark_total, sidenote_total=sidenote_total, get_sidenote_id=get_sidenote_id, get_bookmark_id=get_bookmark_id)


@pages.route("/edit", methods=["GET", "POST"])
def edit_page(page_title, page_name):

    if request.method == "GET":
        page_edit = db.session.query(Page).filter(
            Page.page_title == page_name).first()

        return render_template("pages/editPage.html", page_edit=page_edit, title=page_title, page=page_name)
    else:
        form_title = request.form.get("title")

        page_update = db.session.query(
            Page).filter(Page.page_title == page_name).first()

        if page_update:
            page_update.page_title = form_title,
            generate_page_slug(None, None, page_update)

        db.session.commit()
        db.session.close()

        return redirect(f"/notes/{page_title}/")


@pages.route("/full_view", methods=["GET"])
def full_view(page_title, page_name):
    if request.method == "GET":
        user = session['user_id']

        full_page = db.session.query(Blocks).filter(
            Page.page_title == page_name, Blocks.page_id == Page.id)

        bookmarks = db.session.query(BookMarks).filter(
            Page.page_title == page_name, BookMarks.page_id == Page.id)

        get_page_title = db.session.query(Page).filter(
            Users.id == user, Page.page_title == page_name).first()

        block_count = full_page.count()

        bookmark_count = bookmarks.count()

        return render_template("pages/fullView.html", title=page_title, page=get_page_title, full_page=full_page, bookmarks=bookmarks, block_count=block_count, bookmark_count=bookmark_count)


@pages.route("/delete", methods=["GET", "DELETE"])
def delete_page(page_title, page_name):

    user = session['user_id']

    page_delete = db.session.query(Page).filter(
        Page.page_title == page_name, Users.id == user).first()

    db.session.delete(page_delete)
    db.session.commit()
    db.session.close()

    return redirect(f"/notes/{page_title}")
