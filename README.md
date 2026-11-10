# Books API — реєстрація, JWT-авторизація та права доступу

Django + Django REST Framework + `djangorestframework-simplejwt`.
Увесь функціонал авторизації винесено в окремий Django app **`accounts`**.

## Запуск

```bash
python -m venv venv
venv\Scripts\activate           # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
python manage.py makemigrations books
python manage.py migrate
python manage.py createsuperuser   # адміністратор (is_staff = true)
python manage.py runserver
```

API: `http://127.0.0.1:8000/api/`

## Як передавати токен

Для захищених ендпоінтів додайте хедер:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Життя токенів і refresh

| Токен   | Термін дії |
|---------|------------|
| access  | 5 хвилин   |
| refresh | 1 день     |

Access токен живе недовго. Коли він протермінований, сервер повертає `401` з
`"code": "token_not_valid"`. Тоді клієнт надсилає refresh токен на `POST /api/auth/refresh/`,
отримує новий access і повторює запит. Коли протермінований і refresh, користувач логіниться знову.

---

## Ендпоінти авторизації (`accounts`)

### `POST /api/auth/register/` — реєстрація

Доступ: усі.

Request body:

| Поле             | Обов'язкове | Обмеження                                  |
|------------------|-------------|--------------------------------------------|
| username         | так         | max 150, унікальний                        |
| first_name       | ні          | max 150, може бути порожнім                |
| last_name        | ні          | max 150, може бути порожнім                |
| email            | так         | max 254, формат `name@example.com`, унікальний |
| password         | так         | max 128, min 8, не надто простий, не лише цифри, не схожий на username/email |
| password_confirm | так         | має збігатися з `password`                 |

```json
{
  "username": "artem",
  "first_name": "Artem",
  "last_name": "",
  "email": "artem@example.com",
  "password": "StrongPass123!",
  "password_confirm": "StrongPass123!"
}
```

**201 Created**
```json
{ "id": 1, "username": "artem", "first_name": "Artem", "last_name": "", "email": "artem@example.com", "is_staff": false }
```

**400 Bad Request**: помилки окремо для кожного поля:
```json
{
  "username": ["This field is required."],
  "email": ["Enter a valid email address."],
  "password": ["This password is too short. It must contain at least 8 characters.", "This password is too common."],
  "password_confirm": ["Passwords do not match."]
}
```

Пароль зберігається в БД лише у захешованому вигляді (`create_user` → PBKDF2).

### `POST /api/auth/login/` — логін

Доступ: усі.

```json
{ "username": "artem", "password": "StrongPass123!" }
```

**200 OK**
```json
{ "refresh": "eyJhbGciOi...", "access": "eyJhbGciOi..." }
```

**401 Unauthorized**
```json
{ "detail": "No active account found with the given credentials" }
```

**400 Bad Request**: не передано поле: `{ "password": ["This field is required."] }`

### `POST /api/auth/refresh/` — оновлення access токена

Доступ: усі (потрібен валідний refresh токен).

```json
{ "refresh": "eyJhbGciOi..." }
```

**200 OK**
```json
{ "access": "eyJhbGciOi..." }
```

**401 Unauthorized**
```json
{ "detail": "Token is invalid", "code": "token_not_valid" }
```

### `GET /api/auth/me/` — поточний користувач

Доступ: лише авторизовані. Хедер `Authorization: Bearer <access>`.

**200 OK**
```json
{ "id": 1, "username": "artem", "first_name": "Artem", "last_name": "", "email": "artem@example.com", "is_staff": false }
```

**401 Unauthorized**
```json
{ "detail": "Authentication credentials were not provided." }
```

### Logout

Окремого ендпоінта немає: під час виходу клієнт видаляє збережені `access` і `refresh` токени
(з `localStorage`).

---

## Права доступу до книг

| Метод | Ендпоінт             | Хто має доступ   |
|-------|----------------------|------------------|
| GET   | `/api/books/`        | усі              |
| GET   | `/api/books/{id}/`   | усі              |
| POST  | `/api/books/`        | авторизовані     |
| PUT   | `/api/books/{id}/`   | авторизовані     |
| PATCH | `/api/books/{id}/`   | авторизовані     |
| DELETE| `/api/books/{id}/`   | лише адміністратор (`is_staff`) |

Body для POST/PUT:
```json
{ "title": "1984", "author": "George Orwell", "year": 1949 }
```

Відповіді:
- `200 OK` / `201 Created`: книга; `204 No Content`: видалено
- `400 Bad Request`: помилки валідації по полях
- `401 Unauthorized`: немає токена або він невалідний:
  `{ "detail": "Authentication credentials were not provided." }`
- `403 Forbidden`: авторизований, але не адміністратор (DELETE):
  `{ "detail": "Only administrators can delete books." }`
- `404 Not Found`: книги не існує

## Postman

Колекція: `postman_collection.json`. Після запиту **Login** токени автоматично зберігаються
у змінні колекції `access` / `refresh` і підставляються в хедер `Authorization`.

## Фронтенд

Знаходиться в папці `frontend/`. Запуск (другий термінал):

```bash
cd frontend
python -m http.server 5500
```

Відкрити `http://127.0.0.1:5500/index.html`. Детальніше: `frontend/README.md`.
