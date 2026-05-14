import os
from datetime import datetime, timezone, timedelta
from flask import Blueprint, render_template
from app.models import Post

MSK = timezone(timedelta(hours=3))


def plural_days(n):
    """Возвращает правильную форму слова 'день' для числа n."""
    if 11 <= n % 100 <= 14:
        return "дней"
    last_digit = n % 10
    if last_digit == 1:
        return "день"
    if 2 <= last_digit <= 4:
        return "дня"
    return "дней"


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
    memorial_date_str = os.environ.get("MEMORY_DATE", "")

    days_passed = None
    if memorial_date_str:
        try:
            memorial_date = datetime.strptime(memorial_date_str, "%Y-%m-%d").replace(
                tzinfo=MSK
            )
            now_msk = datetime.now(MSK)
            delta = now_msk - memorial_date
            days_passed = delta.days
        except ValueError:
            days_passed = None

    return render_template(
        "index.html",
        flying_posts=flying_posts,
        memorial_name=memorial_name,
        memorial_years=memorial_years,
        days_passed=days_passed,
        plural_days=plural_days,
        year=datetime.now().year,
    )


@bp.route("/donate")
def donate():
    donate_info = {
        "title": os.environ.get("DONATE_TITLE", "Поддержать проект"),
        "description": os.environ.get("DONATE_DESCRIPTION", ""),
        "boosty_link": os.environ.get("DONATE_DONATIONS_LINK", ""),
        "boosty_text": os.environ.get("DONATE_DONATIONS_TEXT", "Поддержать"),
        "card_number": os.environ.get("DONATE_CARD_NUMBER", ""),
        "card_bank": os.environ.get("DONATE_CARD_BANK", ""),
        "card_holder": os.environ.get("DONATE_CARD_HOLDER", ""),
        "card_purpose": os.environ.get("DONATE_CARD_PURPOSE", ""),
    }
    return render_template(
        "donate.html",
        donate=donate_info,
        year=datetime.now().year,
    )
