# Полное руководство по проекту Online Store

Этот документ объясняет текущее устройство учебного интернет-магазина NOVA Store: как запускаются его части, как frontend обращается к backend, как данные сохраняются в PostgreSQL, как работает авторизация, для чего нужен каждый файл и какие ошибки могут возникнуть.

Состояние проекта на 19 ноября 2026 года:

- frontend реализован на React, TypeScript и Vite;
- backend реализован на FastAPI, SQLAlchemy и Pydantic;
- данные сохраняются в PostgreSQL;
- база запускается через Docker Compose;
- реализованы товары, категории, регистрация, вход, профиль и базовая админ-панель;
- корзина, заказы, оплата и доставка пока не реализованы.

## Оглавление

1. Общая архитектура
2. Инструменты проекта
3. Запуск проекта с нуля
4. Корневые файлы
5. Конфигурация backend
6. База данных и SQLAlchemy
7. Безопасность, пароли и JWT
8. Пользователи и авторизация
9. Товары
10. Категории
11. Миграции Alembic
12. Backend-тесты
13. Конфигурация frontend
14. Маршруты и точка входа frontend
15. API-клиент
16. Состояние авторизации frontend
17. Общие React-компоненты
18. Страницы frontend
19. Стили и графические файлы
20. Полный путь регистрации
21. Полный путь административного запроса
22. HTTP-ошибки
23. Ошибки запуска и отладки
24. Как добавлять новый модуль
25. Что сделано хорошо
26. Что нужно улучшить

# 1. Общая архитектура

Проект состоит из трёх главных работающих частей:

    Браузер пользователя
            |
            | HTTP-запросы и JSON
            v
    React frontend
    http://127.0.0.1:5173
            |
            | fetch и JWT
            v
    FastAPI backend
    http://127.0.0.1:8000
            |
            | SQLAlchemy и psycopg
            v
    PostgreSQL
    localhost:5433

Frontend отвечает за интерфейс. Он показывает страницы, формы, кнопки, товары, сообщения загрузки и ошибки.

Backend отвечает за правила приложения. Он проверяет данные, пароли, токены, права администратора и выполняет операции с базой.

PostgreSQL хранит постоянные данные. После закрытия браузера или перезапуска backend товары и пользователи остаются в базе.

Используется архитектура «модульный монолит». Backend является одним приложением, но разделён по функциональным модулям:

- auth — регистрация и вход;
- users — пользователи, роли и профиль;
- products — товары;
- category — категории;
- core — настройки и безопасность;
- api — объединение API-маршрутов;
- scripts — служебные команды.

Основной путь backend-запроса:

    Router
      -> Pydantic Schema
      -> Service
      -> Repository
      -> SQLAlchemy Session
      -> PostgreSQL

Router отвечает за HTTP. Schema отвечает за формат данных. Service отвечает за бизнес-правила. Repository отвечает за запросы к базе. SQLAlchemy-модель отвечает за структуру таблицы.

# 2. Инструменты проекта

| Инструмент | Назначение |
|---|---|
| Python | Язык backend |
| FastAPI | HTTP API, маршруты, зависимости, Swagger |
| Pydantic | Валидация запросов и формирование ответов |
| SQLAlchemy | ORM и работа Python с PostgreSQL |
| Alembic | Версионирование структуры базы |
| PostgreSQL | Хранение пользователей, товаров и категорий |
| psycopg | Драйвер подключения Python к PostgreSQL |
| Docker Compose | Локальный запуск PostgreSQL |
| Argon2 | Стойкое хеширование паролей |
| JWT | Токен авторизации |
| React | Интерфейс пользователя |
| TypeScript | Типизация frontend |
| React Router | Переходы между страницами |
| Vite | Dev-сервер и production-сборка |
| Oxlint | Проверка frontend-кода |
| unittest | Backend-тесты |

# 3. Запуск проекта с нуля

## 3.1 PostgreSQL

Из корня проекта выполняется:

    docker compose up -d

Docker читает docker-compose.yml и запускает контейнер online-store-db.

Локальные параметры:

| Параметр | Значение |
|---|---|
| Хост | localhost |
| Внешний порт | 5433 |
| Внутренний порт контейнера | 5432 |
| База | online_store |
| Пользователь | store_user |
| Пароль | store_password |

Запись портов 127.0.0.1:5433:5432 означает: компьютер принимает подключение на 5433 и передаёт его PostgreSQL внутри контейнера на 5432.

## 3.2 Python-окружение

Первоначальное создание:

    cd backend
    python -m venv .venv
    .\.venv\Scripts\pip.exe install -r requirements.txt

Виртуальное окружение изолирует зависимости проекта от системного Python.

## 3.3 Настройки backend

Файл backend/.env.example копируется в backend/.env. В настоящем .env необходимо указать JWT_SECRET_KEY длиной не меньше 32 символов.

Файл .env нельзя добавлять в Git.

## 3.4 Миграции

Из каталога backend:

    .\.venv\Scripts\alembic.exe upgrade head

Alembic сравнивает текущую ревизию базы с цепочкой миграций и применяет недостающие изменения.

## 3.5 Backend

Из каталога backend:

    .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

app.main означает модуль app/main.py. Последнее app — объект FastAPI внутри этого файла. Флаг reload перезапускает сервер после изменения Python-кода.

Адреса:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## 3.6 Frontend

Из каталога frontend:

    npm install
    npm run dev

Адрес интерфейса:

    http://127.0.0.1:5173

# 4. Корневые файлы

## .gitignore

Исключает из Git:

- виртуальные окружения;
- кэш Python;
- .env;
- coverage;
- логи;
- настройки IDE.

Главная задача — не допустить публикацию секретов и автоматически создаваемых файлов.

## docker-compose.yml

Описывает PostgreSQL-контейнер.

Ключевые настройки:

- image postgres:17 выбирает версию PostgreSQL;
- container_name задаёт имя online-store-db;
- restart unless-stopped включает автоматический перезапуск;
- environment создаёт пользователя и базу;
- ports публикует порт 5433;
- volumes сохраняет данные;
- healthcheck проверяет готовность базы.

Volume postgres_data сохраняет данные между перезапусками контейнера.

Пароль store_password предназначен только для локальной разработки. В production нужно использовать секретное значение.

## README.md

Краткая инструкция разработчика:

- установка Python-зависимостей;
- подготовка .env;
- запуск PostgreSQL;
- миграции;
- backend;
- frontend;
- авторизация;
- назначение администратора;
- запуск тестов.

## Online_Store_TZ_Beige_Design (1).docx

Техническое задание и целевой план магазина.

В нём описаны:

- роли;
- каталог;
- корзина;
- заказы;
- оплата;
- доставка;
- админ-панель;
- будущая структура таблиц;
- визуальный стиль;
- план из восьми спринтов.

Документ описывает целевое состояние. Код содержит только уже реализованную часть. Корзина и заказы в техническом задании есть, но в backend пока отсутствуют.

# 5. Конфигурация backend

## backend/.env.example

Шаблон переменных:

    DATABASE_URL=postgresql+psycopg://store_user:store_password@localhost:5433/online_store
    APP_ENVIRONMENT=development
    SQL_ECHO=false
    JWT_SECRET_KEY=CHANGE_ME
    JWT_ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30

DATABASE_URL задаёт подключение к PostgreSQL.

APP_ENVIRONMENT разрешает development, test или production.

SQL_ECHO включает вывод SQL-запросов.

JWT_SECRET_KEY подписывает токены. CHANGE_ME слишком короткий и должен быть заменён.

ACCESS_TOKEN_EXPIRE_MINUTES задаёт срок жизни JWT.

## backend/requirements.txt

Список Python-зависимостей с фиксированными версиями:

- fastapi — API;
- uvicorn — сервер;
- SQLAlchemy — ORM;
- psycopg — PostgreSQL;
- alembic — миграции;
- pydantic — схемы;
- pydantic-settings — .env;
- pwdlib с Argon2 — пароли;
- PyJWT — JWT;
- email-validator — проверка email;
- httpx — TestClient.

## backend/app/core/config.py

Центральная конфигурация backend.

Класс Settings наследует BaseSettings. Pydantic получает значения из переменных окружения и .env.

Объект settings создаётся при импорте:

    settings = Settings()

Проверяется:

- JWT-ключ не короче 32 символов;
- срок действия токена положительный;
- алгоритм равен HS256;
- окружение входит в разрешённый список.

CORS разрешён для:

- http://localhost:5173
- http://127.0.0.1:5173

Возможные ошибки:

- .env не найден;
- отсутствует DATABASE_URL;
- отсутствует JWT_SECRET_KEY;
- JWT-ключ слишком короткий;
- backend запущен из каталога, где .env не обнаруживается;
- frontend открыт с адреса, которого нет в cors_origins.

## backend/app/main.py

Точка входа FastAPI.

Создаёт приложение:

    app = FastAPI(title="Online Store API")

Подключает CORS middleware и общий api_router.

Маршрут GET / возвращает приветствие.

Маршрут GET /db-check выполняет SELECT 1 и проверяет соединение с PostgreSQL.

Если db-check не работает, причины обычно такие:

- PostgreSQL выключен;
- неправильный DATABASE_URL;
- порт 5433 занят или недоступен;
- неправильный пользователь или пароль.

## backend/app/api/router.py

Создаёт общий APIRouter с префиксом /api/v1.

Подключает:

- auth_router;
- users_router;
- products_router;
- categories_router.

Версия v1 позволяет позже создать API v2, не ломая frontend и старых клиентов.

## Файлы __init__.py

В каталогах app, api, auth, core, products, category, users, scripts и tests находятся __init__.py.

Они делают каталоги Python-пакетами и позволяют использовать импорты вроде:

    from app.users.models import User

# 6. База данных и SQLAlchemy

## backend/app/database.py

Создаёт engine:

    create_engine(DATABASE_URL, echo=settings.sql_echo, pool_pre_ping=True)

Engine управляет подключениями. pool_pre_ping проверяет соединение перед использованием.

SessionLocal создаёт SQLAlchemy Session. Session — рабочая область для запросов и транзакций.

Основные методы:

- add — добавить объект;
- get — получить по primary key;
- flush — отправить изменения внутри текущей транзакции;
- commit — подтвердить транзакцию;
- rollback — отменить транзакцию;
- refresh — перечитать объект из базы;
- delete — отметить объект для удаления.

Base наследует DeclarativeBase. От Base наследуются модели User, Product и Category.

get_db создаёт Session для одного HTTP-запроса и закрывает её после завершения.

# 7. Безопасность, пароли и JWT

## backend/app/core/security.py

Содержит хеширование, проверку паролей, создание и чтение JWT.

### Хеширование

PasswordHash.recommended выбирает безопасную конфигурацию Argon2.

hash_password превращает пароль в хеш. В базе никогда не хранится открытый пароль.

verify_password сравнивает введённый пароль с хешем.

Хеш нельзя расшифровать обратно. При забытом пароле нужно создавать процедуру сброса, а не пытаться получить старый пароль.

### JWT

create_access_token записывает:

- sub — ID пользователя;
- iat — время создания;
- exp — срок действия.

Токен подписывается JWT_SECRET_KEY алгоритмом HS256.

decode_access_token проверяет:

- подпись;
- срок действия;
- наличие exp;
- наличие sub;
- положительный ID.

При ошибке возвращается None.

Роль не записывается в токен. Пользователь загружается из базы при каждом защищённом запросе. Поэтому удаление пользователя или изменение его роли действует сразу.

Текущие ограничения:

- нет refresh token;
- нет отзыва отдельных токенов;
- нет подтверждения email;
- нет восстановления пароля;
- нет issuer и audience.

# 8. Пользователи и авторизация

## backend/app/users/models.py

SQLAlchemy-модель users.

UserRole содержит customer и admin.

Поля User:

- id — primary key;
- name — имя до 100 символов;
- email — уникальный индексированный адрес;
- password_hash — Argon2-хеш;
- role — customer или admin;
- created_at — время создания.

Роль по умолчанию customer задаётся и в Python, и на уровне PostgreSQL.

## backend/app/users/schemas.py

Pydantic-схемы.

UserRegister принимает имя, email и пароль.

Ограничения:

- имя от 1 до 100 символов;
- email должен быть корректным;
- пароль от 8 до 128 символов.

Имя очищается через strip. Имя из одних пробелов запрещено. Email очищается и переводится в нижний регистр.

UserLogin принимает email и пароль.

UserResponse возвращает id, name, email, role и created_at. Пароль и password_hash в ответ не попадают.

TokenResponse возвращает access_token и token_type bearer.

## backend/app/users/repository.py

Слой запросов к users.

Методы:

- get_by_id;
- get_by_email;
- create.

SQLAlchemy создаёт параметризованные запросы, поэтому значения пользователя не вставляются в SQL через конкатенацию.

create вызывает flush, чтобы объект получил ID внутри транзакции.

## backend/app/users/service.py

Бизнес-логика регистрации и входа.

Регистрация:

1. Проверяет email.
2. Хеширует пароль.
3. Создаёт пользователя.
4. Делает commit.
5. Делает refresh.
6. Возвращает User.

IntegrityError ловится отдельно. Это защищает от двух одновременных регистраций одинакового email.

При любой ошибке транзакция откатывается.

authenticate получает пользователя и проверяет пароль.

Для неизвестного email и неправильного пароля возвращается одинаковая ошибка Invalid email or password.

## backend/app/auth/router.py

POST /api/v1/auth/register:

1. FastAPI получает JSON.
2. Pydantic создаёт UserRegister.
3. Depends создаёт Session.
4. UserService регистрирует пользователя.
5. UserResponse фильтрует ответ.
6. Возвращается 201 Created.

POST /api/v1/auth/login:

1. Проверяет UserLogin.
2. Ищет пользователя.
3. Проверяет Argon2-хеш.
4. Создаёт JWT.
5. Возвращает TokenResponse.

## backend/app/users/dependencies.py

HTTPBearer извлекает Authorization: Bearer token.

get_current_user:

1. Проверяет наличие заголовка.
2. Проверяет Bearer.
3. Декодирует JWT.
4. Получает пользователя по ID.
5. Возвращает User.

При ошибке возвращается 401.

require_admin сначала получает пользователя, затем сравнивает role с admin. Если роль недостаточна, возвращается 403.

Разница:

- 401 — пользователь не авторизован;
- 403 — пользователь авторизован, но не имеет прав.

## backend/app/users/router.py

GET /api/v1/users/me возвращает профиль пользователя из JWT.

## backend/app/scripts/create_admin.py

CLI-команда для назначения администратора:

    .\.venv\Scripts\python.exe -m app.scripts.create_admin admin@example.com

Скрипт не создаёт аккаунт. Он находит уже зарегистрированного пользователя и меняет его роль.

# 9. Товары

## backend/app/products/models.py

Таблица products.

Поля:

- id;
- name;
- description;
- price;
- stock;
- category_id.

Цена использует Numeric(12, 2), а Python работает с Decimal. Для денег нельзя использовать float из-за ошибок двоичного округления.

Ограничения базы:

- price не меньше нуля;
- stock не меньше нуля.

category_id может быть NULL. Товар можно создать без категории.

Foreign key использует ondelete RESTRICT. Категорию нельзя удалить, пока на неё ссылается товар.

Relationship Product.category связан с Category.products.

## backend/app/products/schemas.py

ProductCreate проверяет:

- name от 1 до 200 символов;
- description до 1000 символов;
- price неотрицательный, максимум 12 цифр и 2 после точки;
- stock целый и неотрицательный;
- category_id положительный или null.

ProductResponse наследует поля ProductCreate и добавляет id.

ConfigDict с from_attributes позволяет Pydantic читать SQLAlchemy-объекты.

## backend/app/products/repository.py

Методы:

- get_all;
- get_by_id;
- create.

get_all сортирует товары по id.

Repository не возвращает HTTPException. Он отвечает только за базу.

## backend/app/products/service.py

get_product возвращает 404, если товара нет.

create_product сначала проверяет существование категории.

Далее:

1. Создаёт объект через repository.
2. Делает commit.
3. Делает refresh.
4. Возвращает Product.

При ошибке выполняется rollback.

Сейчас отсутствуют:

- обновление товара;
- удаление товара;
- изображения;
- публикация и скрытие;
- серверные фильтры;
- пагинация.

## backend/app/products/router.py

| Метод | Путь | Доступ |
|---|---|---|
| GET | /api/v1/products | Все |
| GET | /api/v1/products/{id} | Все |
| POST | /api/v1/products | Только admin |

Зависимость require_admin выполняется до создания товара.

# 10. Категории

## backend/app/category/models.py

Таблица categories:

- id;
- уникальное name;
- необязательное description.

Одна категория связана со многими товарами.

## backend/app/category/schemas.py

CategoryCreate используется для POST.

CategoryUpdate используется для PATCH. Все поля необязательные, потому что PATCH меняет только присланные поля.

CategoryResponse формирует ответ.

## backend/app/category/repository.py

Методы:

- get_all;
- get_by_id;
- create;
- delete.

## backend/app/category/service.py

get_category возвращает 404, если категория отсутствует.

create_category преобразует нарушение уникальности имени в 409.

update_category использует model_dump с exclude_unset. Поэтому поле, которого нет в JSON, не изменяется.

Явное name: null запрещено.

delete_category ловит IntegrityError. Если категория используется товаром, API возвращает 409.

## backend/app/category/router.py

| Метод | Путь | Доступ |
|---|---|---|
| GET | /api/v1/categories | Все |
| GET | /api/v1/categories/{id} | Все |
| POST | /api/v1/categories | Admin |
| PATCH | /api/v1/categories/{id} | Admin |
| DELETE | /api/v1/categories/{id} | Admin |

Успешный DELETE возвращает 204 без JSON.

# 11. Миграции Alembic

## backend/alembic.ini

Конфигурация Alembic.

script_location указывает каталог backend/alembic.

sqlalchemy.url в ini является шаблоном. Настоящий URL подставляется из приложения.

## backend/alembic/env.py

Устанавливает DATABASE_URL из settings.

Импортирует Product, Category и User, чтобы они попали в Base.metadata.

Поддерживает online и offline режимы миграций.

## backend/alembic/script.py.mako

Шаблон новых миграций Alembic. Обычно вручную не редактируется.

## backend/alembic/README

Служебная документация Alembic.

## f97f95adc06f_create_products_table.py

Первая миграция. Создала таблицу Products с заглавной буквы.

## f790a812fb9b_rename_products_to_products.py

Переименовала Products в products.

## 2964d08fe7cc_fix_products_table_name.py

Пустая миграция с pass. Она не меняет схему, но остаётся звеном истории.

## b7e3a91c0f42_repair_catalog_schema.py

Ремонтирует каталог:

- обнаруживает старое имя Products;
- запрещает автоматический запуск, если есть обе таблицы;
- создаёт categories;
- добавляет category_id;
- добавляет foreign key.

Если существуют Products и products одновременно, нужна ручная проверка данных.

## c4a19d6f28b1_create_users_table.py

Создаёт:

- enum user_role;
- таблицу users;
- уникальный индекс email;
- роль customer по умолчанию;
- created_at.

Применённые миграции нельзя бездумно переписывать. Для изменения схемы создаётся новая миграция.

# 12. Backend-тесты

## backend/tests/__init__.py

Делает tests Python-пакетом.

## backend/tests/base.py

Базовый класс интеграционных тестов.

Открывает соединение, начинает внешнюю транзакцию и заменяет get_db тестовой Session.

После тестов выполняет rollback, поэтому тестовые записи не должны оставаться в базе.

Риск: используется база из обычного DATABASE_URL. В будущем нужна отдельная тестовая база.

## backend/tests/test_auth_api.py

Проверяет:

- регистрацию;
- нормализацию имени и email;
- хеширование;
- отсутствие пароля в ответе;
- повторный email;
- неверный email;
- короткий пароль;
- пустое имя;
- вход;
- профиль;
- неверные учётные данные;
- истёкший JWT;
- некорректный JWT;
- токен удалённого пользователя;
- права администратора;
- OpenAPI.

## backend/tests/test_catalog_api.py

Проверяет:

- создание тестового admin;
- CRUD категорий;
- товар с категорией;
- неизвестную категорию;
- списки;
- детали товара;
- 404.

Один тест полагается на товар, созданный другим тестом. Позже каждый тест должен самостоятельно готовить данные.

Запуск:

    cd backend
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v

# 13. Конфигурация frontend

## frontend/package.json

Основные команды:

- npm run dev — Vite dev-сервер;
- npm run build — TypeScript и production-сборка;
- npm run lint — Oxlint;
- npm run preview — просмотр production-сборки.

Основные зависимости:

- react;
- react-dom;
- react-router-dom.

## frontend/package-lock.json

Автоматически фиксирует точные версии всех npm-зависимостей.

Его не редактируют вручную. Для воспроизводимой установки используется npm ci.

## frontend/.env.example

Содержит VITE_API_URL.

Переменные, начинающиеся с VITE_, попадают в браузерную сборку. В них нельзя хранить секреты.

## frontend/.gitignore

Исключает:

- node_modules;
- dist;
- логи;
- локальные файлы;
- настройки IDE.

## frontend/.oxlintrc.json

Настройки Oxlint.

Включает проверку React Hooks и предупреждение для экспорта компонентов.

В проекте нет eslint.config.js, потому что используется Oxlint.

## frontend/vite.config.ts

Подключает React-плагин Vite. Плагин отвечает за JSX и Fast Refresh.

## frontend/tsconfig.json

Корневая TypeScript-конфигурация со ссылками на app и node конфигурации.

## frontend/tsconfig.app.json

Настройки TypeScript для src:

- target ES2023;
- DOM;
- JSX react-jsx;
- noEmit;
- запрет неиспользуемых переменных;
- запрет неиспользуемых параметров.

## frontend/tsconfig.node.json

Настройки TypeScript для vite.config.ts, который работает в Node.js.

## frontend/index.html

HTML-шаблон.

Содержит:

- lang ru;
- meta charset;
- viewport;
- description;
- title;
- favicon;
- div с id root;
- подключение src/main.tsx.

React монтируется в div root.

# 14. Маршруты и точка входа frontend

## frontend/src/main.tsx

Создаёт React root и рендерит:

    StrictMode
      -> BrowserRouter
        -> AuthProvider
          -> App

BrowserRouter даёт маршрутизацию.

AuthProvider предоставляет пользователя и методы входа всем компонентам.

StrictMode помогает находить side effects. В development некоторые useEffect могут запускаться дважды.

## frontend/src/App.tsx

Маршруты:

| Путь | Страница |
|---|---|
| / | HomePage |
| /catalog | CatalogPage |
| /products/:productId | ProductPage |
| /login | LoginPage |
| /register | RegisterPage |
| /cart | CartPage |
| /profile | ProfilePage |
| /admin | AdminPage |
| любой неизвестный | NotFoundPage |

Profile защищён обычным ProtectedRoute.

Admin защищён ProtectedRoute с requireAdmin.

/home перенаправляется на /.

## frontend/src/types.ts

TypeScript-типы:

- UserRole;
- User;
- AuthToken;
- Product;
- Category;
- RegisterPayload;
- LoginPayload;
- ProductPayload.

Типы позволяют обнаружить несовместимость до запуска приложения.

Цена допускает string или number, потому что Decimal из backend может сериализоваться строкой.

## frontend/src/utils/format.ts

formatPrice форматирует KZT через Intl.NumberFormat.

formatDate форматирует дату по русской локали.

# 15. API-клиент

## frontend/src/api/client.ts

Центральное место HTTP-запросов.

API_URL берётся из VITE_API_URL. Если переменной нет, используется http://127.0.0.1:8000/api/v1.

TOKEN_STORAGE_KEY задаёт имя JWT в sessionStorage.

ApiError хранит HTTP-статус и сообщение.

errorMessage умеет читать обычный detail и массив ошибок Pydantic.

Универсальная request:

1. Создаёт Headers.
2. Устанавливает Content-Type.
3. Получает JWT.
4. Добавляет Authorization.
5. Вызывает fetch.
6. Проверяет response.ok.
7. Преобразует ошибку.
8. Возвращает JSON.

Для статуса 204 JSON не читается.

Методы api:

- register;
- login;
- me;
- products;
- product;
- createProduct;
- categories;
- createCategory;
- updateCategory;
- deleteCategory.

# 16. Состояние авторизации frontend

## frontend/src/auth/context.ts

Описывает AuthContextValue:

- user;
- loading;
- login;
- register;
- logout.

## frontend/src/auth/useAuth.ts

Hook для получения AuthContext.

Если useAuth вызван вне AuthProvider, выбрасывается понятная ошибка.

## frontend/src/auth/AuthContext.tsx

Хранит user и loading.

При загрузке:

1. Читает JWT из sessionStorage.
2. Вызывает /users/me.
3. Сохраняет профиль.
4. При ошибке удаляет токен.

login:

1. Вызывает /auth/login.
2. Сохраняет JWT.
3. Вызывает /users/me.
4. Сохраняет User.

register сначала создаёт пользователя, затем вызывает login.

logout удаляет JWT и user.

Токен хранится в sessionStorage:

- сохраняется после перезагрузки;
- удаляется после закрытия вкладки;
- доступен JavaScript;
- при XSS может быть похищен.

Для production можно рассмотреть HttpOnly cookies.

## frontend/src/components/ProtectedRoute.tsx

Состояния:

- loading — проверяем сессию;
- нет user — переход на login;
- требуется admin, но роль customer — 403;
- доступ разрешён — показываются children.

Frontend-проверка улучшает интерфейс. Настоящую безопасность обеспечивает backend.

# 17. Общие React-компоненты

## frontend/src/components/AppLayout.tsx

Общий каркас:

- announcement;
- header;
- бренд;
- навигация;
- профиль;
- выход;
- корзина;
- Outlet;
- footer.

Ссылка Admin показывается только роли admin.

Счётчик корзины пока всегда равен нулю.

## frontend/src/components/PageState.tsx

LoadingState показывает spinner и текст.

ErrorState показывает ошибку и необязательную кнопку повторной загрузки.

## frontend/src/components/ProductCard.tsx

Показывает:

- визуал товара;
- категорию;
- остаток;
- название;
- цену;
- ссылку на детали.

Получает данные через props и сам не обращается к API.

## frontend/src/components/ProductVisual.tsx

Временная замена изображения.

Цвет выбирается по productId modulo 4. В центре выводятся первые буквы названия.

После добавления изображений этот компонент можно заменить или сделать fallback.

## frontend/src/components/Icons.tsx

React SVG-компоненты:

- SearchIcon;
- UserIcon;
- BagIcon;
- ArrowIcon.

Используют currentColor и наследуют цвет CSS.

# 18. Страницы frontend

## frontend/src/pages/HomePage.tsx

Параллельно получает товары и категории.

Показывает первые четыре товара, hero, преимущества и CTA.

Текущая проблема: ошибка API подавляется. При выключенном backend пользователь может увидеть сообщение о пустом каталоге вместо ошибки.

## frontend/src/pages/CatalogPage.tsx

Реализует:

- загрузку товаров и категорий;
- поиск по названию и описанию;
- фильтр по категории;
- сортировку по цене;
- сортировку по названию;
- сортировку по ID;
- сброс фильтров;
- loading;
- error;
- retry;
- empty state.

Фильтрация выполняется в браузере. Для большого каталога понадобятся серверные фильтры и пагинация.

## frontend/src/pages/ProductPage.tsx

Получает productId через useParams.

Проверяет положительный целый ID.

Загружает товар и категории, показывает:

- breadcrumbs;
- название;
- описание;
- категорию;
- цену;
- остаток.

Кнопка корзины пока disabled.

## frontend/src/pages/LoginPage.tsx

Управляемая форма email и password.

При submit:

1. Отменяет стандартную отправку.
2. Включает submitting.
3. Вызывает login.
4. Переходит в профиль или на исходную защищённую страницу.
5. Показывает ошибку.
6. Выключает submitting.

## frontend/src/pages/RegisterPage.tsx

Форма name, email и password.

Проверка есть в HTML и backend. Backend-проверка обязательна, потому что frontend можно обойти.

После регистрации выполняется автоматический вход.

## frontend/src/pages/ProfilePage.tsx

Показывает:

- имя;
- email;
- роль;
- дату регистрации;
- кнопку выхода.

История заказов пока является информационным блоком.

## frontend/src/pages/AdminPage.tsx

Вкладка товаров:

- загрузка списка;
- создание товара;
- цена;
- остаток;
- категория.

Пока нет редактирования и удаления товара.

Вкладка категорий:

- создание;
- выбор для редактирования;
- изменение;
- удаление.

Перед удалением используется window.confirm.

Если категория связана с товаром, backend возвращает 409.

## frontend/src/pages/CartPage.tsx

Страница-заглушка.

Модели корзины, API корзины и логика количества пока отсутствуют.

## frontend/src/pages/NotFoundPage.tsx

Показывает frontend 404 и ссылку на главную.

# 19. Стили и графические файлы

## frontend/src/styles/global.css

Главный подключённый CSS.

Содержит:

- CSS-переменные;
- общие reset-правила;
- шапку;
- кнопки;
- hero;
- сетку товаров;
- карточки;
- каталог;
- формы;
- профиль;
- админку;
- footer;
- loader;
- ошибки;
- media queries.

Палитра:

- beige #f5f0e8;
- cream #fffcf7;
- navy #14243f;
- burgundy #8b2332;
- success #237a57;
- error #b42335.

Адаптивность:

- до 980 px — две карточки;
- до 760 px — основные блоки в одну колонку;
- до 520 px — одна карточка.

Google Fonts загружаются из интернета. Без интернета используются fallback-шрифты.

## frontend/src/App.css

Остаток шаблона Vite. Не импортируется и не влияет на сайт.

## frontend/src/index.css

Старый шаблон Vite. Не импортируется.

## frontend/public/nova.svg

Текущий favicon, подключённый в index.html.

## frontend/public/favicon.svg

Старый Vite favicon. Не используется.

## frontend/public/icons.svg

Старый SVG sprite. Не используется.

## frontend/src/assets/react.svg

Шаблонный логотип React. Не используется.

## frontend/src/assets/vite.svg

Шаблонный логотип Vite. Не используется.

## frontend/src/assets/hero.png

Изображение существует, но текущий HomePage строит hero через HTML и CSS. Файл не импортируется.

# 20. Полный путь регистрации

    RegisterPage
        |
        | register(name, email, password)
        v
    AuthContext
        |
        | api.register
        v
    frontend/api/client.ts
        |
        | POST /api/v1/auth/register
        v
    backend/auth/router.py
        |
        | UserRegister и Pydantic
        v
    UserService.register
        |
        | проверка email
        | Argon2
        | commit или rollback
        v
    UserRepository.create
        |
        v
    SQLAlchemy
        |
        v
    PostgreSQL users

После регистрации AuthContext выполняет login, сохраняет JWT и запрашивает /users/me.

# 21. Полный путь административного запроса

Пример создания категории:

    AdminPage
        |
        | api.createCategory
        v
    client.ts
        |
        | JWT из sessionStorage
        | Authorization: Bearer token
        v
    POST /api/v1/categories
        |
        v
    require_admin
        |
        | проверка Bearer
        | проверка JWT
        | загрузка User
        | проверка role
        v
    CategoryService
        |
        | бизнес-логика
        | commit или rollback
        v
    CategoryRepository
        |
        v
    PostgreSQL

Скрытие кнопки на frontend не является безопасностью. Пользователь может вручную отправить HTTP-запрос. Поэтому права всегда проверяются backend.

# 22. HTTP-ошибки

| Код | Значение | Пример |
|---|---|---|
| 200 | Успешный запрос | Список товаров |
| 201 | Объект создан | Регистрация, товар |
| 204 | Удалено без тела | Категория |
| 401 | Нет действующей авторизации | Нет JWT или токен истёк |
| 403 | Недостаточно прав | Customer вызывает admin API |
| 404 | Объект не найден | Товар или категория |
| 409 | Конфликт | Дубликат email или имени |
| 422 | Ошибка данных | Неверный email, отрицательная цена |
| 500 | Необработанная ошибка | Ошибка кода или базы |

# 23. Ошибки запуска и отладки

## Docker Access is denied

Docker Desktop не запущен или текущий процесс не имеет доступа к Docker Engine.

## Connection refused

Возможные причины:

- PostgreSQL выключен;
- backend выключен;
- неправильный порт;
- контейнер ещё запускается.

## No script_location key found

Alembic запущен не из backend или без правильного alembic.ini.

## Failed to fetch

Frontend не смог обратиться к backend.

Нужно открыть:

    http://127.0.0.1:8000/docs

Если Swagger не открывается, backend не работает.

## CORS error

Frontend открыт с origin, которого нет в cors_origins.

## 401 Unauthorized

Причины:

- токен отсутствует;
- токен повреждён;
- токен истёк;
- пользователь удалён;
- изменился JWT_SECRET_KEY.

## 403 Administrator access required

Пользователь вошёл, но имеет роль customer.

## 409 Category cannot be deleted

На категорию ссылается товар.

## 422 Unprocessable Entity

Pydantic отклонил данные:

- неверный email;
- короткий пароль;
- отрицательная цена;
- отрицательный остаток;
- неправильный тип;
- слишком длинная строка.

## Port already in use

Занят один из портов:

- 5173 — frontend;
- 8000 — backend;
- 5433 — PostgreSQL.

# 24. Как добавлять новый модуль

Для корзины правильная последовательность:

1. Создать SQLAlchemy-модель CartItem.
2. Создать Alembic-миграцию.
3. Применить миграцию.
4. Создать Pydantic-схемы.
5. Создать repository.
6. Создать service.
7. Создать router.
8. Подключить router в api/router.py.
9. Добавить методы в frontend api/client.ts.
10. Добавить TypeScript-типы.
11. Создать frontend-состояние корзины.
12. Реализовать CartPage.
13. Подключить кнопку ProductPage.
14. Написать backend-тесты.
15. Написать frontend-тесты.
16. Запустить build, lint и тесты.

Правило слоёв:

| Слой | Ответственность |
|---|---|
| Router | HTTP, Depends, status code |
| Schema | Формат и валидация |
| Service | Бизнес-правила |
| Repository | Запросы к базе |
| Model | Таблица и связи |
| Migration | Изменение структуры базы |
| API client | HTTP-запросы frontend |
| React component | Интерфейс и состояние |

# 25. Что сделано хорошо

- Backend разделён на слои.
- Пароли используют Argon2.
- JWT имеет срок действия.
- Роль проверяется на backend.
- Пользователь загружается из базы при защищённом запросе.
- Email уникален на уровне PostgreSQL.
- Цена использует Decimal и NUMERIC.
- Цена и остаток защищены constraints.
- Транзакции откатываются при ошибках.
- Есть Alembic.
- Есть интеграционные тесты.
- Frontend использует общий API-клиент.
- Есть loading, error и empty states.
- Profile и Admin защищены.
- Интерфейс адаптирован под мобильные экраны.

# 26. Что нужно улучшить

1. Создать отдельную тестовую базу.
2. Убрать зависимость тестов от порядка.
3. Добавить редактирование и удаление товаров.
4. Нормализовать названия товаров и категорий.
5. Добавить серверный поиск.
6. Добавить пагинацию.
7. Реализовать автоматический logout при 401.
8. Показывать ошибку API на главной.
9. Удалить неиспользуемые Vite-файлы.
10. Добавить изображения товаров.
11. Реализовать корзину в PostgreSQL.
12. Реализовать заказы и позиции заказа.
13. Оформлять заказ одной транзакцией.
14. Проверять остаток при конкурентных покупках.
15. Добавить refresh token или HttpOnly cookies.
16. Ужесточить production CORS.
17. Добавить безопасное логирование.
18. Добавить frontend-тесты.
19. Добавить CI для сборки и тестов.
20. Подготовить production deployment.

Текущая основная цепочка проекта уже построена правильно:

    React
      -> API client
      -> FastAPI router
      -> Pydantic
      -> Service
      -> Repository
      -> SQLAlchemy
      -> PostgreSQL

Следующий большой учебный этап — корзина. Она закрепит связи между таблицами, CRUD, проверку остатков, защищённые пользовательские данные и синхронизацию frontend с backend.
