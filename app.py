from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

musisi = []

html = """
<!DOCTYPE html>
<html>
<head>
<title>Musisi Entertainment</title>
</head>

<body>

<h1>Musisi Entertainment</h1>

<form method="post">

<input name="nama" placeholder="Nama"><br><br>

<select name="kategori">
<option>Penyanyi</option>
<option>Player</option>
<option>Tukang Kendang</option>
<option>Sound</option>
<option>Tratag</option>
</select><br><br>

<input name="alamat" placeholder="Alamat"><br><br>

<input name="skill" placeholder="Skill"><br><br>

<input name="status" placeholder="Status (boleh kosong)"><br><br>

<button type="submit">Daftar</button>

</form>

<hr>

<h2>Daftar Musisi</h2>

{% for m in musisi %}

<div>

<b>{{m['nama']}}</b><br>
Kategori : {{m['kategori']}}<br>
Alamat : {{m['alamat']}}<br>
Skill : {{m['skill']}}<br>
Status : {{m['status']}}<br><br>

</div>

{% endfor %}

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():

    if request.method == "POST":

        musisi.append({
        "nama":request.form["nama"],
        "kategori":request.form["kategori"],
        "alamat":request.form["alamat"],
        "skill":request.form["skill"],
        "status":request.form["status"]
        })

        return redirect("/")

    return render_template_string(html,musisi=musisi)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080)
