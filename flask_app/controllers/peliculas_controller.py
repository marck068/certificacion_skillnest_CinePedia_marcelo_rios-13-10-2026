# Este controlador contiene las páginas y acciones relacionadas con las películas.
# Comprueba quién inició sesión y quién tiene permiso para editar o borrar.

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from config.database import consultar_todos, consultar_uno, ejecutar

# Agrupa las direcciones web que pertenecen a la sección de películas.
peliculas = Blueprint("peliculas", __name__, url_prefix="/peliculas")


# Comprueba si la persona inició sesión antes de permitirle continuar.
def iniciar_sesion_requerido():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión primero.", "warning")
        return False
    return True


# Revisa que los campos de la película no estén vacíos ni sean demasiado cortos.
def validar_pelicula(datos):
    for campo in datos.values():
        if len(campo.strip()) < 3:
            return False
    return True


@peliculas.route("/")
# Muestra las películas. Si se escribió una búsqueda, filtra por nombre o director.
def inicio():
    if not iniciar_sesion_requerido():
        return redirect(url_for("auth.login"))

    busqueda = request.args.get("q", "").strip()
    if busqueda:
        lista = consultar_todos(
            """SELECT peliculas.*, usuarios.nombre AS creador
            FROM peliculas JOIN usuarios ON peliculas.usuario_id = usuarios.id
            WHERE peliculas.nombre LIKE %s OR peliculas.director LIKE %s
            ORDER BY peliculas.created_at DESC""",
            ("%" + busqueda + "%", "%" + busqueda + "%")
        )
    else:
        lista = consultar_todos(
            """SELECT peliculas.*, usuarios.nombre AS creador
            FROM peliculas JOIN usuarios ON peliculas.usuario_id = usuarios.id
            ORDER BY peliculas.created_at DESC"""
        )

    return render_template("peliculas/inicio.html", peliculas=lista, q=busqueda)


@peliculas.route("/nueva", methods=["GET", "POST"])
# Muestra el formulario y guarda una película nueva cuando se envía.
def nueva():
    if not iniciar_sesion_requerido():
        return redirect(url_for("auth.login"))

    datos = {"nombre": "", "director": "", "fecha_estreno": "", "sinopsis": ""}

    if request.method == "POST":
        for campo in datos:
            datos[campo] = request.form.get(campo, "").strip()

        if not validar_pelicula(datos):
            flash("Todos los campos deben tener al menos 3 caracteres.", "danger")
        else:
            existe = consultar_uno(
                "SELECT id FROM peliculas WHERE LOWER(nombre) = LOWER(%s)",
                (datos["nombre"],)
            )
            if existe:
                flash("Ya existe una película con ese nombre.", "danger")
            else:
                ejecutar(
                    """INSERT INTO peliculas
                    (nombre, director, fecha_estreno, sinopsis, usuario_id)
                    VALUES (%s, %s, %s, %s, %s)""",
                    (datos["nombre"], datos["director"], datos["fecha_estreno"],
                     datos["sinopsis"], session["usuario_id"])
                )
                flash("Película guardada.", "success")
                return redirect(url_for("peliculas.inicio"))

    return render_template("peliculas/nueva.html", datos=datos)


@peliculas.route("/<int:pelicula_id>")
# Busca una película por su número identificador y carga sus comentarios.
def ver(pelicula_id):
    if not iniciar_sesion_requerido():
        return redirect(url_for("auth.login"))

    pelicula = consultar_uno(
        """SELECT peliculas.*, usuarios.nombre AS creador
        FROM peliculas JOIN usuarios ON peliculas.usuario_id = usuarios.id
        WHERE peliculas.id = %s""", (pelicula_id,)
    )
    if not pelicula:
        return render_template("errors/error.html", codigo=404,
                               mensaje="No encontramos esa película."), 404

    comentarios = consultar_todos(
        """SELECT comentarios.*, usuarios.nombre AS autor
        FROM comentarios JOIN usuarios ON comentarios.usuario_id = usuarios.id
        WHERE comentarios.pelicula_id = %s
        ORDER BY comentarios.created_at DESC""", (pelicula_id,)
    )
    puede_comentar = pelicula["usuario_id"] != session["usuario_id"]
    return render_template("peliculas/detalle.html", pelicula=pelicula,
                           comentarios=comentarios, puede_comentar=puede_comentar)


@peliculas.route("/<int:pelicula_id>/editar", methods=["GET", "POST"])
# Permite cambiar una película solo si pertenece al usuario actual.
def editar(pelicula_id):
    if not iniciar_sesion_requerido():
        return redirect(url_for("auth.login"))

    pelicula = consultar_uno("SELECT * FROM peliculas WHERE id = %s", (pelicula_id,))
    if not pelicula:
        return render_template("errors/error.html", codigo=404,
                               mensaje="No encontramos esa película."), 404
    if pelicula["usuario_id"] != session["usuario_id"]:
        flash("Solo puedes editar las películas que tú creaste.", "danger")
        return redirect(url_for("peliculas.inicio"))

    datos = {
        "nombre": pelicula["nombre"],
        "director": pelicula["director"],
        "fecha_estreno": pelicula["fecha_estreno"].isoformat(),
        "sinopsis": pelicula["sinopsis"]
    }

    if request.method == "POST":
        for campo in datos:
            datos[campo] = request.form.get(campo, "").strip()

        if not validar_pelicula(datos):
            flash("Todos los campos deben tener al menos 3 caracteres.", "danger")
        else:
            existe = consultar_uno(
                "SELECT id FROM peliculas WHERE LOWER(nombre) = LOWER(%s) AND id != %s",
                (datos["nombre"], pelicula_id)
            )
            if existe:
                flash("Otra película ya tiene ese nombre.", "danger")
            else:
                ejecutar(
                    """UPDATE peliculas SET nombre=%s, director=%s,
                    fecha_estreno=%s, sinopsis=%s WHERE id=%s""",
                    (datos["nombre"], datos["director"], datos["fecha_estreno"],
                     datos["sinopsis"], pelicula_id)
                )
                flash("Película actualizada.", "success")
                return redirect(url_for("peliculas.ver", pelicula_id=pelicula_id))

    return render_template("peliculas/editar.html", datos=datos, pelicula=pelicula)


@peliculas.route("/<int:pelicula_id>/borrar", methods=["POST"])
# Elimina una película solo si la creó el usuario que inició sesión.
def borrar(pelicula_id):
    if not iniciar_sesion_requerido():
        return redirect(url_for("auth.login"))

    pelicula = consultar_uno("SELECT * FROM peliculas WHERE id = %s", (pelicula_id,))
    if not pelicula:
        return render_template("errors/error.html", codigo=404,
                               mensaje="No encontramos esa película."), 404

    if pelicula["usuario_id"] != session["usuario_id"]:
        flash("Solo puedes borrar las películas que tú creaste.", "danger")
    else:
        ejecutar("DELETE FROM comentarios WHERE pelicula_id = %s", (pelicula_id,))
        ejecutar("DELETE FROM peliculas WHERE id = %s", (pelicula_id,))
        flash("Película eliminada.", "success")

    return redirect(url_for("peliculas.inicio"))
