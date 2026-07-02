from datetime import datetime, timedelta
import uuid

from main import app, db, User, Post

SEED_IMAGE = "/images/image.png"

AUTHORS = [
    {
        "fullname": "Sarah Chen",
        "email": "sarah.chen@example.com",
        "password": "seedpass123",
        "image": SEED_IMAGE,
    },
    {
        "fullname": "Marcus Rivera",
        "email": "marcus.rivera@example.com",
        "password": "seedpass123",
        "image": SEED_IMAGE,
    },
]

POSTS = [
    {
        "title": "Getting Started with Flask REST APIs",
        "caption": (
            "Flask is a lightweight Python framework that makes it easy to spin up "
            "REST APIs without a lot of boilerplate. In this post, we walk through "
            "setting up routes, returning JSON responses, and connecting to a database "
            "with Flask-SQLAlchemy. By the end, you will have a working API ready for "
            "your frontend to consume."
        ),
        "author_email": "sarah.chen@example.com",
        "days_ago": 45,
    },
    {
        "title": "Why SQLite Is Perfect for Side Projects",
        "caption": (
            "When you are building a side project, you do not need a full database "
            "server on day one. SQLite stores everything in a single file, requires "
            "zero configuration, and works seamlessly with SQLAlchemy. It is fast "
            "enough for most prototypes and small apps, and you can always migrate "
            "to PostgreSQL later if your project takes off."
        ),
        "author_email": "sarah.chen@example.com",
        "days_ago": 30,
    },
    {
        "title": "Building a Photo Blog Without Overengineering",
        "caption": (
            "A photo blog does not need microservices, message queues, or a CDN on "
            "launch day. A simple Flask app that serves images from a local folder "
            "and stores metadata in SQLite is more than enough to get started. Focus "
            "on shipping something real, then optimize when you actually have users "
            "and performance data to guide your decisions."
        ),
        "author_email": "marcus.rivera@example.com",
        "days_ago": 21,
    },
    {
        "title": "Five Lessons from Shipping My First Backend",
        "caption": (
            "Shipping my first backend taught me more than any tutorial ever could. "
            "Keep your models simple, validate inputs early, and write endpoints "
            "that return consistent JSON shapes. Test your API with real HTTP "
            "requests before wiring up the frontend. Most importantly, done is better "
            "than perfect when you are learning."
        ),
        "author_email": "marcus.rivera@example.com",
        "days_ago": 14,
    },
    {
        "title": "How to Structure a Small Python Web App",
        "caption": (
            "For a small project, a single main.py file with models and routes is "
            "perfectly fine. As the app grows, split models into models.py, routes "
            "into blueprints, and configuration into a config module. The key is to "
            "refactor when pain appears, not before. Premature structure adds "
            "complexity without delivering value to your users."
        ),
        "author_email": "sarah.chen@example.com",
        "days_ago": 7,
    },
]


def seed():
    with app.app_context():
        db.create_all()

        if Post.query.filter_by(title=POSTS[0]["title"]).first():
            print("Seed data already present. Skipping.")
            return

        users_created = 0
        for author_data in AUTHORS:
            existing = User.query.filter_by(email=author_data["email"]).first()
            if existing:
                continue
            user = User(
                fullname=author_data["fullname"],
                email=author_data["email"],
                password=author_data["password"],
                token=str(uuid.uuid4()),
                image=author_data["image"],
            )
            db.session.add(user)
            users_created += 1

        db.session.flush()

        posts_created = 0
        for post_data in POSTS:
            author = User.query.filter_by(email=post_data["author_email"]).first()
            if not author:
                raise RuntimeError(f"Author not found: {post_data['author_email']}")

            post = Post(
                title=post_data["title"],
                caption=post_data["caption"],
                published_at=datetime.utcnow() - timedelta(days=post_data["days_ago"]),
                image=SEED_IMAGE,
                author_id=author.id,
            )
            db.session.add(post)
            posts_created += 1

        db.session.commit()
        print(f"Seeded {users_created} user(s) and {posts_created} post(s).")


if __name__ == "__main__":
    seed()
