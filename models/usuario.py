# Este modelo agrupa consultas básicas relacionadas con los usuarios.
# Separa las consultas de base de datos del resto del programa.

from config.database import consultar_uno, ejecutar


# Busca un usuario usando su correo electrónico.
def buscar_usuario(email):
    return consultar_uno("SELECT * FROM usuarios WHERE email = %s", (email,))


# Guarda un usuario nuevo en la base de datos.
def crear_usuario(nombre, apellido, email, password):
    ejecutar(
        "INSERT INTO usuarios (nombre, apellido, email, password) VALUES (%s, %s, %s, %s)",
        (nombre, apellido, email, password)
    )
