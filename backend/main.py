from flask import Flask, send_from_directory, abort, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
from flask_cors import CORS
from datetime import datetime
import os
import uuid
app = Flask(__name__)
CORS(app)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "SQLALCHEMY_DATABASE_URI", "sqlite:///blog.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Swagger configuration
app.config["SWAGGER"] = {
    "title": "Blog API",
    "uiversion": 3,
    "openapi": "3.0.2"
}

swagger_template = {
    "openapi": "3.0.2",
    "info": {
        "title": "Blog API",
        "description": "API documentation for blog users, posts, authentication and image serving.",
        "version": "1.0.0"
    },
    "servers": [
        {
            "url": "/",
            "description": "Current server"
        }
    ],
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "fullname": {"type": "string", "example": "Ali Ahmadi"},
                    "email": {"type": "string", "example": "ali@example.com"},
                    "image": {"type": "string", "example": "/images/abc.jpg"}
                }
            },
            "UserAuth": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "fullname": {"type": "string", "example": "Ali Ahmadi"},
                    "email": {"type": "string", "example": "ali@example.com"},
                    "token": {"type": "string", "example": "550e8400-e29b-41d4-a716-446655440000"},
                    "image": {"type": "string", "example": "/images/abc.jpg"}
                }
            },
            "PostWithAuthor": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "example": 1},
                    "title": {"type": "string", "example": "My First Post"},
                    "caption": {"type": "string", "example": "This is the content of my first post."},
                    "published_at": {"type": "string", "format": "date-time", "example": "2025-01-01T12:00:00"},
                    "image": {"type": "string", "example": "/images/post1.jpg"},
                    "author_id": {"type": "integer", "example": 1},
                    "author": {"type": "string", "example": "Ali Ahmadi"}
                }
            },
            "LoginRequest": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "example": "ali@example.com"},
                    "password": {"type": "string", "example": "123456"}
                }
            },
            "RegisterRequest": {
                "type": "object",
                "required": ["fullname", "email", "password"],
                "properties": {
                    "fullname": {"type": "string", "example": "Ali Ahmadi"},
                    "email": {"type": "string", "example": "ali@example.com"},
                    "password": {"type": "string", "example": "123456"}
                }
            },
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "error"},
                    "message": {"type": "string", "example": "something went wrong"}
                }
            },
            "SuccessRegisterLogin": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "success"},
                    "message": {"type": "string", "example": "operation successful"},
                    "data": {
                        "$ref": "#/components/schemas/UserAuth"
                    }
                }
            }
        }
    }
}

swagger = Swagger(app, template=swagger_template)


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
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "image": self.image,
            "author_id": self.author_id,
        }

    def to_json_author(self):
        return {
            "id": self.id,
            "title": self.title,
            "caption": self.caption,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "image": self.image,
            "author_id": self.author_id,
            "author": self.author.fullname,
        }


def generate_random():
    return str(uuid.uuid4())


@app.route("/images/<path:filename>", methods=["GET"])
@swag_from({
    "tags": ["Images"],
    "summary": "Get image file",
    "description": "Returns an image file from the images directory.",
    "parameters": [
        {
            "name": "filename",
            "in": "path",
            "required": True,
            "schema": {"type": "string"},
            "description": "Image filename"
        }
    ],
    "responses": {
        "200": {
            "description": "Image file returned successfully"
        },
        "404": {
            "description": "Image not found",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ErrorResponse"
                    }
                }
            }
        }
    }
})
def get_image(filename):
    file_path = os.path.join(IMAGE_FOLDER, filename)

    if not os.path.isfile(file_path):
        abort(404, description="Image not found")

    return send_from_directory(IMAGE_FOLDER, filename)


@app.route("/", methods=["GET"])
@swag_from({
    "tags": ["General"],
    "summary": "Health check / welcome route",
    "responses": {
        "200": {
            "description": "Welcome message",
            "content": {
                "text/html": {
                    "schema": {
                        "type": "string",
                        "example": "<p>Hello, World! uni</p>"
                    }
                }
            }
        }
    }
})
def hello_world():
    return "<p>Hello, World! uni</p>"


@app.route("/allusers", methods=["GET"])
@swag_from({
    "tags": ["Users"],
    "summary": "Get all users",
    "responses": {
        "200": {
            "description": "List of all users",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/User"}
                    }
                }
            }
        }
    }
})
def allusers():
    users = User.query.all()
    json_data = [user.to_json() for user in users]
    return jsonify(json_data)


@app.route("/allposts", methods=["GET"])
@swag_from({
    "tags": ["Posts"],
    "summary": "Get all posts",
    "responses": {
        "200": {
            "description": "List of all posts with author name",
            "content": {
                "application/json": {
                    "schema": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/PostWithAuthor"}
                    }
                }
            }
        }
    }
})
def allposts():
    posts = Post.query.all()
    json_data = [post.to_json_author() for post in posts]
    return jsonify(json_data)


@app.route("/post/<int:post_id>", methods=["GET"])
@swag_from({
    "tags": ["Posts"],
    "summary": "Get a single post by ID",
    "parameters": [
        {
            "name": "post_id",
            "in": "path",
            "required": True,
            "schema": {"type": "integer"},
            "description": "Post ID"
        }
    ],
    "responses": {
        "200": {
            "description": "Post found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/PostWithAuthor"}
                }
            }
        },
        "404": {
            "description": "Post not found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
    }
})
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
@swag_from({
    "tags": ["Authentication"],
    "summary": "Register a new user",
    "description": "Register a new user with fullname, email and password.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/RegisterRequest"}
            }
        }
    },
    "responses": {
        "201": {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/SuccessRegisterLogin"}
                }
            }
        },
        "400": {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "409": {
            "description": "User already exists",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
    }
})
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
@swag_from({
    "tags": ["Authentication"],
    "summary": "Login user",
    "description": "Login with email and password and get a new token.",
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/LoginRequest"}
            }
        }
    },
    "responses": {
        "200": {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/SuccessRegisterLogin"}
                }
            }
        },
        "400": {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "401": {
            "description": "Wrong password",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        },
        "404": {
            "description": "User not found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                }
            }
        }
    }
})
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


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host=host, port=port, debug=debug)
