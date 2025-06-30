from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import init_db, save_message, get_messages, delete_message, get_message_by_id, update_message, create_post_table, init_all
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = "starcoder-supersecretkey123" # Needed for flash messages

# Models
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Post {self.title}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    
# Only run once to create admin user
def create_admin_user():
    if not User.query.filter_by(username="admin").first():
        hashed_pw = generate_password_hash("admin123")
        admin = User(username="admin", password=hashed_pw)
        db.session.add(admin)
        db.session.commit()

@app.route("/")
def home():
    projects = [
        {"name": "Expression Evaluator",
        "desc": "Parses and evaluates math expressions"},
        {"name": "MinHeap Dijkstra", "desc": "Shortest path finder using custom heaps."},
        {"name": "Hospital Queue Sim",
        "desc": "Priority queue simulation using heapq."},
        {"name": "'Flatten-utils' Python module",
        "desc": "🔧 A lightweight utility to deeply flatten nested Python structure like 'lists', 'tuples', 'sets','dicts' and more -- without breaking a sweat."}
    ]

    return render_template("index.html", projects=projects)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")

        if not name or not message:
            flash("Please fill out all fields!", "error")
        
        else:
            save_message(name, message)
            flash("Message saved successfully!", "success")

            return redirect(url_for('contact'))

    saved_messages = get_messages()
    return render_template("contact.html", saved_messages=saved_messages)

@app.route("/delete/<int:message_id>", methods=["POST"])
def delete(message_id):
    if "user" not in session:
        flash("Unauthorized access!", "error")
        return redirect(url_for("login"))

    delete_message(message_id)
    flash("Message deleted successfully!", "success")

    return redirect(url_for("contact"))

@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit(message_id):
    if "user" not in session:
        flash("Unauthorized access!", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_name = request.form.get("name")
        new_msg = request.form.get("message")

        if not new_name or not new_msg:
            flash("Please fill all the fields to update.", "error")
        else:
            update_message(message_id, new_name, new_msg)
            flash("Message updated successfully.", "success")
            return redirect(url_for("contact"))
    
    message = get_message_by_id(message_id)
    if not message:
        flash("Message not found!", "error")
        return redirect(url_for("contact"))
    
    return render_template("edit.html", message_id=message_id, name=message[0], message=message[1])


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("blog"))
        else:
            flash("Invalid username or password", "error")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("blog"))

@app.route("/blog")
def blog():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("blog.html", posts=[(p.id, p.title, p.content) for p in posts])

@app.route("/blog/new", methods=["GET", "POST"])
def new_post():
    if "user" not in session:
        flash("Please login to add a post", "error")

        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title or not content:
            flash("Both title and content are required", "error")
            return redirect(url_for("new_post"))
        
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        
        flash("Post added successfully!", "success")
        return redirect(url_for("blog"))

    return render_template("new_post.html")


@app.route("/blog/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    if "user" not in session:
        flash("Please login to add a post.", "error")
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("blog"))
    
    return render_template("edit_post.html", post=(post.title, post.content), post_id=post_id)

@app.route("/blog/delete/<int:post_id>")
def delete_post(post_id):
    if "user" not in session:
        flash("Please login to add a post.", "error")
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!", "success")
    return redirect(url_for("blog"))

# Set up db on first run
if __name__=="__main__":
    with app.app_context():
        db.create_all()
        create_admin_user()
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

