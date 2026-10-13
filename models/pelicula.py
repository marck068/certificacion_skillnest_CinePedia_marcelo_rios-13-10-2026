# Este modelo agrupa consultas básicas para buscar y guardar películas.

from config.database import consultar_todos, consultar_uno, ejecutar


# Devuelve todas las películas ordenadas desde la más reciente.
def listar_peliculas():
    return consultar_todos("SELECT * FROM peliculas ORDER BY created_at DESC")


# Busca una película por su identificador numérico.
def buscar_pelicula(pelicula_id):
    return consultar_uno("SELECT * FROM peliculas WHERE id = %s", (pelicula_id,))


# Guarda una película y el identificador del usuario que la creó.
def crear_pelicula(datos, usuario_id):
    ejecutar(
        """INSERT INTO peliculas (nombre, director, fecha_estreno, sinopsis, usuario_id)
        VALUES (%s, %s, %s, %s, %s)""",
        (datos["nombre"], datos["director"], datos["fecha_estreno"],
         datos["sinopsis"], usuario_id)
    )
