from flask import Blueprint, render_template, url_for, redirect, session, request
from models import db, Notes, Page, SideNotes, Users, Blocks, BookMarks
import bleach
import datetime
current_date = datetime.datetime.now()

blocks = Blueprint('Blocks', __name__)


def check_login(view_func):
    def wrapped_view(*args, **kwargs):
        if 'user_id' not in session:
            # Redirect to the login page if not logged in
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return wrapped_view


@blocks.route("/new", methods=["GET", "POST"])
def block_form(block_title, block_page):

    if request.method == "POST":
        user = session['user_id']

        title_of_block = request.form.get('block-title')
        block_body = request.form.get('block-body')

        sanitize_block_title = bleach.clean(title_of_block)
        sanitize_block_body = bleach.clean(block_body)

        get_page = db.session.query(Page).filter(
            Page.page_title == block_page).first()

        new_block = Blocks(
            created_on=current_date,
            block_title=sanitize_block_title,
            page_id=get_page.id,
            block_notes=sanitize_block_body,
        )

        try:
            db.session.add(new_block)
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()

        return redirect(f"/note/{block_title}/page/{block_page}/")
    else:
        blocking = "hello"
        return render_template("blocks/block.html", blocks=blocking, title=block_title, page=block_page)


@blocks.route("/<int:id>/", methods=["GET", "DELETE"])
def delete_block(block_title, block_page, id):

    # Use update() on the query object to update the block's title.
    block_delete = db.session.query(
        Blocks).filter(Blocks.id == id).first()

    db.session.delete(block_delete)
    db.session.commit()
    db.session.close()

    return redirect(f"/note/{block_title}/page/{block_page}")


@blocks.route("<int:id>/edit", methods=["GET", "POST"])
def page_edit(block_title, block_page, id):

    if request.method == "GET":
        user = session['user_id']
        blocks = db.session.query(Blocks).filter(
            Page.page_title == block_page, Blocks.id == id).first()

        return render_template("blocks/editBlock.html", title=block_title, page=block_page, blocks=blocks, id=id)
    else:

        block_body = request.form.get("block-body")
        title_of_block = request.form.get("block-title")

        # Use update() on the query object to update the block's title.
        update_query = db.session.query(Blocks).filter(Blocks.id == id)

        update_query.update(
            {"block_title": title_of_block, "block_notes": block_body})

        db.session.commit()
        db.session.close()

        return redirect(f"/note/{block_title}/page/{block_page}")
