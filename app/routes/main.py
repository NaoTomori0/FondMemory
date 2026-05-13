from flask import Blueprint, render_template
from app.models import Post
from datetime import datetime
import os

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    flying_posts = (
        Post.query.filter_by(approved=True)
        .order_by(Post.created_at.desc())
        .limit(30)
        .all()
    )
    memorial_name = os.environ.get("MEMORY_NAME", "")
    memorial_years = os.environ.get("MEMORY_YEARS", "")
    return render_template(
        "index.html",
        flying_posts=flying_posts,
        memorial_name=memorial_name,
        memorial_years=memorial_years,
        year=datetime.now().year,
    )
