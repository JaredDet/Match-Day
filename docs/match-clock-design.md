# Reloj oficial del partido

El servidor es la fuente de verdad del reloj. No persiste un contador cada
segundo: conserva el inicio del periodo, el tiempo añadido anunciado, el cierre
del periodo y una versión. Con esos datos calcula un snapshot usando la hora UTC
del servidor.

## Flujo

1. `StartMatchUseCase` inicia el partido y el reloj del primer tiempo.
2. `SetMatchPeriodAddedTimeUseCase` anuncia o corrige el tiempo añadido.
3. `EndMatchPeriodUseCase` cierra el periodo cuando alcanzó su límite anunciado.
4. `StartMatchPeriodUseCase` inicia el segundo tiempo o un tiempo suplementario.
5. La tanda de penales y el cierre del partido mantienen sus casos de uso.

El reloj de fútbol no se pausa. Tampoco existe un comando independiente para
detenerlo: cerrar el periodo congela el reloj. Alcanzar el deadline genera un
aviso, pero nunca cambia de periodo automáticamente; la decisión sigue siendo
del árbitro y el operador la confirma.

## Snapshot

Cada `GET /api/matches` y `GET /api/matches/{id}` incluye:

```json
{
  "clock": {
    "period": "second_half",
    "status": "running",
    "minute": 73,
    "second": 18,
    "added_minute": 0,
    "elapsed_seconds": 1698,
    "remaining_seconds": 1002,
    "deadline_at": "2026-09-13T20:15:00Z",
    "announced_added_minutes": 0,
    "version": 3,
    "as_of": "2026-09-13T19:58:18Z"
  }
}
```

El cliente puede avanzar visualmente desde `as_of`, pero ese cálculo es solo
provisional. Al recibir otro snapshot prevalece la versión mayor y, para una
misma versión, el `as_of` más reciente.

## Sincronización en segundo plano

`run_match_clock_monitor` revisa todos los relojes activos cada 30 segundos:

- calcula el snapshot oficial sin escribir el minuto en la base de datos;
- publica una corrección por WebSocket;
- avisa al alcanzar el tiempo reglamentario cuando hay añadido;
- avisa al alcanzar el deadline final;
- nunca finaliza ni cambia el periodo automáticamente.

Las marcas `regulation_time_alerted_at` y `period_deadline_alerted_at` hacen que
cada aviso se emita una sola vez. Cambiar el tiempo añadido incrementa
`clock_version` y habilita un nuevo aviso de deadline.

## WebSocket

Cada partido expone:

```text
ws://HOST/ws/matches/{match_id}/clock/
```

Al conectar se entrega un snapshot inmediatamente. Después se reciben mensajes
`match.clock.snapshot` y `match.clock.alert`.

El canal en memoria sirve para pruebas o un único proceso. Para comunicar el
servidor ASGI con el monitor independiente debe configurarse `REDIS_URL`; Redis
es el bus entre ambos procesos.
