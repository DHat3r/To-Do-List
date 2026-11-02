from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.database import get_session
from app.models import UserRecord
from app.security import decode_access_token

# Inyección de dependencias: cada endpoint que declare "session: SessionDep"
# recibe una sesión abierta por get_session, sin crearla él mismo.
# Así los tests pueden reemplazar get_session por una base de datos de prueba.
SessionDep = Annotated[Session, Depends(get_session)]

# Lee el header "Authorization: Bearer <token>" y devuelve el token.
# Si falta, responde 401 solo. tokenUrl le dice a /docs dónde hacer login,
# y así aparece el botón "Authorize".
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
) -> UserRecord:
    """Dependencia que convierte el token en el usuario que hace la petición."""
    # Mismo mensaje para todos los fallos: no le damos pistas a un atacante
    # sobre si el token expiró, estaba mal firmado o el usuario ya no existe.
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},  # lo exige el estándar HTTP
    )
    try:
        user_id = decode_access_token(token)
    except jwt.InvalidTokenError:
        raise unauthorized from None
    user = session.get(UserRecord, user_id)
    if user is None:
        raise unauthorized
    return user


CurrentUserDep = Annotated[UserRecord, Depends(get_current_user)]
