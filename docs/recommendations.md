# Recomendaciones por comportamiento

El módulo `recommendations` obtiene intereses de navegación, sin seguir equipos,
marcar intereses ni completar formularios. Funciona con visitantes anónimos. No
hay vinculación con cuentas ni recomendaciones colaborativas entre usuarios todavía.
El frontend demo conserva su funcionamiento local; este cambio no lo conecta a la API.

## Modelo y separación

| Elemento | Persistencia / responsabilidad |
| --- | --- |
| `Visitor` | UUID anónimo, última actividad, versión recibida/procesada y próxima actualización |
| `NavigationActivity` | Referencia al contenido, UUID de visita, fecha UTC, si cuenta como visita y segundos activos acumulados |
| `ContentReference` | Objeto de valor con tipo e ID; se resuelve contra el módulo propietario |
| `InterestProfile` | Afinidades calculadas por equipo y torneo, con fecha del cálculo |
| `RecommendationSnapshot` | Referencias ordenadas, puntuaciones y motivos por sección, generación y vencimiento |

Noticias, equipos y partidos no se copian. El repositorio de consulta resuelve
las referencias en lotes y vuelve a comprobar la existencia y publicación al
servir el resultado. Una noticia que dejó de estar publicada desaparece incluso
si figuraba en un snapshot. La respuesta contiene `preview`, no el cuerpo completo.

Las reglas de tiempo y puntuación están en dominio; los casos de uso coordinan
repositorios y transacciones. El middleware registra la consulta ya resuelta;
el comando de management solo planifica los casos de uso.
Los límites de navegación pertenecen a `NavigationPolicy`. Los repositorios de
escritura están separados de los de consulta; `GetRecommendationsQuery` devuelve
DTOs inmutables que los contratos serializan sin nuevas consultas a la base.

## Visitas en GET existentes

Solo se observan los GET de detalle de equipos, jugadores, noticias publicadas,
partidos y torneos. Los torneos se consultan por **slug**; la actividad guarda el
UUID del torneo que devolvió esa consulta. No hay endpoint POST para crear visitas.

```http
GET /api/teams/{uuid}/
X-Navigation-Intent: detail-view
X-Navigation-Id: 1c47c1e7-c363-41a2-b216-e514ec9b5a45
```

El frontend genera un UUID nuevo por visita y lo reutiliza en reintentos y pings.
Solo envía estos encabezados cuando muestra efectivamente una página de detalle,
no en polling, precarga ni consultas auxiliares. El backend exige respuesta 200,
referencia existente y contenido elegible. Ignora HEAD, listados, acciones,
respuestas fallidas, UUID inválidos y peticiones marcadas como prefetch mediante
`Purpose`, `Sec-Purpose` o `X-Moz`. No basta con hacer GET para sumar interés.

La primera visita elegible entrega `matchday_visitor`, una cookie **firmada**,
HttpOnly, SameSite=Lax, Secure bajo HTTPS y con duración de treinta días. También
entrega la cookie CSRF para los pings. Las peticiones siguientes deben enviar
cookies. No se acepta un ID de visitante libre en encabezados o cuerpo. Una
cookie inválida no da acceso al historial de otro visitante.

Las peticiones señalizadas llevan `Cache-Control: private, no-store`; los detalles
varían por Cookie y encabezados de navegación. Si un proxy no deja llegar el GET
al servidor, no se registra. El contrato debe respetarse también en ese proxy.
Un fallo del registro se registra en el log y no rompe la consulta de contenido.

## Tiempo activo: ping y envío final

```http
POST /api/recommendations/activity/heartbeat/
Content-Type: application/json
X-CSRFToken: {token de la cookie csrftoken}
Cookie: matchday_visitor=...; csrftoken=...

{
  "navigation_id": "1c47c1e7-c363-41a2-b216-e514ec9b5a45",
  "content_kind": "team",
  "content_id": "a12bbb69-381a-43ba-a545-f116e288a321",
  "active_seconds": 30
}
```

`content_kind` y `content_id` identifican el contenido que se está viendo.
Deben coincidir con la visita creada por el GET; otro tipo o ID devuelve 400.
No se envía una URL completa. Al cambiar de página se utiliza otro UUID de visita.

`active_seconds` es el **total acumulado**, no un incremento. La respuesta es
204. Enviar 30, 30, 15 y 45 deja 45 segundos; reintentos y mensajes fuera de orden
no duplican tiempo. El servidor exige una visita del propietario de la cookie;
devuelve 404 si no existe o caducó. Rechaza valores negativos, fraccionarios,
mayores de 120 o mayores que los segundos transcurridos desde el GET más cinco
segundos de tolerancia. Los campos inválidos producen 400.

Contrato para la futura integración del navegador:

1. Contar tiempo solo con documento visible y actividad de teclado, puntero o
   desplazamiento reciente; detener el contador tras treinta segundos inactivo.
2. Enviar un ping cada **quince segundos** si el acumulado cambió. Pausar en
   segundo plano; no sumar el tiempo oculto al volver.
3. En `visibilitychange` a oculto y `pagehide`, intentar el último envío. Al
   cambiar de ruta también se envía el último acumulado antes de cambiar el UUID.
4. Preferir `sendBeacon` con `FormData` en el envío final, o `fetch` con `keepalive`.
   No depender de `unload` ni asumir que el envío final siempre llegará.
5. Detener el contador enviado en 120 segundos. El servidor también aplica el límite.

Ejemplo de payload para `sendBeacon`, que no permite encabezados personalizados:

```javascript
const data = new FormData()
data.set('navigation_id', navigationId)
data.set('content_kind', contentKind)
data.set('content_id', contentId)
data.set('active_seconds', String(Math.min(120, Math.floor(activeSeconds))))
data.set('csrfmiddlewaretoken', csrfToken)
navigator.sendBeacon('/api/recommendations/activity/heartbeat/', data)
```

El navegador envía cookies en este escenario del mismo origen. `csrfToken` se
lee de `csrftoken`, no de la cookie HttpOnly del visitante. Los pings JSON usan
`X-CSRFToken`. Ambos formatos se comprueban en pruebas. No se desactiva CSRF para
permitir el envío al salir. Para otra topología de despliegue deben configurarse
los orígenes, cookies y proxy correspondientes.

El backend **no puede demostrar** que la pestaña estaba activa: recibe una señal
del cliente y limita su efecto. No guarda teclas, coordenadas, IP, búsquedas ni
formularios. Si el navegador se cierra bruscamente, el último ping recibido queda
guardado; se puede perder el tramo final, no todo el tiempo de la visita.

## Casos de uso

| Caso de uso | Invocador |
| --- | --- |
| `RecordNavigationUseCase` | Middleware después del GET elegible |
| `RecordActiveTimeUseCase` | POST de heartbeat |
| `GenerateRecommendationsUseCase` | Worker; calcula perfil y snapshot en la misma transacción |
| `ProcessRecommendationsUseCase` | Worker; purga, refresca feed general y procesa un lote pendiente |
| `GetRecommendationsQuery` | GET de recomendaciones; lee snapshots, no calcula el perfil del visitante |
| `ClearNavigationHistoryUseCase` | DELETE de historial |
| `PurgeNavigationHistoryUseCase` | Worker; retención de treinta días |

## Cálculo en segundo plano

```sh
uv run python manage.py migrate recommendations
uv run python manage.py run_recommendations_worker
# Una ejecución, útil para un planificador externo:
uv run python manage.py run_recommendations_worker --once --batch-size 100
```

El proceso es independiente del servidor web y no arranca dentro de sus workers.
Por defecto revisa cada sesenta segundos y procesa hasta cien visitantes por
ciclo (`--interval` y `--batch-size`). Debe desplegarse como proceso supervisado
o mediante un planificador con `--once`; no se instala un servicio del sistema.

Los visitantes con cambios se detectan mediante versiones. Sin cambios se
renueva el resultado cada quince minutos; un snapshot vence después de una hora.
Registro, heartbeat, generación y borrado bloquean la fila del visitante dentro
de transacciones. Así no se marca como procesada actividad recibida después del
cálculo ni se recrea un visitante eliminado desde un trabajo pendiente. Los
bloqueos de fila requieren PostgreSQL para concurrencia real; SQLite sirve para
desarrollo y pruebas secuenciales. Operar inicialmente un único worker.

La captura admite hasta doscientas visitas distintas por visitante y día UTC.
El mismo UUID de navegación es idempotente y no puede reutilizarse para otro
contenido. Una recarga con UUID nuevo puede reportar tiempo, pero no añade peso
de visita dentro de treinta minutos. Como máximo cuentan tres visitas del mismo
contenido por día; su tiempo activo suma como máximo dos minutos por día,
incluso si hubo varias pestañas o recargas.

El peso combina visitas contadas y minutos activos. Se reduce a la mitad cada
siete días. Las relaciones de jugadores y noticias aportan interés a equipos;
la inscripción en temporadas relaciona equipos con torneos. Los partidos solo
aportan interés a un torneo cuando tienen un fixture real asociado.

Se combinan afinidad por equipo, afinidad por torneo con factor 0,7, cercanía de
la fecha y un refuerzo para partidos en juego. Se seleccionan hasta cuatro
elementos por sección. Descubrimiento evita repetir las otras secciones y el
contenido visitado, y da preferencia a menor afinidad. No usa otros usuarios.
Los candidatos se acotan a doscientos por consulta de categoría (recientes,
próximos, en vivo o relacionados); los intereses principales también entran en
las consultas para no limitarse al contenido reciente general.

## Consulta y borrado

`GET /api/recommendations/` devuelve:

```json
{
  "personalized": true,
  "generated_at": "2026-09-21T20:00:00Z",
  "expires_at": "2026-09-21T21:00:00Z",
  "news": [],
  "matches": [],
  "tournaments": [],
  "discovery": []
}
```

Cada elemento contiene `kind`, `id`, `title`, `endpoint`, `preview`, `score` y
`reason`. Motivos: `team_interest`, `tournament_interest`, `recent_content`,
`live_match`, `discovery`. `endpoint` apunta al detalle del backend. Si aún no
hay snapshot personal válido, se utiliza el general. Antes de la primera
ejecución del worker se consulta contenido general acotado, sin crear un perfil
ni registrar una visita a «Para ti». En ese caso las fechas son null.

`DELETE /api/recommendations/history/`, con CSRF, borra visitante, actividad,
perfil y snapshot personal, y elimina la cookie. Es idempotente. Las visitas
posteriores comienzan un historial nuevo. GET no borra ni recalcula historiales.
Las respuestas del módulo son privadas y no almacenables en cachés compartidas.

## Verificación

```sh
uv run pytest tests/modules/recommendations
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py spectacular --validate --file schema.yml
```

Se comprueban los cinco detalles GET, prefetch/HEAD/errores, cookies, aislamiento,
CSRF, multipart para beacon, idempotencia, límites de tiempo, recencia, lotes,
retención, snapshots, referencias desaparecidas y noticias no públicas. Las
pruebas de worker usan una base de pruebas, no la base de desarrollo.
