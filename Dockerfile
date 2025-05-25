FROM python:3.12-slim

WORKDIR /app

COPY frontend/ /app
COPY frontend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
