# Django CRUD Blog

Блог на Django с аутентификацией по email, разделением на черновики/опубликованные и полным CRUD с контролем авторства.

![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-092e20)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Результат

**2 приложения**, **2 модели**, **8 представлений**, **9 URL-маршрутов**. Покрытие тестами — модели, CRUD, авторизация, контроль доступа. Линтер чистый: `ruff` — 0 ошибок.

```text
Ran 36 tests in 38.4s
OK
```

---

## Как это работает

Пользователь регистрируется по email, создаёт посты в статусе **черновик**, а при смене статуса на **опубликован** пост автоматически появляется на главной с проставленной датой публикации. Черновики видны только автору. Редактировать и удалять пост может только владелец — чужой запрос возвращает 403. Пагинация по 5 постов на страницу.

---

## Быстрый старт

```bash
git clone https://github.com/ITouch228/django-crud-blog.git
cd django-crud-blog

python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/Mac

pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env            # заполни SECRET_KEY

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Открой http://127.0.0.1:8000/

---

## Стек

- **Python** 3.12
- **Django** 6.0
- **SQLite** (разработка, переключаемый на PostgreSQL)
- **Bootstrap 5** — адаптивный интерфейс
- **python-dotenv** — env-driven конфигурация
- **Ruff** (lint + format)
- **pytest** / Django TestClient — тесты

---

## Архитектура

Проект разбит на два независимых приложения с односторонней зависимостью `blog → accounts`:

- `accounts/` — кастомная модель пользователя (`AbstractBaseUser` + `PermissionsMixin`), регистрация и вход по email
- `blog/` — модель поста, CRUD-операции, пагинация, контроль доступа
- `blog_project/` — настройки, URL-роуты, WSGI/ASGI
- `templates/` — базовый шаблон с Bootstrap 5 и дочерние страницы

### Ключевые решения

- **Кастомная модель пользователя на email.** `AbstractBaseUser` + `PermissionsMixin` + `AccountManager` вместо стандартного `User` с username. `USERNAME_FIELD = "email"`.
- **Автогенерация уникального slug.** При сохранении поста slug генерируется из заголовка через `slugify`; при коллизии добавляется счётчик (`my-post-1`, `my-post-2`).
- **Автоматический `published_at`.** При смене статуса на `published` поле `published_at` заполняется текущим временем — без ручного ввода.
- **Контроль авторства в views.** `post_edit` и `post_delete` проверяют `post.author != request.user` → `HttpResponseForbidden`.
- **Черновики скрыты от чужих.** `post_detail` использует `Q(status=published) | Q(author=user)` — гость видит только опубликованные, автор видит свои черновики.
- **Env-driven настройки.** `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` читаются из `.env` через `python-dotenv`.

### Что решалось по ходу

- **`requirements.txt` в UTF-16 с BOM** ломал `pip` на Linux/CI → переписан в UTF-8.
- **Линтеры сведены с трёх (flake8/isort/black) к одному Ruff** — один конфиг в `pyproject.toml`, быстрее и без конфликтов форматтеров.
- **`ALLOWED_HOSTS="".split(",")`** давал `[""]` при пустом env → fallback на `localhost,127.0.0.1`.

---

## Модель данных

```text
Account (email, first_name, last_name, is_active, is_staff, date_joined)
 └─ Post (title, slug, content, status, created_at, updated_at, published_at, author)
```

Статусы поста: `draft` → `published`.

---

## URL-маршруты

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Список опубликованных постов (пагинация) |
| GET | `/post/<slug>/` | Детали поста |
| POST | `/post/new/` | Создание поста |
| POST | `/post/<slug>/edit/` | Редактирование поста |
| POST | `/post/<slug>/delete/` | Удаление поста |
| GET | `/my-posts/` | Мои посты (включая черновики) |
| POST | `/accounts/register/` | Регистрация по email |
| POST | `/accounts/login/` | Вход по email |
| GET | `/accounts/logout/` | Выход |

---

## Структура проекта

```text
manage.py                # точка входа Django
pyproject.toml           # конфиг ruff
Makefile                 # команды разработки
requirements.txt         # прод-зависимости
requirements-dev.txt     # ruff, pytest
.env.example             # шаблон конфигурации
blog_project/
    settings.py          # env-driven настройки
    urls.py              # корневые URL
accounts/
    models.py            # Account + AccountManager
    forms.py             # AccountCreationForm, AccountAuthenticationForm
    views.py             # register_view, login_view
    urls.py              # маршруты accounts
blog/
    models.py            # Post + slug-генерация + published_at
    forms.py             # PostForm с валидацией
    views.py             # CRUD + пагинация + контроль доступа
    urls.py              # маршруты blog
templates/
    base.html            # Bootstrap 5 layout
    blog/                # home, post_detail, post_form, my_posts, delete
    registration/        # login, register
```

---

## Команды (Makefile)

```bash
make install     # pip install -r requirements.txt -r requirements-dev.txt
make run         # python manage.py runserver
make migrate     # применить миграции
make makemigrations  # создать миграции
make createsuperuser # завести админа
make test        # запустить тесты
make lint        # ruff check
make format      # ruff format
make fix         # ruff check --fix + ruff format
make check       # линтер + тесты
make clean       # очистить временные файлы
```

---

## Тесты

```bash
make test
```

Покрыты: модели (slug-генерация, published_at), CRUD-представления (доступ, авторство, пагинация), аутентификация (регистрация, вход, уникальность email).

---

## Планы по улучшению

- **Комментарии к постам** — модель `Comment` + форма под постом.
- **Поиск** по заголовку и содержанию через `Q`-фильтры.
- **PostgreSQL** вместо SQLite для продакшена.
- **Теги и категории** через `ManyToManyField`.
- **Деплой** (gunicorn + nginx + WhiteNoise).

---

## Лицензия

Учебный pet-проект. MIT. См. [LICENSE](LICENSE).