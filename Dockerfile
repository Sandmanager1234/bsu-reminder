FROM python:3.13-alpine

# Устанавливаем системные зависимости
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    gcc \
    libc-dev \
    libffi-dev

# Создаём рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

# Копируем весь проект
COPY . /app

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONASYNCIODEBUG=1

# Команда по умолчанию (бот)
CMD ["python", "src/main.py"]
