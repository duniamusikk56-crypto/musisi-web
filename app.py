from flask import Flask,render_template,request,redirect,session,url_for
import sqlite3

app = Flask(__name__)
app.secret_key="musisi123"

def db():
    return sqlite3.connect("database.db")

def init():
    conn=db()
    c=conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    username TEXT,
    password TEXT,
    alamat TEXT,
    kategori TEXT,
    status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS booking(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pemesan TEXT,
    target TEXT,
    tanggal TEXT,
    metode TEXT
    )
    """)

    conn.commit()
    conn.close()

init()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO users(nama,username,password,alamat,kategori,status)
        VALUES(?,?,?,?,?,?)
        """,(
        request.form["nama"],
        request.form["username"],
        request.form["password"],
        request.form["alamat"],
        request.form["kategori"],
        request.form["status"]
        ))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
        (request.form["username"],request.form["password"]))

        user=c.fetchone()
        conn.close()

        if user:
            session["user"]=user[2]
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM users")
    users=c.fetchall()

    conn.close()

    return render_template("dashboard.html",users=users)

@app.route("/profil/<username>")
def profil(username):

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?",(username,))
    user=c.fetchone()

    conn.close()

    return render_template("profil.html",user=user)

@app.route("/booking/<username>",methods=["GET","POST"])
def booking(username):

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO booking(pemesan,target,tanggal,metode)
        VALUES(?,?,?,?)
        """,(
        session["user"],
        username,
        request.form["tanggal"],
        request.form["metode"]
        ))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("booking.html",username=username)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()
