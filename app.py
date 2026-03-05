from flask import Flask,render_template_string,request,redirect,url_for,session
import sqlite3

app = Flask(__name__)
app.secret_key="musisi123"

def db():
    return sqlite3.connect("database.db")

def init_db():
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

init_db()

# REGISTER
@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        nama=request.form["nama"]
        username=request.form["username"]
        password=request.form["password"]
        alamat=request.form["alamat"]
        kategori=request.form["kategori"]
        status=request.form["status"]

        conn=db()
        c=conn.cursor()

        c.execute("INSERT INTO users(nama,username,password,alamat,kategori,status) VALUES(?,?,?,?,?,?)",
        (nama,username,password,alamat,kategori,status))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template_string(register_html)

# LOGIN
@app.route("/login",methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        conn=db()
        c=conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user=c.fetchone()

        conn.close()

        if user:
            session["user"]=username
            return redirect("/dashboard")

    return render_template_string(login_html)

# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM users")
    users=c.fetchall()

    conn.close()

    return render_template_string(dashboard_html,users=users)

# PROFIL
@app.route("/profil/<username>")
def profil(username):

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?",(username,))
    user=c.fetchone()

    conn.close()

    return render_template_string(profil_html,user=user)

# BOOKING
@app.route("/booking/<username>",methods=["GET","POST"])
def booking(username):

    if request.method=="POST":

        tanggal=request.form["tanggal"]
        metode=request.form["metode"]

        conn=db()
        c=conn.cursor()

        c.execute("INSERT INTO booking(pemesan,target,tanggal,metode) VALUES(?,?,?,?)",
        (session["user"],username,tanggal,metode))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template_string(booking_html,username=username)

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# HOME
@app.route("/")
def home():
    return redirect("/login")

# ================= HTML =================

register_html="""
<h2>Registrasi Musisi</h2>

<form method="post">

Nama<br>
<input name="nama"><br><br>

Username<br>
<input name="username"><br><br>

Password<br>
<input type="password" name="password"><br><br>

Alamat<br>
<input name="alamat"><br><br>

Kategori<br>
<select name="kategori">
<option>Player</option>
<option>Gitaris</option>
<option>Penyanyi</option>
<option>Kendang</option>
<option>Sound System</option>
<option>MC</option>
<option>Videografer</option>
<option>Decoration</option>
</select>

<br><br>

Status<br>
<input name="status"><br><br>

<button>Daftar</button>

</form>

<a href="/login">Login</a>
"""

login_html="""
<h2>Login Com Musisi</h2>

<form method="post">

Username<br>
<input name="username"><br><br>

Password<br>
<input type="password" name="password"><br><br>

<button>Login</button>

</form>

<a href="/register">Daftar akun</a>
"""

dashboard_html="""
<h2>Dashboard Musisi</h2>

<a href="/logout">Logout</a>

<hr>

{% for u in users %}

<div style="border:1px solid #ccc;padding:10px;margin:10px">

<b>{{u[1]}}</b><br>

Kategori : {{u[5]}}<br>

Alamat : {{u[4]}}<br>

Status : {{u[6]}}<br><br>

<a href="/profil/{{u[2]}}">Lihat Profil</a>

</div>

{% endfor %}
"""

profil_html="""
<h2>Profil Musisi</h2>

Nama : {{user[1]}}<br>
Kategori : {{user[5]}}<br>
Alamat : {{user[4]}}<br>
Status : {{user[6]}}<br><br>

<a href="/booking/{{user[2]}}">Booking Musisi</a>
"""

booking_html="""
<h2>Booking {{username}}</h2>

<form method="post">

Tanggal Acara<br>
<input type="date" name="tanggal"><br><br>

Metode<br>

<select name="metode">

<option>DP Transfer BRI</option>
<option>DP DANA</option>
<option>Non DP</option>

</select>

<br><br>

<button>Booking</button>

</form>
"""

if __name__=="__main__":
    app.run()
