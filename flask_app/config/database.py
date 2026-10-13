# Este archivo contiene la configuración de MySQL.
# También incluye funciones pequeñas para consultar, guardar y actualizar datos.

import os
import pymysql
from pymysql.cursors import DictCursor

# Intenta cargar las variables del archivo .env, si está instalada la biblioteca python-dotenv.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Datos para conectarse a MySQL. Si no existe una variable en .env, se usa el valor de ejemplo.
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "cinepedia")
SECRET_KEY = os.getenv("SECRET_KEY", "clave-local-cinepedia")


# Abre una conexión con la base de datos y devuelve el objeto de conexión.
def conectar():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=DictCursor
    )


# Ejecuta una consulta que puede devolver varias filas, por ejemplo una lista de películas.
def consultar_todos(sql, datos=()):
    conexion = conectar()
# Intenta cargar las variables del archivo .env, si está instalada la biblioteca python-dotenv.
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, datos)
            resultado = cursor.fetchall()
        return resultado
    finally:
        conexion.close()


# Ejecuta una consulta que devuelve una sola fila, por ejemplo un usuario.
def consultar_uno(sql, datos=()):
    conexion = conectar()
# Intenta cargar las variables del archivo .env, si está instalada la biblioteca python-dotenv.
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, datos)
            resultado = cursor.fetchone()
        return resultado
    finally:
        conexion.close()


# Ejecuta una instrucción que cambia datos, como INSERT, UPDATE o DELETE.
def ejecutar(sql, datos=()):
    conexion = conectar()
# Intenta cargar las variables del archivo .env, si está instalada la biblioteca python-dotenv.
    try:
        with conexion.cursor() as cursor:
            cursor.execute(sql, datos)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()
