# Este archivo contiene comprobaciones pequeñas que pueden reutilizarse.

# Devuelve True si el texto tiene al menos 3 caracteres que no sean espacios.
def texto_valido(texto):
    return len(texto.strip()) >= 3


# Comprobación sencilla para revisar que el correo contenga arroba y punto.
def correo_valido(correo):
    return "@" in correo and "." in correo
