from flask import Flask, request, redirect, session, render_template_string, send_from_directory
import sqlite3, os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key="com_musisi_pro"

UPLOAD_FOLDER="uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DATABASE="data.db"

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

    c.execute("""
    CREATE TABLE IF NOT EXISTS chat(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pengirim TEXT,
    penerima TEXT,
    pesan TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= HTML =================

html="""

<style>

body{font-family:Arial;background:#f0f2f5;margin:0;}

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
background:white;
padding:15px;
margin:10px;
border-radius:10px;
box-shadow:0 0 5px rgba(0,0,0,0.1);
}

button{
padding:8px;
background:#1877f2;
color:white;
border:none;
}

</style>

<div class="header">Com Musisi PRO</div>

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
<option>Bass</option>
<option>Drum</option>
<option>Kendang</option>
<option>Keyboard</option>
<option>MC</option>
<option>Sound System</option>
<option>Dekorasi</option>
<option>Videografer</option>

</select><br><br>

<input type="file" name="foto"><br><br>

<button>Register</button>

</form>

</div>

{% endif %}

{% if page=="dashboard" %}

<div style="padding:10px">

<a href="/profil-saya">Profil Saya</a> |
<a href="/logout">Logout</a>

<h3>Cari Musisi</h3>

<form method="get">

<input name="search" placeholder="nama / kota">

<button>Cari</button>

</form>

{% for u in users %}

<div class="card">

<b>{{u[1]}}</b><br>

Kategori : {{u[5]}}<br>

Kota : {{u[4]}}<br>

<a href="/profil/{{u[2]}}">Profil</a> |
<a href="/chat/{{u[2]}}">Chat</a>

</div>

{% endfor %}

</div>

{% endif %}

{% if page=="profil" %}

<div style="padding:15px">

<h3>{{user[1]}}</h3>

Kategori : {{user[5]}}<br>
Kota : {{user[4]}}<br>

{% if user[6] %}
<img src="/uploads/{{user[6]}}" width="120"><br>
{% endif %}

{% if user[2]!=session["user"] %}

<a href="/booking/{{user[2]}}">Booking</a>

<h3>Rating</h3>

<form method="post" action="/review/{{user[2]}}">

<select name="rating">
<option>5</option>
<option>4</option>
<option>3</option>
<option>2</option>
<option>1</option>
</select>

<textarea name="komentar"></textarea><br>

<button>Kirim</button>

</form>

{% endif %}

{% for r in reviews %}

<div class="card">

⭐ {{r[3]}}<br>

{{r[4]}}

</div>

{% endfor %}

</div>

{% endif %}

{% if page=="chat" %}

<div style="padding:15px">

<h3>Chat dengan {{target}}</h3>

<div style="height:250px;overflow:auto;border:1px solid #ddd;padding:10px">

{% for c in chats %}

<b>{{c[1]}}</b> : {{c[3]}}<br>

{% endfor %}

</div>

<form method="post">

<input name="pesan" style="width:70%">

<button>Kirim</button>

</form>

</div>

{% endif %}

{% if page=="booking" %}

<div class="container">

<h3>Booking {{target}}</h3>

<form method="post">

Tanggal
<input type="date" name="tanggal"><br><br>

Acara
<input name="acara"><br><br>

Lokasi Maps
<input name="lokasi"><br><br>

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

{% if page=="profil_saya" %}

<div style="padding:15px">

<h3>Profil Saya</h3>

<b>{{user[1]}}</b><br>
Kategori : {{user[5]}}<br><br>

<h3>Booking Masuk</h3>

{% for b in bookings %}

<div class="card">

Tanggal : {{b[3]}}<br>
Acara : {{b[6]}}<br>

Lokasi :

{% if b[7] %}
<a href="{{b[7]}}" target="_blank">Buka Maps</a>
{% else %}
Menyusul
{% endif %}

<br>
Pemesan : {{b[1]}}<br>

{% if b[5]==0 %}

Belum Konfirmasi
<a href="/konfirmasi/{{b[0]}}">Konfirmasi</a>

{% else %}

Sudah Dikonfirmasi

{% endif %}

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

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template_string(html,page="booking",target=username)

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

@app.route("/chat/<username>",methods=["GET","POST"])
def chat(username):

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO chat(pengirim,penerima,pesan)
        VALUES(?,?,?)
        """,(

        session["user"],
        username,
        request.form["pesan"]

        ))

        conn.commit()
        conn.close()

    conn=db()
    c=conn.cursor()

    c.execute("""
    SELECT * FROM chat
    WHERE (pengirim=? AND penerima=?)
    OR (pengirim=? AND penerima=?)
    """,(session["user"],username,username,session["user"]))

    chats=c.fetchall()

    conn.close()

    return render_template_string(html,page="chat",chats=chats,target=username)

@app.route("/uploads/<filename>")
def upload(filename):

    return send_from_directory(UPLOAD_FOLDER,filename)

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

# ================= RUN =================

if __name__=="__main__":

    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
