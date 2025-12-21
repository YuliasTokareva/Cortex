FROM python:3.9-slim

# зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# экспонируем порт
EXPOSE 8000
#запуск
CMD ["gunicorn", "cortex.wsgi:application", "--bind", "0.0.0.0:8000"]