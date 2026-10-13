# Este controlador se encarga del registro, el inicio de sesión y el cierre de sesión.
# Una ruta es una dirección de la página que Flask sabe cómo responder.

import re
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config.database import consultar_uno, ejecutar

# Blueprint permite guardar juntas las rutas de una sección del sitio.
auth = Blueprint("auth", __name__)


# La dirección que aparece en la página web se conecta con la función que viene debajo.
@auth.route("/")
# Decide si el visitante debe ver la página de acceso o ir a la lista de películas.
def acceso():
    if session.get("usuario_id"):
        return redirect(url_for("peliculas.inicio"))
    return render_template("auth/acceso.html")


# La dirección que aparece en la página web se conecta con la función que viene debajo.
@auth.route("/login", methods=["GET", "POST"])
# Comprueba el correo y la contraseña enviados desde el formulario.
def login():
    if session.get("usuario_id"):
        return redirect(url_for("peliculas.inicio"))

    email = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        usuario = consultar_uno(
            "SELECT * FROM usuarios WHERE email = %s", (email,)
        )

        if usuario and bcrypt.checkpw(
            password.encode("utf-8"), usuario["password"].encode("utf-8")
        ):
            session["usuario_id"] = usuario["id"]
            session["usuario_nombre"] = usuario["nombre"]
            flash("Inicio de sesión correcto.", "success")
            return redirect(url_for("peliculas.inicio"))

        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("auth/login.html", email=email)


# La dirección que aparece en la página web se conecta con la función que viene debajo.
@auth.route("/registro", methods=["GET", "POST"])
# Recibe los datos del formulario y comprueba que sean válidos antes de crear una cuenta.
def registro():
    if session.get("usuario_id"):
        return redirect(url_for("peliculas.inicio"))

    datos = {"nombre": "", "apellido": "", "email": ""}

    if request.method == "POST":
        datos["nombre"] = request.form.get("nombre", "").strip()
        datos["apellido"] = request.form.get("apellido", "").strip()
        datos["email"] = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar", "")

# Revisamos que los datos escritos por la persona tengan un formato aceptable.
        # Validar los campos del formulario.
        if len(datos["nombre"]) < 3 or len(datos["apellido"]) < 3:
            flash("El nombre y el apellido deben tener al menos 3 caracteres.", "danger")
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", datos["email"]):
            flash("Ingresa un correo válido.", "danger")
        elif len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "danger")
        elif password != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
        else:
            usuario = consultar_uno(
                "SELECT id FROM usuarios WHERE email = %s", (datos["email"],)
            )
            if usuario:
                flash("Ese correo ya está registrado.", "danger")
            else:
                clave_segura = bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
                ejecutar(
                    "INSERT INTO usuarios (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)",
                    (datos["nombre"], datos["apellido"], datos["email"], clave_segura)
                )
                flash("Cuenta creada. Ahora inicia sesión.", "success")
                return redirect(url_for("auth.login"))

    return render_template("auth/registro.html", datos=datos)


# La dirección que aparece en la página web se conecta con la función que viene debajo.
@auth.route("/logout", methods=["POST"])
# Borra los datos de la sesión para cerrar la cuenta actual.
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("auth.login"))
