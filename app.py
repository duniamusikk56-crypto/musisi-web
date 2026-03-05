from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

musisi = []

html = """

<!DOCTYPE html>
<html>

<head>

<title>Musisi Entertainment</title>

<style>

body{
font-family:Arial;
background:#f2f2f2;
margin:0;
}

.header{
background:#111;
color:white;
text-align:center;
padding:20px;
font-size:28px;
}

.container{
width:90%;
max-width:900px;
margin:auto;
margin-top:20px;
}

.form-box{
background:white;
padding:20px;
border-radius:10px;
box-shadow:0 0 10px rgba(0,0,0,0.1);
margin-bottom:20px;
}

input,select{
width:100%;
padding:10px;
margin:5px 0;
border:1px solid #ccc;
border-radius:5px;
}

button{
padding:10px;
background:#28a745;
color:white;
border:none;
border-radius:5px;
cursor:pointer;
}

button:hover{
background:#218838;
}

.card{
background:white;
padding:15px;
margin-top:15px;
border-radius:10px;
box-shadow:0 0 10px rgba(0,0,0,0.1);
}

.nama{
font-size:20px;
font-weight:bold;
}

</style>

</head>

<body>

<div class="header">

Platform Musisi Entertainment

</div>

<div class="container">

<div class="form-box">

<h2>Daftar Musisi / Kru Entertainment</h2>

<form method="post">

<input name="nama" placeholder="Nama">

<select name="kategori">

<option>Penyanyi</option>
<option>Player</option>
<option>Tukang Kendang</option>
<option>MC</option>
<option>Sound System</option>
<option>Tratag</option>

</select>

<input name="alamat" placeholder="Alamat">

<input name="skill" placeholder="Skill / Alat">

<input name="status" placeholder="Status (boleh kosong)">

<button type="submit">Daftar</button>

</form>

</div>

<h2>Daftar Musisi</h2>

{% for m in musisi %}

<div class="card">

<div class="nama">{{m['nama']}}</div>

Kategori : {{m['kategori']}} <br>

Alamat : {{m['alamat']}} <br>

Skill : {{m['skill']}} <br>

Status : {{m['status']}} <br>

</div>

{% endfor %}

</div>

</body>

</html>

"""

@app.route("/", methods=["GET","POST"])
def home():

    if request.method == "POST":

        data = {

        "nama":request.form["nama"],
        "kategori":request.form["kategori"],
        "alamat":request.form["alamat"],
        "skill":request.form["skill"],
        "status":request.form["status"]

        }

        musisi.append(data)

        return redirect("/")

    return render_template_string(html, musisi=musisi)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
