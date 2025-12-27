# База данных для веб-помощника (AI чат-бот для сайта)

## Описание

Полная база данных для AI помощника на веб-сайте с поддержкой:
- Анонимных и зарегистрированных пользователей
- Истории диалогов
- Базы знаний (FAQ)
- Настройки виджета чата
- Аналитики и оценки качества

## Структура базы данных

### Таблицы

1. **visitors** - анонимные посетители сайта
   - ID, visitor_uuid, IP-адрес, браузер, устройство
   - Время первого и последнего визита

2. **users** - зарегистрированные пользователи (опционально)
   - Имя, email, телефон

3. **sessions** - сессии чатов
   - Связь с visitor или user
   - UUID сессии, URL страницы
   - Оценка удовлетворенности (1-5)

4. **messages** - сообщения в чате
   - Роль (user/assistant/system)
   - Содержимое, количество токенов

5. **knowledge_base** - база знаний
   - Вопросы и ответы
   - Категории, ключевые слова
   - Статистика просмотров

6. **chat_widget** - настройки виджета
   - Цвета, тексты приветствия
   - Время работы, позиция на странице

7. **context** - контекст и настройки агента

## Установка

### Базовая (только реляционная БД)
```bash
pip install sqlalchemy psycopg2-binary
```

### С векторным поиском (DeepSeek API - рекомендуется)
```bash
pip install sqlalchemy psycopg2-binary pgvector requests
```
См. подробнее: [DEEPSEEK_GUIDE.md](DEEPSEEK_GUIDE.md)

### С векторным поиском (локальные модели)
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sqlalchemy psycopg2-binary pgvector sentence-transformers
```
См. подробнее: [PGVECTOR_GUIDE.md](PGVECTOR_GUIDE.md)

## Использование

### Базовый пример

```python
from db.db import Database

# Создание БД (SQLite для разработки)
db = Database('sqlite:///web_assistant.db')
db.create_tables()

# Для продакшена (PostgreSQL)
# db = Database('postgresql://user:password@localhost/dbname')

# 1. Создать анонимного посетителя
visitor_id = db.create_or_get_visitor(
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0...",
    device_type="desktop",
    browser="Chrome"
)

# 2. Начать сессию чата
session_id, session_uuid = db.create_session(
    visitor_id=visitor_id,
    page_url="https://example.com/products"
)

# 3. Добавить сообщения
db.add_message(session_id, "assistant", "Здравствуйте! Чем могу помочь?")
db.add_message(session_id, "user", "Как оформить заказ?")

# 4. Поиск в базе знаний
results = db.search_knowledge("заказ")
if results:
    db.add_message(session_id, "assistant", results[0].answer)

# 5. Завершить сессию с оценкой
db.end_session(session_id, satisfaction_rating=5)
```

### Настройка виджета

```python
db.update_widget_settings(
    'default',
    welcome_message="Здравствуйте! Я ваш виртуальный помощник",
    bot_name="Помощник сайта",
    primary_color="#4CAF50",
    position="bottom-right",
    auto_open_delay=5  # Открыть автоматически через 5 сек
)

# Получить настройки
widget = db.get_widget_settings('default')
print(widget.welcome_message)
```

### Работа с базой знаний

```python
# Добавить FAQ
db.add_knowledge(
    question="Как оформить заказ?",
    answer="Выберите товар, добавьте в корзину...",
    category="Заказы",
    keywords="заказ, купить, корзина"
)

# Поиск
results = db.search_knowledge("доставка", limit=5)
for item in results:
    print(f"Q: {item.question}")
    print(f"A: {item.answer}\n")
```

## API методы

### Посетители
- `create_or_get_visitor(visitor_id, ip_address, user_agent, device_type, browser)`
- `create_user(username, email, phone)` - для регистрации

### Сессии
- `create_session(visitor_id, user_id, title, page_url)` → session_id, session_uuid
- `end_session(session_id, satisfaction_rating)`
- `get_session_messages(session_id)`

### Сообщения
- `add_message(session_id, role, content, tokens_used)`

### База знаний
- `add_knowledge(question, answer, category, keywords)`
- `search_knowledge(query, category, limit)`

### Виджет
- `get_widget_settings(name)`
- `update_widget_settings(name, **kwargs)`

### Контекст
- `set_context(key, value, category)`
- `get_context(key)`

## Запуск примера

```bash
cd /home/brokender/edu/llm_agent_consultant_with_db
python db/db.py
```

## Для продакшена

1. Используйте PostgreSQL вместо SQLite
2. Добавьте полнотекстовый поиск для knowledge_base
3. Настройте индексы для производительности
4. Реализуйте очистку старых сессий
5. Добавьте логирование ошибок

## Пример с Flask

```python
from flask import Flask, request, jsonify
from db.db import Database

app = Flask(__name__)
db = Database('sqlite:///web_assistant.db')

@app.route('/chat/start', methods=['POST'])
def start_chat():
    data = request.json
    visitor_id = db.create_or_get_visitor(
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    session_id, session_uuid = db.create_session(
        visitor_id=visitor_id,
        page_url=data.get('page_url')
    )
    return jsonify({'session_uuid': session_uuid})

@app.route('/chat/message', methods=['POST'])
def send_message():
    data = request.json
    db.add_message(
        data['session_id'],
        'user',
        data['message']
    )
    # Здесь интеграция с AI для генерации ответа
    return jsonify({'status': 'ok'})
```

## Лицензия

MIT
