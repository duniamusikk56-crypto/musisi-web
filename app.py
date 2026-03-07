from flask import Flask,request,redirect,session,render_template_string,send_from_directory
import sqlite3,os
from werkzeug.utils import secure_filename

app=Flask(__name__)
app.secret_key="com_musisi_pro"

UPLOAD_FOLDER="uploads"
DATABASE="data.db"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DATABASE):
    open(DATABASE,"w").close()

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
    acara TEXT,
    lokasi TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pengirim TEXT,
    penerima TEXT,
    pesan TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS notif(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    pesan TEXT
    )
    """)

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
padding:12px;
display:flex;
justify-content:space-between;
}

.menu a{
color:white;
margin-right:10px;
text-decoration:none;
font-weight:bold;
}

.container{
width:500px;
margin:auto;
margin-top:20px;
}

.card{
background:white;
padding:15px;
margin-bottom:15px;
border-radius:10px;
box-shadow:0 1px 4px rgba(0,0,0,0.2);
}

.profile{
display:flex;
align-items:center;
}

.profile img{
width:50px;
height:50px;
border-radius:50%;
margin-right:10px;
}

.btn{
background:#1877f2;
color:white;
padding:6px 10px;
border-radius:5px;
text-decoration:none;
}

</style>

<div class="header">

<div><b>COM MUSISI</b></div>

{% if session.get("user") %}

<div class="menu">
<a href="/dashboard">Home</a>
<a href="/chat-list">Chat</a>
<a href="/booking-saya">Booking</a>
<a href="/notif">Notif</a>
<a href="/kalender">Kalender</a>
<a href="/logout">Logout</a>
</div>

{% endif %}

</div>

{% if page=="login" %}

<div class="container">

<div class="card">

<h3>Login</h3>

<form method=post>

<input name=username placeholder=username><br><br>
<input type=password name=password placeholder=password><br><br>

<button>Login</button>

</form>

<br>

<a href="/register">Daftar akun</a>

</div>

</div>

{% endif %}

{% if page=="register" %}

<div class="container">

<div class="card">

<h3>Register</h3>

<form method=post enctype=multipart/form-data>

<input name=nama placeholder="Nama"><br><br>
<input name=username placeholder="Username"><br><br>
<input type=password name=password placeholder="Password"><br><br>
<input name=kota placeholder="Kota"><br><br>

Kategori<br>

<select name="kategori">

<option>Vokal</option>
<option>Gitar</option>
<option>Keyboard</option>
<option>Drum</option>
<option>Band</option>
<option>DJ</option>
<option>MC</option>
<option>Sound System</option>
<option>Dekorasi</option>
<option>Videografer</option>
<option>Fotografer</option>
<option>Organ Tunggal</option>

</select>

<br><br>

Foto Profil<br>
<input type=file name=foto><br><br>

<button>Daftar</button>

</form>

</div>

</div>

{% endif %}

{% if page=="dashboard" %}

<div class="container">

<form>
<input name=search placeholder="Cari musisi atau kota">
<button>Cari</button>
</form>

<br>

{% for u in users %}

<div class="card">

<div class="profile">

{% if u[6] %}
<img src="/uploads/{{u[6]}}">
{% endif %}

<div>

<b>{{u[1]}}</b><br>
{{u[5]}} - {{u[4]}}

</div>

</div>

<br>

<a class="btn" href="/profil/{{u[2]}}">Profil</a>

</div>

{% endfor %}

</div>

{% endif %}

{% if page=="profil" %}

<div class="container">

<div class="card">

<h2>{{user[1]}}</h2>

{% if user[6] %}
<img src="/uploads/{{user[6]}}" width=120>
{% endif %}

<br><br>

Kategori : {{user[5]}}<br>
Kota : {{user[4]}}<br><br>

{% if user[2]!=session["user"] %}

<a class="btn" href="/booking/{{user[2]}}">Booking</a>
<a class="btn" href="/chat/{{user[2]}}">Chat</a>

{% endif %}

</div>

</div>

{% endif %}

"""

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

@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        foto=None

        if "foto" in request.files:

            f=request.files["foto"]

            if f.filename!="":

                foto=secure_filename(f.filename)
                f.save(os.path.join(UPLOAD_FOLDER,foto))

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO users(nama,username,password,kota,kategori,foto)
        VALUES(?,?,?,?,?,?)
        """,(request.form["nama"],
        request.form["username"],
        request.form["password"],
        request.form["kota"],
        request.form["kategori"],
        foto))

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

    conn.close()

    return render_template_string(html,page="profil",user=user)

@app.route("/chat-list")
def chat_list():

    conn=db()
    c=conn.cursor()

    c.execute("""
    SELECT DISTINCT pengirim FROM messages
    WHERE penerima=?
    """,(session["user"],))

    data=c.fetchall()

    conn.close()

    text="<h3>Daftar Chat</h3>"

    for d in data:
        text+=f'<a href="/chat/{d[0]}">'+d[0]+"</a><br>"

    return text

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

    text="<h3>Chat</h3>"

    for m in msgs:
        text+=m[1]+": "+m[3]+"<br>"

    text+="""
    <form method=post>
    <input name=pesan>
    <button>Kirim</button>
    </form>
    """

    return text

@app.route("/booking/<username>",methods=["GET","POST"])
def booking(username):

    if request.method=="POST":

        conn=db()
        c=conn.cursor()

        c.execute("""
        INSERT INTO booking(pemesan,target,tanggal,acara,lokasi)
        VALUES(?,?,?,?,?)
        """,(session["user"],username,
        request.form["tanggal"],
        request.form["acara"],
        request.form["lokasi"]))

        c.execute("INSERT INTO notif(user,pesan) VALUES(?,?)",
        (username,"Booking baru dari "+session["user"]))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return """
    <h3>Booking</h3>
    <form method=post>
    Tanggal<input type=date name=tanggal><br><br>
    Acara<input name=acara><br><br>
    Lokasi<input name=lokasi><br><br>
    <button>Booking</button>
    </form>
    """

@app.route("/notif")
def notif():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM notif WHERE user=?",(session["user"],))
    data=c.fetchall()

    conn.close()

    text="<h3>Notifikasi</h3>"

    for n in data:
        text+=n[2]+"<br>"

    return text

@app.route("/kalender")
def kalender():

    conn=db()
    c=conn.cursor()

    c.execute("SELECT * FROM kalender WHERE user=?",(session["user"],))
    data=c.fetchall()

    conn.close()

    text="<h3>Kalender Job</h3>"

    for k in data:
        text+=k[2]+" - "+k[3]+"<br>"

    return text

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
