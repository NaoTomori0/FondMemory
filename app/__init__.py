from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from datetime import datetime
from authlib.integrations.flask_client import OAuth
from config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
mail = Mail()
oauth = OAuth()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    # OAuth провайдеры
    oauth.register(
        name="google",
        client_id=app.config.get("GOOGLE_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    oauth.register(
        name="github",
        client_id=app.config.get("GITHUB_CLIENT_ID"),
        client_secret=app.config.get("GITHUB_CLIENT_SECRET"),
        authorize_url="https://github.com/login/oauth/authorize",
        access_token_url="https://github.com/login/oauth/access_token",
        api_base_url="https://api.github.com",
        client_kwargs={"scope": "user:email"},
    )

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    from app.routes import auth, main, board, admin, cabinet

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(board.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(cabinet.bp)

    @app.cli.command("create-admin")
    def create_admin():
        username = os.environ.get("ADMIN_USERNAME", "admin")
        email = os.environ.get("ADMIN_EMAIL", "admin@fondmemory.local")
        password = os.environ.get("ADMIN_PASSWORD")
        if not password:
            print("❌ ADMIN_PASSWORD не задан в .env")
            return
        with app.app_context():
            from app.models import User

            if User.query.filter_by(role="admin").first():
                print("ℹ️ Администратор уже существует")
                return
            admin = User(
                username=username, email=email, role="admin", email_verified=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"✅ Администратор {username} создан")

    @app.cli.command("gen-admin-login")
    def gen_admin_login():
        import os
        from .routes.utils import generate_admin_permanent_token

        with app.app_context():
            from app.models import User

            admin = User.query.filter_by(role="admin").first()
            if not admin:
                print(
                    "❌ Администратор не найден. Создайте его через flask create-admin"
                )
                return
            token = generate_admin_permanent_token(admin.id)
            base_url = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
            print(f"✅ Постоянная ссылка для входа администратора (не истекает):")
            print(f"{base_url}/auth/admin-login/{token}")

    return app
