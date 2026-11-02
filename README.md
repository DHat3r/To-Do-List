# To-Do List API

[![CI](https://github.com/DHat3r/To-Do-List/actions/workflows/ci.yml/badge.svg)](https://github.com/DHat3r/To-Do-List/actions/workflows/ci.yml)

> API REST de tareas con autenticación JWT: cada usuario registra, consulta, edita y borra solo sus propias tareas.

![Captura o GIF de la demo](docs/demo.gif)
<!-- TODO: agregar captura de /docs -->

## Demo

- Enlace en vivo: Aún no desplegada
- Documentación de la API (Swagger): `http://localhost:8000/docs` al correrla localmente

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.14, FastAPI, Pydantic |
| Frontend | — (solo API, documentación interactiva en /docs) |
| Base de datos | SQLite con SQLModel (SQLAlchemy) |
| Autenticación | JWT (PyJWT) y hash Argon2 (pwdlib) |
| Infraestructura | Docker, Docker Compose, GitHub Actions |
| Calidad | pytest (19 tests), ruff |

## Cómo ejecutarlo

```bash
git clone https://github.com/DHat3r/To-Do-List.git
cd To-Do-List
cp .env.example .env
```

1. Edita `.env` y pon una `SECRET_KEY` generada con:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   La app no arranca sin `SECRET_KEY`.

2. Levanta la aplicación:

   ```bash
   docker compose up --build
   ```

La aplicación queda disponible en `http://localhost:8000`.

> Si el puerto 8000 está ocupado, define `API_PORT=8001` en `.env` y usa `http://localhost:8001`.

### Sin Docker

Requiere el `.env` con `SECRET_KEY` del paso 1.

```bash
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

python -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload --env-file .env
```

## Endpoints

| Método | Ruta | Auth | Descripción |
|--------|------|------|-------------|
| GET | `/health` | No | Estado del servicio |
| POST | `/auth/register` | No | Crea usuario; body JSON `{username, password}` |
| POST | `/auth/token` | No | Login; formulario `x-www-form-urlencoded`; devuelve `access_token` |
| GET | `/tasks` | Sí | Lista tus tareas |
| POST | `/tasks` | Sí | Crea tarea `{title, description?}` |
| GET | `/tasks/{id}` | Sí | Obtiene una de tus tareas |
| PATCH | `/tasks/{id}` | Sí | Actualización parcial `{title?, description?, completed?}` |
| DELETE | `/tasks/{id}` | Sí | Borra la tarea; responde `204` |

Las rutas con Auth = Sí requieren el header `Authorization: Bearer <token>`.

## Tests

```bash
python -m pytest -v
ruff check .
```

Los tests usan SQLite en memoria, así que no tocan la base de datos real. El CI los corre en cada push.

## Arquitectura

```
app/
├── main.py           # crea la app, registra routers, crea tablas al arrancar
├── database.py       # engine y sesión por petición
├── models.py         # tablas users y tasks
├── schemas.py        # esquemas Pydantic de entrada/salida
├── security.py       # hash de contraseñas y JWT
├── dependencies.py   # sesión y usuario actual inyectados con Depends
└── routers/
    ├── auth.py       # registro y login
    └── tasks.py      # CRUD de tareas del usuario
tests/
├── conftest.py       # fixtures
├── test_tasks.py
└── test_auth.py
```

Flujo: petición → router → dependencia `get_current_user` valida el JWT → sesión SQLModel → SQLite.

## Decisiones técnicas

- **Esquemas separados de los modelos de tabla:** lo que entra y sale por la API no es igual a lo que se guarda; así el hash de la contraseña nunca sale.
- **Inyección de dependencias:** los endpoints reciben sesión y usuario con `Depends`; los tests reemplazan la base de datos con `dependency_overrides`.
- **404 y no 403 al pedir tareas de otro usuario:** no revela que esas tareas existen.
- **Mismo error para usuario inexistente y contraseña incorrecta:** no revela qué usuarios existen.
- **SECRET_KEY obligatoria por variable de entorno:** la app no arranca sin ella en vez de usar una clave por defecto.
- **SQLite y no PostgreSQL:** suficiente para un proyecto de un solo servicio; cambiar a PostgreSQL es cambiar `DATABASE_URL`.
- **Contenedor con usuario sin privilegios y datos en un volumen:** los datos persisten entre reinicios y el contenedor corre con menos permisos.

## Resultados / métricas

19 tests automatizados (CRUD, validación, autenticación y aislamiento entre usuarios).

## Qué mejoraría con más tiempo

- Migraciones con Alembic
- Refresh tokens
- Paginación y filtros en `GET /tasks` (por ejemplo `?completed=true`)
- PostgreSQL
- Despliegue público
- Medir cobertura de tests

## Autor

Leandro · [GitHub](https://github.com/DHat3r)
