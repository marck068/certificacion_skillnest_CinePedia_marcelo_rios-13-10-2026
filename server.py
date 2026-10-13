"""CinePedia: catálogo de películas con Flask, MySQL y arquitectura MVC."""
import secrets
import pymysql
from flask import Flask, abort, render_template, request, session
from config.database import SECRET_KEY
from controllers.auth_controller import bp as auth_bp
from controllers.peliculas_controller import bp as peliculas_bp
from controllers.comentarios_controller import bp as comentarios_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(auth_bp)
app.register_blueprint(peliculas_bp)
app.register_blueprint(comentarios_bp)

@app.before_request
def proteger_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(24)
    if request.method == "POST":
        enviado = request.form.get("csrf_token", "")
        esperado = session.get("csrf_token", "")
        if not secrets.compare_digest(enviado, esperado):
            abort(400)

@app.context_processor
def inyectar_globales():
    return {"csrf_token": lambda: session.get("csrf_token", "")}

def pagina_error(codigo, mensaje):
    return render_template("errors/error.html", codigo=codigo, mensaje=mensaje), codigo

@app.errorhandler(400)
def error_400(_):
    return pagina_error(400, "El formulario expiró o la solicitud no es válida. Vuelve a intentarlo.")
@app.errorhandler(404)
def error_404(_):
    return pagina_error(404, "La página o película que buscas no existe.")
@app.errorhandler(pymysql.MySQLError)
def error_bd(_):
    return pagina_error(500, "No se pudo conectar con MySQL. Comprueba que el servidor esté iniciado y que el archivo .env tenga los datos correctos.")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
