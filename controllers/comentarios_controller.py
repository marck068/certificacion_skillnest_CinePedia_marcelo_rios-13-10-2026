# Este controlador permite publicar y borrar comentarios de las películas.
# Las reglas evitan comentar una película propia y borrar comentarios ajenos.

from flask import Blueprint, request, redirect, url_for, session, flash
from config.database import consultar_uno, ejecutar

# Agrupa las rutas web relacionadas con los comentarios.
comentarios = Blueprint("comentarios", __name__)


@comentarios.route("/peliculas/<int:pelicula_id>/comentarios", methods=["POST"])
# Recibe el comentario del formulario y lo guarda si pasa las comprobaciones.
def crear(pelicula_id):
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión para comentar.", "warning")
        return redirect(url_for("auth.login"))

    pelicula = consultar_uno(
        "SELECT * FROM peliculas WHERE id = %s", (pelicula_id,)
    )
    if not pelicula:
        return "Película no encontrada", 404

    if pelicula["usuario_id"] == session["usuario_id"]:
        flash("No puedes comentar tu propia película.", "danger")
    else:
        contenido = request.form.get("contenido", "").strip()
        if len(contenido) < 3:
            flash("El comentario debe tener al menos 3 caracteres.", "danger")
        elif len(contenido) > 1000:
            flash("El comentario no puede superar los 1000 caracteres.", "danger")
        else:
            ejecutar(
                "INSERT INTO comentarios (contenido, pelicula_id, usuario_id) VALUES (%s, %s, %s)",
                (contenido, pelicula_id, session["usuario_id"])
            )
            flash("Comentario publicado.", "success")

    return redirect(url_for("peliculas.ver", pelicula_id=pelicula_id))


@comentarios.route("/comentarios/<int:comentario_id>/borrar", methods=["POST"])
# Busca un comentario y permite borrarlo solo a su autor.
def borrar(comentario_id):
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión primero.", "warning")
        return redirect(url_for("auth.login"))

    comentario = consultar_uno(
        "SELECT * FROM comentarios WHERE id = %s", (comentario_id,)
    )
    if not comentario:
        return "Comentario no encontrado", 404

    if comentario["usuario_id"] == session["usuario_id"]:
        ejecutar("DELETE FROM comentarios WHERE id = %s", (comentario_id,))
        flash("Comentario eliminado.", "success")
    else:
        flash("Solo puedes borrar tus propios comentarios.", "danger")

    return redirect(url_for("peliculas.ver", pelicula_id=comentario["pelicula_id"]))
