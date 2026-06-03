# AC-10: Control de alertas duplicadas

El sistema evita alertas duplicadas mediante una llave única compuesta por la consulta guardada y la noticia detectada. Para cada noticia se genera un identificador estable a partir de su URL; si la URL no existe, se usa el título como respaldo. Después, se combina `consulta_id + noticia_id` y se calcula un hash SHA-1. Ese hash se guarda en `reportes/ac10_historial_alertas.json`.

Cuando se evalúan noticias nuevas, el sistema calcula la similitud entre cada consulta persistida y cada noticia. Si la similitud supera el umbral, antes de emitir la alerta revisa si la llave ya existe en el historial. Si existe, la alerta se omite y se contabiliza como duplicada. Si no existe, se registra con consulta, noticia, URL, categoría, similitud y marca de tiempo.

Con este mecanismo, una misma noticia puede activar diferentes consultas si realmente coincide con varias, pero la misma consulta no vuelve a alertar por la misma noticia en ejecuciones posteriores.
