# Diagramas de Matchday

La colección conserva un diagrama por perspectiva útil. Los contratos HTTP se
documentan en OpenAPI y en la documentación de cada módulo para evitar mantener
diagramas que repitan esa información.

## Arquitectura

- [Contexto del sistema](architecture.puml): nivel 1 de C4; personas, Matchday y
  sistemas externos.
- [Contenedores](architecture/containers.puml): nivel 2 de C4; frontend, backend,
  procesos independientes y almacenamiento.
- [Despliegue Docker](architecture/deployment-docker.puml): servicios, workers y
  volúmenes de la composición local.
- Componentes por módulo, nivel 3 de C4:
  - [Teams](architecture/modules/teams.puml).
  - [Matches](architecture/modules/matches.puml).
  - [News](architecture/modules/news.puml).
  - [Tournaments](architecture/modules/tournaments.puml).
  - [Recommendations](architecture/modules/recommendations.puml).

Estos diagramas usan C4-PlantUML mediante `<C4/C4_Context>`,
`<C4/C4_Container>` y `<C4/C4_Component>`.

## Dominio

- [Equipos](domain/teams.puml): equipos, jugadores y capitán habitual.
- [Partidos](domain/matches.puml): núcleo, convocatoria, eventos, estadísticas y
  tanda de penales.
- [Noticias](domain/news.puml): equipo opcional, contenido y estados.
- [Torneos](domain/tournaments.puml): temporadas, fases, grupos, inscripciones y
  relación con Match.
- [Recomendaciones](domain/recommendations.puml): visitante, actividad, perfil y
  snapshot.

## Casos de uso

- [Equipos](use-cases/teams.puml): comandos y consultas de equipos y jugadores.
- [Partidos](use-cases/matches.puml): ciclo, eventos, estadísticas, tanda y consultas.
- [Noticias](use-cases/news.puml): gestión editorial, consulta y publicación programada.
- [Torneos](use-cases/tournaments.puml): configuración, clasificación y cuadro.
- [Recomendaciones](use-cases/recommendations.puml): captura, consulta y procesamiento.

## Estados y comprobación

- [Ciclo de noticias](news-lifecycle.puml): transiciones DRAFT, SCHEDULED y PUBLISHED.
- [Testing](../testing.md): comandos de verificación y escenarios cubiertos.

Los actores son roles funcionales, no permisos implementados.

## Reloj en tiempo real

- `design/match-clock-domain.puml`: estado persistido, snapshot y monitor V5.
- `design/match-clock-sequence.puml`: flujo entre operador, API, monitor, Redis
  y clientes WebSocket.

## Avance de torneos

- [Generación y avance](design/tournament-advancement.puml): creación transaccional,
  resultados confirmados, siguiente ronda, tercer puesto y reintentos.

## Recomendaciones

- [Secuencia](design/recommendations-sequence.puml): visita, pings y worker.
- [Contrato y operación](../recommendations.md): endpoints, cookies y respuestas.
