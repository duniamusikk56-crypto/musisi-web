from flask import Flask, request, redirect, render_template_string
import uuid
import os

app = Flask(__name__)

users=[]
chat=[]
booking=[]

kategori_list=[
"Penyanyi",
"Mendang",
"Player",
"MC",
"Sound System",
"Tratag",
"Lighting",
"Organ Tunggal",
"Videografer",
"Decoration"
]

home="""
<h1>Com_Musisi</h1>

<h3>Daftar Akun</h3>

<form method="post" action="/register">

Nama<br>
<input name="nama" required><br>

Kategori<br>
<select name="kategori">
""" + "".join([f"<option>{k}</option>" for k in kategori_list]) + """

</select><br>

Alamat<br>
<input name="alamat"><br>

Status<br>
<input name="status"><br>

Foto Profil (link gambar)<br>
<input name="foto"><br>

Password<br>
<input name="password" required><br><br>

<button>Daftar</button>

</form>

<hr>

<h3>Login</h3>

<form method="post" action="/login">

Nama<br>
<input name="nama" required><br>

Password<br>
<input name="password" required><br><br>

<button>Login</button>

</form>
"""

@app.route("/")
def index():
    return render_template_string(home)

@app.route("/register",methods=["POST"])
def register():

    users.append({
        "id":str(uuid.uuid4()),
        "nama":request.form.get("nama"),
        "kategori":request.form.get("kategori"),
        "alamat":request.form.get("alamat"),
        "status":request.form.get("status"),
        "foto":request.form.get("foto"),
        "password":request.form.get("password")
    })

    return redirect("/")

@app.route("/login",methods=["POST"])
def login():

    nama=request.form.get("nama")
    password=request.form.get("password")

    for u in users:
        if u["nama"]==nama and u["password"]==password:
            return redirect("/dashboard/"+nama)

    return "Login gagal"

@app.route("/dashboard/<login>")
def dashboard(login):

    page=f"<h2>Dashboard {login}</h2>"

    page+=f"""
<form method="post" action="/cari/{login}">
Cari Musisi
<input name="cari">
<button>Cari</button>
</form>
<hr>
"""

    for k in kategori_list:

        page+=f"<h3>{k}</h3>"

        for u in users:

            if u["kategori"]==k:

                foto=u["foto"] if u["foto"] else ""

                page+=f"""

<div style="border:1px solid #ccc;padding:10px;margin:10px;width:250px">

<img src="{foto}" width="80"><br>

<b>{u['nama']}</b><br>

{u['status']}<br>

<a href="/profil/{login}/{u['nama']}">Profil</a>

</div>

"""

    return page

@app.route("/cari/<login>",methods=["POST"])
def cari(login):

    keyword=request.form.get("cari","")

    page="<h2>Hasil Pencarian</h2>"

    for u in users:

        if keyword.lower() in u["nama"].lower():

            page+=f"<a href='/profil/{login}/{u['nama']}'>{u['nama']}</a><br>"

    return page

@app.route("/profil/<login>/<nama>")
def profil(login,nama):

    for u in users:

        if u["nama"]==nama:

            foto=u["foto"] if u["foto"] else ""

            page=f"""

<h2>{u['nama']}</h2>

<img src="{foto}" width="150"><br>

Kategori : {u['kategori']}<br>
Alamat : {u['alamat']}<br>
Status : {u['status']}<br>

<hr>

<h3>Booking</h3>

<form method="post" action="/booking/{login}/{nama}">

Tanggal<br>
<input name="tanggal" required><br>

Lokasi<br>
<input name="lokasi"><br>

Keterangan<br>
<input name="ket"><br>

Metode<br>

<select name="metode">
<option>DP</option>
<option>NON DP</option>
</select><br><br>

<button>Booking</button>

</form>

<hr>

<h3>Chat</h3>

<form method="post" action="/chat/{login}/{nama}">
<input name="pesan">
<button>Kirim</button>
</form>

<hr>
"""

            page+="<h3>Riwayat Booking</h3>"

            for b in booking:

                if b["tujuan"]==nama:

                    page+=f"""

Pemesan : {b['pemesan']}<br>
Tanggal : {b['tanggal']}<br>
Lokasi : {b['lokasi']}<br>
Metode : {b['metode']}<br>
Status : {b['status']}<br>
<hr>

"""

            page+="<h3>Chat Masuk</h3>"

            for c in chat:

                if c["tujuan"]==nama:

                    page+=c["pengirim"]+" : "+c["pesan"]+"<br>"

            return page

    return "User tidak ditemukan"

@app.route("/chat/<login>/<nama>",methods=["POST"])
def kirim_chat(login,nama):

    chat.append({
        "pengirim":login,
        "tujuan":nama,
        "pesan":request.form.get("pesan")
    })

    return redirect("/profil/"+login+"/"+nama)

@app.route("/booking/<login>/<nama>",methods=["POST"])
def booking_job(login,nama):

    tanggal=request.form.get("tanggal")

    for b in booking:
        if b["tujuan"]==nama and b["tanggal"]==tanggal:
            return "Tanggal sudah dibooking"

    booking.append({
        "id":str(uuid.uuid4()),
        "pemesan":login,
        "tujuan":nama,
        "tanggal":tanggal,
        "lokasi":request.form.get("lokasi"),
        "ket":request.form.get("ket"),
        "metode":request.form.get("metode"),
        "status":"MENUNGGU"
    })

    if request.form.get("metode")=="DP":
        return redirect("/pembayaran/"+login)

    return redirect("/dashboard/"+login)

@app.route("/pembayaran/<login>")
def pembayaran(login):

    return f"""

<h2>Pembayaran DP</h2>

BRI<br>
1234567890<br>
a.n Com_Musisi<br><br>

DANA<br>
08123456789<br><br>

OVO<br>
08123456789<br><br>

<a href="/dashboard/{login}">Kembali</a>

"""

# RUN SERVER UNTUK RAILWAY

if __name__ == "__main__":
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
