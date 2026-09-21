# Diagramas de Matchday

Los archivos de la raíz son vistas generales. El detalle está dividido por
responsabilidad para evitar diagramas que mezclen todo el sistema.

## Arquitectura

- `architecture.puml`: módulos, capas y dependencias principales.

## Dominio

- `domain/teams.puml`: equipos, jugadores y capitán habitual.
- `domain/match-core.puml`: partido, convocatoria, formación y sustituciones.
- `domain/match-events.puml`: eventos que forman la cronología.
- `domain/match-statistics.puml`: estadísticas acumuladas por equipo.
- `domain/penalty-shootout.puml`: tanda, lanzamientos y participantes.
- [Noticias](domain/news.puml): equipo opcional, contenido y estados.
- [Torneos](domain/tournaments.puml): temporadas, fases, grupos, inscripciones y relación con Match.

## Casos de uso

- `use-cases/teams.puml`: comandos y consultas de equipos y jugadores.
- `use-cases/match-lifecycle.puml`: configuración y ciclo del partido.
- `use-cases/match-events.puml`: registro y corrección de eventos.
- `use-cases/match-queries.puml`: listados y detalles públicos.
- `use-cases/penalty-shootout.puml`: operaciones de la tanda.
- [Noticias](use-cases/news.puml): gestión editorial, consulta y publicación programada.
- [Torneos](use-cases/tournaments.puml): configuración, clasificación y cuadro.

## Entradas y salidas

- `api/teams.puml`: endpoints de equipos y jugadores.
- `api/match-lifecycle.puml`: endpoints que controlan el partido.
- `api/match-events.puml`: endpoints de eventos y estadísticas.
- `api/match-queries.puml`: respuestas de consulta.
- [Noticias](api/news.puml): creación, edición, filtros y acciones de publicación.
- [Torneos](api/tournaments.puml): recursos, asociaciones y lecturas para la UI.

## Estados y comprobación

- [Ciclo de noticias](news-lifecycle.puml): transiciones DRAFT, SCHEDULED y PUBLISHED.
- [Testing](../testing.md): comandos de verificación y escenarios cubiertos.

Los actores son roles funcionales, no permisos implementados. Las vistas generales
`architecture.puml`, `domain-model.puml`, `use-cases.puml` e `inputs-outputs.puml`
incluyen equipos, partidos, noticias y torneos.

## Reloj en tiempo real

- `design/match-clock-domain.puml`: estado persistido, snapshot y monitor V5.
- `design/match-clock-sequence.puml`: flujo entre operador, API, monitor, Redis
  y clientes WebSocket.

## Avance de torneos

- [Generación y avance](design/tournament-advancement.puml): creación transaccional,
  resultados confirmados, siguiente ronda, tercer puesto y reintentos.

## Recomendaciones

- [Dominio](domain/recommendations.puml): visitante, actividad, perfil y snapshot.
- [Casos de uso](use-cases/recommendations.puml): API frente a procesamiento en segundo plano.
- [Entradas y salidas](api/recommendations.puml): GET de visita, ping contextual, consulta y borrado.
- [Secuencia](design/recommendations-sequence.puml): visita, pings y worker.
- [Contrato y operacion](../recommendations.md).
