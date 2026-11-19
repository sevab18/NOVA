# Online Store

Учебный backend интернет-магазина на FastAPI, SQLAlchemy, Alembic и PostgreSQL.

## Запуск

1. Создайте виртуальное окружение и установите зависимости:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\pip.exe install -r requirements.txt
   ```

2. Скопируйте `backend/.env.example` в `backend/.env` и задайте
   `JWT_SECRET_KEY` длиной не меньше 32 символов. Этот ключ нельзя добавлять
   в Git или публиковать.

3. Запустите PostgreSQL и примените миграции:

   ```powershell
   cd ..
   docker compose up -d
   cd backend
   .\.venv\Scripts\alembic.exe upgrade head
   ```

4. Запустите API:

   ```powershell
   .\.venv\Scripts\uvicorn.exe app.main:app --reload
   ```

Документация API будет доступна по адресу `http://127.0.0.1:8000/docs`.

## Frontend

Frontend находится в каталоге `frontend` и использует React, TypeScript и Vite.

Установка и запуск:

```powershell
cd frontend
npm install
npm run dev
```

Интерфейс будет доступен по адресу `http://127.0.0.1:5173`. По умолчанию он
обращается к API `http://127.0.0.1:8000/api/v1`. Другой адрес можно указать в
`frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

Перед запуском frontend запустите PostgreSQL, примените миграции и запустите
FastAPI. Проверки frontend:

```powershell
npm run build
npm run lint
```

## Авторизация

API использует access token в формате JWT. Основные маршруты:

- `POST /api/v1/auth/register` — регистрация покупателя;
- `POST /api/v1/auth/login` — вход и получение токена;
- `GET /api/v1/users/me` — профиль текущего пользователя;
- `GET /api/v1/products` и `GET /api/v1/categories` — публичный каталог;
- изменение товаров и категорий — только для администратора.

Пример регистрации:

```json
{
  "name": "Alex",
  "email": "alex@example.com",
  "password": "StrongPassword123"
}
```

Пример входа:

```json
{
  "email": "alex@example.com",
  "password": "StrongPassword123"
}
```

Ответ входа содержит `access_token`. В Swagger нажмите `Authorize` и вставьте
этот токен. В HTTP-запросах используется заголовок:

```text
Authorization: Bearer <access_token>
```

Регистрация всегда создаёт пользователя с ролью `customer`. Для назначения
первого администратора выполните из каталога `backend`:

```powershell
.\.venv\Scripts\python.exe -m app.scripts.create_admin alex@example.com
```

Сначала пользователь с таким email должен зарегистрироваться обычным способом.

## Проверка

При запущенном PostgreSQL:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Интеграционные тесты работают внутри внешней транзакции и откатывают созданные ими данные.
