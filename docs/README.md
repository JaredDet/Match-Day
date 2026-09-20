# Documentación del backend

- [Noticias](news.md): contenido, endpoints, estados, portadas y publicación programada.
- [Torneos](tournaments.md): temporadas, inscripción de equipos, fases, grupos y partidos.
- [Testing](testing.md): pruebas por módulo y capa, regresiones y verificaciones.
- [Diagramas](diagrams/README.md): arquitectura, dominio, casos de uso y contratos API.
- [Reloj de partidos](match-clock-design.md): snapshots, monitor y WebSocket.
- [Tandas de penales](penalty-shootout-rules.md): reglas del dominio.

La referencia completa de campos y respuestas se genera desde los contratos en
`/api/schema/` y se consulta en `/api/docs/`.
