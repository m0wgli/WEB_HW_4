# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.10
FROM python:3.11.0

# Встановимо змінну середовища
ENV APP_HOME /app

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME


RUN apt-get update && apt-get install -y openssl

COPY pyproject.toml $APP_HOME/pyproject.toml
COPY poetry.lock $APP_HOME/poetry.lock
VOLUME /app/storage

# Встановимо залежності всередині контейнера
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry

# Скопіюємо інші файли в робочу директорію контейнера
COPY . $APP_HOME


# Позначимо порт, де працює застосунок всередині контейнера
EXPOSE 3000

# Запустимо наш застосунок всередині контейнера
CMD ["python", "main.py"]