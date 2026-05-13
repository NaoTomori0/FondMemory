from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    jsonify,
)
from flask_login import login_required, current_user
from app import db
from app.models import Post, Like
import os, uuid
from werkzeug.utils import secure_filename
from threading import Thread
from datetime import datetime

bp = Blueprint("board", __name__, url_prefix="/board")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mov", "avi"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def async_save(file, filepath):
    file.save(filepath)


@bp.route("/")
def index():
    posts = Post.query.filter_by(approved=True).order_by(Post.created_at.desc()).all()
    posts_data = []
    for post in posts:
        likes_count = post.likes.count()
        liked = False
        if current_user.is_authenticated:
            liked = (
                Like.query.filter_by(user_id=current_user.id, post_id=post.id).first()
                is not None
            )
        posts_data.append({"post": post, "likes_count": likes_count, "liked": liked})
    return render_template(
        "board.html", posts_data=posts_data, year=datetime.now().year
    )


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        content = request.form.get("content", "").strip()
        file = request.files.get("file")

        if not file or file.filename == "":
            if not content:
                flash("Введите текст сообщения или выберите файл", "danger")
                return render_template("upload.html", year=datetime.now().year)
            post = Post(
                file_filename=None,
                file_type="text",
                content=content,
                user_id=current_user.id,
            )
            db.session.add(post)
            db.session.commit()
            flash("Сообщение отправлено на модерацию", "success")
            return redirect(url_for("board.index"))

        if not allowed_file(file.filename):
            flash("Допустимые форматы: PNG, JPG, GIF, MP4, MOV, AVI", "danger")
            return render_template("upload.html", year=datetime.now().year)

        filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        Thread(target=async_save, args=(file, filepath)).start()

        file_type = (
            "video" if filename.lower().endswith(("mp4", "mov", "avi")) else "photo"
        )
        post = Post(
            file_filename=filename,
            file_type=file_type,
            description=request.form.get("description", "").strip(),
            user_id=current_user.id,
        )
        db.session.add(post)
        db.session.commit()
        flash("Файл загружен и отправлен на модерацию", "success")
        return redirect(url_for("board.index"))
    return render_template("upload.html", year=datetime.now().year)


# API-маршруты для AJAX-лайков
@bp.route("/api/like/<int:post_id>", methods=["POST"])
@login_required
def api_like(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        return jsonify({"error": "Already liked"}), 400
    like = Like(user_id=current_user.id, post_id=post_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({"likes_count": post.likes.count()})


@bp.route("/api/unlike/<int:post_id>", methods=["POST"])
@login_required
def api_unlike(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if not existing:
        return jsonify({"error": "Not liked"}), 400
    db.session.delete(existing)
    db.session.commit()
    return jsonify({"likes_count": post.likes.count()})
