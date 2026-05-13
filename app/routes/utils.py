import smtplib
import threading
from flask_mail import Message
from flask import current_app
from app import mail


import traceback


def _send_email_async(app, msg):
    """Отправляет письмо в отдельном потоке, с обработкой ошибок."""
    try:
        with app.app_context():
            print("1 - Запуск отправки...")
            mail.send(msg)
            print(f"✅ Письмо отправлено на {msg.recipients}")
    except Exception as e:
        print(f"❌ Перехвачена ошибка: {type(e).__name__} -> {e}")
        traceback.print_exc()


def send_verification_email(user):
    if not current_app.config.get("MAIL_USERNAME"):
        print(
            f"===== Verification code for {user.email}: {user.verification_code} ====="
        )
        return
    msg = Message(
        subject="Подтверждение email",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user.email],
    )
    msg.body = f"Ваш код подтверждения: {user.verification_code}"

    app = current_app._get_current_object()

    thread = threading.Thread(target=_send_email_async, args=(app, msg))
    thread.start()
