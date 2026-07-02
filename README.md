# Binary Blog

A simple photo blog with a Flask API and static frontend served by nginx.

## Project layout

```
binary-blog/
├── frontend/          # Static HTML, CSS, JS, and UI assets
├── backend/           # Flask API, database, and upload storage
├── nginx.conf         # Reverse proxy and static file server config
└── docker-compose.yml
```

## Run with Docker

```bash
docker compose up -d --build
```

Open http://localhost/

## Run backend locally

```bash
cd backend
pip install -r modules.txt
python main.py
```

API docs: http://localhost:5000/apidocs/
