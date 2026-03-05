from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

users = []

html = """
<!DOCTYPE html>
<html>
<head>
<title>Com Musisi</title>
<style>
body{
font-family: Arial;
background:#f0f2f5;
margin:0;
}

.header{
background:#1877f2;
color:white;
padding:15px;
text-align:center;
font-size:24px;
}

.container{
width:350px;
margin:auto;
margin-top:40px;
background:white;
padding:25px;
border-radius:10px;
box-shadow:0 0 10px rgba(0,0,0,0.1);
}

input,select{
width:100%;
padding:10px;
margin-top:8px;
margin-bottom:15px;
border:1px solid #ccc;
border-radius:6px;
}

button{
width:100%;
padding:10px;
background:#1877f2;
color:white;
border:none;
border-radius:6px;
font-size:16px;
}

.list{
width:90%;
margin:auto;
margin-top:30px;
}

.card{
background:white;
padding:15px;
margin-bottom:10px;
border-radius:8px;
box-shadow:0 0 5px rgba(0,0,0,0.1);
}
</style>
</head>

<body>

<div class="header">
Com Musisi
</div>

<div class="container">

<h3>Daftar Musisi</h3>

<form method="post">

<label>Nama Lengkap</label>
<input type="text" name="nama" required>

<label>Username</label>
<input type="text" name="username" required>

<label>Password</label>
<input type="password" name="password" required>

<label>Alamat</label>
<input type="text" name="alamat">

<label>Kategori Bidang</label>
<select name="kategori" required>
<option value="">Pilih Bidang</option>
<option>Player</option>
<option>Gitaris</option>
<option>Penyanyi</option>
<option>Sound System</option>
<option>Mendang</option>
<option>MC</option>
<option>Videografer</option>
<option>Decoration</option>
</select>

<label>Status (boleh kosong)</label>
<input type="text" name="status">

<button type="submit">Daftar</button>

</form>
</div>

<div class="list">
<h3>Daftar Musisi Terdaftar</h3>

{% for u in users %}
<div class="card">
<b>{{u.nama}}</b><br>
Kategori : {{u.kategori}}<br>
Alamat : {{u.alamat}}<br>
Status : {{u.status}}
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
        "username":request.form["username"],
        "password":request.form["password"],
        "alamat":request.form["alamat"],
        "kategori":request.form["kategori"],
        "status":request.form["status"]
        }

        users.append(data)

        return redirect(url_for("home"))

    return render_template_string(html, users=users)

if __name__ == "__main__":
    app.run()
