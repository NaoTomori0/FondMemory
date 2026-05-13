# Fond Memory

Веб-приложение для сохранения воспоминаний о близком человеке.  
Пользователи могут делиться фотографиями, видео и текстовыми сообщениями, которые после модерации появляются на общей доске.  
Сайт поддерживает регистрацию с подтверждением email, вход через Google/GitHub, систему лайков и удобную панель администратора.

## Основные возможности

- **Доска памяти** с плиточной раскладкой (Masonry)
- **Три типа контента**: фото, видео (MP4), текстовые сообщения
- **Загрузка контента** с выбором типа (текст или файл)
- **Модерация**: администратор одобряет или удаляет посты
- **Лайки** (AJAX, без перезагрузки страницы)
- **Личный кабинет** с историей своих публикаций и статусом модерации
- **Редактирование профиля** (никнейм)
- **Регистрация с подтверждением email** (код отправляется на почту)
- **OAuth-вход** через Google и GitHub
- **Безопасность**: пароли хешированы (Werkzeug), защита от CSRF через AJAX
- **Полностью адаптивный дизайн** (Bootstrap 5)

## Технологический стек

- **Backend**: Python 3, Flask, Gunicorn
- **База данных**: SQLite (легко заменить на PostgreSQL)
- **Очереди**: опционально Celery + Redis (в текущей версии не используется)
- **Аутентификация**: Flask-Login, OAuth (Google, GitHub)
- **Отправка писем**: Flask-Mail (SMTP Яндекс.Почты или Gmail)
- **Frontend**: Bootstrap 5, Masonry, Font Awesome
- **Прокси-сервер**: Nginx

## Установка и запуск (для разработки)

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/NaoTomori/FondMemory.git
cd FondMemory
```

### 2. Установите зависимости
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. Настройте переменные окружения
Создайте файл .env в корне проекта:

```text
SECRET_KEY=очень-длинный-секретный-ключ
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@fondmemory.local
ADMIN_PASSWORD=сильный_пароль
MAIL_SERVER=smtp.yandex.ru
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@yandex.ru
MAIL_PASSWORD=пароль_приложения_яндекса
MAIL_DEFAULT_SENDER=your_email@yandex.ru
MEMORY_NAME=Иван Иванович Иванов
MEMORY_YEARS=1956–2024
```
### 4. Инициализируйте базу данных
```bash
flask db init
flask db migrate -m "Initial"
flask db upgrade
flask create-admin
```
### 5. Запустите сервер
```bash
python run.py
```
Сайт будет доступен по адресу http://127.0.0.1:5000.

## Развёртывание на продакшен-сервере (Ubuntu + Nginx + Gunicorn)
### 1. Установите системные зависимости
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx git -y
2. Скопируйте проект на сервер
bash
git clone https://github.com/NaoTomori/FondMemory.git /home/nao/FondMemory
cd /home/nao/FondMemory
```
### 2. Настройте виртуальное окружение и установите зависимости
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
### 3. Создайте файл .env (как в шаге 3 разработки)
### 4. Инициализируйте базу данных
```bash
flask db init
flask db migrate -m "Initial"
flask db upgrade
flask create-admin
```

### 5. Настройте Gunicorn
Создайте файл wsgi.py:
```
python
from app import create_app
app = create_app()
```
### 6. Создайте systemd-юнит /etc/systemd/system/fondmemory.service:

```ini
[Unit]
Description=Fond Memory Gunicorn
After=network.target

[Service]
User=nao
Group=nao
WorkingDirectory=/home/nao/FondMemory
Environment="PATH=/home/nao/FondMemory/venv/bin"
EnvironmentFile=/home/nao/FondMemory/.env
ExecStart=/home/nao/FondMemory/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```
### 7. Запустите сервис:
```
bash
sudo systemctl daemon-reload
sudo systemctl start fondmemory
sudo systemctl enable fondmemory
```

### 8. Настройте Nginx
Создайте конфигурацию /etc/nginx/sites-available/fondmemory:

```
nginx
server {
    listen 80;
    server_name ваш_домен.ru www.ваш_домен.ru;

    client_max_body_size 200M;

    location /static/ {
        alias /home/nao/FondMemory/app/static/;
        expires 30d;
        add_header Cache-Control "public";
        types {
            video/mp4 mp4;
            video/webm webm;
            video/ogg ogv;
        }
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
### 9. Активируйте сайт:
```
bash
sudo ln -s /etc/nginx/sites-available/fondmemory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 10. Настройте SSL (если есть домен)

```
bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d ваш_домен.ru -d www.ваш_домен.ru
```

## Структура проекта

```text
FondMemory/
├── app/
│   ├── __init__.py          # фабрика приложения
│   ├── models.py            # модели SQLAlchemy
│   ├── routes/
│   │   ├── auth.py          # регистрация, вход, OAuth
│   │   ├── main.py          # главная страница
│   │   ├── board.py         # доска, загрузка, лайки
│   │   ├── cabinet.py       # личный кабинет
│   │   └── admin.py         # модерация
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── board.html
│   │   ├── upload.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── verify_email.html
│   │   ├── cabinet/
│   │   │   ├── index.html
│   │   │   ├── edit_profile.html
│   │   │   └── edit_post.html
│   │   └── admin/
│   │       └── moderate.html
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── sign-in.js
│   │   └── uploads/
│   └── utils.py             # отправка email
├── config.py
├── run.py
├── wsgi.py
├── requirements.txt
└── .env
```

## Лицензия

GPL-3.0 license

## Если у вас возникнут вопросы или понадобится помощь, создайте issue.

```text
Этот README полностью описывает проект и поможет другим разработчикам
или вам самим быстро развернуть сайт в будущем. Удачи с репозиторием!
```
