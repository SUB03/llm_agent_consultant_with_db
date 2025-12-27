# Руководство по работе с pgvector

## Что такое pgvector?

**pgvector** - расширение для PostgreSQL, позволяющее хранить векторные эмбеддинги и выполнять семантический поиск прямо в базе данных.

### Преимущества для веб-помощника:
- 🎯 **Семантический поиск** - находит похожие вопросы, даже если слова разные
- 🌍 **Многоязычность** - понимает синонимы и перефразирование
- ⚡ **Производительность** - поиск в миллионах векторов за миллисекунды
- 🔗 **Интеграция** - работает с вашей существующей PostgreSQL БД

---

## Установка

### Шаг 1: Установка PostgreSQL с pgvector

**Вариант А: Docker (рекомендуется для разработки)**
```bash
docker run -d \
  --name postgres-pgvector \
  -p 5434:5432 \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=agent_db \
  ankane/pgvector
```

**Вариант Б: Установка на Ubuntu**
```bash
# Установка PostgreSQL 16
sudo apt install postgresql-16 postgresql-16-pgvector

# Запуск
sudo systemctl start postgresql
```

### Шаг 2: Установка Python зависимостей

**Вариант А: С DeepSeek API (легкий, рекомендуется)**
```bash
# Только необходимые пакеты, без PyTorch
pip install pgvector sqlalchemy psycopg2-binary requests
```

**Вариант Б: С локальными моделями (тяжелый)**
```bash
# CPU-версия PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install pgvector sentence-transformers sqlalchemy psycopg2-binary
```

---

## Быстрый старт

### 1. Создание векторной БД с DeepSeek

```python
from db.deepseek_vector_db import DeepSeekVectorDatabase
import os

# Установите API ключ
os.environ['DEEPSEEK_API_KEY'] = 'your-api-key'

# Подключение к PostgreSQL
db = DeepSeekVectorDatabase('postgresql://postgres:password@localhost:5434/agent_db')

# Создание таблиц с поддержкой векторов
db.create_tables()
```

**Альтернатива: локальные модели**
```python
from db.vector_db import VectorDatabase

db = VectorDatabase('postgresql://postgres:password@localhost:5434/agent_db')
db.create_tables()
db.init_embedder('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
```

### 2. Добавление FAQ

```python
# Добавить один вопрос
db.add_knowledge(
    question="Как оформить заказ?",
    answer="Выберите товар, нажмите 'В корзину', оформите заказ",
    category="Заказы"
)

# Массовое добавление
faq_data = [
    {
        "question": "Какие способы оплаты?",
        "answer": "Карты, PayPal, наличные при получении",
        "category": "Оплата"
    },
    {
        "question": "Сколько времени доставка?",
        "answer": "1-2 дня по Москве, 3-7 дней по России",
        "category": "Доставка"
    }
]
db.bulk_add_knowledge(faq_data)
```

### 3. Семантический поиск

```python
# Поиск похожих вопросов
results = db.semantic_search("как купить товар?", limit=3)

for kb, similarity in results:
    print(f"Сходство: {similarity:.2%}")
    print(f"Q: {kb.question}")
    print(f"A: {kb.answer}\n")
```

**Пример вывода:**
```
Сходство: 87%
Q: Как оформить заказ?
A: Выберите товар, нажмите 'В корзину'...
```

---

## Интеграция с существующей БД

### Вариант 1: Гибридный подход (рекомендуется)

```python
# db/hybrid_db.py
from db.db import Database as RelationalDB
from db.vector_db import VectorDatabase

class HybridDatabase:
    """Объединяет реляционную и векторную БД"""
    
    def __init__(self, db_url):
        self.relational = RelationalDB(db_url)
        self.vector = VectorDatabase(db_url)
    
    def create_all_tables(self):
        self.relational.create_tables()
        self.vector.create_tables()
    
    def smart_search_knowledge(self, query, use_vector=True):
        """Умный поиск: сначала векторный, затем fallback на ключевые слова"""
        if use_vector:
            results = self.vector.semantic_search(query, limit=3, threshold=0.5)
            if results:
                return [kb for kb, score in results]
        
        # Fallback на обычный поиск
        return self.relational.search_knowledge(query)
```

### Вариант 2: Миграция существующих данных

```python
def migrate_to_vector():
    """Перенести существующую базу знаний в векторное хранилище"""
    rel_db = Database('postgresql://...')
    vec_db = VectorDatabase('postgresql://...')
    
    vec_db.init_embedder()
    
    # Получить все существующие FAQ
    session = rel_db.get_session()
    knowledge = session.query(KnowledgeBase).all()
    
    # Конвертировать в векторный формат
    items = [
        {
            'question': kb.question,
            'answer': kb.answer,
            'category': kb.category
        }
        for kb in knowledge
    ]
    
    vec_db.bulk_add_knowledge(items)
    session.close()
```

---

## Настройка производительности

### 1. Выбор источника эмбеддингов

| Вариант | Размер установки | Требования | Стоимость | Качество |
|---------|------------------|------------|-----------|----------|
| **DeepSeek API** | ~5 MB | API ключ | ~$0.0001/1K токенов | ⭐⭐⭐⭐ |
| OpenAI API | ~5 MB | API ключ | ~$0.0001/1K токенов | ⭐⭐⭐⭐⭐ |
| Локальные модели | ~500 MB-2 GB | CPU/GPU | Бесплатно | ⭐⭐⭐ |

**Рекомендация: DeepSeek API**
```python
# Легко, быстро, качественно
from db.deepseek_vector_db import DeepSeekVectorDatabase
db = DeepSeekVectorDatabase('postgresql://...')
```

**Локальные модели (если нужна офлайн работа)**
```python
# Требует установки PyTorch
db.init_embedder('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
```

### 2. Создание индексов

Для баз > 10,000 записей:

```python
# IVFFlat индекс - быстрый поиск
db.create_index()

# В SQL:
# CREATE INDEX ON knowledge_vectors 
# USING ivfflat (embedding vector_cosine_ops) 
# WITH (lists = 100);
```

### 3. Настройка порога сходства

```python
# Строгий поиск (только очень похожие)
results = db.semantic_search(query, threshold=0.8)

# Свободный поиск (больше результатов)
results = db.semantic_search(query, threshold=0.3)
```

---

## Использование с веб-API

### FastAPI пример

```python
from fastapi import FastAPI
from db.vector_db import VectorDatabase

app = FastAPI()
db = VectorDatabase('postgresql://...')
db.init_embedder()

@app.post("/chat")
async def chat(message: str, session_id: str):
    # Поиск в базе знаний
    results = db.semantic_search(message, limit=1, threshold=0.6)
    
    if results:
        kb, similarity = results[0]
        if similarity > 0.7:
            # Высокое сходство - возвращаем готовый ответ
            return {
                "answer": kb.answer,
                "source": "knowledge_base",
                "confidence": similarity
            }
    
    # Низкое сходство - передаем в LLM с контекстом
    context = [kb.answer for kb, _ in results[:3]]
    # ... вызов OpenAI/Anthropic с контекстом
    
    return {"answer": ai_response}
```

---

## Мониторинг и аналитика

### Отслеживание качества поиска

```python
def track_search_quality(query, selected_result_id):
    """Отслеживать какие результаты выбирают пользователи"""
    session = db.get_session()
    kb = session.query(KnowledgeVector).get(selected_result_id)
    if kb:
        kb.helpful_count += 1
        session.commit()
    session.close()
```

### Анализ популярных вопросов

```python
from sqlalchemy import func

session = db.get_session()
popular = session.query(
    KnowledgeVector.category,
    func.count(KnowledgeVector.id).label('count')
).group_by(KnowledgeVector.category).all()

for category, count in popular:
    print(f"{category}: {count} вопросов")
```

---

## Частые вопросы

**Q: Сколько нужно RAM для векторного поиска?**  
A: ~1-2 GB для 10K векторов (384 dim). Используйте индексы для больших баз.

**Q: Можно ли использовать SQLite вместо PostgreSQL?**  
A: Нет, pgvector работает только с PostgreSQL. Альтернатива: ChromaDB, FAISS.

**Q: Как часто пересоздавать эмбеддинги?**  
A: Только при изменении модели или самого текста вопроса/ответа.

**Q: Что делать, если поиск медленный?**  
A: Создайте индекс (IVFFlat/HNSW), уменьшите размерность модели.

---

## Примеры запросов для тестирования

```python
# Тестовые запросы (разная формулировка одного вопроса)
test_cases = [
    ("как купить?", "Как оформить заказ?"),
    ("сколько стоит доставка", "Время доставки"),
    ("можно вернуть товар", "Политика возврата"),
    ("способы оплаты", "Как оплатить заказ"),
]

for query, expected in test_cases:
    results = db.semantic_search(query, limit=1)
    if results:
        kb, score = results[0]
        print(f"✓ '{query}' → {score:.0%} → '{kb.question}'")
```

---

## Запуск примера

```bash
# 1. Запустить PostgreSQL с pgvector
docker run -d --name postgres-pgvector -p 5434:5432 \
  -e POSTGRES_PASSWORD=password ankane/pgvector

# 2. Установить зависимости
pip install pgvector sentence-transformers psycopg2-binary

# 3. Запустить пример
python db/vector_db.py
```

---

## Полезные ссылки

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [sentence-transformers](https://www.sbert.net/)
- [Модели на HuggingFace](https://huggingface.co/models?library=sentence-transformers)
