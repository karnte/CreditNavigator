
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
