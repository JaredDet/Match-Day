# Noticias

`modules.news` sigue las capas del backend: dominio `News`, comandos transaccionales,
consultas con DTOs, repositorios separados de lectura/escritura, contratos y ViewSet.
`NewsModule` registra sus dependencias en el inyector.

Una noticia puede ser general (`team_id: null`) o pertenecer a un equipo existente.
La relación con `Team` usa PROTECT. No hay relación directa con torneos o partidos.

## Contenido y portada

```json
{
  "title": "Nueva jornada",
  "team_id": null,
  "content": {"children": ["Primer párrafo", "Texto con <b>negrita</b> e <i>itálica</i>"]}
}
```

El título se normaliza y admite hasta 200 caracteres en la API. `NewsContentParser`
valida un objeto `content` con `children` como lista de cadenas. Admite etiquetas
`<b>` e `<i>` balanceadas y anidadas, sin atributos; rechaza las demás etiquetas
completas. El límite es 500 caracteres de texto acumulado, sin contar esas etiquetas.
La lista vacía está permitida. El parser valida el formato; no es un sanitizador HTML.

`cover_image` es una imagen opcional recibida como archivo multipart. En multipart,
`content` se envía como JSON serializado. Las lecturas devuelven la ruta almacenada
(por ejemplo `news/covers/foto.jpg`) o null, no una URL absoluta.
En edición, omitir la portada conserva la existente; enviar null en JSON la quita.
La retirada de la referencia no elimina el archivo físico del almacenamiento.
El almacenamiento y la entrega de archivos deben configurarse para cada entorno;
el proyecto no incorpora una ruta de descarga de portadas.

## Endpoints

Todas las rutas incluyen el prefijo `/api/` y barra final.

| Método y ruta | Entrada | Salida |
| --- | --- | --- |
| `POST news/` | `title`, `content`, `team_id?`, `cover_image?` | 201, `{id}` |
| `GET news/` | filtros opcionales | 200, lista de noticias |
| `GET news/{id}/` | UUID | 200, noticia |
| `PATCH news/{id}/` | `title`, `content`, `cover_image?` | 204 |
| `POST news/{id}/schedule/` | `scheduled_at` ISO 8601 | 204 |
| `POST news/{id}/unschedule/` | sin cuerpo | 204 |
| `POST news/{id}/publish/` | sin cuerpo | 204 |
| `DELETE news/{id}/` | sin cuerpo | 204 |

Aunque el método es PATCH, el contrato actual exige título y contenido. El equipo
no se cambia mediante ese endpoint. Los filtros son `status`, `team_id`,
`published_from` y `published_to`; los límites de publicación son inclusivos.
Se ordena por `published_at` descendente y UUID descendente. Las consultas sin
filtro incluyen los tres estados; para una lista de publicaciones usar
`?status=PUBLISHED`. El detalle tampoco restringe el estado. Actualmente no hay
permisos por rol configurados en el ViewSet; los actores de los diagramas describen
responsabilidades funcionales.

Ambas respuestas incluyen `id`, `title`, `team_id`, `cover_image`, `status`,
`scheduled_at` y `published_at`. El listado devuelve `preview` en lugar de `content`:
texto plano del primer párrafo no vacío, sin etiquetas `<b>`/`<i>`, con entidades HTML
decodificadas y espacios normalizados. Su máximo es `NEWS_PREVIEW_MAX_LENGTH = 200`
caracteres, incluida la elipsis `…` si se recorta. Si no hay texto, devuelve `""`.
El detalle mantiene `content` completo, incluidos todos los párrafos y su formato.
La preview se calcula al consultar y no modifica el contenido almacenado.
Este cambio de contrato requiere que los consumidores del listado usen `preview`;
no necesita migración de base de datos. La extracción aún lee el JSON almacenado,
pero el cuerpo completo no se incluye en la respuesta del listado.

Los errores usan `code` y `message`: validaciones
400 y entidades inexistentes 404. Los errores de contrato añaden `details`.

## Ciclo de vida

| Estado | Operaciones permitidas |
| --- | --- |
| `DRAFT` | editar, eliminar, programar, publicar |
| `SCHEDULED` | cancelar programación o publicar, incluso manualmente antes de la fecha |
| `PUBLISHED` | consultar |

Crear produce un borrador. Programar asigna `scheduled_at`; cancelar programación
lo limpia. Publicar asigna `published_at` y limpia `scheduled_at`.
No se permite volver una publicación a borrador. La API no exige que la fecha de
programación sea futura: una fecha vencida se publica en la siguiente revisión.

## Operación y datos demo

```sh
uv run python manage.py seed_demo_news
uv run python manage.py publish_scheduled_news --once
```

El seed crea siete noticias (tres publicadas, dos programadas, dos borradores),
reutilizando títulos existentes. Crea únicamente los equipos asociados que falten;
no crea ni cambia jugadores o partidos, ni renombra equipos existentes. Funciona
sin ejecutar `seed_demo_match`. Las fechas de la demo son fijas de 2026.

Para mantener el monitor activo:

```sh
uv run python manage.py publish_scheduled_news
```

Publica las noticias `SCHEDULED` con `scheduled_at <= ahora`, dentro de una transacción
y con bloqueo de filas en bases que lo soportan. Revisa cada cinco minutos cuando
la próxima noticia está a 24 horas o menos; en otro caso espera 24 horas. Una noticia
programada durante esa espera no despierta el proceso. Para revisiones periódicas
predecibles puede ejecutarse `--once` desde el planificador del entorno.
Los errores del modo continuo se registran y se reintenta en cinco minutos;
`--once` propaga el error. El monitor debe ejecutarse aparte del servidor web.

## Verificación y diagramas

Ver [testing](testing.md), [dominio](diagrams/domain/news.puml),
[estados](diagrams/news-lifecycle.puml), [casos de uso](diagrams/use-cases/news.puml)
y [contratos](diagrams/api/news.puml).
