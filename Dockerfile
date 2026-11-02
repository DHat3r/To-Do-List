# Imagen base oficial de Python. "slim" trae lo mínimo: pesa ~5 veces menos que la completa.
FROM python:3.14-slim

# No generar .pyc (inútiles en un contenedor) y mostrar los logs al instante.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Primero solo las dependencias: esta capa queda en caché y no se reinstala
# cada vez que cambias el código, solo cuando cambia requirements.txt.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Correr como un usuario sin privilegios: si alguien explota la app,
# no es root dentro del contenedor.
RUN useradd --create-home appuser && mkdir /code/data && chown appuser /code/data
USER appuser

# La base de datos vive en /code/data, que docker-compose monta como volumen
# para que las tareas sobrevivan al borrar el contenedor.
ENV DATABASE_URL=sqlite:////code/data/tasks.db

EXPOSE 8000

# --host 0.0.0.0: escuchar en todas las interfaces. Con 127.0.0.1 (el valor
# por defecto) solo aceptaría conexiones desde dentro del propio contenedor.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
