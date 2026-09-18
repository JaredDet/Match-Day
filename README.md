# Matchday

API para administrar y consultar partidos de fútbol, incluyendo equipos,
jugadores, formaciones, alineaciones y una cronología completa de eventos.

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

Crea cuatro equipos ficticios, sus 64 jugadores, quince partidos y siete
noticias. Los partidos demostrativos incluyen ocho finalizados, tres en vivo y
cuatro programados, además de estadio, árbitro, directores técnicos,
formaciones, alineaciones, capitanes habituales, goles, autogoles, asistencias,
tarjetas, sustituciones, lesiones, penales, VAR, faltas, tiros de esquina,
fueras de juego, tiros, atajadas y posesión.

Las noticias demostrativas incluyen noticias publicadas, programadas y en
borrador, tanto asociadas a equipos como de carácter general.

## Para crear los datos de partidos:

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

## Para crear los datos de noticias:

```bash
uv run python manage.py seed_demo_news
```

El comando es idempotente: reutiliza las noticias que ya existan y crea las que
falten.

## Recursos principales

- `/api/matches`: partidos, alineaciones, marcador y eventos.
- `/api/teams`: equipos, plantilla y capitán habitual.
- `/api/players`: jugadores, apariciones, goles e historial reciente.
- `/api/news`: creación, consulta, edición, programación, publicación y
  eliminación de noticias.

Las noticias pueden ser generales o estar asociadas a un equipo. Su ciclo de
vida contempla los estados DRAFT, SCHEDULED y PUBLISHED.

Al configurar una alineación, captain_id es opcional. Si se omite, se intenta
usar el capitán habitual. Si no forma parte de los once jugadores, la alineación
queda sin capitán y se registra una advertencia para que el operador la revise;
nunca se elige otro jugador automáticamente.

La especificación completa de requests, filtros y responses está disponible en
la documentación OpenAPI del proyecto.

## Reglas de dominio

La selección de jugadores, alternancia, rotación, victoria anticipada y muerte
súbita de las tandas están documentadas en
[`docs/penalty-shootout-rules.md`](docs/penalty-shootout-rules.md). La
implementación sigue la Regla 10 de las Reglas de Juego de IFAB.

## Diagramas

Los diagramas PlantUML de la V5 se encuentran en `docs/diagrams`. Las vistas
generales se complementan con diagramas pequeños por responsabilidad:

- `domain-model.puml`: vista general y rutas hacia los modelos detallados.
- `architecture.puml`: módulos y dependencias entre capas.
- `use-cases.puml`: vista general y rutas hacia los casos de uso detallados.
- `inputs-outputs.puml`: vista general de contratos de entrada y salida.
- `match-lifecycle.puml`: estados y operaciones permitidas del partido.

El índice [`docs/diagrams/README.md`](docs/diagrams/README.md) enlaza los
diagramas detallados de dominio, casos de uso, API y el reloj en tiempo real.

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

## Reloj en tiempo real

Cada consulta de partidos devuelve un snapshot calculado con la hora del
servidor. Para emitir correcciones y alertas por WebSocket, configura Redis:

```env
REDIS_URL=redis://localhost:6379/0
```

Ejecuta el servidor ASGI y el monitor en terminales separadas:

```bash
uv run python manage.py runserver
uv run python manage.py run_match_clock_monitor
```

El monitor se ejecuta cada 30 segundos. Para una sola revisión operativa o de
diagnóstico:

```bash
uv run python manage.py run_match_clock_monitor --once
```

Los clientes se conectan a `ws://HOST/ws/matches/{match_id}/clock/`. El diseño,
el formato del snapshot y la estrategia de reconexión están documentados en
[`docs/match-clock-design.md`](docs/match-clock-design.md).
