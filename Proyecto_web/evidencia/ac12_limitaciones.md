# AC-12: Anexo de limitaciones conocidas

**Alumno:** Eladio Martinez Ambriz  
**Proyecto:** SIMANW 1.0 - Enero Junio 2026

## Limitaciones técnicas

1. **Cambios en sitios rastreados:** los portales de noticias pueden modificar su estructura HTML, sus selectores, su paginación o su archivo `robots.txt`, lo que puede afectar el rastreo real.
2. **Dependencia de conexión a Internet:** las fases que consultan RSS, sitios web o endpoints externos dependen de la disponibilidad de red.
3. **Disponibilidad de fuentes externas:** servicios como Wikidata, DBpedia o portales de datos abiertos pueden limitar peticiones, cambiar respuestas o estar temporalmente fuera de servicio.
4. **Variación temporal del corpus:** si se vuelve a rastrear en otra fecha, las noticias disponibles pueden cambiar. Por eso se conservan datasets JSON versionados.
5. **Calidad de los textos rastreados:** algunas noticias pueden tener cuerpos cortos, metadatos incompletos o contenido duplicado.
6. **Clasificación automática:** los modelos de clasificación dependen de los datos de entrenamiento y pueden cometer errores en noticias ambiguas o multitemáticas.
7. **Análisis de sentimiento:** VADER y técnicas léxicas pueden no capturar ironía, sarcasmo o contexto político complejo.
8. **Knowledge Graph:** los enlaces semánticos externos pueden ser aproximados y requieren revisión si se usa el sistema en producción.

## Mitigaciones aplicadas

- Se genera un corpus depurado con AC-8.
- Se guarda historial de alertas para evitar duplicados en AC-10.
- Se exportan artefactos RDF en varios formatos.
- Se registra un manifiesto por ejecución con versiones, archivos y conteos.
- Se conserva un procedimiento reproducible para ejecutar el pipeline desde datos versionados.
