from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.dependencies import SessionDep
from app.models import UserRecord
from app.schemas import Token, User, UserCreate
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: SessionDep) -> User:
    existing = session.exec(
        select(UserRecord).where(UserRecord.username == data.username)
    ).first()
    if existing is not None:
        # 409 Conflict: la petición es válida, pero choca con un dato que ya existe.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe"
        )
    user = UserRecord(
        username=data.username, hashed_password=hash_password(data.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    # El tipo de retorno User filtra el hashed_password: no sale en la respuesta.
    return user


# OAuth2PasswordRequestForm lee "username" y "password" como formulario
# (no JSON), porque así lo define el estándar OAuth2 y así lo envía /docs.
@router.post("/token")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = session.exec(
        select(UserRecord).where(UserRecord.username == form.username)
    ).first()
    # Mismo error si el usuario no existe o la contraseña está mal: así nadie
    # puede averiguar qué nombres de usuario están registrados.
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.id))
