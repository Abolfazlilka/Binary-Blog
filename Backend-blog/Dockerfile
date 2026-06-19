FROM python:3.12-slim

WORKDIR /app

COPY modules.txt .

RUN pip install --no-cache-dir -r modules.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
