from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ---------- Database Connection ----------
def get_db():
    conn = sqlite3.connect('taskflash.db')
    conn.row_factory = sqlite3.Row
    return conn

# ---------- Setup Database on App Start ----------
def setup_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        duration INTEGER,
        urgency TEXT,
        dueDate TEXT,
        completed INTEGER DEFAULT 0
    )''')
    db.commit()

# ---------- Routes ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect("/login")
        except:
            return "Username already exists."
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            return redirect("/dashboard")
        else:
            return "Invalid credentials."
    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/add-task", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return "Unauthorized", 401
    data = request.get_json()
    db = get_db()
    db.execute("INSERT INTO tasks (user_id, name, duration, urgency, dueDate) VALUES (?, ?, ?, ?, ?)",
               (session["user_id"], data["name"], data["duration"], data["urgency"], data["dueDate"]))
    db.commit()
    return jsonify({"status": "ok"})

@app.route("/tasks")
def get_tasks():
    if "user_id" not in session:
        return jsonify([])
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks WHERE user_id = ?", (session["user_id"],)).fetchall()
    return jsonify([dict(task) for task in tasks])

@app.route("/complete-task/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET completed = 1 WHERE id = ? AND user_id = ?", (task_id, session["user_id"]))
    db.commit()
    return jsonify({"status": "completed"})

@app.route("/delete-task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session["user_id"]))
    db.commit()
    return jsonify({"status": "deleted"})

# ---------- Start App ----------
if __name__ == "__main__":
    with app.app_context():
        setup_db()
    app.run(debug=True)  
import os
def delete_db_if_corrupt():
    try:
        db = get_db()
        db.execute("SELECT 1")  # Just a simple query
    except sqlite3.DatabaseError:
        db.close()
        os.remove("taskflash.db")
        print("⚠️ Corrupted database found and deleted.")

# ---------- Start App ----------
if __name__ == "__main__":
    with app.app_context():
        delete_db_if_corrupt() 
        setup_db()             
    app.run(debug=True)
