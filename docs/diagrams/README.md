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

## Casos de uso

- `use-cases/teams.puml`: comandos y consultas de equipos y jugadores.
- `use-cases/match-lifecycle.puml`: configuración y ciclo del partido.
- `use-cases/match-events.puml`: registro y corrección de eventos.
- `use-cases/match-queries.puml`: listados y detalles públicos.
- `use-cases/penalty-shootout.puml`: operaciones de la tanda.

## Entradas y salidas

- `api/teams.puml`: endpoints de equipos y jugadores.
- `api/match-lifecycle.puml`: endpoints que controlan el partido.
- `api/match-events.puml`: endpoints de eventos y estadísticas.
- `api/match-queries.puml`: respuestas de consulta.

## Reloj en tiempo real

- `design/match-clock-domain.puml`: estado persistido, snapshot y monitor V5.
- `design/match-clock-sequence.puml`: flujo entre operador, API, monitor, Redis
  y clientes WebSocket.
