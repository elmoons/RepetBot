FROM python:3.12.9

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir $(grep -v "sdamgia-api" requirements.txt)

# Установите sdamgia-api без зависимостей
RUN pip install --no-cache-dir --no-deps sdamgia-api==0.1.7

COPY . .

CMD alembic upgrade head; python src/main.py
