from flask import Blueprint, render_template
from app.models import Post
from datetime import datetime

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    flying_posts = (
        Post.query.filter_by(approved=True)
        .order_by(Post.created_at.desc())
        .limit(30)
        .all()
    )
    return render_template(
        "index.html", flying_posts=flying_posts, year=datetime.now().year
    )
