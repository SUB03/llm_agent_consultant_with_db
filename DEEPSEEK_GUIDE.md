# DeepSeek для векторной базы данных

## Почему DeepSeek?

✅ **Не нужен PyTorch** - экономия ~2 GB дискового пространства  
✅ **Не нужен NVIDIA CUDA** - работает на любом сервере  
✅ **Высокое качество** - отличные эмбеддинги для русского языка  
✅ **Низкая стоимость** - ~$0.0001 за 1000 токенов  
✅ **Простая интеграция** - всего несколько строк кода  

---

## Быстрый старт

### 1. Получить API ключ

1. Зарегистрируйтесь на https://platform.deepseek.com/
2. Создайте API ключ
3. Сохраните ключ в безопасном месте

### 2. Установка зависимостей

```bash
# Только легкие пакеты, БЕЗ PyTorch
pip install pgvector sqlalchemy psycopg2-binary requests
```

**Размер установки: ~5 MB** (вместо ~2 GB с PyTorch)

### 3. Запуск PostgreSQL

```bash
docker run -d \
  --name postgres-pgvector \
  -p 5434:5432 \
  -e POSTGRES_PASSWORD=password \
  ankane/pgvector
```

### 4. Использование

```python
from db.deepseek_vector_db import DeepSeekVectorDatabase
import os

# Установить API ключ
os.environ['DEEPSEEK_API_KEY'] = 'sk-your-key-here'

# Создать БД
db = DeepSeekVectorDatabase('postgresql://postgres:password@localhost:5434/postgres')
db.create_tables()

# Добавить FAQ
db.add_knowledge(
    question="Как оформить заказ?",
    answer="Выберите товар, добавьте в корзину, оформите заказ",
    category="Заказы"
)

# Поиск
results = db.semantic_search("как купить товар?", limit=3)
for kb, similarity in results:
    print(f"{similarity:.0%}: {kb.answer}")
```

---

## Полный пример

```python
import os
from db.deepseek_vector_db import DeepSeekVectorDatabase

# API ключ (лучше через переменную окружения)
os.environ['DEEPSEEK_API_KEY'] = 'sk-your-key-here'

# Инициализация
db = DeepSeekVectorDatabase('postgresql://postgres:password@localhost:5434/postgres')
db.create_tables()

# Массовое добавление FAQ
faq_data = [
    {
        "question": "Как оформить заказ?",
        "answer": "Выберите товар, нажмите 'В корзину', оформите заказ",
        "category": "Заказы"
    },
    {
        "question": "Способы оплаты?",
        "answer": "Карты Visa/MasterCard, PayPal, наличные",
        "category": "Оплата"
    },
    {
        "question": "Сроки доставки?",
        "answer": "1-2 дня по Москве, 3-7 дней по России",
        "category": "Доставка"
    }
]

# Один API запрос для всех FAQ (эффективно!)
db.bulk_add_knowledge(faq_data)

# Тестирование поиска
test_queries = [
    "как мне купить?",           # найдет "оформить заказ"
    "сколько стоит доставка?",   # найдет "сроки доставки"
    "можно платить картой?",     # найдет "способы оплаты"
]

for query in test_queries:
    print(f"\n❓ {query}")
    results = db.semantic_search(query, limit=1, threshold=0.5)
    
    if results:
        kb, similarity = results[0]
        print(f"✓ {similarity:.0%} сходство")
        print(f"📝 {kb.answer}")
```

---

## Интеграция с веб-помощником

```python
from db.deepseek_vector_db import DeepSeekVectorDatabase
from db.db import Database as RelationalDB

class WebAssistant:
    def __init__(self):
        # Векторная БД для поиска
        self.vector_db = DeepSeekVectorDatabase('postgresql://...')
        
        # Реляционная БД для сессий/пользователей
        self.relational_db = RelationalDB('postgresql://...')
    
    def answer_question(self, session_id, question):
        """Ответить на вопрос пользователя"""
        
        # Сохранить вопрос
        self.relational_db.add_message(session_id, 'user', question)
        
        # Поиск в базе знаний
        results = self.vector_db.semantic_search(question, limit=1, threshold=0.7)
        
        if results and results[0][1] > 0.7:
            # Высокое сходство - вернуть готовый ответ
            answer = results[0][0].answer
            self.relational_db.add_message(session_id, 'assistant', answer)
            return answer
        
        # Низкое сходство - передать в DeepSeek Chat
        return self.ask_deepseek_chat(question, results)
```

---

## Стоимость

### DeepSeek Embeddings Pricing

- **$0.0001 за 1,000 токенов**
- Примерная длина FAQ: 50-100 токенов
- **1000 FAQ ≈ $0.01** (один цент!)

### Пример расчета для 10,000 пользователей в день:

```
10,000 запросов × 50 токенов = 500,000 токенов
500,000 / 1,000 × $0.0001 = $0.05/день = $1.50/месяц
```

**Вывод: Очень дешево!**

---

## Сравнение с альтернативами

| Вариант | Установка | Стоимость/месяц | Качество | Офлайн |
|---------|-----------|-----------------|----------|--------|
| **DeepSeek API** | 5 MB | $1-5 | ⭐⭐⭐⭐ | ❌ |
| OpenAI API | 5 MB | $3-10 | ⭐⭐⭐⭐⭐ | ❌ |
| Локальные модели | 2 GB | $0 | ⭐⭐⭐ | ✅ |

---

## Безопасность API ключа

### ❌ Плохо:
```python
db = DeepSeekVectorDatabase('...', api_key='sk-hardcoded-key')
```

### ✅ Хорошо:
```python
import os

# В .env файле
# DEEPSEEK_API_KEY=sk-your-key

from dotenv import load_dotenv
load_dotenv()

db = DeepSeekVectorDatabase('...')  # Автоматически возьмет из env
```

### Для продакшена:
```bash
# Docker
docker run -e DEEPSEEK_API_KEY='sk-xxx' ...

# Kubernetes
kubectl create secret generic deepseek-api-key --from-literal=key='sk-xxx'
```

---

## Тестирование

```bash
# 1. Установить зависимости
pip install pgvector sqlalchemy psycopg2-binary requests

# 2. Запустить PostgreSQL
docker run -d --name postgres-pgvector -p 5434:5432 \
  -e POSTGRES_PASSWORD=password ankane/pgvector

# 3. Установить API ключ
export DEEPSEEK_API_KEY='sk-your-key-here'

# 4. Запустить тест
python db/deepseek_vector_db.py
```

---

## FAQ

**Q: Нужен ли мне GPU?**  
A: Нет, DeepSeek API работает на их серверах.

**Q: Работает ли без интернета?**  
A: Нет, нужен интернет для API запросов. Для офлайн используйте локальные модели.

**Q: Сколько запросов в секунду?**  
A: DeepSeek поддерживает высокую нагрузку, но проверьте лимиты вашего тарифа.

**Q: Безопасно ли отправлять данные?**  
A: Да, DeepSeek использует шифрование. Но для конфиденциальных данных используйте локальные модели.

**Q: Как получить бесплатные кредиты?**  
A: При регистрации DeepSeek обычно дает пробные кредиты.

---

## Полезные ссылки

- [DeepSeek Platform](https://platform.deepseek.com/)
- [DeepSeek API Docs](https://platform.deepseek.com/api-docs/)
- [Pricing](https://platform.deepseek.com/pricing)

---

## Запуск полного примера

```bash
cd /home/brokender/edu/llm_agent_consultant_with_db

# Установить ключ
export DEEPSEEK_API_KEY='ваш-ключ'

# Запустить пример
python db/deepseek_vector_db.py
```

✅ **Готово! Векторная БД без тяжелых зависимостей.**
