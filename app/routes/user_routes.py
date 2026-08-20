from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

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


# 1. GET /users
# Obtener todos los usuarios
@router.get("/")
def get_users(
    role: str | None = Query(default=None),
    is_active: bool | None = Query(default=None)
):
    result = users

    # 3. GET /users?role=admin
    if role is not None:
        result = [
            user for user in result
            if user["role"] == role
        ]

    # 4. GET /users?is_active=true
    if is_active is not None:
        result = [
            user for user in result
            if user["is_active"] == is_active
        ]

    return result


# 2. GET /users/{user_id}
# Obtener un usuario por ID
@router.get("/{user_id}")
def get_user(user_id: int):

    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )