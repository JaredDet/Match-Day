# Testing del backend

Ejecutar desde la raíz de `matchday`, después de `uv sync --locked --dev`.
Pytest usa `config.settings` y una base de pruebas; no ejecutar seeds o monitores
contra la base de desarrollo para comprobar regresiones.

```sh
uv run pytest
uv run pytest tests/modules/news tests/modules/tournaments
uv run pytest tests/modules/recommendations
uv run pytest tests/core/test_dependency_injector.py
```

## Cobertura funcional

Noticias distingue listado (`preview`, primer párrafo no vacío, texto plano de
hasta 200 caracteres) y detalle (`content` completo). Las pruebas cubren formato,
entidades HTML, espacios, contenido vacío, límite exacto, recorte con elipsis,
Unicode y ausencia del cuerpo completo en el listado.

| Módulo / capa | Comprobaciones |
| --- | --- |
| News / dominio | normalización, borrador, programación, cancelación, publicación y restricciones de edición/borrado |
| News / aplicación | referencias a equipos, parser, comandos, consultas y publicación de noticias vencidas |
| News / infraestructura | persistencia, filtros, orden, lecturas y restricción de título |
| News / API | creación, lectura, filtros, edición, acciones, errores y portada omitida frente a null |
| News / management | intervalos del monitor, `--once`, errores e idempotencia del seed sin modificar partidos ni jugadores |
| Tournaments / dominio | configuración y estado de fases, pertenencia de grupo, equipos elegibles, posición del tercer puesto y jornada |
| Tournaments / aplicación | rechazo de temporada con referencias inexistentes y consulta de clasificación de temporada inexistente |
| Tournaments / infraestructura | conflictos de slug y recuperación de transacción; DTOs inmutables, lectura de penales y serialización sin consultas extra |
| Tournaments / API | ciclo de creación por inyector, grupos, fixtures, final y tercer puesto, fechas/temporadas aisladas, duplicados y errores 400/404/409 |
| Tournaments / clasificación | solo finalizados, victorias locales y visitantes, empates, puntos, actualización de resultados y clasificación al cerrar fase |
| Tournaments / gestión | altas/bajas idempotentes, dependencias, edición validada, eliminación que conserva Match y bloqueos con partidos iniciados |
| Tournaments / generación | 2–64 participantes, rollback, clasificados de grupos, empates pendientes, avance tras commit, penales, final y tercer puesto, reintentos y correcciones conflictivas |
| Tournaments / desempates | mini-tabla de enfrentamientos directos, disciplina, empate sin resolver y orden manual como último criterio |
| Recommendations / dominio | recencia, afinidad por relaciones, descubrimiento y tiempo acumulado |
| Recommendations / API | GET elegibles, cookies firmadas, CSRF, contexto de ping, aislamiento, duplicados y beacon multipart |
| Recommendations / aplicacion | perfiles, snapshots, limites diarios, borrado, retencion, candidatos en lotes y worker --once |
| Core / inyector | resolución de comandos y consultas de todos los módulos |

Para ejecutar una capa concreta:

```sh
uv run pytest tests/modules/tournaments/domain
uv run pytest tests/modules/tournaments/application
uv run pytest tests/modules/tournaments/infrastructure
uv run pytest tests/modules/tournaments/api
uv run pytest tests/modules/news/management
```

Estas pruebas no constituyen cobertura exhaustiva: no hay prueba concurrente de
bloqueos sobre PostgreSQL ni integración con almacenamiento externo de portadas.
La suite utiliza la base configurada por el entorno; la ejecución local habitual
es SQLite. Los límites funcionales de torneos (avance manual y sin edición de
estructura) están descritos en [tournaments.md](tournaments.md).

## Calidad, migraciones y OpenAPI

```sh
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py spectacular --validate --file schema.yml
```

`schema.yml` es una salida de verificación, no un archivo que deba versionarse.
El generador puede advertir sobre nombres de enums compartidos; distinguir estas
advertencias de errores de generación o validación.
El hook pre-push y GitHub Actions ejecutan Ruff y toda la suite, incluyendo
`tests/modules/tournaments` y `tests/modules/news` sin configuración adicional.

## Diagramas

Las fuentes están en [diagrams](diagrams/README.md). Con PlantUML instalado:

```sh
java -jar plantuml.jar -checkonly "docs/diagrams/**/*.puml"
java -jar plantuml.jar -tsvg "docs/diagrams/**/*.puml"
```

Los comandos requieren disponer del JAR de PlantUML; las fuentes `.puml` son los
artefactos mantenidos en el repositorio.
