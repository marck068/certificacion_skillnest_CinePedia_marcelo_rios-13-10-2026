# Este archivo es el punto de inicio de CinePedia.
# Aquí se crea la aplicación y se conectan las rutas de cada sección del sitio.

from flask import Flask, render_template, session, request
from config.database import SECRET_KEY
from controllers.auth_controller import auth
from controllers.peliculas_controller import peliculas
from controllers.comentarios_controller import comentarios

# Crea la aplicación Flask. __name__ ayuda a Flask a encontrar los archivos del proyecto.
app = Flask(__name__)
# Esta clave permite que Flask proteja la información guardada en la sesión del usuario.
app.secret_key = SECRET_KEY

# Conecta las rutas de registro y acceso con la aplicación principal.
app.register_blueprint(auth)
# Conecta las rutas para ver y administrar películas.
app.register_blueprint(peliculas)
# Conecta las rutas para crear y borrar comentarios.
app.register_blueprint(comentarios)


# Esta función comparte un dato con las plantillas HTML.
@app.context_processor
def datos_globales():
    return {"csrf_token": lambda: session.get("csrf_token", "")}


# Muestra una página propia cuando se visita una dirección que no existe.
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("errors/error.html", codigo=404,
                           mensaje="La página que buscas no existe."), 404


# Muestra un mensaje cuando ocurre un error interno del servidor.
@app.errorhandler(500)
def error_servidor(error):
    return render_template("errors/error.html", codigo=500,
                           mensaje="Ocurrió un error. Revisa la conexión con MySQL."), 500


# Ejecuta el servidor solo cuando este archivo se inicia directamente.
if __name__ == "__main__":
    app.run(debug=True)
