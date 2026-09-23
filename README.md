# Matchday

API para administrar y consultar partidos de fútbol, incluyendo equipos,
jugadores, formaciones, alineaciones, noticias, torneos y una cronología completa de eventos.

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

Para conectar el frontend Nuxt desde otro origen, configura sus orígenes en
`DJANGO_CORS_ALLOWED_ORIGINS` y `DJANGO_CSRF_TRUSTED_ORIGINS`. Las peticiones
que usen las cookies anónimas de recomendaciones deben enviar credenciales. En
desarrollo, Django sirve las portadas de noticias desde `/media/`; en producción
esa ruta debe publicarla el servidor web o el almacenamiento de archivos.

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

## Docker

Desde este repositorio se puede levantar la solución completa, incluido el
frontend hermano `../matchday-ui`:

```bash
docker compose up --build
```

Quedan disponibles el frontend en `http://localhost:3000`, la API en
`http://localhost:8000/api/` y Swagger en `http://localhost:8000/api/docs/`.
La composición crea PostgreSQL y Redis con volúmenes persistentes, aplica las
migraciones, carga los seeds idempotentes y arranca por separado el monitor del
reloj, el publicador de noticias y el worker de recomendaciones.

Para detener los contenedores conservando los datos:

```bash
docker compose down
```

Para reiniciar completamente la base, Redis y los archivos multimedia demo:

```bash
docker compose down --volumes
```

## Datos de demostración

Crea cuatro equipos ficticios con escudos, sus 64 jugadores, quince partidos,
siete noticias con portada y una Copa Matchday completa. Los partidos
demostrativos incluyen ocho finalizados, tres en vivo y
cuatro programados, además de estadio, árbitro, directores técnicos,
formaciones, alineaciones, capitanes habituales, goles, autogoles, asistencias,
tarjetas, sustituciones, lesiones, penales, VAR, faltas, tiros de esquina,
fueras de juego, tiros, atajadas y posesión.

Las noticias demostrativas incluyen noticias publicadas, programadas y en
borrador, tanto asociadas a equipos como de carácter general.

Para preparar partidos, equipos, recursos visuales, temporada, grupos y
eliminatorias en una sola ejecución:

```bash
uv run python manage.py seed_demo_tournament
uv run python manage.py seed_demo_news
```

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
- `/api/tournaments/`: torneos y temporadas por slug.
- `/api/tournament-seasons/`: equipos inscritos, clasificación, cuadro y partidos de una edición.
- `/api/tournament-phases/`, `/api/tournament-groups/`,
  `/api/tournament-group-entries/`, `/api/tournament-fixtures/`: etapas, grupos,
  inscripción por grupo y asociación con partidos existentes.

Las noticias pueden ser generales o estar asociadas a un equipo. Su ciclo de
vida contempla los estados DRAFT, SCHEDULED y PUBLISHED.

El [índice de documentación](docs/README.md) reúne las guías de
[noticias](docs/news.md), [torneos](docs/tournaments.md) y [testing](docs/testing.md).
La publicación programada requiere ejecutar `publish_scheduled_news` aparte del
servidor, o `publish_scheduled_news --once` desde un planificador.

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

Los diagramas PlantUML se encuentran en `docs/diagrams` y están separados por
nivel de arquitectura y módulo:

- `architecture.puml`: contexto del sistema (C4 nivel 1).
- `architecture/containers.puml`: aplicaciones y almacenes (C4 nivel 2).
- `architecture/modules/*.puml`: componentes internos por módulo (C4 nivel 3).
- `domain/*.puml`: un modelo de dominio por módulo.
- `use-cases/*.puml`: un diagrama de casos de uso por módulo.
- `match-lifecycle.puml`: estados y operaciones permitidas del partido.

El índice [`docs/diagrams/README.md`](docs/diagrams/README.md) enlaza los
diagramas de dominio, casos de uso y los flujos complejos.

Pueden renderizarse con cualquier extensión o CLI compatible con PlantUML.

## Pruebas y calidad

Ejecuta toda la suite:

```bash
uv run pytest
```

Para comprobar noticias y torneos, incluidas las pruebas por capa:

```bash
uv run pytest tests/modules/news tests/modules/tournaments
```

La [guía de testing](docs/testing.md) detalla los escenarios cubiertos y los
comandos para comprobar migraciones, OpenAPI y diagramas.

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

## Recomendaciones por comportamiento

El backend registra visitas de detalle mediante encabezados en los GET existentes.
El tiempo activo llega como acumulado con tipo e ID de contenido en pings POST.
Un proceso independiente calcula los perfiles y las recomendaciones:

```sh
uv run python manage.py migrate recommendations
uv run python manage.py run_recommendations_worker
```

Contrato, CSRF, cookies, envío final con `sendBeacon` y límites en
[docs/recommendations.md](docs/recommendations.md). El frontend consume estos
endpoints mediante su repositorio de recomendaciones.
