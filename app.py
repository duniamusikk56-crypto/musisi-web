from flask import Flask, request, redirect, session, render_template_string, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key="com_musisi_v3"

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

.container{
width:420px;
margin:auto;
margin-top:20px;
background:white;
padding:20px;
border-radius:10px;
}

.card{
display:flex;
gap:10px;
align-items:center;
background:white;
padding:10px;
margin:10px;
border-radius:10px;
box-shadow:0 0 5px rgba(0,0,0,0.1);
}

.card img{
border-radius:50%;
}

button{
padding:8px;
background:#1877f2;
color:white;
border:none;
border-radius:5px;
}

.status0{color:red;font-weight:bold}
.status1{color:green;font-weight:bold}

.menu{
padding:10px;
background:white;
}

</style>

<div class="header">COM MUSISI PRO</div>

{% if session.get("user") %}
<div class="menu">

<a href="/dashboard">Dashboard</a> |
<a href="/profil-saya">Profil Saya</a> |
<a href="/booking-saya">Booking Saya</a> |
<a href="/booking-masuk">Booking Masuk</a> |
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


{% if page=="register" %}

<div class="container">

<h3>Register</h3>

<form method="post" enctype="multipart/form-data">

<input name="nama" placeholder="nama"><br><br>
<input name="username" placeholder="username"><br><br>
<input type="password" name="password" placeholder="password"><br><br>
<input name="kota" placeholder="kota"><br><br>

<select name="kategori">

<option>Penyanyi</option>
<option>Gitaris</option>
<option>Kendang</option>
<option>MC</option>
<option>Player</option>

</select><br><br>

<input type="file" name="foto"><br><br>

<button>Register</button>

</form>

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

<div>

<b>{{u[1]}}</b><br>

{{u[5]}} - {{u[4]}}<br>

<a href="/profil/{{u[2]}}">Lihat Profil</a>

</div>

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

<a href="/booking/{{user[2]}}"><button>Booking</button></a>

{% endif %}

<h3>Rating</h3>

{% for r in reviews %}

<div class="card">

⭐ {{r[3]}}<br>

{{r[4]}}

</div>

{% endfor %}

</div>

{% endif %}



{% if page=="booking" %}

<div class="container">

<h3>Booking {{target}}</h3>

<form method="post">

Tanggal
<input type="date" name="tanggal"><br><br>

Acara
<input name="acara" placeholder="Wedding / Hajatan"><br><br>

Pilih Lokasi

<select name="tipe_lokasi">

<option value="maps">Share Google Maps</option>
<option value="alamat">Alamat Manual</option>

</select><br><br>

Link Maps
<input name="lokasi_maps"><br><br>

Alamat Manual
<textarea name="lokasi_alamat"></textarea><br><br>

Metode

<select name="metode">

<option>Transfer</option>
<option>DANA</option>
<option>Cash</option>

</select><br><br>

<button>Booking</button>

</form>

</div>

{% endif %}



{% if page=="booking_saya" %}

<div style="padding:15px">

<h3>Booking Saya</h3>

{% for b in bookings %}

<div class="card">

<div>

Musisi : {{b[2]}}<br>
Tanggal : {{b[3]}}<br>
Acara : {{b[6]}}<br>

{% if b[5]==0 %}
<span class="status0">Menunggu Konfirmasi</span>
{% else %}
<span class="status1">Dikonfirmasi</span>
{% endif %}

</div>

</div>

{% endfor %}

</div>

{% endif %}



{% if page=="booking_masuk" %}

<div style="padding:15px">

<h3>Booking Masuk</h3>

{% for b in bookings %}

<div class="card">

<div>

Pemesan : {{b[1]}}<br>
Tanggal : {{b[3]}}<br>
Acara : {{b[6]}}<br>

{% if b[5]==0 %}

<span class="status0">Belum Konfirmasi</span>

<a href="/konfirmasi/{{b[0]}}"><button>Konfirmasi</button></a>

{% else %}

<span class="status1">Dikonfirmasi</span>

{% endif %}

</div>

</div>

{% endfor %}

</div>

{% endif %}



{% if page=="profil_saya" %}

<div style="padding:15px">

<h3>Profil Saya</h3>

<b>{{user[1]}}</b><br>

{{user[5]}} - {{user[4]}}

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

        user=c.fetchone()
        conn.close()

        if user:

            session["user"]=user[2]
            return redirect("/dashboard")

    return render_template_string(html,page="login")


@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        foto=request.files["foto"]
        filename=secure_filename(foto.filename)

        if filename:
            foto.save(os.path.join(UPLOAD_FOLDER,filename))

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO users
        (nama,username,password,kota,kategori,foto)
        VALUES(?,?,?,?,?,?)
        """,(

        request.form["nama"],
        request.form["username"],
        request.form["password"],
        request.form["kota"],
        request.form["kategori"],
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

    c.execute("SELECT * FROM review WHERE target=?",(username,))
    reviews=c.fetchall()

    conn.close()

    return render_template_string(html,page="profil",user=user,reviews=reviews)


@app.route("/booking/<username>",methods=["GET","POST"])
def booking(username):

    if request.method=="POST":

        tipe=request.form["tipe_lokasi"]

        if tipe=="maps":
            lokasi=request.form["lokasi_maps"]
        else:
            lokasi=request.form["lokasi_alamat"]

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
        lokasi

        ))

        conn.commit()
        conn.close()

        return redirect("/booking-saya")

    return render_template_string(html,page="booking",target=username)


@app.route("/booking-saya")
def booking_saya():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM booking WHERE pemesan=?",(session["user"],))
    bookings=c.fetchall()

    conn.close()

    return render_template_string(html,page="booking_saya",bookings=bookings)


@app.route("/booking-masuk")
def booking_masuk():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM booking WHERE target=?",(session["user"],))
    bookings=c.fetchall()

    conn.close()

    return render_template_string(html,page="booking_masuk",bookings=bookings)


@app.route("/konfirmasi/<int:id>")
def konfirmasi(id):

    conn=db()
    c=conn.cursor()

    c.execute("UPDATE booking SET konfirmasi=1 WHERE id=?",(id,))
    conn.commit()
    conn.close()

    return redirect("/booking-masuk")


@app.route("/profil-saya")
def profil_saya():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?",(session["user"],))
    user=c.fetchone()

    conn.close()

    return render_template_string(html,page="profil_saya",user=user)


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
