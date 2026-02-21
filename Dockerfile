FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY src /app/src
WORKDIR /app/src

EXPOSE 8000
CMD ["sh", "-c", "python wait_for_db.py && python manage.py migrate --noinput && python manage.py collectstatic --noinput && uvicorn memory_box.asgi:application --host 0.0.0.0 --port 8000"]
