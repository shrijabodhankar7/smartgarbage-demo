from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"

#  MYSQL CONNECTION 
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shrija@04",
        database="smart_garbage"
    )

# CREATE TABLES 
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            fullname VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            phone INT(10) UNIQUE,
            address TEXT,
            area VARCHAR(50),
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports(
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            description TEXT,
            image VARCHAR(255),
            latitude VARCHAR(50),
            longitude VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

init_db()

# ROUTES 

#  Registration Page
@app.route("/")
def register_page():
    return render_template("register.html")


#  Registration FORM SUBMIT
@app.route("/register", methods=["POST"])
def register_user():

    fullname = request.form.get("fullname")
    email = request.form.get("email")
    phone = request.form.get("phone")
    address = request.form.get("address")
    area = request.form.get("area")
    username = request.form.get("username")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    # VALIDATIONS 
    if password != confirm_password:
        return render_template("register.html", error="Passwords do not match!")

    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters!")

    if not any(char.isdigit() for char in password):
        return render_template("register.html", error="Password must contain 1 number!")

    if not any(not c.isalnum() for c in password):
        return render_template("register.html", error="Password must contain 1 special character!")

    conn = get_db_connection()
    cur = conn.cursor()

    # check duplicates
    cur.execute("SELECT * FROM users WHERE email=%s OR username=%s", (email, username))
    if cur.fetchone():
        conn.close()
        return render_template("register.html", error="User Already Exists!")

    #  INSERT USER
    cur.execute("""
        INSERT INTO users(fullname, email, phone, address, area, username, password)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (fullname, email, phone, address, area, username, password))

    conn.commit()
    user_id = cur.lastrowid
    cur.close()
    conn.close()

    session["user_id"] = user_id
    session["username"] = username

    #  Redirect to report page
    return redirect(url_for("report_garbage"))


#  Report Garbage PAGE
@app.route("/user")
def report_garbage():
    return render_template("reportgarbage.html")


#  My Reports Page
@app.route("/my-reports")
def my_reports():
    return render_template("Myreport.html")


#  Profile Page
@app.route("/profile")
def profile():
    return render_template("profile.html")

#  RUN 
if __name__ == "__main__":
    app.run(debug=True)
