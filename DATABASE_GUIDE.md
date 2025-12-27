# Документация базы данных веб-помощника

## Оглавление
1. [Обзор](#обзор)
2. [Структура таблиц](#структура-таблиц)
3. [Инициализация](#инициализация)
4. [Работа с посетителями](#работа-с-посетителями)
5. [Работа с пользователями](#работа-с-пользователями)
6. [Работа с сессиями](#работа-с-сессиями)
7. [Работа с сообщениями](#работа-с-сообщениями)
8. [База знаний (FAQ)](#база-знаний-faq)
9. [Настройки виджета](#настройки-виджета)
10. [Контекст агента](#контекст-агента)
11. [Полные примеры](#полные-примеры)

---

## Обзор

База данных веб-помощника построена на PostgreSQL с использованием SQLAlchemy ORM. Она поддерживает:
- Анонимных посетителей и зарегистрированных пользователей
- Хранение истории диалогов
- Базу знаний для быстрых ответов
- Настройки виджета чата
- Контекст и настройки AI агента

---

## Структура таблиц

### 1. **visitors** - Анонимные посетители

Хранит информацию о посетителях сайта до регистрации.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| visitor_id | String(100) | UUID посетителя (уникальный) |
| ip_address | String(50) | IP-адрес |
| user_agent | String(500) | User-Agent браузера |
| device_type | String(50) | desktop, mobile, tablet |
| browser | String(100) | Chrome, Firefox, Safari и т.д. |
| first_visit | DateTime | Первый визит |
| last_visit | DateTime | Последний визит |

**Связи:**
- `sessions` → Один-ко-многим с таблицей `sessions`

---

### 2. **users** - Зарегистрированные пользователи

Хранит информацию о зарегистрированных пользователях (опционально).

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| username | String(100) | Имя пользователя (уникальное) |
| email | String(255) | Email (уникальный) |
| phone | String(50) | Телефон |
| created_at | DateTime | Дата регистрации |

**Связи:**
- `sessions` → Один-ко-многим с таблицей `sessions`

---

### 3. **sessions** - Сессии чатов

Каждая сессия представляет один диалог с пользователем.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| visitor_id | Integer | FK на visitors (для анонимных) |
| user_id | Integer | FK на users (для зарегистрированных) |
| session_uuid | String(100) | UUID сессии для внешнего API |
| title | String(255) | Название сессии |
| page_url | String(500) | URL страницы, где начался чат |
| created_at | DateTime | Время начала |
| updated_at | DateTime | Время последнего обновления |
| ended_at | DateTime | Время завершения |
| is_active | Boolean | Активна ли сессия |
| satisfaction_rating | Integer | Оценка 1-5 |

**Связи:**
- `visitor` → Многие-к-одному с `visitors`
- `user` → Многие-к-одному с `users`
- `messages` → Один-ко-многим с `messages`

---

### 4. **messages** - Сообщения

Все сообщения в диалоге.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| session_id | Integer | FK на sessions |
| role | String(50) | user, assistant, system |
| content | Text | Текст сообщения |
| timestamp | DateTime | Время отправки |
| tokens_used | Integer | Использованные токены (для аналитики) |

**Связи:**
- `session` → Многие-к-одному с `sessions`

---

### 5. **knowledge_base** - База знаний (FAQ)

Вопросы и ответы для быстрых ответов.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| question | Text | Вопрос |
| answer | Text | Ответ |
| category | String(100) | Категория (Доставка, Оплата и т.д.) |
| keywords | Text | Ключевые слова для поиска |
| **embedding** | **Vector(1024)** | **Векторное представление вопроса (для семантического поиска)** |
| priority | Integer | Приоритет отображения |
| is_active | Boolean | Активна ли запись |
| views_count | Integer | Количество просмотров |
| helpful_count | Integer | Количество положительных оценок |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

> **💡 Поле `embedding`** содержит векторное представление вопроса (1024 числа от DeepSeek API).  
> Используется для семантического поиска - находит похожие по смыслу вопросы.  
> Подробнее: [VECTOR_SEARCH_GUIDE.md](VECTOR_SEARCH_GUIDE.md)

---

### 6. **chat_widget** - Настройки виджета

Настройки внешнего вида и поведения чат-виджета.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| name | String(100) | Название профиля (уникальное) |
| welcome_message | Text | Приветственное сообщение |
| placeholder_text | String(255) | Placeholder в поле ввода |
| bot_name | String(100) | Имя бота |
| bot_avatar_url | String(500) | URL аватара |
| primary_color | String(20) | Основной цвет (#hex) |
| position | String(20) | bottom-right, bottom-left и т.д. |
| auto_open_delay | Integer | Задержка автооткрытия (сек) |
| offline_message | Text | Сообщение в нерабочее время |
| is_active | Boolean | Активен ли виджет |
| business_hours | JSON | Рабочие часы |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

---

### 7. **context** - Контекст агента

Ключ-значение хранилище для настроек и контекста AI.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer | Первичный ключ |
| key | String(255) | Ключ (уникальный) |
| value | Text | Значение |
| category | String(100) | Категория |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

---

## Инициализация

### Подключение к базе данных

```python
from db.db import Database

# SQLite (для разработки)
db = Database('sqlite:///web_assistant.db')

# PostgreSQL (для продакшена)
db = Database('postgresql://user:password@localhost:5432/web_assistant')

# Через Docker
db = Database('postgresql://user:password@vector_db:5432/web_assistant')

# Через переменную окружения
import os
db_url = os.getenv('DATABASE_URL')
db = Database(db_url)
```

### Создание таблиц

```python
# Создать все таблицы
db.create_tables()

# Удалить все таблицы (осторожно!)
db.drop_tables()
```

---

## Работа с посетителями

### Создание нового посетителя

```python
# Автоматическая генерация visitor_id
visitor_id = db.create_or_get_visitor(
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    device_type="desktop",
    browser="Chrome"
)
print(f"Создан посетитель: {visitor_id}")
```

**Вывод:**
```
Создан посетитель: 1
```

### Получение существующего посетителя

```python
# По существующему UUID
visitor_uuid = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
visitor_id = db.create_or_get_visitor(
    visitor_id=visitor_uuid,
    ip_address="192.168.1.1"
)

# Если visitor_uuid существует - обновит last_visit
# Если нет - создаст нового
```

### Пример: Отслеживание посетителя с cookies

```python
from flask import request, session as flask_session

def track_visitor():
    # Получить UUID из cookies или создать новый
    visitor_uuid = flask_session.get('visitor_id')
    
    visitor_id = db.create_or_get_visitor(
        visitor_id=visitor_uuid,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        device_type=get_device_type(request),
        browser=get_browser_name(request)
    )
    
    # Сохранить UUID в cookies для следующих визитов
    if not visitor_uuid:
        # Получить сохраненный UUID из БД
        flask_session['visitor_id'] = visitor_uuid
    
    return visitor_id
```

---

## Работа с пользователями

### Создание пользователя

```python
# Минимальная информация
user_id = db.create_user("john_doe")

# Полная информация
user_id = db.create_user(
    username="john_doe",
    email="john@example.com",
    phone="+79001234567"
)
print(f"Создан пользователь: {user_id}")
```

**Вывод:**
```
Создан пользователь: 1
```

### Получение пользователя

```python
user = db.get_user(user_id=1)

if user:
    print(f"Имя: {user.username}")
    print(f"Email: {user.email}")
    print(f"Телефон: {user.phone}")
    print(f"Зарегистрирован: {user.created_at}")
```

**Вывод:**
```
Имя: john_doe
Email: john@example.com
Телефон: +79001234567
Зарегистрирован: 2025-12-27 18:30:45
```

### Пример: Регистрация пользователя

```python
def register_user(username, email, phone):
    try:
        user_id = db.create_user(username, email, phone)
        return {"success": True, "user_id": user_id}
    except Exception as e:
        # Обработка ошибок (например, дубликат email)
        return {"success": False, "error": str(e)}

# Использование
result = register_user("alice", "alice@example.com", "+79991234567")
if result['success']:
    print(f"Пользователь создан с ID: {result['user_id']}")
```

---

## Работа с сессиями

### Создание сессии для анонимного посетителя

```python
# Начать новую сессию
session_id, session_uuid = db.create_session(
    visitor_id=1,
    page_url="https://example.com/shop/products"
)

print(f"Session ID: {session_id}")
print(f"Session UUID: {session_uuid}")
```

**Вывод:**
```
Session ID: 1
Session UUID: 7a8b9c0d-1e2f-3g4h-5i6j-7k8l9m0n1o2p
```

### Создание сессии для зарегистрированного пользователя

```python
session_id, session_uuid = db.create_session(
    user_id=1,
    title="Вопросы по заказу #12345",
    page_url="https://example.com/order/12345"
)
```

### Завершение сессии

```python
# Без оценки
db.end_session(session_id=1)

# С оценкой
db.end_session(session_id=1, satisfaction_rating=5)
```

### Получение всех сообщений сессии

```python
messages = db.get_session_messages(session_id=1)

for msg in messages:
    print(f"[{msg.timestamp}] {msg.role}: {msg.content}")
```

**Вывод:**
```
[2025-12-27 18:35:12] assistant: Здравствуйте! Чем могу помочь?
[2025-12-27 18:35:45] user: Как оформить заказ?
[2025-12-27 18:35:50] assistant: Выберите товар, добавьте в корзину...
```

### Пример: Полный цикл сессии

```python
def start_chat(visitor_id, page_url):
    """Начать новый чат"""
    session_id, session_uuid = db.create_session(
        visitor_id=visitor_id,
        page_url=page_url
    )
    
    # Отправить приветствие
    widget = db.get_widget_settings('default')
    db.add_message(
        session_id=session_id,
        role='assistant',
        content=widget.welcome_message if widget else "Здравствуйте!"
    )
    
    return session_uuid

def end_chat(session_id, rating=None):
    """Завершить чат"""
    db.end_session(session_id, satisfaction_rating=rating)
    
    # Получить статистику
    messages = db.get_session_messages(session_id)
    user_messages = [m for m in messages if m.role == 'user']
    
    return {
        'total_messages': len(messages),
        'user_messages': len(user_messages),
        'rating': rating
    }
```

---

## Работа с сообщениями

### Добавление сообщения

```python
# Сообщение пользователя
msg_id = db.add_message(
    session_id=1,
    role='user',
    content='Как оформить заказ?'
)

# Сообщение ассистента
msg_id = db.add_message(
    session_id=1,
    role='assistant',
    content='Выберите товар, нажмите "Добавить в корзину"...'
)

# Системное сообщение
msg_id = db.add_message(
    session_id=1,
    role='system',
    content='Пользователь перешел на страницу оплаты'
)

# С учетом токенов (для аналитики)
msg_id = db.add_message(
    session_id=1,
    role='assistant',
    content='Ответ от AI...',
    tokens_used=150
)
```

### Пример: Обработка сообщения пользователя

```python
def process_message(session_id, user_message):
    """Обработать сообщение пользователя"""
    
    # Сохранить сообщение пользователя
    db.add_message(session_id, 'user', user_message)
    
    # Поиск в базе знаний
    kb_results = db.search_knowledge(user_message, limit=1)
    
    if kb_results and kb_results[0]:
        # Найден готовый ответ
        answer = kb_results[0].answer
        db.add_message(session_id, 'assistant', answer)
        return {'answer': answer, 'source': 'knowledge_base'}
    else:
        # Передать в AI для генерации ответа
        # ... вызов AI API ...
        ai_answer = "Ответ от AI..."
        db.add_message(session_id, 'assistant', ai_answer, tokens_used=120)
        return {'answer': ai_answer, 'source': 'ai'}
```

---

## База знаний (FAQ)

> **🔥 ВАЖНО:** База знаний поддерживает **векторный поиск** для семантического понимания вопросов!  
> См. [VECTOR_SEARCH_GUIDE.md](VECTOR_SEARCH_GUIDE.md) для подробностей.

### Добавление FAQ

```python
# Простое добавление (эмбеддинг создастся автоматически)
faq_id = db.add_knowledge(
    question="Как оформить заказ?",
    answer="Выберите товар, нажмите 'Добавить в корзину', оформите заказ"
)
# ✅ Автоматически создается embedding через DeepSeek API

# С полной информацией
faq_id = db.add_knowledge(
    question="Какие способы оплаты доступны?",
    answer="Мы принимаем банковские карты Visa/MasterCard, PayPal, наличные при получении",
    category="Оплата",
    keywords="оплата, карта, деньги, paypal, visa, mastercard"
)

# Без автоматического создания эмбеддинга
faq_id = db.add_knowledge(
    question="Вопрос",
    answer="Ответ",
    auto_embed=False  # Отключить DeepSeek API
)
```

### Поиск в базе знаний

База знаний использует **векторный поиск** для понимания смысла вопросов:

```python
# Векторный поиск (по умолчанию, если есть DEEPSEEK_API_KEY)
results = db.search_knowledge("доставка")

# Понимает синонимы и контекст:
# "доставка" найдет: "когда придет", "сколько ждать", "отправка"

for kb in results:
    print(f"Q: {kb.question}")
    print(f"A: {kb.answer}")
    print(f"Категория: {kb.category}")
    print("---")
```

**Вывод:**
```
Q: Сколько времени занимает доставка?
A: Доставка по Москве - 1-2 дня, по России - 3-7 дней
Категория: Доставка
---
Q: Когда придет мой заказ?
A: После отправки мы пришлем трек-номер
Категория: Доставка
---
```

**Текстовый поиск (если нужен точный поиск):**
```python
results = db.search_knowledge("доставка", use_vector=False)
```

### Поиск с фильтром по категории

```python
# Только вопросы по оплате
results = db.search_knowledge("карта", category="Оплата", limit=3)
```

### Массовое добавление FAQ

```python
faq_data = [
    {
        'question': 'Как отследить заказ?',
        'answer': 'После отправки вы получите трек-номер на email',
        'category': 'Доставка',
        'keywords': 'трек, отследить, где заказ'
    },
    {
        'question': 'Можно ли вернуть товар?',
        'answer': 'Да, возврат возможен в течение 14 дней',
        'category': 'Возвраты',
        'keywords': 'возврат, вернуть, обмен'
    },
    {
        'question': 'Есть ли доставка в регионы?',
        'answer': 'Да, доставляем по всей России',
        'category': 'Доставка',
        'keywords': 'регионы, россия, доставка'
    }
]

for faq in faq_data:
    db.add_knowledge(**faq)

print(f"Добавлено {len(faq_data)} FAQ")
```

### Пример: Умный поиск с fallback

```python
def smart_search(query):
    """Умный поиск с несколькими попытками"""
    
    # Попытка 1: Точный поиск
    results = db.search_knowledge(query, limit=3)
    if results:
        return results
    
    # Попытка 2: Поиск по отдельным словам
    words = query.split()
    for word in words:
        if len(word) > 3:  # Игнорировать короткие слова
            results = db.search_knowledge(word, limit=3)
            if results:
                return results
    
    return None

# Использование
results = smart_search("сколько стоит доставка курьером")
```

---

## Настройки виджета

### Получение настроек

```python
widget = db.get_widget_settings('default')

if widget:
    print(f"Имя бота: {widget.bot_name}")
    print(f"Приветствие: {widget.welcome_message}")
    print(f"Цвет: {widget.primary_color}")
    print(f"Позиция: {widget.position}")
```

**Вывод:**
```
Имя бота: Помощник
Приветствие: Здравствуйте! Чем могу помочь?
Цвет: #4CAF50
Позиция: bottom-right
```

### Обновление настроек

```python
# Обновить отдельные поля
db.update_widget_settings(
    'default',
    bot_name="AI Консультант",
    primary_color="#2196F3"
)

# Обновить все настройки
db.update_widget_settings(
    'default',
    welcome_message="Привет! Я ваш виртуальный помощник. Как я могу помочь?",
    placeholder_text="Напишите ваш вопрос...",
    bot_name="Умный помощник",
    bot_avatar_url="https://example.com/avatar.png",
    primary_color="#4CAF50",
    position="bottom-right",
    auto_open_delay=10,
    offline_message="Мы сейчас offline. Оставьте сообщение!",
    is_active=True,
    business_hours={
        "monday": {"start": "09:00", "end": "18:00"},
        "tuesday": {"start": "09:00", "end": "18:00"},
        "wednesday": {"start": "09:00", "end": "18:00"},
        "thursday": {"start": "09:00", "end": "18:00"},
        "friday": {"start": "09:00", "end": "18:00"}
    }
)
```

### Создание нескольких профилей виджета

```python
# Профиль для продаж
db.update_widget_settings(
    'sales',
    bot_name="Менеджер продаж",
    welcome_message="Здравствуйте! Помогу выбрать товар!",
    primary_color="#FF5722"
)

# Профиль для поддержки
db.update_widget_settings(
    'support',
    bot_name="Техподдержка",
    welcome_message="Здравствуйте! Опишите вашу проблему",
    primary_color="#607D8B"
)

# Использование
sales_widget = db.get_widget_settings('sales')
support_widget = db.get_widget_settings('support')
```

---

## Контекст агента

### Сохранение контекста

```python
# Системный промпт
db.set_context(
    key='system_prompt',
    value='Ты дружелюбный помощник интернет-магазина. Отвечай кратко и по делу.',
    category='system'
)

# Настройки AI
db.set_context(
    key='ai_model',
    value='deepseek-chat',
    category='config'
)

db.set_context(
    key='ai_temperature',
    value='0.7',
    category='config'
)

# Кастомные данные
db.set_context(
    key='shop_name',
    value='Мой Магазин',
    category='branding'
)
```

### Получение контекста

```python
system_prompt = db.get_context('system_prompt')
model = db.get_context('ai_model')
temperature = db.get_context('ai_temperature')
shop_name = db.get_context('shop_name')

print(f"Промпт: {system_prompt}")
print(f"Модель: {model}")
print(f"Temperature: {temperature}")
print(f"Название магазина: {shop_name}")
```

**Вывод:**
```
Промпт: Ты дружелюбный помощник интернет-магазина...
Модель: deepseek-chat
Temperature: 0.7
Название магазина: Мой Магазин
```

### Обновление существующего контекста

```python
# При повторном вызове set_context - значение обновится
db.set_context('ai_temperature', '0.5', 'config')
```

---

## Полные примеры

### Пример 1: Обработка нового посетителя

```python
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)
db = Database('postgresql://user:password@localhost:5432/web_assistant')

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    """Начать новый чат"""
    data = request.json
    
    # Создать или получить посетителя
    visitor_id = db.create_or_get_visitor(
        visitor_id=data.get('visitor_id'),  # От клиента
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        device_type=data.get('device_type'),
        browser=data.get('browser')
    )
    
    # Создать сессию
    session_id, session_uuid = db.create_session(
        visitor_id=visitor_id,
        page_url=data.get('page_url')
    )
    
    # Получить приветствие
    widget = db.get_widget_settings('default')
    welcome_msg = widget.welcome_message if widget else "Здравствуйте!"
    
    # Добавить приветственное сообщение
    db.add_message(session_id, 'assistant', welcome_msg)
    
    return jsonify({
        'session_uuid': session_uuid,
        'welcome_message': welcome_msg
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
```

### Пример 2: Обработка сообщения с поиском в FAQ

```python
@app.route('/api/chat/message', methods=['POST'])
def process_message():
    """Обработать сообщение пользователя"""
    data = request.json
    session_uuid = data.get('session_uuid')
    user_message = data.get('message')
    
    # Найти сессию по UUID
    from db.db import Session as DBSession
    session_obj = db.get_session()
    chat_session = session_obj.query(DBSession).filter(
        DBSession.session_uuid == session_uuid
    ).first()
    session_obj.close()
    
    if not chat_session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Сохранить сообщение пользователя
    db.add_message(chat_session.id, 'user', user_message)
    
    # Поиск в FAQ
    kb_results = db.search_knowledge(user_message, limit=1)
    
    if kb_results and len(kb_results) > 0:
        # Найден готовый ответ
        answer = kb_results[0].answer
        confidence = 'high'
    else:
        # Нужно обратиться к AI
        answer = "К сожалению, я не нашел точного ответа. Давайте свяжем вас с оператором."
        confidence = 'low'
    
    # Сохранить ответ
    db.add_message(chat_session.id, 'assistant', answer)
    
    return jsonify({
        'answer': answer,
        'confidence': confidence
    })
```

### Пример 3: Аналитика сессии

```python
def get_session_analytics(session_id):
    """Получить аналитику по сессии"""
    
    messages = db.get_session_messages(session_id)
    
    user_messages = [m for m in messages if m.role == 'user']
    assistant_messages = [m for m in messages if m.role == 'assistant']
    
    total_tokens = sum(m.tokens_used or 0 for m in messages)
    
    duration = None
    if len(messages) > 1:
        duration = (messages[-1].timestamp - messages[0].timestamp).total_seconds()
    
    return {
        'total_messages': len(messages),
        'user_messages_count': len(user_messages),
        'assistant_messages_count': len(assistant_messages),
        'total_tokens': total_tokens,
        'duration_seconds': duration,
        'first_message': messages[0].timestamp if messages else None,
        'last_message': messages[-1].timestamp if messages else None
    }

# Использование
analytics = get_session_analytics(session_id=1)
print(f"Всего сообщений: {analytics['total_messages']}")
print(f"Длительность: {analytics['duration_seconds']} сек")
print(f"Токенов использовано: {analytics['total_tokens']}")
```

### Пример 4: Экспорт истории чата

```python
def export_chat_history(session_id, format='text'):
    """Экспортировать историю чата"""
    
    messages = db.get_session_messages(session_id)
    
    if format == 'text':
        lines = []
        for msg in messages:
            timestamp = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            role_emoji = '👤' if msg.role == 'user' else '🤖'
            lines.append(f"[{timestamp}] {role_emoji} {msg.role}: {msg.content}")
        return '\n'.join(lines)
    
    elif format == 'json':
        import json
        data = [{
            'timestamp': msg.timestamp.isoformat(),
            'role': msg.role,
            'content': msg.content,
            'tokens_used': msg.tokens_used
        } for msg in messages]
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    elif format == 'html':
        html_lines = ['<div class="chat-history">']
        for msg in messages:
            css_class = 'user-message' if msg.role == 'user' else 'bot-message'
            html_lines.append(
                f'<div class="{css_class}">'
                f'<span class="timestamp">{msg.timestamp}</span>'
                f'<span class="content">{msg.content}</span>'
                f'</div>'
            )
        html_lines.append('</div>')
        return '\n'.join(html_lines)

# Использование
text_export = export_chat_history(1, 'text')
print(text_export)
```

### Пример 5: Миграция анонимного посетителя в пользователя

```python
def convert_visitor_to_user(visitor_id, username, email, phone=None):
    """Конвертировать анонимного посетителя в зарегистрированного пользователя"""
    
    # Создать пользователя
    user_id = db.create_user(username, email, phone)
    
    # Перенести все сессии посетителя к пользователю
    from db.db import Session as DBSession
    session_obj = db.get_session()
    
    sessions = session_obj.query(DBSession).filter(
        DBSession.visitor_id == visitor_id
    ).all()
    
    for chat_session in sessions:
        chat_session.user_id = user_id
        # Можно оставить visitor_id для истории или удалить
        # chat_session.visitor_id = None
    
    session_obj.commit()
    session_obj.close()
    
    return user_id

# Использование
user_id = convert_visitor_to_user(
    visitor_id=1,
    username="john_doe",
    email="john@example.com",
    phone="+79001234567"
)
print(f"Посетитель конвертирован в пользователя ID: {user_id}")
```

---

## Практические советы

### 1. Обработка ошибок

```python
try:
    user_id = db.create_user("john", "john@example.com")
except Exception as e:
    if "UNIQUE constraint failed" in str(e):
        print("Пользователь с таким email уже существует")
    else:
        print(f"Ошибка: {e}")
```

### 2. Транзакции

Все методы Database автоматически используют транзакции. При ошибке происходит rollback.

### 3. Производительность

```python
# ❌ Плохо - много отдельных запросов
for i in range(100):
    db.add_knowledge(f"Question {i}", f"Answer {i}")

# ✅ Хорошо - используйте batch операции
faq_list = [
    {'question': f"Question {i}", 'answer': f"Answer {i}"}
    for i in range(100)
]
for faq in faq_list:
    db.add_knowledge(**faq)
```

### 4. Закрытие соединений

Методы Database автоматически закрывают сессии в блоке `finally`.

---

## SQL запросы (продвинутое использование)

Если нужны кастомные запросы:

```python
from db.db import Visitor, Session as DBSession, Message

# Получить все активные сессии
session = db.get_session()
active_sessions = session.query(DBSession).filter(
    DBSession.is_active == True
).all()

# Статистика по категориям FAQ
from sqlalchemy import func
stats = session.query(
    KnowledgeBase.category,
    func.count(KnowledgeBase.id).label('count')
).group_by(KnowledgeBase.category).all()

for category, count in stats:
    print(f"{category}: {count} вопросов")

session.close()
```

---

## Дополнительные ресурсы

- [SQLAlchemy документация](https://docs.sqlalchemy.org/)
- [PostgreSQL документация](https://www.postgresql.org/docs/)
- [README_DOCKER.md](README_DOCKER.md) - Запуск через Docker

---

## Поддержка

Если возникли вопросы, создайте issue в репозитории проекта.
