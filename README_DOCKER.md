# Docker Setup для Web Assistant

## Быстрый старт

### 1. Настройка переменных окружения

```bash
# Скопировать пример
cp .env.example .env

# Отредактировать .env и добавить ваш API ключ DeepSeek
nano .env
```

### 2. Запуск с Docker Compose

```bash
# Запустить все сервисы
docker-compose up -d

# Посмотреть логи
docker-compose logs -f

# Проверить статус
docker-compose ps
```

### 3. Инициализация базы данных

```bash
# БД инициализируется автоматически при первом запуске
# Или можно запустить вручную:
docker-compose exec web_assistant python3 create_db.py
```

### 4. Остановка

```bash
# Остановить сервисы
docker-compose down

# Остановить и удалить данные
docker-compose down -v
```

---

## Архитектура

```
┌─────────────────┐
│  web_assistant  │  (Python 3.11)
│   Port: 8000    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   vector_db     │  (PostgreSQL + pgvector)
│   Port: 5432    │
└─────────────────┘
```

---

## Сервисы

### vector_db (PostgreSQL + pgvector)
- **Image**: pgvector/pgvector:pg16
- **Port**: 5432
- **Database**: web_assistant
- **User**: user
- **Password**: password

### web_assistant (Python App)
- **Port**: 8000
- **Auto-reload**: Да (для разработки)
- **Зависимости**: requirements.txt

---

## Полезные команды

### Подключение к БД

```bash
# Через docker
docker-compose exec vector_db psql -U user -d web_assistant

# Локально (если установлен psql)
psql -h localhost -U user -d web_assistant
```

### Просмотр таблиц

```sql
-- В psql
\dt

-- Посмотреть структуру таблицы
\d visitors
\d sessions
\d messages
```

### Работа с приложением

```bash
# Запустить Python shell
docker-compose exec web_assistant python3

# Выполнить скрипт
docker-compose exec web_assistant python3 your_script.py

# Установить дополнительные пакеты
docker-compose exec web_assistant pip install package_name
```

### Логи

```bash
# Все логи
docker-compose logs -f

# Только БД
docker-compose logs -f vector_db

# Только приложение
docker-compose logs -f web_assistant
```

### Перезапуск

```bash
# Перезапустить все
docker-compose restart

# Перезапустить только приложение
docker-compose restart web_assistant

# Пересобрать и перезапустить
docker-compose up -d --build
```

---

## Разработка

### Изменения в коде

Приложение запущено с `--reload`, поэтому изменения применяются автоматически.

### Обновление зависимостей

```bash
# Редактировать requirements.txt
nano requirements.txt

# Пересобрать образ
docker-compose up -d --build web_assistant
```

### Debugging

```bash
# Подключиться к контейнеру
docker-compose exec web_assistant bash

# Проверить переменные окружения
docker-compose exec web_assistant env

# Проверить установленные пакеты
docker-compose exec web_assistant pip list
```

---

## Продакшен

Для продакшена измените `docker-compose.yml`:

```yaml
web_assistant:
  # Убрать --reload
  command: python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
  
  # Не монтировать код
  # volumes:
  #   - ./:/app
  
  # Использовать secrets для API ключей
  secrets:
    - deepseek_api_key
```

---

## Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DATABASE_URL` | URL PostgreSQL | `postgresql://user:password@vector_db:5432/web_assistant` |
| `DEEPSEEK_API_KEY` | API ключ DeepSeek | - |
| `PYTHONUNBUFFERED` | Отключить буферизацию Python | `1` |

---

## Backup и восстановление

### Создать backup

```bash
# Backup всей БД
docker-compose exec vector_db pg_dump -U user web_assistant > backup.sql

# Backup только данных
docker-compose exec vector_db pg_dump -U user --data-only web_assistant > data.sql
```

### Восстановить из backup

```bash
# Восстановить БД
cat backup.sql | docker-compose exec -T vector_db psql -U user web_assistant
```

---

## Мониторинг

### Проверка здоровья БД

```bash
# Health check
docker-compose exec vector_db pg_isready -U user

# Статистика
docker-compose exec vector_db psql -U user -d web_assistant -c "SELECT * FROM pg_stat_database WHERE datname='web_assistant';"
```

### Размер БД

```bash
docker-compose exec vector_db psql -U user -d web_assistant -c "SELECT pg_size_pretty(pg_database_size('web_assistant'));"
```

---

## Troubleshooting

### БД не запускается

```bash
# Проверить логи
docker-compose logs vector_db

# Удалить volumes и пересоздать
docker-compose down -v
docker-compose up -d
```

### Приложение не может подключиться к БД

```bash
# Проверить что БД готова
docker-compose exec vector_db pg_isready -U user

# Проверить network
docker network inspect llm_agent_consultant_with_db_default
```

### Порт уже занят

```bash
# Изменить порт в docker-compose.yml
ports:
  - "5433:5432"  # Вместо 5432
```

---

## Структура проекта

```
.
├── docker-compose.yml    # Конфигурация сервисов
├── Dockerfile           # Сборка Python приложения
├── requirements.txt     # Python зависимости
├── .env                 # Переменные окружения (не в git)
├── .env.example         # Пример переменных
├── .dockerignore        # Исключения при сборке
├── create_db.py         # Инициализация БД
├── db/
│   ├── __init__.py
│   ├── db.py           # Реляционная БД
│   └── deepseek_vector_db.py  # Векторная БД
└── README_DOCKER.md    # Эта документация
```

---

## Полезные ссылки

- [Docker Compose](https://docs.docker.com/compose/)
- [pgvector](https://github.com/pgvector/pgvector)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostgreSQL](https://www.postgresql.org/docs/)
