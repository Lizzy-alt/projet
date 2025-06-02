from flask import Flask, render_template, g, request, redirect
import sqlite3
import os
from flask import session

app = Flask(__name__)
app.secret_key = "Lizon"
def get_db():
    if "db" not in g:
        if os.path.isfile("movies.db"):
            g.db = sqlite3.connect("movies.db")
        else:
            g.db = sqlite3.connect("movies.db")
            cur = g.db.cursor()
            cur.execute("CREATE TABBLE movie(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL UNIQUE, year INTEGER NOT NULL)")
            g.db.commit()
            cur.execute("INSERT INTO movies (title, year) VALUES ('Film', '1')")
            g.db.commit()
            cur.execute("INSERT INTO movies (title, year) VALUES ('Film 2', '2')")
            g.db.commit()
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/")
def movies():
    conn = get_db()
    cur = conn.cursor()
    movies = cur.execute("SELECT * FROM movies").fetchall()  
    return render_template("index.html", movies=movies)  

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method =="POST":
        username=request.form["username"]
        password=request.form["password"]
        session["username"] = username
        return redirect("/")
    
    if request.method=="GET":
        return render_template("login.html")

@app.route("/")
def index():
    if "username" in session:
        return render_template("index.html", username=session["username"])
    else:
        return redirect("/login")
    
@app.route("/logout", methods=["GET"])
def logout():
    session.pop("username", None)
    return redirect("/login")

@app.route("/add",methods=["GET","POST"])
def add():
    if request.method =="GET":
        return render_template("add.html")
    if request.method == "POST":
        title = request.form["title"]
        year = request.form["year"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO movies(title, year) VALUES (?, ?)", (title, year))
        conn.commit()
        return redirect("/")
    
    
if __name__ == "__main__":
    app.run(debug=True)
    