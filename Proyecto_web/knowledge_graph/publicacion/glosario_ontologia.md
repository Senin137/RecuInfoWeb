# Glosario de ontología SIMANW

## Prefijos

| Prefijo | URI | Uso |
|---|---|---|
| simanw | https://simanw.local/ontology# | Vocabulario propio del proyecto SIMANW |
| data | https://simanw.local/recurso/ | Recursos locales del Knowledge Graph |
| schema | https://schema.org/ | Vocabulario público para describir noticias |
| dc | http://purl.org/dc/elements/1.1/ | Metadatos Dublin Core |
| dcterms | http://purl.org/dc/terms/ | Términos extendidos Dublin Core |
| foaf | http://xmlns.com/foaf/0.1/ | Personas/autores |
| skos | http://www.w3.org/2004/02/skos/core# | Etiquetas y relaciones conceptuales |
| owl | http://www.w3.org/2002/07/owl# | Equivalencias y ontología |
| wd | http://www.wikidata.org/entity/ | Entidades de Wikidata |

## Clases principales

| Clase | Descripción |
|---|---|
| simanw:Noticia | Recurso que representa una noticia procesada por SIMANW |
| simanw:Categoria | Tema o categoría asignada a una noticia |
| simanw:Fuente | Portal, medio o fuente de la noticia |
| simanw:Autor | Autor identificado o no identificado de la noticia |
| simanw:Sentimiento | Polaridad emocional asociada a una noticia |
| simanw:Entidad | Persona, organización o lugar mencionado en el texto |
| simanw:DatasetAbierto | Dataset público relacionado con una noticia o categoría |

## Propiedades principales

| Propiedad | Descripción |
|---|---|
| simanw:titulo | Título textual de la noticia |
| simanw:resumen | Fragmento o resumen de la noticia |
| simanw:url | URL original de la noticia |
| simanw:fechaPublicacion | Fecha de publicación o rastreo |
| simanw:tieneCategoria | Relación entre noticia y categoría |
| simanw:publicadaPor | Relación entre noticia y fuente |
| simanw:escritaPor | Relación entre noticia y autor |
| simanw:tieneSentimiento | Relación entre noticia y sentimiento |
| simanw:sentimientoEtiqueta | Etiqueta textual: positivo, negativo, neutral |
| simanw:sentimientoScore | Valor numérico de sentimiento |
| simanw:mencionaEntidad | Entidades detectadas en una noticia |
| simanw:relacionadaConDataset | Relación entre noticia y dataset abierto |
