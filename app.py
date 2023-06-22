from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Add a secret key for session management


# Database initialization and sample data
conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS vaccination_centres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        working_hours TEXT
    )
    """
)

c.execute(
    """
    INSERT OR IGNORE INTO vaccination_centres (name, working_hours) VALUES
        ('Centre A', '9:00 AM - 5:00 PM'),
        ('Centre B', '8:00 AM - 4:00 PM'),
        ('Centre C', '10:00 AM - 6:00 PM')
    """
)

conn.commit()
conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Validate user credentials (implement your own logic here)
        if validate_user(username, password):
            session["username"] = username
            return redirect("/dashboard")
        else:
            error = "Invalid credentials. Please try again."
            return render_template("login.html", error=error)
    else:
        return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Perform data validations (implement your own logic here)
        if validate_signup(username, password):
            add_user(username, password)
            session["username"] = username
            return redirect("/dashboard")
        else:
            error = "Invalid data. Please try again."
            return render_template("signup.html", error=error)
    else:
        return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    if "username" in session:
        username = session["username"]
        return render_template("dashboard.html", username=username)
    else:
        return redirect("/login")


@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form["query"]
        
        # Search for vaccination centers matching the query
        centres = search_vaccination_centres(query)
        return render_template("search.html", query=query, centres=centres)
    else:
        return render_template("search.html", query="", centres=[])


@app.route("/apply/<int:centre_id>", methods=["GET", "POST"])
def apply(centre_id):
    if "username" in session:
        if request.method == "POST":
            # Apply for a vaccination slot (add your own implementation here)
            return redirect("/dashboard")
        else:
            centre = get_vaccination_centre(centre_id)
            return render_template("apply.html", centre=centre)
    else:
        return redirect("/login")


@app.route("/admin")
def admin():
    if "username" in session:
        if is_admin(session["username"]):
            centres = get_all_vaccination_centres()
            return render_template("admin.html", centres=centres)
    return redirect("/login")


@app.route("/admin/add", methods=["GET", "POST"])
def add_centre():
    if "username" in session:
        if is_admin(session["username"]):
            if request.method == "POST":
                name = request.form["name"]
                working_hours = request.form["working_hours"]
                add_vaccination_centre(name, working_hours)
                return redirect("/admin")
            else:
                return render_template("add_centre.html")
    return redirect("/login")


@app.route("/admin/remove/<int:centre_id>")
def remove_centre(centre_id):
    if "username" in session:
        if is_admin(session["username"]):
            remove_vaccination_centre(centre_id)
            return redirect("/admin")
    return redirect("/login")

@app.route('/get-all-centres')
def get_all_centres():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM vaccination_centres")
    centres = c.fetchall()
    return render_template('all_centres.html', centres=centres)


@app.route('/get-vaccination-details')
def get_vaccination_details():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM vaccination_centres")
    details = c.fetchall()
    conn.close()
    return render_template('vaccination_details.html', details=details)


# Helper functions for database operations
def validate_user(username, password):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None


def validate_signup(username, password):
    # Add your data validation logic here
    return True


def add_user(username, password):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()


def search_vaccination_centres(query):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM vaccination_centres WHERE name LIKE ?", ('%' + query + '%',))
    centres = c.fetchall()
    conn.close()
    return centres


def get_vaccination_centre(centre_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM vaccination_centres WHERE id=?", (centre_id,))
    centre = c.fetchone()
    conn.close()
    return centre


def get_all_vaccination_centres():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM vaccination_centres")
    centres = c.fetchall()
    conn.close()
    return centres


def is_admin(username):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user[0] == 1


def add_vaccination_centre(name, working_hours):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO vaccination_centres (name, working_hours) VALUES (?, ?)", (name, working_hours))
    conn.commit()
    conn.close()


def remove_vaccination_centre(centre_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("DELETE FROM vaccination_centres WHERE id=?", (centre_id,))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    app.run(debug=True)
