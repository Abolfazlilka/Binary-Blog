FROM python:3.12-slim

WORKDIR /app

RUN mkdir -p instance images

COPY modules.txt .
RUN pip install --no-cache-dir -r modules.txt

COPY . .

ENV FLASK_HOST=0.0.0.0 \
    FLASK_DEBUG=false \
    SQLALCHEMY_DATABASE_URI=sqlite:////app/instance/blog.db

EXPOSE 5000

CMD ["python", "main.py"]
