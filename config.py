import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, "app/static/uploads")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    WTF_CSRF_ENABLED = True

    MAIL_SERVER = os.environ.get("MAIL_SERVER")

    MAIL_PORT = int(os.environ.get("MAIL_PORT"))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    try:
        GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
        GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
        GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
        GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
    except:
        pass
