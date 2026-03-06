# app.py - Com_Musisi Ultimate Pro
from flask import Flask, request, redirect, session, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit, join_room
import sqlite3, os
from werkzeug.utils import secure_filename

# ======= CONFIG =======
app = Flask(__name__)
app.secret_key = "com_musisi_ultimate"
socketio = SocketIO(app)
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = "data.db"

# ======= DATABASE =======
def db():
    return sqlite3.connect(DATABASE)

def init_db():
    conn = db()
    c = conn.cursor()
    # users table
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
    # booking table
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
    # review table
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

# ======= HTML TEMPLATE =======
html = """
<style>
body{font-family:Arial;background:#f0f2f5;margin:0;}
.header{background:#1877f2;color:white;padding:15px;font-size:22px;}
.container{width:400px;margin:auto;margin-top:20px;background:white;padding:20px;border-radius:10px;box-shadow:0 0 10px rgba(0,0,0,0.1);}
input,select,textarea{width:100%;padding:10px;margin:5px 0;}
button{width:100%;padding:10px;background:#1877f2;color:white;border:none;margin-top:5px;}
.card{background:white;padding:10px;margin:10px;border-radius:8px;box-shadow:0 0 5px rgba(0,0,0,0.1);}
a{color:#1877f2;text-decoration:none;}
.notif{color:red;font-weight:bold;}
</style>

<div class="header">Com Musisi Ultimate Pro</div>

{% if page=="login" %}
<div class="container">
<h3>Login</h3>
<form method="post">
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<button>Login</button>
</form>
<a href="/register">Daftar akun</a>
</div>
{% endif %}

{% if page=="register" %}
<div class="container">
<h3>Registrasi Musisi</h3>
<form method="post" enctype="multipart/form-data">
<input name="nama" placeholder="Nama lengkap" required>
<input name="username" placeholder="Username" required>
<input type="password" name="password" placeholder="Password" required>
<input name="alamat" placeholder="Alamat">
<input name="kota" placeholder="Kota">
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
<label>Upload Foto Profil:</label>
<input type="file" name="foto">
<button>Daftar</button>
</form>
</div>
{% endif %}

{% if page=="dashboard" %}
<div style="padding:15px">
<a href="/profil-saya">Profil Saya</a> | <a href="/logout">Logout</a>
<h3>Daftar Musisi</h3>
<form method="get">
Filter Kategori:
<select name="kategori" onchange="this.form.submit()">
<option value="">Semua</option>
{% for k in kategori_list %}
<option value="{{k}}" {% if filter_kategori==k %}selected{% endif %}>{{k}}</option>
{% endfor %}
</select>
</form>
{% for u in users %}
<div class="card">
<b>{{u[1]}}</b> - {{u[6]}}<br>
Kota: {{u[5]}}<br>
Alamat: {{u[4]}}<br>
Status: {{u[7]}}<br>
{% if u[2]!=session["user"] %}
<a href="/profil/{{u[2]}}">Lihat Profil</a>
{% endif %}
</div>
{% endfor %}
</div>
{% endif %}

{% if page=="profil" %}
<div style="padding:15px">
<h3>{{user[1]}}</h3>
Kategori: {{user[6]}}<br>
Alamat: {{user[4]}}<br>
Kota: {{user[5]}}<br>
Status: {{user[7]}}<br>
{% if user[8] %}
<img src="/uploads/{{user[8]}}" width="100"><br>
{% endif %}
{% if user[2]!=session["user"] %}
<a href="/booking/{{user[2]}}">Booking Musisi</a>
{% else %}
<a href="/profil-saya">Lihat Kalender & Chat</a>
{% endif %}
</div>
{% endif %}

{% if page=="profil_saya" %}
<div style="padding:15px">
<h3>Profil Saya - {{user[1]}}</h3>
Kategori: {{user[6]}}<br>
Alamat: {{user[4]}}<br>
Kota: {{user[5]}}<br>
Status: {{user[7]}}<br>
{% if user[8] %}
<img src="/uploads/{{user[8]}}" width="100"><br>
{% endif %}

<h4>Kalender Job & Notifikasi</h4>
{% for b in bookings %}
<div class="card">
Tanggal: {{b[3]}}<br>
Pemesan: {{b[1]}}<br>
Metode: {{b[4]}}<br>
Status: {% if b[5]==0 %}<span class="notif">Belum dikonfirmasi</span>{% else %}Dikonfirmasi{% endif %}<br>
{% if b[5]==0 %}
<a href="/konfirmasi/{{b[0]}}">Konfirmasi</a>
{% endif %}
</div>
{% endfor %}

<h4>Edit Profil</h4>
<form method="post" action="/edit-profil" enctype="multipart/form-data">
<input name="nama" value="{{user[1]}}" required>
<input name="alamat" value="{{user[4]}}">
<input name="kota" value="{{user[5]}}">
<select name="kategori" required>
{% for k in kategori_list %}
<option value="{{k}}" {% if user[6]==k %}selected{% endif %}>{{k}}</option>
{% endfor %}
</select>
<input name="status" value="{{user[7]}}">
<label>Foto Profil:</label>
<input type="file" name="foto">
<button>Simpan Profil</button>
</form>

<h4>Chat Realtime</h4>
<div id="chatbox" style="height:200px;overflow-y:scroll;border:1px solid #ccc;padding:5px;margin-bottom:5px;"></div>
<input type="text" id="chat_input" placeholder="Ketik pesan">
<button onclick="sendMessage()">Kirim</button>

<script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.4/socket.io.min.js"></script>
<script>
var socket = io();
var room = "{{user[2]}}";
socket.emit('join', room);
socket.on('message', function(msg){
    var box = document.getElementById('chatbox');
    box.innerHTML += msg+"<br>";
    box.scrollTop = box.scrollHeight;
});
function sendMessage(){
    var msg = document.getElementById('chat_input').value;
    socket.emit('send_message', {'room':room,'msg':msg,'user':'{{user[1]}}'});
    document.getElementById('chat_input').value='';
}
</script>

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

kategori_list = ["Player","Gitaris","Penyanyi","Kendang","Sound System","MC","Videografer","Decoration"]

# ======= ROUTE =======
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
        foto_file = request.files.get("foto")
        filename = secure_filename(foto_file.filename) if foto_file else ""
        if filename:
            foto_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        conn=db()
        c=conn.cursor()
        try:
            c.execute("INSERT INTO users(nama,username,password,alamat,kota,kategori,status,foto) VALUES(?,?,?,?,?,?,?,?)",(
                request.form["nama"],request.form["username"],request.form["password"],
                request.form["alamat"],request.form.get("kota",""),
                request.form["kategori"],request.form["status"], filename
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
    filter_kategori = request.args.get("kategori","")
    conn=db()
    c=conn.cursor()
    if filter_kategori:
        c.execute("SELECT * FROM users WHERE kategori=?",(filter_kategori,))
    else:
        c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return render_template_string(html,page="dashboard",users=users,kategori_list=kategori_list,filter_kategori=filter_kategori)

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

@app.route("/profil-saya")
def profil_saya():
    if "user" not in session:
        return redirect("/")
    conn=db()
    c=conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?",(session["user"],))
    user=c.fetchone()
    c.execute("SELECT * FROM booking WHERE target=? ORDER BY tanggal",(session["user"],))
    bookings=c.fetchall()
    conn.close()
    return render_template_string(html,page="profil_saya",user=user,bookings=bookings,kategori_list=kategori_list)

@app.route("/edit-profil",methods=["POST"])
def edit_profil():
    if "user" not in session:
        return redirect("/")
    foto_file = request.files.get("foto")
    filename = secure_filename(foto_file.filename) if foto_file else ""
    conn=db()
    c=conn.cursor()
    if filename:
        foto_path = filename
        c.execute("UPDATE users SET nama=?,alamat=?,kota=?,kategori=?,status=?,foto=? WHERE username=?",
                  (request.form["nama"],request.form["alamat"],request.form["kota"],
                   request.form["kategori"],request.form["status"],foto_path, session["user"]))
    else:
        c.execute("UPDATE users SET nama=?,alamat=?,kota=?,kategori=?,status=? WHERE username=?",
                  (request.form["nama"],request.form["alamat"],request.form["kota"],
                   request.form["kategori"],request.form["status"], session["user"]))
    conn.commit()
    conn.close()
    return redirect("/profil-saya")

@app.route("/booking/<username>",methods=["GET","POST"])
def booking(username):
    if "user" not in session:
        return redirect("/")
    if request.method=="POST":
        conn=db()
        c=conn.cursor()
        c.execute("INSERT INTO booking(pemesan,target,tanggal,metode) VALUES(?,?,?,?)",
                  (session["user"],username,request.form["tanggal"],request.form["metode"]))
        conn.commit()
        conn.close()
        return redirect("/dashboard")
    return render_template_string(html,page="booking",target=username)

@app.route("/konfirmasi/<int:id>")
def konfirmasi(id):
    if "user" not in session:
        return redirect("/")
    conn=db()
    c=conn.cursor()
    c.execute("UPDATE booking SET konfirmasi=1 WHERE id=?",(id,))
    conn.commit()
    conn.close()
    return redirect("/profil-saya")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ======= SOCKETIO =======
@socketio.on('join')
def join(data):
    join_room(data)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    msg = f"{data['user']}: {data['msg']}"
    emit('message', msg, room=room)

# ======= RUN =======
if __name__=="__main__":
    port=int(os.environ.get("PORT",8080))
    socketio.run(app,host="0.0.0.0",port=port)
