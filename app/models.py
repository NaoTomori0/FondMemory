from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

moscow_tz = zoneinfo.ZoneInfo("Europe/Moscow")
current_time = datetime.now(moscow_tz)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default="user")
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship("Like", backref="user", lazy="dynamic")

    posts = db.relationship("Post", backref="author", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == "admin"

    @staticmethod
    def create_with_random_password(email, username=None):
        user = User(email=email, username=username or email.split("@")[0], role="user")
        user.set_password(secrets.token_urlsafe(16))
        return user


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_filename = db.Column(db.String(256), nullable=True)
    file_type = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.relationship(
        "Like", backref="post", lazy="dynamic", cascade="all, delete-orphan"
    )


class Like(db.Model):
    __tablename__ = "like"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "post_id", name="_user_post_like_uc"),
    )


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
