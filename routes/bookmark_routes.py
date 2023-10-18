from flask import Blueprint, render_template, url_for, redirect, session, request
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks
import bleach
import datetime
current_date = datetime.datetime.now()

bookmarks = Blueprint('Bookmarks', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


@bookmarks.route("/new", methods=["GET", "POST"])
def page_bookmark(bookmark_title, bookmark_page):

    if request.method == "POST":

        # sesssion id of he logged in user
        user = session['user_id']

        # get the name field from the form (url / title)
        bookmark_url = request.form.get('bookmark_url')
        title = request.form.get('bookmark_title')

        page_title = db.session.query(Page.id).filter(
            Page.page_title == bookmark_page)

        new_bookmark = BookMarks(
            bookmark_url=bookmark_url,
            created_on=current_date,
            page_id=page_title[0].id,
            bookmark_title=title
        )
        try:
            db.session.add(new_bookmark)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Error: {str(e)}"
        finally:
            db.session.close()
        return redirect(f"/note/{bookmark_title}/page/{bookmark_page}")
    else:
        return render_template("bookmark.html", title=bookmark_title, page=bookmark_page)


@bookmarks.route("/<int:id>", methods=["GET", "DELETE"])
def delete_bookmark(bookmark_title, bookmark_page, id):

    # Use update() on the query object to update the block's title.
    bookmark_delete = db.session.query(
        BookMarks).filter(BookMarks.id == id).first()

    db.session.delete(bookmark_delete)
    db.session.commit()
    db.session.close()

    return redirect(f"/note/{bookmark_title}/page/{bookmark_page}")


@bookmarks.route("/<int:id>/edit", methods=["GET", "POST"])
def bookmark_edit(bookmark_title, bookmark_page, id):

    if request.method == "GET":
        user = session['user_id']

        bookmarks = db.session.query(BookMarks).filter(
            Page.page_title == bookmark_page, BookMarks.id == id).first()

        return render_template("editBookmark.html", title=bookmark_title, page=bookmark_page, bookmarks=bookmarks, id=id)
    else:

        bookmark_url = request.form.get("bookmark_url")
        title_of_bookmark = request.form.get("bookmark_title")

        # Use update() on the query object to update the block's title.
        bookmark_query_update = db.session.query(
            BookMarks).filter(BookMarks.id == id)

        bookmark_query_update.update(
            {"bookmark_url": bookmark_url, "bookmark_title": title_of_bookmark})

        db.session.commit()
        db.session.close()

        return redirect(f"/note/{bookmark_title}/page/{bookmark_page}")
