from flask import Flask, request, render_template_string, redirect
import sqlite3
import webbrowser
from threading import Timer

app = Flask(__name__)

def conectar():
    return sqlite3.connect("citas.db")

# Crear base de datos
conn = conectar()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS citas(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nombre TEXT,
servicio TEXT,
fecha TEXT,
hora TEXT
)
""")

conn.commit()
conn.close()

horarios = [
"09:00","10:00","11:00","12:00",
"13:00","14:00","15:00","16:00",
"17:00","18:00"
]

pagina = """

<html>

<head>

<title>Ale Beauty</title>

<style>

body{
font-family:Arial;
background:#ffe6f2;
text-align:center;
}

.card{
background:white;
width:420px;
margin:auto;
padding:25px;
border-radius:12px;
box-shadow:0px 0px 12px #ccc;
}

input,select{
width:90%;
padding:8px;
margin:6px;
}

button{
background:#e83e8c;
color:white;
border:none;
padding:10px 20px;
border-radius:6px;
cursor:pointer;
}

a{
text-decoration:none;
color:#e83e8c;
}

</style>

</head>

<body>

<div class="card">

<h2>💅 Reserva tu cita</h2>

<form method="post">

<input name="nombre" placeholder="Nombre" required>

<select name="servicio">
<option>Manicure</option>
<option>Pedicure</option>
<option>Tinte de cabello</option>
</select>

<input type="date" name="fecha" required>

<select name="hora">
{% for h in horarios %}
<option>{{h}}</option>
{% endfor %}
</select>

<br><br>

<button>Reservar</button>

</form>

<br>

<a href="/panel">📊 Ver citas</a>

</div>

</body>

</html>
"""

@app.route("/", methods=["GET","POST"])
def reservar():

    if request.method == "POST":

        nombre = request.form["nombre"]
        servicio = request.form["servicio"]
        fecha = request.form["fecha"]
        hora = request.form["hora"]

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
        "SELECT * FROM citas WHERE fecha=? AND hora=?",
        (fecha,hora)
        )

        ocupado = cursor.fetchone()

        if ocupado:
            conn.close()
            return "<h3>⚠️ Esa hora ya está reservada</h3><a href='/'>Volver</a>"

        cursor.execute(
        "INSERT INTO citas(nombre,servicio,fecha,hora) VALUES(?,?,?,?)",
        (nombre,servicio,fecha,hora)
        )

        conn.commit()
        conn.close()

        return f"""
        <h2>✅ Cita confirmada</h2>
        {nombre}<br>
        {servicio}<br>
        {fecha}<br>
        {hora}
        <br><br>
        <a href="/">Nueva cita</a>
        """

    return render_template_string(pagina, horarios=horarios)


@app.route("/panel")
def panel():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM citas")
    datos = cursor.fetchall()

    conn.close()

    tabla = """
    <h2>Panel de citas</h2>
    <table border=1 style="margin:auto">
    <tr>
    <th>ID</th>
    <th>Nombre</th>
    <th>Servicio</th>
    <th>Fecha</th>
    <th>Hora</th>
    <th>Eliminar</th>
    </tr>
    """

    for fila in datos:
        tabla += f"""
        <tr>
        <td>{fila[0]}</td>
        <td>{fila[1]}</td>
        <td>{fila[2]}</td>
        <td>{fila[3]}</td>
        <td>{fila[4]}</td>
        <td><a href='/eliminar/{fila[0]}'>❌</a></td>
        </tr>
        """

    tabla += "</table><br><a href='/'>Volver</a>"

    return tabla


@app.route("/eliminar/<int:id>")
def eliminar(id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM citas WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/panel")


def abrir():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    Timer(1, abrir).start()
    app.run(debug=False)
