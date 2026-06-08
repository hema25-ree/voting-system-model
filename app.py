from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS voters (
                    id INTEGER PRIMARY KEY,
                    aadhaar TEXT,
                    voted INTEGER DEFAULT 0
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY,
                    aadhaar TEXT,
                    candidate TEXT
                )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("login.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    aadhaar = request.form["aadhaar"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT * FROM voters WHERE aadhaar=?", (aadhaar,))
    user = c.fetchone()

    if not user:
        c.execute("INSERT INTO voters (aadhaar, voted) VALUES (?,0)", (aadhaar,))
        conn.commit()

    session["aadhaar"] = aadhaar
    return redirect("/vote")

# ---------------- VOTE PAGE ----------------
@app.route("/vote")
def vote():
    return render_template("vote.html")

# ---------------- CAST VOTE ----------------
@app.route("/cast_vote", methods=["POST"])
def cast_vote():
    candidate = request.form["candidate"]
    aadhaar = session["aadhaar"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # check if already voted
    c.execute("SELECT voted FROM voters WHERE aadhaar=?", (aadhaar,))
    result = c.fetchone()

    if result[0] == 1:
        return "❌ You already voted!"

    # store vote
    c.execute("INSERT INTO votes (aadhaar, candidate) VALUES (?,?)",
              (aadhaar, candidate))

    # mark voted
    c.execute("UPDATE voters SET voted=1 WHERE aadhaar=?", (aadhaar,))

    conn.commit()
    conn.close()

    return "✅ Vote Cast Successfully!"

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
