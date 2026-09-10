# Tanda de penales: Regla 10 de IFAB

La implementación de la tanda de penales sigue la
[Regla 10 de las Reglas de Juego de IFAB](https://www.theifab.com/laws/latest/determining-the-outcome-of-a-match/).

## Jugadores habilitados

La tanda no se limita a una lista previamente cerrada de cinco lanzadores. Son
elegibles los jugadores que permanecen en el terreno de juego al finalizar el
partido, incluidos quienes se encuentren temporalmente fuera por lesión o por
ajustar su equipamiento. Un jugador expulsado no puede participar.

Cuando un equipo tiene más jugadores habilitados que el contrario, debe excluir
exactamente la diferencia. Los jugadores excluidos no pueden lanzar. Matchday
recibe esas exclusiones mediante `equalization_excluded_player_ids` y conserva
el conjunto definitivo en `PenaltyShootoutParticipant`.

Ejemplo: si un equipo termina con once jugadores habilitados y el otro con diez,
el primero debe indicar exactamente un jugador excluido.

La igualdad también debe conservarse durante la tanda. Si un participante queda
fuera definitivamente por lesión o expulsión, el rival debe excluir un jugador
habilitado en la misma operación. Matchday registra esta reducción mediante:

```text
POST /api/matches/{id}/penalty-shootout/participants/reduce
```

El request identifica al jugador que quedó fuera, el motivo (`injury` o
`sent_off`) y el jugador contrario excluido para compensar. Los dos permanecen
en el historial con su motivo y fecha de inhabilitación. Mientras las cantidades
no sean iguales, no se permite registrar otro lanzamiento.

Un jugador excluido no es un suplente general. La sustitución excepcional de un
portero que no pueda continuar se modelará de manera independiente.

## Orden y desarrollo

- `starting_team_side` identifica al equipo que ejecuta el primer lanzamiento.
- Los equipos lanzan alternativamente.
- Cada equipo dispone inicialmente de cinco lanzamientos, salvo que exista una
  victoria matemática anticipada.
- Todos los jugadores habilitados de un equipo deben lanzar antes de que alguno
  pueda ejecutar un segundo lanzamiento.
- Si continúa el empate después de cinco lanzamientos por equipo, comienza la
  muerte súbita. El ganador solo se decide después de que ambos hayan completado
  la misma cantidad de lanzamientos.
- Una vez decidido el ganador, no se admiten nuevos lanzamientos.

Los cinco lanzamientos iniciales no implican que solamente cinco jugadores
estén habilitados. Si la tanda continúa, deben participar los demás jugadores
habilitados antes de repetir un lanzador.

## Estado persistido

La base de datos conserva el equipo que comenzó, los participantes habilitados,
cada lanzamiento, los marcadores, los contadores, el ganador y el estado de la
tanda. `next_team_side` se calcula a partir del equipo inicial y de los
contadores, y solo existe mientras la tanda está en progreso.

Documento oficial consultado el 7 de septiembre de 2026.
