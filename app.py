from flask import Flask, request, redirect, session, render_template_string, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key="com_musisi_v4"

UPLOAD_FOLDER="uploads"
DATABASE="data.db"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================= DATABASE =================

def db():
    return sqlite3.connect(DATABASE)

def init_db():

    conn=db()
    c=conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    username TEXT UNIQUE,
    password TEXT,
    kota TEXT,
    kategori TEXT,
    foto TEXT
    )
    """)

    # BOOKING
    c.execute("""
    CREATE TABLE IF NOT EXISTS booking(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pemesan TEXT,
    target TEXT,
    tanggal TEXT,
    metode TEXT,
    konfirmasi INTEGER DEFAULT 0,
    acara TEXT,
    lokasi TEXT
    )
    """)

    # REVIEW
    c.execute("""
    CREATE TABLE IF NOT EXISTS review(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reviewer TEXT,
    target TEXT,
    rating INTEGER,
    komentar TEXT
    )
    """)

    # CHAT
    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pengirim TEXT,
    penerima TEXT,
    pesan TEXT
    )
    """)

    # NOTIFIKASI
    c.execute("""
    CREATE TABLE IF NOT EXISTS notif(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    pesan TEXT
    )
    """)

    # KALENDER
    c.execute("""
    CREATE TABLE IF NOT EXISTS kalender(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    tanggal TEXT,
    acara TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= HTML =================

html="""

<style>

body{
font-family:Arial;
background:#f0f2f5;
margin:0;
}

.header{
background:#1877f2;
color:white;
padding:15px;
font-size:22px;
}

.menu{
background:white;
padding:10px;
}

.container{
width:420px;
margin:auto;
margin-top:20px;
background:white;
padding:20px;
border-radius:10px;
}

.card{
background:white;
padding:10px;
margin:10px;
border-radius:10px;
box-shadow:0 0 5px rgba(0,0,0,0.1);
}

img{
border-radius:50%;
}

</style>

<div class="header">COM MUSISI PRO</div>

{% if session.get("user") %}

<div class="menu">

<a href="/dashboard">Dashboard</a> |
<a href="/profil-saya">Profil Saya</a> |
<a href="/booking-saya">Booking Saya</a> |
<a href="/booking-masuk">Booking Masuk</a> |
<a href="/chat">Chat</a> |
<a href="/notif">Notifikasi</a> |
<a href="/kalender">Kalender</a> |
<a href="/logout">Logout</a>

</div>

{% endif %}

{% if page=="login" %}

<div class="container">

<h3>Login</h3>

<form method="post">

<input name="username" placeholder="username"><br><br>
<input type="password" name="password" placeholder="password"><br><br>

<button>Login</button>

</form>

<a href="/register">Daftar</a>

</div>

{% endif %}

{% if page=="dashboard" %}

<div style="padding:10px">

<h3>Cari Musisi</h3>

<form>
<input name="search" placeholder="nama / kota">
<button>Cari</button>
</form>

{% for u in users %}

<div class="card">

{% if u[6] %}
<img src="/uploads/{{u[6]}}" width="50">
{% endif %}

<b>{{u[1]}}</b><br>
{{u[5]}} - {{u[4]}}<br>

<a href="/profil/{{u[2]}}">Profil</a>

</div>

{% endfor %}

</div>

{% endif %}

{% if page=="profil" %}

<div style="padding:15px">

<h2>{{user[1]}}</h2>

{% if user[6] %}
<img src="/uploads/{{user[6]}}" width="120">
{% endif %}

<br>

Kategori : {{user[5]}}<br>
Kota : {{user[4]}}<br><br>

{% if user[2]!=session["user"] %}

<a href="/booking/{{user[2]}}">Booking</a> |
<a href="/chat/{{user[2]}}">Chat</a>

{% endif %}

</div>

{% endif %}

{% if page=="chat" %}

<div class="container">

<h3>Chat dengan {{target}}</h3>

{% for m in msgs %}

<div class="card">

<b>{{m[1]}}</b><br>
{{m[3]}}

</div>

{% endfor %}

<form method="post">

<input name="pesan" placeholder="tulis pesan">
<button>Kirim</button>

</form>

</div>

{% endif %}

{% if page=="notif" %}

<div style="padding:10px">

<h3>Notifikasi</h3>

{% for n in notifs %}

<div class="card">
{{n[2]}}
</div>

{% endfor %}

</div>

{% endif %}

{% if page=="kalender" %}

<div style="padding:10px">

<h3>Kalender Job</h3>

{% for k in kal %}

<div class="card">

{{k[2]}} - {{k[3]}}

</div>

{% endfor %}

</div>

{% endif %}

"""

# ================= ROUTES =================

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
        (request.form["username"],request.form["password"]))

        u=c.fetchone()
        conn.close()

        if u:
            session["user"]=u[2]
            return redirect("/dashboard")

    return render_template_string(html,page="login")

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    search=request.args.get("search","")

    conn=db()
    c=conn.cursor()

    if search:
        c.execute("SELECT * FROM users WHERE nama LIKE ? OR kota LIKE ?",
        ('%'+search+'%','%'+search+'%'))
    else:
        c.execute("SELECT * FROM users")

    users=c.fetchall()
    conn.close()

    return render_template_string(html,page="dashboard",users=users)

@app.route("/profil/<username>")
def profil(username):

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?",(username,))
    user=c.fetchone()

    conn.close()

    return render_template_string(html,page="profil",user=user)

@app.route("/booking/<username>",methods=["GET","POST"])
def booking(username):

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO booking
        (pemesan,target,tanggal,metode,acara,lokasi)
        VALUES(?,?,?,?,?,?)
        """,(

        session["user"],
        username,
        request.form["tanggal"],
        request.form["metode"],
        request.form["acara"],
        request.form["lokasi"]

        ))

        c.execute("INSERT INTO notif(user,pesan) VALUES(?,?)",
        (username,"Ada booking baru dari "+session["user"]))

        conn.commit()
        conn.close()

        return redirect("/booking-saya")

    return """

    <form method=post>

    Tanggal<input type=date name=tanggal><br>
    Acara<input name=acara><br>
    Lokasi<input name=lokasi><br>

    Metode
    <select name=metode>
    <option>Transfer</option>
    <option>DANA</option>
    <option>Cash</option>
    </select>

    <button>Booking</button>

    </form>
    """

@app.route("/booking-saya")
def booking_saya():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM booking WHERE pemesan=?",(session["user"],))
    data=c.fetchall()

    conn.close()

    return str(data)

@app.route("/booking-masuk")
def booking_masuk():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM booking WHERE target=?",(session["user"],))
    data=c.fetchall()

    conn.close()

    return str(data)

@app.route("/chat/<username>",methods=["GET","POST"])
def chat(username):

    conn=db()
    c=conn.cursor()

    if request.method=="POST":

        c.execute("INSERT INTO messages(pengirim,penerima,pesan) VALUES(?,?,?)",
        (session["user"],username,request.form["pesan"]))

        conn.commit()

    c.execute("""
    SELECT * FROM messages
    WHERE (pengirim=? AND penerima=?)
    OR (pengirim=? AND penerima=?)
    """,(session["user"],username,username,session["user"]))

    msgs=c.fetchall()
    conn.close()

    return render_template_string(html,page="chat",msgs=msgs,target=username)

@app.route("/notif")
def notif():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM notif WHERE user=?",(session["user"],))
    n=c.fetchall()

    conn.close()

    return render_template_string(html,page="notif",notifs=n)

@app.route("/kalender")
def kalender():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM kalender WHERE user=?",(session["user"],))
    k=c.fetchall()

    conn.close()

    return render_template_string(html,page="kalender",kal=k)

@app.route("/uploads/<filename>")
def upload(filename):

    return send_from_directory(UPLOAD_FOLDER,filename)

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

if __name__=="__main__":

    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
