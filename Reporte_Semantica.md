# Actividad previa Web Semántica

**Estudiante:** Eladio Martinez Ambriz / 22120687

## Misión 0

**1. ¿Qué diferencia hay entre una página web que describe a un museo y un dataset que lista museos con coordenadas y horarios?**

Una página web está diseñada para que una persona lea y planifique una visita, mientras que un dataset organiza datos en bruto (como coordenadas y horarios) para que sean procesados por programas informáticos, aplicaciones móviles o sistemas de mapas.

**2. Busca «*Tim Berners-Lee four rules of linked data*» o «*cinco estrellas datos abiertos*». Resume con tus palabras qué significa que un dato esté «enlazado».**

Que un dato esté «enlazado» significa que está publicado en la web de tal manera que cualquier programa informático puede saltar de un dato a otro para entender su contexto, descubrir nueva información relacionada y combinar bases de datos de diferentes partes del mundo de forma automática, sin necesidad de que un humano tenga que unirlas manualmente. Es, literalmente, crear una "Web de datos" en lugar de una "Web de documentos".

**3. Abre en el navegador la consulta de ejemplo de Wikidata Query Service (https://query.wikidata.org/) y ejecuta una consulta de demostración. ¿El resultado parece una tabla SQL o algo distinto? Anota una observación.**

Si, se parece mucho a una tabla SQL, con su propia id de dato enlazado, inclusive puedes agregarle date entre otros tipos de datos para que muestre la tabla, tambien puedes ver mas info si le das click al ID.

## Misión 1
Si, se supone que dejaría de funcionar ya que, si estuviera programado para extraer el triple buscando estrictamente el texto dentro de **h1**, un cambio a un **span** o una transformación de texto rompería el recolector. Tendría que volver a modificar el código de extracción manualmente para adaptarlo a la nueva estructura.

## Misión 3

**1. Construye una tabla (en tu reporte) con columnas: nombre_en_texto | URI_propuesta | tipo_entidad para cada fila problemática de fuente_a.**

| nombre_en_texto | URI_propuesta | tipo_entidad |
|---|---|---|
| París | `http://simanw.example/recurso/ciudad/paris` | Ciudad |
| París Hilton | `http://simanw.example/recurso/persona/paris-hilton` | Persona |
| Francia | `http://simanw.example/recurso/pais/francia` | País |
| FR | `http://simanw.example/recurso/pais/francia` | Código o alias del país Francia |

**3. La búsqueda literal del término «París» no basta porque la misma cadena puede representar entidades distintas, por ejemplo la ciudad de París o parte del nombre de la persona Paris Hilton. Además, diferentes fuentes pueden usar nombres distintos para la misma entidad, como Francia, FR o France. Un identificador URI permite distinguir de forma única cada entidad, evitando ambigüedades al fusionar datos de varias fuentes. Gracias a las URIs, el sistema puede saber que París como ciudad y París Hilton como persona son conceptos diferentes.**

La búsqueda literal del término «París» no basta porque la misma cadena puede representar entidades distintas, por ejemplo la ciudad de París o parte del nombre de la persona Paris Hilton. Además, diferentes fuentes pueden usar nombres distintos para la misma entidad, como Francia, FR o France. Un identificador URI permite distinguir de forma única cada entidad, evitando ambigüedades al fusionar datos de varias fuentes. Gracias a las URIs, el sistema puede saber que París como ciudad y París Hilton como persona son conceptos diferentes.

**¿Qué riesgo hay si enlazas owl:sameAs de más (falsos positivos)? Menciona un ejemplo concreto con nombres de la misión.**

El riesgo de enlazar owl:sameAs de más es que el sistema trata dos recursos como si fueran exactamente la misma entidad, no solo parecidos. Esto puede contaminar el grafo con información falsa y provocar inferencias incorrectas.

## Misión 3

**1. Completa patron_b y muestra la salida.**

Autores: [ ]
Personas y nombres:
ID: ex:alicia -> Nombre: Alicia García
ID: ex:bob -> Nombre: Bob Martínez

**2. Responde: ¿en qué se parece consulta_simple a la cláusula WHERE de SPARQL? ¿en qué se queda corta?**

consulta_simple se parece a la cláusula WHERE de SPARQL porque ambas sirven para buscar patrones dentro de un grafo de triples. Es decir, permiten consultar relaciones del tipo:

**sujeto - predicado - objeto**

Sin embargo, consulta_simple se queda corta porque normalmente solo permite buscar coincidencias básicas en un conjunto de datos, mientras que SPARQL es mucho más expresivo. SPARQL permite usar variables, múltiples patrones conectados, filtros, prefijos, consultas sobre URIs reales, agregaciones, ordenamientos, límites, consultas opcionales y razonamiento más estructurado sobre RDF.

Por ejemplo:

**París -> esCapitalDe -> Francia**

**3. Escribe la misma consulta de la Tarea A en pseudocódigo SPARQL (no hace falta endpoint real):**

PREFIX ex: <http://ejemplo.org/>

SELECT ?persona
WHERE {
  ex:libro42 ex:autor ?persona .
}

**Responde en 5–8 líneas: «¿Qué problema de esta actividad resuelve RDF que no resuelve solo JSON?»**

RDF resuelve el problema de representar relaciones semánticas entre entidades de forma clara y conectable.
JSON puede guardar datos estructurados, pero por sí solo no indica si dos valores de distintas fuentes representan la misma entidad.
En esta actividad, RDF permite distinguir entre París ciudad y Paris Hilton usando URIs únicas.
También permite alinear entidades equivalentes entre fuentes con predicados como owl:sameAs o skos:exactMatch.
Así, el sistema no depende solo del texto literal, que puede ser ambiguo o variar entre fuentes.
Además, RDF facilita fusionar grafos y consultar relaciones mediante patrones tipo sujeto–predicado–objeto.
Por eso RDF aporta significado y conexión entre datos, mientras JSON principalmente almacena estructura.