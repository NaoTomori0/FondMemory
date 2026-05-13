from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import Post
from datetime import datetime

bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash("Доступ запрещён", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/moderate")
@login_required
@admin_required
def moderate():
    posts = Post.query.filter_by(approved=False).order_by(Post.created_at.desc()).all()
    return render_template("admin/moderate.html", posts=posts, year=datetime.now().year)


@bp.route("/approve/<int:id>")
@login_required
@admin_required
def approve(id):
    post = Post.query.get_or_404(id)
    post.approved = True
    db.session.commit()
    flash("Публикация одобрена", "success")
    return redirect(url_for("admin.moderate"))


@bp.route("/delete/<int:id>")
@login_required
@admin_required
def delete(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Публикация удалена", "info")
    return redirect(url_for("admin.moderate"))


@bp.route("/post/delete/<int:id>", methods=["POST"])
@login_required
@admin_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Пост удалён", "info")
    return redirect(url_for("board.index"))
