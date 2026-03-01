# from flask import Flask, render_template, request, redirect, url_for, flash
# import sqlite3

# app = Flask(__name__)
# app.secret_key = "secretkey"

# # Database connection
# def get_db_connection():
#     conn = sqlite3.connect("database.db")
#     conn.row_factory = sqlite3.Row
#     return conn

# # Create table
# with get_db_connection() as conn:
#     conn.execute("""
#         CREATE TABLE IF NOT EXISTS students (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             roll_no TEXT UNIQUE,
#             name TEXT,
#             marks INTEGER,
#             grade TEXT
#         )
#     """)

# # Home
# @app.route("/")
# def home():
#     return render_template("home.html")

# # Add student
# @app.route("/add", methods=["GET", "POST"])
# def add_student():
#     if request.method == "POST":
#         roll_no = request.form["roll_no"]
#         name = request.form["name"]
#         marks = int(request.form["marks"])

#         if marks >= 90:
#             grade = "A"
#         elif marks >= 75:
#             grade = "B"
#         elif marks >= 50:
#             grade = "C"
#         else:
#             grade = "F"

#         try:
#             conn = get_db_connection()
#             conn.execute(
#                 "INSERT INTO students (roll_no, name, marks, grade) VALUES (?, ?, ?, ?)",
#                 (roll_no, name, marks, grade)
#             )
#             conn.commit()
#             conn.close()
#             flash("Student added successfully!")
#         except:
#             flash("Roll Number already exists!")

#         return redirect(url_for("add_student"))

#     return render_template("add_student.html")

# # View all students
# @app.route("/students")
# def view_students():
#     conn = get_db_connection()
#     students = conn.execute("SELECT * FROM students").fetchall()
#     conn.close()
#     return render_template("view_students.html", students=students)

# # Search student
# @app.route("/search", methods=["GET", "POST"])
# def search_student():
#     if request.method == "POST":
#         roll_no = request.form["roll_no"]
#         conn = get_db_connection()
#         student = conn.execute(
#             "SELECT * FROM students WHERE roll_no = ?", (roll_no,)
#         ).fetchone()
#         conn.close()
#         return render_template("result.html", student=student)
#     return render_template("search.html")

# # Update student
# @app.route("/update/<int:id>", methods=["GET", "POST"])
# def update_student(id):
#     conn = get_db_connection()
#     student = conn.execute("SELECT * FROM students WHERE id = ?", (id,)).fetchone()

#     if request.method == "POST":
#         name = request.form["name"]
#         marks = int(request.form["marks"])

#         if marks >= 90:
#             grade = "A"
#         elif marks >= 75:
#             grade = "B"
#         elif marks >= 50:
#             grade = "C"
#         else:
#             grade = "F"

#         conn.execute(
#             "UPDATE students SET name=?, marks=?, grade=? WHERE id=?",
#             (name, marks, grade, id)
#         )
#         conn.commit()
#         conn.close()
#         return redirect(url_for("view_students"))

#     conn.close()
#     return render_template("update_student.html", student=student)

# # Delete student
# @app.route("/delete/<int:id>")
# def delete_student(id):
#     conn = get_db_connection()
#     conn.execute("DELETE FROM students WHERE id = ?", (id,))
#     conn.commit()
#     conn.close()
#     return redirect(url_for("view_students"))

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- DATABASE ----------------
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
with get_db_connection() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE,
            name TEXT,
            marks INTEGER,
            grade TEXT
        )
    """)

# ---------------- CHECK ADMIN EXISTS ----------------
def admin_exists():
    conn = get_db_connection()
    admin = conn.execute("SELECT * FROM admin").fetchone()
    conn.close()
    return admin is not None

# ---------------- AUTH CHECK ----------------
def login_required():
    return session.get("admin_logged_in")

# ---------------- ROOT ----------------
@app.route("/")
def index():
    if admin_exists():
        return redirect(url_for("login"))
    else:
        return redirect(url_for("signup"))

# ---------------- SIGN UP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if admin_exists():
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO admin (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
            conn.close()
            session["admin_logged_in"] = True
            return redirect(url_for("home"))
        except:
            flash("Username already exists")

    return render_template("signup.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if not admin_exists():
        return redirect(url_for("signup"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session["admin_logged_in"] = True
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- HOME ----------------
@app.route("/home")
def home():
    if not login_required():
        return redirect(url_for("login"))
    return render_template("home.html")

# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["GET", "POST"])
def add_student():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        name = request.form["name"]
        marks = int(request.form["marks"])

        if marks >= 90:
            grade = "A"
        elif marks >= 75:
            grade = "B"
        elif marks >= 50:
            grade = "C"
        else:
            grade = "F"

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO students (roll_no, name, marks, grade) VALUES (?, ?, ?, ?)",
                (roll_no, name, marks, grade)
            )
            conn.commit()
            conn.close()
            flash("Student added successfully")
        except:
            flash("Roll Number already exists")

    return render_template("add_student.html")

# ---------------- VIEW STUDENTS ----------------
@app.route("/students")
def view_students():
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()
    return render_template("view_students.html", students=students)

# ---------------- SEARCH ----------------
@app.route("/search", methods=["GET", "POST"])
def search_student():
    if not login_required():
        return redirect(url_for("login"))

    if request.method == "POST":
        roll_no = request.form["roll_no"]
        conn = get_db_connection()
        student = conn.execute(
            "SELECT * FROM students WHERE roll_no=?",
            (roll_no,)
        ).fetchone()
        conn.close()
        return render_template("result.html", student=student)

    return render_template("search.html")

# ---------------- UPDATE ----------------
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_student(id):
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()

    if request.method == "POST":
        name = request.form["name"]
        marks = int(request.form["marks"])

        if marks >= 90:
            grade = "A"
        elif marks >= 75:
            grade = "B"
        elif marks >= 50:
            grade = "C"
        else:
            grade = "F"

        conn.execute(
            "UPDATE students SET name=?, marks=?, grade=? WHERE id=?",
            (name, marks, grade, id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("view_students"))

    conn.close()
    return render_template("update_student.html", student=student)

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete_student(id):
    if not login_required():
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("view_students"))
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)