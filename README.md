# Device Systems API

API REST sencilla construida con **FastAPI** para la gestion de usuarios.

## Estructura del proyecto

```
device_systems/
  app/
    main.py
    routes/
      user_routes.py
    schemas/
      user_schema.py
  requirements.txt
  README.md
```

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/users` | Obtiene todos los usuarios |
| GET | `/users?role=admin` | Filtra usuarios por rol |
| GET | `/users?is_active=true` | Filtra usuarios por estado |
| GET | `/users/{user_id}` | Obtiene un usuario por ID |

## Datos de ejemplo

- **Harold** — admin — activo
- **Carlos** — support — activo
- **Maria** — user — inactivo

## Requisitos

- Python 3.8+
- FastAPI
- Uvicorn

## Ejecucion

```bash
pip install fastapi uvicorn
uvicorn app.main:app --reload
```

Luego abre `http://127.0.0.1:8000/docs` para ver la documentacion interactiva.
