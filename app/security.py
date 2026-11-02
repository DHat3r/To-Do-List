import os
from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

# La clave que firma los tokens. Es un secreto: va en .env, nunca en el código.
# Si falta, la app no arranca. Es mejor fallar al inicio que firmar tokens con
# una clave por defecto que cualquiera podría leer en GitHub.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Falta la variable de entorno SECRET_KEY (ver .env.example)")

ALGORITHM = "HS256"  # HMAC con SHA-256: firma con una clave compartida
ACCESS_TOKEN_EXPIRE = timedelta(minutes=30)

# Argon2 es el algoritmo de hash recomendado hoy para contraseñas: es lento a
# propósito, para que probar millones de contraseñas por fuerza bruta no sirva.
_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    # Cada hash lleva una "sal" aleatoria: la misma contraseña da hashes distintos.
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return _password_hash.verify(password, hashed)


def create_access_token(
    user_id: int, expires_in: timedelta = ACCESS_TOKEN_EXPIRE
) -> str:
    # "sub" (subject) y "exp" (expiration) son campos estándar de JWT.
    # El token va firmado, no cifrado: cualquiera puede leer su contenido,
    # pero nadie puede modificarlo sin la SECRET_KEY. No pongas datos sensibles.
    payload = {"sub": str(user_id), "exp": datetime.now(UTC) + expires_in}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int:
    """Devuelve el id del usuario. Lanza jwt.InvalidTokenError si el token es
    inválido, fue modificado o ya expiró."""
    # algorithms=[...] es obligatorio: sin él, un atacante podría elegir el
    # algoritmo "none" y saltarse la firma.
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])
