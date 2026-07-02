from flask import Flask, send_from_directory, abort, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import uuid
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

IMAGE_FOLDER = os.path.join(os.getcwd(), "images")
os.makedirs(IMAGE_FOLDER, exist_ok=True)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(500))
    image = db.Column(db.String(500))
    posts = db.relationship("Post", back_populates="author", lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "image": self.image
        }

    def to_json_auth(self):
        return {
            "id": self.id,
            "fullname": self.fullname,
            "email": self.email,
            "token": self.token,
            "image": self.image
        }

    def __repr__(self):
        return f"User : {self.fullname}"

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400), nullable=False)
    caption = db.Column(db.String(2500), nullable=False)
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    image = db.Column(db.String(300), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", back_populates="posts")

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "caption": self.caption,
            "published_at": self.published_at,
            "image": self.image,
            "author_id": self.author_id,
        }

    def to_json_author(self):
        return {
            "id": self.id,
            "title": self.title,
            "caption": self.caption,
            "published_at": self.published_at,
            "image": self.image,
            "author_id": self.author_id,
            "author": self.author.fullname,
        }

@app.route("/images/<path:filename>", methods=["GET"])
def get_image(filename):
    file_path = os.path.join(IMAGE_FOLDER, filename)

    if not os.path.isfile(file_path):
        abort(404, description="Image not found")

    return send_from_directory(IMAGE_FOLDER, filename)

@app.route("/")
def hello_world():
    return "<p>Hello, World! uni</p>"

@app.route("/allusers", methods=["GET"])
def allusers():
    users = User.query.all()
    json_data = [user.to_json() for user in users]
    return jsonify(json_data)

@app.route("/allposts", methods=["GET"])
def allposts():
    posts = Post.query.all()
    json_data = [post.to_json_author() for post in posts]
    return jsonify(json_data)

@app.route("/post/<int:post_id>", methods=["GET"])
def getpost(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({
            "status": "error",
            "message": "post not found"
        }), 404
    return jsonify(post.to_json_author())

# register : fullname , email , password
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "invalid json body"
        }), 400

    fullname = data.get("fullname")
    email = data.get("email")
    password = data.get("password")

    if not fullname or not email or not password:
        return jsonify({
            "status": "error",
            "message": "fullname, email and password are required"
        }), 400

    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify({
            "status": "error",
            "message": "user with this email already exists"
        }), 409

    token = generate_random()
    user = User(
        fullname=fullname,
        email=email,
        password=password,
        token=token,
        image=None,
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "user registered successfully",
        "data": user.to_json_auth()
    }), 201

# login : email , password
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "invalid json body"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            "status": "error",
            "message": "user does not exist"
        }), 404

    if user.password != password:
        return jsonify({
            "status": "error",
            "message": "wrong password"
        }), 401

    user.token = generate_random()
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "login successful",
        "data": user.to_json_auth()
    }), 200

def generate_random():
    return str(uuid.uuid4())

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=False)
