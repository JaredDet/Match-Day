# Matchday

API para administrar y consultar partidos de fútbol, incluyendo equipos,
jugadores, formaciones, alineaciones, goles y tarjetas.

## Requisitos

- Python 3.11
- [uv](https://docs.astral.sh/uv/)

## Puesta en marcha

Instala las dependencias:

```bash
uv sync
```

Crea la configuración local en PowerShell:

```powershell
Copy-Item .env.example .env
```

En macOS o Linux:

```bash
cp .env.example .env
```

La plantilla activa `DEBUG` y permite `localhost` y `127.0.0.1`. En producción
deben configurarse una clave secreta, los hosts permitidos y
`DJANGO_DEBUG=false`.

Aplica las migraciones:

```bash
uv run python manage.py migrate
```

Inicia el servidor de desarrollo:

```bash
uv run python manage.py runserver
```

La documentación de la API queda disponible en:

```text
http://127.0.0.1:8000/api/docs/
```

## Datos de demostración

Crea cuatro equipos ficticios, sus 44 jugadores y diez partidos: seis
finalizados y cuatro programados. El partido demostrativo principal incluye
estadio, árbitro, formaciones, alineaciones, capitanes habituales, goles y
tarjetas:

```bash
uv run python manage.py seed_demo_match
```

El comando es idempotente: reutiliza los equipos, jugadores y partidos que ya
existan. La salida indica cuántos partidos nuevos se crearon.

Para ejecutar los listados y detalles de partidos, equipos y jugadores y
mostrar sus respuestas como JSON:

```bash
uv run python manage.py show_demo_match
```

`show_demo_match` requiere haber ejecutado primero `seed_demo_match`.

## Recursos principales

- `/api/matches`: partidos, alineaciones, marcador y eventos.
- `/api/teams`: equipos, plantilla y capitán habitual.
- `/api/players`: jugadores, apariciones, goles e historial reciente.

Al configurar una alineación, `captain_id` es opcional. Si se omite, se intenta
usar el capitán habitual. Si no forma parte de los once jugadores, la alineación
queda sin capitán y se registra una advertencia para que el operador la revise;
nunca se elige otro jugador automáticamente.

La especificación completa de requests, filtros y responses está disponible en
la documentación OpenAPI del proyecto.

## Diagramas

Los diagramas PlantUML de la V3 se encuentran en `docs/diagrams`:

- `domain-model.puml`: entidades, relaciones y reglas principales.
- `architecture.puml`: módulos y dependencias entre capas.
- `use-cases.puml`: operaciones disponibles para administradores y espectadores.
- `inputs-outputs.puml`: requests, casos de uso y respuestas de cada operación.
- `match-lifecycle.puml`: estados y operaciones permitidas del partido.

Pueden renderizarse con cualquier extensión o CLI compatible con PlantUML.

## Pruebas y calidad

Ejecuta toda la suite:

```bash
uv run pytest
```

Comprueba formato y reglas de Ruff:

```bash
uv run ruff format --check .
uv run ruff check .
```

Comprueba la configuración de Django y que no falten migraciones:

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

### Verificacion antes de cada push

Instala una sola vez el hook local del repositorio:

```bash
uv run pre-commit install --hook-type pre-push
```

Antes de cada `git push`, el hook comprueba el formato, las reglas de calidad,
las convenciones de nombres de Python y toda la suite de pruebas. Si alguna
comprobacion falla, el push se cancela.

Para ejecutar manualmente las mismas comprobaciones:

```bash
uv run pre-commit run --all-files --hook-stage pre-push
```

GitHub Actions repite las comprobaciones en cada push y pull request.
