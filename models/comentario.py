# Este modelo agrupa consultas básicas relacionadas con los comentarios.

from config.database import consultar_todos, ejecutar


# Devuelve los comentarios asociados a una película.
def listar_comentarios(pelicula_id):
    return consultar_todos(
        "SELECT * FROM comentarios WHERE pelicula_id = %s ORDER BY created_at DESC",
        (pelicula_id,)
    )


# Guarda el texto del comentario, la película y el usuario que lo escribió.
def crear_comentario(contenido, pelicula_id, usuario_id):
    ejecutar(
        "INSERT INTO comentarios (contenido, pelicula_id, usuario_id) VALUES (%s, %s, %s)",
        (contenido, pelicula_id, usuario_id)
    )
