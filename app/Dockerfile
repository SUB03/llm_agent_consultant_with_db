FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
# PyTorch CPU версия напрямую (без дополнительного индекса для совместимости)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu || \
    pip install --no-cache-dir torch torchvision torchaudio
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Команда по умолчанию
CMD ["python3", "create_db.py"]
