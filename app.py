from flask import Flask, request, redirect, session, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = "com_musisi_pro"
socketio = SocketIO(app)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATABASE = "data.db"

# ================= DATABASE =================

def db():
    return sqlite3.connect(DATABASE)

def init_db():
    conn = db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT,
        username TEXT UNIQUE,
        password TEXT,
        alamat TEXT,
        kota TEXT,
        kategori TEXT,
        status TEXT,
        foto TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS booking(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pemesan TEXT,
        target TEXT,
        tanggal TEXT,
        metode TEXT,
        konfirmasi INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS review(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reviewer TEXT,
        target TEXT,
        rating INTEGER,
        komentar TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= HTML =================

html = """

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

.container{
width:420px;
margin:auto;
margin-top:20px;
background:white;
padding:20px;
border-radius:10px;
box-shadow:0 0 10px rgba(0,0,0,0.1);
}

input,select,textarea{
width:100%;
padding:10px;
margin:5px 0;
}

button{
width:100%;
padding:10px;
background:#1877f2;
color:white;
border:none;
margin-top:5px;
}

.card{
background:white;
padding:10px;
margin:10px;
border-radius:8px;
box-shadow:0 0 5px rgba(0,0,0,0.1);
}

.notif{
color:red;
font-weight:bold;
}

</style>

<div class="header">Com Musisi Ultimate</div>

{% if page=="login" %}

<div class="container">

<h3>Login</h3>

<form method="post">

<input name="username" placeholder="Username" required>

<input type="password" name="password" placeholder="Password" required>

<button>Login</button>

</form>

<a href="/register">Daftar</a>

</div>

{% endif %}


{% if page=="register" %}

<div class="container">

<h3>Register Musisi</h3>

<form method="post" enctype="multipart/form-data">

<input name="nama" placeholder="Nama">

<input name="username" placeholder="Username">

<input type="password" name="password" placeholder="Password">

<input name="alamat" placeholder="Alamat">

<input name="kota" placeholder="Kota">

<select name="kategori">

<option>Penyanyi</option>
<option>Gitaris</option>
<option>Player</option>
<option>MC</option>
<option>Kendang</option>
<option>Sound System</option>

</select>

<input name="status" placeholder="Status">

<input type="file" name="foto">

<button>Register</button>

</form>

</div>

{% endif %}


{% if page=="dashboard" %}

<div style="padding:15px">

<a href="/profil-saya">Profil Saya</a> |
<a href="/logout">Logout</a>

<h3>Musisi</h3>

<form method="get">

<input name="search" placeholder="Cari nama/kota">

<button>Cari</button>

</form>

{% for u in users %}

<div class="card">

<b>{{u[1]}}</b> - {{u[6]}} <br>

Kota : {{u[5]}} <br>

<a href="/profil/{{u[2]}}">Lihat Profil</a>

</div>

{% endfor %}

</div>

{% endif %}


{% if page=="profil" %}

<div style="padding:15px">

<h3>{{user[1]}}</h3>

Kategori : {{user[6]}} <br>
Kota : {{user[5]}} <br>
Status : {{user[7]}} <br>

{% if user[8] %}
<img src="/uploads/{{user[8]}}" width="120">
{% endif %}

{% if user[2]!=session["user"] %}

<a href="/booking/{{user[2]}}">Booking</a>

<br><br>

<h4>Rating</h4>

<form method="post" action="/review/{{user[2]}}">

<select name="rating">

<option>5</option>
<option>4</option>
<option>3</option>
<option>2</option>
<option>1</option>

</select>

<textarea name="komentar"></textarea>

<button>Kirim Review</button>

</form>

{% endif %}

{% for r in reviews %}

<div class="card">

⭐ {{r[3]}} <br>
{{r[4]}}

</div>

{% endfor %}

</div>

{% endif %}


{% if page=="profil_saya" %}

<div style="padding:15px">

<h3>Profil Saya</h3>

<b>{{user[1]}}</b> <br>

Kategori : {{user[6]}} <br>

{% if user[8] %}
<img src="/uploads/{{user[8]}}" width="120">
{% endif %}

<h4>Job Booking</h4>

{% for b in bookings %}

<div class="card">

Tanggal : {{b[3]}} <br>

Pemesan : {{b[1]}} <br>

{% if b[5]==0 %}

<span class="notif">Belum Konfirmasi</span>

<a href="/konfirmasi/{{b[0]}}">Konfirmasi</a>

{% else %}

Dikonfirmasi

{% endif %}

</div>

{% endfor %}

</div>

{% endif %}


{% if page=="booking" %}

<div class="container">

<h3>Booking {{target}}</h3>

<form method="post">

<input type="date" name="tanggal">

<select name="metode">

<option>Transfer BRI</option>
<option>DANA</option>
<option>Cash</option>

</select>

<button>Booking</button>

</form>

</div>

{% endif %}
"""

# ================= ROUTES =================

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?",(request.form["username"],))
        user=c.fetchone()

        conn.close()

        if user and check_password_hash(user[3],request.form["password"]):
            session["user"]=user[2]
            return redirect("/dashboard")

    return render_template_string(html,page="login")


@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        foto = request.files["foto"]
        filename = secure_filename(foto.filename)

        if filename:
            foto.save(os.path.join(UPLOAD_FOLDER,filename))

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO users
        (nama,username,password,alamat,kota,kategori,status,foto)
        VALUES(?,?,?,?,?,?,?,?)
        """,(
        request.form["nama"],
        request.form["username"],
        generate_password_hash(request.form["password"]),
        request.form["alamat"],
        request.form["kota"],
        request.form["kategori"],
        request.form["status"],
        filename
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template_string(html,page="register")


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    search=request.args.get("search","")

    conn=db()
    c=conn.cursor()

    if search:
        c.execute("SELECT * FROM users WHERE nama LIKE ? OR kota LIKE ?",('%'+search+'%','%'+search+'%'))
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

    c.execute("SELECT * FROM review WHERE target=?",(username,))
    reviews=c.fetchall()

    conn.close()

    return render_template_string(html,page="profil",user=user,reviews=reviews)


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

    return render_template_string(html,page="booking",target=username)


@app.route("/review/<username>",methods=["POST"])
def review(username):

    conn=db()
    c=conn.cursor()

    c.execute("""
    INSERT INTO review(reviewer,target,rating,komentar)
    VALUES(?,?,?,?)
    """,(
    session["user"],
    username,
    request.form["rating"],
    request.form["komentar"]
    ))

    conn.commit()
    conn.close()

    return redirect("/profil/"+username)


@app.route("/profil-saya")
def profil_saya():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?",(session["user"],))
    user=c.fetchone()

    c.execute("SELECT * FROM booking WHERE target=?",(session["user"],))
    bookings=c.fetchall()

    conn.close()

    return render_template_string(html,page="profil_saya",user=user,bookings=bookings)


@app.route("/konfirmasi/<int:id>")
def konfirmasi(id):

    conn=db()
    c=conn.cursor()

    c.execute("UPDATE booking SET konfirmasi=1 WHERE id=?",(id,))

    conn.commit()
    conn.close()

    return redirect("/profil-saya")


@app.route("/uploads/<filename>")
def upload(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= CHAT =================

@socketio.on("join")
def join(data):

    room=data["room"]

    join_room(room)


@socketio.on("send")
def send(data):

    emit("message",data,room=data["room"])


# ================= RUN =================

if __name__=="__main__":

    port=int(os.environ.get("PORT",8080))

    socketio.run(app,host="0.0.0.0",port=port)
