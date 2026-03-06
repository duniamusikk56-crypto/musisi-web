from flask import Flask,request,redirect,session,render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key="com_musisi_1234"

DATABASE="data.db"

# ===== Fungsi database =====
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

# ===== HTML Template Satu File =====
html="""
<style>
body{font-family:Arial;background:#f0f2f5;margin:0;}
.header{background:#1877f2;color:white;padding:15px;font-size:22px;}
.container{width:350px;margin:auto;margin-top:40px;background:white;padding:25px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);}
input,select{width:100%;padding:10px;margin-top:8px;margin-bottom:12px;}
button{width:100%;padding:10px;background:#1877f2;color:white;border:none;}
.card{background:white;padding:15px;margin:10px;border-radius:8px;box-shadow:0 0 5px rgba(0,0,0,0.1);}
a{color:#1877f2;text-decoration:none;}
</style>

<div class="header">Com Musisi</div>

{% if page=="login" %}
<div class="container">
<h3>Login</h3>
<form method="post">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button>Login</button>
</form>
<br>
<a href="/register">Daftar akun</a>
</div>
{% endif %}

{% if page=="register" %}
<div class="container">
<h3>Registrasi Musisi</h3>
<form method="post">
<input name="nama" placeholder="Nama lengkap" required>
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<input name="alamat" placeholder="Alamat">
<select name="kategori" required>
<option>Player</option>
<option>Gitaris</option>
<option>Penyanyi</option>
<option>Kendang</option>
<option>Sound System</option>
<option>MC</option>
<option>Videografer</option>
<option>Decoration</option>
</select>
<input name="status" placeholder="Status (boleh kosong)">
<button>Daftar</button>
</form>
</div>
{% endif %}

{% if page=="dashboard" %}
<div style="padding:15px">
<a href="/logout">Logout</a>
<h3>Daftar Musisi</h3>
{% for u in users %}
<div class="card">
<b>{{u[1]}}</b><br>
Kategori : {{u[5]}}<br>
Alamat : {{u[4]}}<br>
Status : {{u[6]}}<br><br>
<a href="/profil/{{u[2]}}">Lihat Profil</a>
</div>
{% endfor %}
</div>
{% endif %}

{% if page=="profil" %}
<div style="padding:20px">
<h3>{{user[1]}}</h3>
Kategori : {{user[5]}}<br>
Alamat : {{user[4]}}<br>
Status : {{user[6]}}<br><br>
<a href="/booking/{{user[2]}}">Booking Musisi</a>
</div>
{% endif %}

{% if page=="booking" %}
<div class="container">
<h3>Booking {{target}}</h3>
<form method="post">
Tanggal Acara
<input type="date" name="tanggal" required>
Metode Pembayaran
<select name="metode" required>
<option>DP Transfer BRI</option>
<option>DP DANA</option>
<option>Non DP</option>
</select>
<button>Booking</button>
</form>
</div>
{% endif %}
"""

# ===== ROUTE =====

@app.route("/",methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=db()
        c=conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",(request.form["username"],request.form["password"]))
        user=c.fetchone()
        conn.close()
        if user:
            session["user"]=user[2]
            return redirect("/dashboard")
    return render_template_string(html,page="login")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        conn=db()
        c=conn.cursor()
        try:
            c.execute("INSERT INTO users(nama,username,password,alamat,kategori,status) VALUES(?,?,?,?,?,?)",(
                request.form["nama"],
                request.form["username"],
                request.form["password"],
                request.form["alamat"],
                request.form["kategori"],
                request.form["status"]
            ))
            conn.commit()
        except:
            conn.close()
            return "Username sudah dipakai!"
        conn.close()
        return redirect("/")
    return render_template_string(html,page="register")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    conn=db()
    c=conn.cursor()
    c.execute("SELECT * FROM users")
    users=c.fetchall()
    conn.close()
    return render_template_string(html,page="dashboard",users=users)

@app.route("/profil/<username>")
def profil(username):
    if "user" not in session:
        return redirect("/")
    conn=db()
    c=conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?",(username,))
    user=c.fetchone()
    conn.close()
    return render_template_string(html,page="profil",user=user)

@app.route("/booking/<username>",methods=["GET","POST"])
def booking(username):
    if "user" not in session:
        return redirect("/")
    if request.method=="POST":
        conn=db()
        c=conn.cursor()
        c.execute("INSERT INTO booking(pemesan,target,tanggal,metode) VALUES(?,?,?,?)",(
            session["user"],username,request.form["tanggal"],request.form["metode"]
        ))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    return render_template_string(html,page="booking",target=username)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ===== RUN RAILWAY STABLE =====
if __name__=="__main__":
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
