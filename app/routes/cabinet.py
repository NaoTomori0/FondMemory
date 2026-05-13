from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Post, User
from datetime import datetime

bp = Blueprint("cabinet", __name__, url_prefix="/cabinet")


@bp.route("/")
@login_required
def index():
    posts = (
        Post.query.filter_by(user_id=current_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    return render_template("cabinet/index.html", posts=posts, year=datetime.now().year)


@bp.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        new_username = request.form.get("username", "").strip()
        if not new_username:
            flash("Имя пользователя не может быть пустым", "danger")
            return render_template(
                "cabinet/edit_profile.html", year=datetime.now().year
            )
        existing = User.query.filter(
            User.username == new_username, User.id != current_user.id
        ).first()
        if existing:
            flash("Это имя уже занято", "danger")
            return render_template(
                "cabinet/edit_profile.html", year=datetime.now().year
            )
        current_user.username = new_username
        db.session.commit()
        flash("Никнейм обновлён", "success")
        return redirect(url_for("cabinet.index"))
    return render_template("cabinet/edit_profile.html", year=datetime.now().year)


@bp.route("/post/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != current_user.id:
        abort(403)

    if request.method == "POST":
        # Обновление текста или описания
        if post.file_type == "text":
            post.content = request.form.get("content", "").strip()
        else:
            post.description = request.form.get("description", "").strip()

        # Отправляем на модерацию повторно
        post.approved = False
        db.session.commit()
        flash("Пост изменён и отправлен на модерацию", "info")
        return redirect(url_for("cabinet.index"))

    return render_template(
        "cabinet/edit_post.html", post=post, year=datetime.now().year
    )


@bp.route("/post/delete/<int:id>", methods=["POST"])
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Пост удалён", "info")
    return redirect(url_for("cabinet.index"))
