# Flask API Service

REST API сервис на Python Flask с авторизацией по Bearer токену для работы с PostgreSQL базой данных.

## Возможности

- ✅ RESTful API с JSON ответами
- ✅ Авторизация по Bearer токену (JWT)
- ✅ Подключение к PostgreSQL
- ✅ CRUD операции для записей данных
- ✅ Массовые операции
- ✅ Пагинация и фильтрация
- ✅ Веб-интерфейс для тестирования API
- ✅ Docker поддержка

## Быстрый старт

### Локальный запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте переменные окружения:
```bash
export DATABASE_URL="postgresql://username:password@localhost/dbname"
export JWT_SECRET_KEY="your-secret-key"
export SESSION_SECRET="your-session-secret"
```

3. Запустите приложение:
```bash
python main.py
```

### Запуск в Docker

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd flask-api-service
```

2. Запустите с Docker Compose:
```bash
docker-compose up -d
```

Это запустит:
- Flask API на порту 5000
- PostgreSQL базу данных на порту 5432

## API Endpoints

### Авторизация
Все endpoints (кроме `/api/health`) требуют Bearer токен в заголовке:
```
Authorization: Bearer <your-token>
```

### Доступные endpoints:

- `GET /api/health` - Проверка состояния API (без авторизации)
- `GET /api/records` - Получить все записи
- `GET /api/records/<id>` - Получить запись по ID
- `POST /api/records` - Создать новую запись
- `PUT /api/records/<id>` - Обновить запись
- `DELETE /api/records/<id>` - Удалить запись
- `POST /api/records/bulk` - Массовые операции

### Пример запроса:

```bash
# Получить все записи
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     http://localhost:5000/api/records

# Создать новую запись
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title": "Новая запись", "content": "Содержимое", "category": "example"}' \
     http://localhost:5000/api/records
```

## Веб-интерфейс

Откройте браузер и перейдите по адресу:
```
http://localhost:5000
```

Интерфейс позволяет:
- Вводить Bearer токен
- Тестировать все API endpoints
- Просматривать ответы в реальном времени

## Получение токена

При первом запуске создается админский токен. Найдите его в логах приложения:
```
INFO:app:Created admin token: <token-value>
```

## Структура проекта

```
├── app.py              # Основное приложение Flask
├── main.py             # Точка входа
├── models.py           # Модели базы данных
├── auth.py             # Система авторизации
├── api_routes.py       # API endpoints
├── templates/          # HTML шаблоны
├── static/             # Статические файлы
├── Dockerfile          # Docker конфигурация
├── docker-compose.yml  # Docker Compose
└── .dockerignore       # Исключения для Docker
```

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL подключения к PostgreSQL | - |
| `JWT_SECRET_KEY` | Секретный ключ для JWT | `jwt-secret-change-in-production` |
| `SESSION_SECRET` | Секретный ключ для сессий | `dev-secret-key-change-in-production` |

## Модель данных

### DataRecord
- `id` - Уникальный идентификатор
- `title` - Заголовок (обязательно)
- `content` - Содержимое
- `category` - Категория
- `is_active` - Статус активности
- `created_at` - Время создания
- `updated_at` - Время обновления

## Разработка

### Добавление новых endpoints

1. Добавьте функцию в `api_routes.py`
2. Используйте декораторы `@require_auth` и `@validate_json_input`
3. Обработайте ошибки с помощью try/except

### Работа с базой данных

Модели находятся в `models.py`. Для изменения схемы:
1. Обновите модель
2. Перезапустите приложение (таблицы создаются автоматически)

## Безопасность

- Используйте сильные секретные ключи в production
- JWT токены имеют срок действия 24 часа
- Все API endpoints защищены авторизацией
- Используется CORS для браузерных запросов

## Мониторинг

Health check endpoint:
```bash
curl http://localhost:5000/api/health
```

Docker health check настроен автоматически.