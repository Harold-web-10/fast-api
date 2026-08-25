# Archivo de datos en memoria.
# Esta lista simula una base de datos simple para la API.
# Al reiniciar el servidor, los cambios se pierden porque están en RAM.

users = [
    {
        "id": 1,
        "name": "Harold",
        "email": "harold@gmail.com",
        "role": "admin",
        "is_active": True
    },
    {
        "id": 2,
        "name": "Carlos",
        "email": "carlos@gmail.com",
        "role": "support",
        "is_active": True
    },
    {
        "id": 3,
        "name": "Maria",
        "email": "maria@gmail.com",
        "role": "user",
        "is_active": False
    }
]
