#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""
import os
import sys
import time

# Добавить путь к модулям
sys.path.insert(0, '/app')

from db.db import Database

def wait_for_db(db_url, max_retries=30):
    """Ждать готовности БД"""
    print("⏳ Ожидание подключения к БД...")
    
    for i in range(max_retries):
        try:
            db = Database(db_url)
            session = db.get_session()
            session.close()
            print("✓ БД доступна")
            return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"  Попытка {i+1}/{max_retries}...")
                time.sleep(2)
            else:
                print(f"❌ Не удалось подключиться: {e}")
                return False
    return False

def init_database(db_url):
    """Инициализация базы данных"""
    print(f"\n=== Инициализация БД ===")
    print(f"URL: {db_url}\n")
    
    db = Database(db_url)
    
    # Создать таблицы
    db.create_tables()
    print("✓ Таблицы созданы")
    
    # Настроить виджет
    db.update_widget_settings(
        'default',
        welcome_message="Здравствуйте! Чем могу помочь?",
        bot_name="Помощник",
        primary_color="#4CAF50"
    )
    print("✓ Виджет настроен")
    
    # Добавить FAQ
    faq = [
        ("Как оформить заказ?", "Добавьте товар в корзину и оформите заказ", "Заказы", "заказ"),
        ("Способы оплаты?", "Карты, PayPal, наличные", "Оплата", "оплата"),
        ("Сроки доставки?", "1-2 дня по Москве, 3-7 по России", "Доставка", "доставка"),
    ]
    
    for q, a, c, k in faq:
        db.add_knowledge(q, a, c, k)
    
    print(f"✓ Добавлено {len(faq)} FAQ")
    print("\n✅ Инициализация завершена!")

if __name__ == "__main__":
    db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@vector_db:5432/web_assistant')
    
    if not wait_for_db(db_url):
        sys.exit(1)
    
    try:
        init_database(db_url)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
