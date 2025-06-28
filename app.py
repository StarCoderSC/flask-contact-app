from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import init_db, save_message, get_messages, delete_message, get_message_by_id, update_message



app = Flask(__name__)
app.secret_key = "starcoder-secret" # Needed for flash messages



# Initialize db once
init_db()

@app.route("/")
def home():
    projects = [
        {"name": "Expression Evaluator",
        "desc": "Parses and evaluates math expressions"},
        {"name": "MinHeap Dijkstra", "desc": "Shortest path finder using custom heaps."},
        {"name": "Hospital Queue Sim",
        "desc": "Priority queue simulation using heapq."}
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
    if not session.get("logged_in"):
        flash("Unauthorized access!", "error")
        return redirect(url_for("login"))

    delete_message(message_id)
    flash("Message deleted successfully!", "success")

    return redirect(url_for("contact"))

@app.route("/edit/<int:message_id>", methods=["GET", "POST"])
def edit(message_id):
    if not session.get("logged_in"):
        flash("Unauthorized access!", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        new_name = request.form.get("name")
        new_msg = request.form.get("message")

        if not new_name or new_msg:
            flash("Please fill all the fields to update.", "error")
        else:
            update_message(message_id, new_name, new_msg)
            flash("Message updated successfully.", "Success")
            return redirect(url_for("contact"))
    
    message = get_message_by_id(message_id)
    if not message:
        flash("Message not found!", "error")
        return redirect(url_for("contact"))
    
    return render_template("edit.html", message_id=message_id, name=message[0], message=message[1])

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "starcoder/-+123!?"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            flash("Logged in successfully!", "success")
            return redirect(url_for("contact"))
        
        else:
            flash("Invalid credentials", "errors")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You have beeen logged out.", "success")
    return redirect(url_for("login"))


if __name__=="__main__":
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

