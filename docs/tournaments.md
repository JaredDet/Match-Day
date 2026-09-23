# Torneos y fases

El módulo `modules.tournaments` administra torneos, temporadas, equipos inscritos,
fases, grupos y cuadros eliminatorios. La UI continúa usando sus datos demo.

Sigue las convenciones del backend: entidades y reglas en `domain`, comandos y
consultas en `application`, repositorios de escritura y lectura en `infrastructure`,
y contratos request/response y ViewSets en `api`. `models.py` exporta las entidades;
`TournamentsModule` registra las dependencias. Las consultas devuelven DTOs.

## Entidades

| Entidad | Responsabilidad |
| --- | --- |
| `Tournament` | Slug, nombre, país, categoría, emblema opcional y capacidad de grupos |
| `Season` | Edición (por ejemplo `2026` o `2026/27`) y equipos inscritos |
| `Phase` | Grupos, ronda eliminatoria o tercer puesto; orden y estado |
| `Group` | Grupo A, B, etc. y orden de desempate registrado |
| `GroupEntry` | Inscripción de un equipo en un grupo de una fase |
| `Fixture` | Asociación de un `Match` con fase, grupo opcional, jornada y posición |

`Fixture.match` es OneToOne: un partido tiene como máximo una asociación al torneo.
Los marcadores, estadísticas y penales pertenecen a Match. Las referencias usan
PROTECT. Eliminar una asociación nunca elimina el partido.

Las fases generadas incluyen `generated`, `source_phase`, `scheduled_at` y
`expected_matches`. La fase de origen permite obtener ganadores o perdedores de
semifinales. Las rondas futuras existen antes de que se conozcan sus participantes;
sus partidos se crean cuando la ronda anterior está resuelta.

## Creación y consultas de estructura

Todas las rutas usan el prefijo `/api/` y barra final. Cada recurso admite POST,
GET de listado y GET de detalle. El detalle del torneo usa slug; los demás, UUID.
POST devuelve `201 {"id": "UUID"}`. Los errores de contrato devuelven 400; las
entidades inexistentes, 404; los conflictos de estructura o duplicados, 409.

| Recurso | Campos de creación | Filtro de listado |
| --- | --- | --- |
| `tournaments/` | `slug`, `name`, `country`, `category`, `max_teams_per_group?` | ninguno |
| `tournament-seasons/` | `tournament`, `name`, `teams?` (UUID[]) | `tournament` |
| `tournament-phases/` | `season`, `name`, `kind`, `order`, `matchdays?`, `qualifying_teams?`, `status?` | `season` |
| `tournament-groups/` | `phase`, `name` | `phase` |
| `tournament-group-entries/` | `group`, `team` | `group` |
| `tournament-fixtures/` | `phase`, `group?`, `match`, `position`, `matchday?` | `phase` |

`kind` admite `groups`, `knockout` y `third_place`. El orden es único por temporada;
la posición de partido es única por fase, incluso entre grupos diferentes. El
tercer puesto admite un partido en posición 1. La jornada está entre 1 y `matchdays`.
Una asociación de grupos exige que ambos equipos pertenezcan al grupo; en una
eliminatoria ambos deben estar inscritos en la temporada.

## Capacidad e inscripciones

`max_teams_per_group` admite de 1 a 32767. Si se omite, usa
`DEFAULT_MAX_TEAMS_PER_GROUP = 4` de `modules/tournaments/constants.py`. El listado
y detalle devuelven el valor. Se aplica a todos los grupos del torneo, en todas
sus temporadas. La migración asigna 4 a los torneos existentes sin borrar equipos.
Un grupo lleno devuelve `409 tournament_group_full`. Un equipo no puede tener
más de un GroupEntry en la misma fase, aunque sí en otras fases o temporadas.

| Operación | Entrada / resultado |
| --- | --- |
| `POST tournament-seasons/{id}/teams/` | `{team_id}`; añade un equipo existente, 204 |
| `DELETE tournament-seasons/{id}/teams/{team_id}/` | retira un equipo, 204 |
| `DELETE tournament-group-entries/{id}/` | retira una inscripción de grupo, 204 |

Añadir un equipo ya inscrito o retirar uno ausente es idempotente. No se puede
retirar de la temporada un equipo que tenga inscripción de grupo o partidos
asociados. Primero hay que retirar esas dependencias. Tampoco se puede modificar
la inscripción de la temporada después de generar el cuadro.
Para cambiar un equipo de grupo, eliminar su GroupEntry y crear otro. No puede
retirarse del grupo si participa en un partido asociado a él. Cambiar las
inscripciones limpia el orden de desempate registrado para ese grupo.

## Edición y eliminación

| Operación | Campos / condición |
| --- | --- |
| `PATCH tournament-phases/{id}/` | `name?`, `kind?`, `order?`, `matchdays?`, `qualifying_teams?` |
| `PATCH tournament-groups/{id}/` | `name` |
| `PATCH tournament-fixtures/{id}/` | `group?`, `match?`, `position?`, `matchday?` |
| `DELETE tournament-phases/{id}/` | sin grupos ni asociaciones dependientes |
| `DELETE tournament-groups/{id}/` | sin inscripciones ni partidos asociados |
| `DELETE tournament-fixtures/{id}/` | conserva el Match |
| `PUT tournament-phases/{id}/status/` | `{status: scheduled, live o finished}` |

Las mutaciones devuelven 204. La edición y eliminación de estructura exige fase
`scheduled`, sin partidos iniciados, sin rondas dependientes y no generada.
No se cambia el tipo de una fase ni se reduce su número de jornadas mientras tenga
estructura dependiente. Una asociación editada vuelve a validar equipos y grupo;
el Match nuevo debe estar programado. La fase de una asociación no se cambia:
para moverla, eliminarla y crearla en la fase de destino.

Las rondas generadas estón protegidas frente a la edición y eliminación manual:
el avance controla sus participantes y estados. Tampoco se permite reabrir o
cambiar el estado de una fase que alimenta un cuadro existente. Los metadatos del
torneo y la temporada no tienen endpoints de edición/borrado en esta versión.

Las escrituras bloquean la temporada antes de modificar su estructura. Las
operaciones sobre estructura en uso tambión bloquean los partidos consultados.
Los bloqueos de filas se aplican en PostgreSQL; SQLite no ofrece la misma garantía
para escritores concurrentes.

## Clasificación y desempates

Solo cuentan los partidos finalizados del grupo: victoria 3 puntos y empate 1.
Los criterios, en orden, son:

1. Puntos totales.
2. Diferencia de goles total.
3. Goles a favor totales.
4. Puntos, diferencia y goles a favor de una mini-tabla entre los equipos que
   siguen empatados en los tres primeros criterios. Se calcula una sola vez.
5. Victorias totales.
6. Menor penalización disciplinaria: amarillas + 3 × rojas, usando los contadores
   de los partidos finalizados.
7. Orden explícito de desempate registrado por el organizador.

Para registrar el resultado de un sorteo o decisión de desempate:

```text
PUT /api/tournament-groups/{id}/tie-break/
{"team_ids": ["UUID primero", "UUID segundo", "..."]}
```

Debe incluir exactamente una vez todos los equipos del grupo; GET del grupo
expone `tie_break_order`. Este orden solo se aplica después de los criterios
deportivos, no permite alterar puntos ni saltarse un criterio previo. Una fase
que ya alimenta un cuadro no permite cambiar este orden.

Si persiste un empate, las filas afectadas muestran `tie_break_required: true` y
no se marcan como clasificadas. El UUID solo estabiliza la presentación; no resuelve
la clasificación deportiva. La generación desde grupos se bloquea si alguno de
los puestos seleccionados sigue empatado. `qualified` se marca cuando la fase
está cerrada, el puesto está entre los primeros `qualifying_teams` y está resuelto.

## Generación de eliminatorias

```text
POST /api/tournament-seasons/{id}/generate-bracket/
```

```json
{
  "starts_at": "2026-10-01T18:00:00Z",
  "team_ids": ["UUID cabeza de serie 1", "UUID cabeza de serie 2"],
  "round_interval_days": 7,
  "third_place": true
}
```

Indicar **solo uno** de `team_ids` o `source_phase_id`. El primero establece la
lista de cabezas de serie explícitamente. El segundo toma los clasificados de una
fase de grupos de la misma temporada: debe estar finalizada, tener partidos,
todos ellos finalizados, y cada participante debe haber jugado. Cada grupo debe
aportar sus `qualifying_teams`, sin desempates pendientes en esos puestos.
La completitud se comprueba sobre los partidos registrados; el módulo no genera
ni verifica un calendario de todos contra todos.

Se admiten 2, 4, 8, 16, 32 o 64 equipos únicos e inscritos. Desde grupos, las
cabezas se ordenan primero por puesto y después por nombre/ID de grupo. La primera
ronda enfrenta primero con último, segundo con penúltimo, etc.; las siguientes
emparejan ganadores de posiciones consecutivas. No hay sorteo aleatorio ni byes.

La fecha de cada ronda se separa por `round_interval_days` (1–365, defecto 7).
`third_place` vale true por defecto y crea un tercer puesto solo con 4 o más
equipos; se juega en la fecha de la final. Se crean las fases y los partidos de
la primera ronda en una sola transacción. La respuesta es `201 {phase_ids: [...]}`.
No se permite generar otro cuadro si ya hay fases eliminatorias en la temporada.
Un conflicto de partido o validación revierte toda la generación.

## Avance automático y recuperación

Al guardar un partido iniciado o finalizado, o una tanda finalizada, el módulo
programa una revisión del cuadro **después del commit**. Solo procesa cuadros
generados. Una ronda avanza cuando tiene su número esperado de partidos y todos
estón finalizados con ganador. En empate requiere una tanda con estado `finished`
y ganador declarado. No usa marcadores provisionales ni el UUID para avanzar.

El backend crea los partidos de la ronda siguiente con los ganadores. Desde las
semifinales tambión crea el tercer puesto con los perdedores. Las fases generadas
pasan a `live` cuando tienen partidos iniciados y a `finished` cuando todos tienen
ganador. La creación es transaccional e idempotente.

```text
POST /api/tournament-seasons/{id}/advance-bracket/
Respuesta 200: {"created_matches": 0}
```

Esta acción permite reintentar o reconciliar tras un fallo del callback. Si no
hay una ronda lista devuelve cero; si no hay cuadro generado devuelve 404.
Un cambio en resultados de origen incompatible con cruces ya creados devuelve
`409 tournament_advancement_conflict` y no reescribe la ronda siguiente.

El callback es síncrono después del commit, no una cola durable: si falla, registra
el error y mantiene el resultado del partido. Reintentar con `advance-bracket`.
Las escrituras mediante `QuerySet.update`, bulk operations o SQL directo no emiten
estas señales y requieren ejecutar la reconciliación explícita.

## Lecturas para la UI

- `GET tournaments/{slug}/seasons/`: temporadas disponibles.
- `GET tournament-phases/?season={id}`: fases ordenadas, origen y datos de generación.
- `GET tournament-seasons/{id}/matches/`: asociaciones, con IDs de Match consultables
  en la API de partidos.
- `GET tournament-seasons/{id}/groups/`: grupos y filas con `id`, `w`, `d`, `l`, `gf`,
  `ga`, `played`, `goal_difference`, `points`, `qualified` y, si corresponde,
  `tie_break_required`.
- `GET tournament-seasons/{id}/bracket/`: `{rounds, third}`. Una ronda contiene
  `id`, `name`, `ties`. Un cruce contiene `id` de Match, `home`, `away`, `homeScore`,
  `awayScore` y opcionalmente `penalties: [local, visita]`. Los programados tienen
  marcadores null. Las rondas pendientes tienen `ties: []`; `third` es null hasta
  que exista el partido.

## Verificación

```sh
uv run python manage.py migrate
uv run pytest tests/modules/tournaments
```

Ver [testing](testing.md), [dominio](diagrams/domain/tournaments.puml),
[casos de uso](diagrams/use-cases/tournaments.puml),
[secuencia de avance](diagrams/design/tournament-advancement.puml).
Los contratos tambión estón en `/api/docs/`.
