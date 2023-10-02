FROM python:3-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8800

CMD ["python", "run.py"] 