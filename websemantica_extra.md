# Actividades extras Web Semántica (post-lectura)

**Estudiante:** [Eladio Martinez Ambriz / 22120687]
**Fecha: 25/05/2026**

## Misión A: Comprueba el glosario (sin memorizar a ciegas)

**1. Completa la tabla: escribe una frase en tus palabras (no copies la analogía literal del documento).**

| Término | Tu definición (1 frase) | Ejemplo concreto (no del documento) |
|---|---|---|
| URI | Es aquel identificador unico para una página web. Basicamente su verdadero nombre.  |`https://datos.ejemplo.org/persona/ana-martinez` identifica de forma única a una persona llamada Ana Martínez dentro de un conjunto de datos.  |
| Triple | Son los elementos que se relacionan entre  las entidades los cuales mejoran la busqueda   |`Ana Martínez` — `estudiaEn` — `Instituto Tecnológico de Morelia`.|
| Literal |Es un valor basico de datos, como lo es un string, number o boleano.  |`"Morelia"` como valor de texto para indicar la ciudad donde vive una persona.  |
| OWA |Es como el nucleo de la web semantica, fue diseñado para representar conocimiento complejo sobre las cosas, sus grupos y cómo se relacionan entre sí.  |Si una base de conocimiento no dice que Luis tenga mascota, no significa que no tenga; simplemente no se sabe.|
| TBox |Es aquel que establece las reglas, conceptos y relaciones que son siempre verdaderos en ese contexto.|Una regla que define que todo `Estudiante` es también una `Persona`.|
| ABox |Son aquellas afirmaciones o hechos que se presentan que se presentan en la ontología  |El dato específico de que `Carlos Pérez` es un `Estudiante`.|
| Endpoint |es un servicio web o punto de acceso al que se envían consultas para extraer, filtrar y relacionar datos estructurados en formato de grafos.  |Una URL como `https://datos.ejemplo.org/sparql` donde se pueden hacer consultas SPARQL a una base RDF.|
| LOD |Es el de mejores prácticas para publicar y conectar datos estructurados en la web, de modo que tanto humanos como máquinas puedan leerlos, enlazarlos y procesarlos fácilmente. Basicamente de esta forma son sencillos de leer y identificar para tanto humanos como maquinas.  |Un conjunto de datos públicos sobre universidades que enlaza cada ciudad con recursos externos como Wikidata o DBpedia.
|

**2. Emparejamiento: une cada analogía del documento con el término correcto (escribe la letra).**

URI → a
Ontología → b
SPARQL → c
SHACL → d
OWA → e
Literal → f

**3. Pregunta corta: ¿Por qué una URL puede ser URI pero un URI con esquema urn:isbn:... no tiene por qué ser URL? (3 líneas máximo).**

Una URL es un tipo de URI porque identifica un recurso indicando también dónde encontrarlo, por ejemplo https://....
En cambio, un URI como urn:isbn:978... solo identifica algo, como un libro por su ISBN.
No es URL porque no indica una dirección para acceder al recurso en internet.

## Misión B: Capas, mundo abierto y comparación con SQL

**Parte 1 — Ordena las capas**

1. URI/IRI
2. RDF
3. OWL/RDFS
4. SPARQL
5. HTML

**Parte 2 — OWA vs mundo cerrado
Lee el escenario y responde verdadero / falso / depende (mundo abierto) con justificación de una línea.**

Base RDF de una universidad publicada en 2024. No aparece ningún triple:
  ex:maria rdf:type ex:Estudiante .

  Preguntas:
**1. ¿Se puede inferir que María NO es estudiante?**
Falso, En OWA, que no aparezca el triple no significa que María no sea estudiante; solo significa que no se sabe.

**2. ¿Es lo mismo que una consulta SQL SELECT * FROM estudiantes WHERE id='maria' sin filas?**

SQL suele trabajar como mundo cerrado: si no hay fila, se asume que no está en la tabla; RDF no hace esa negación automática.

**3. Si un reasoner OWL deduce ex:maria rdf:type ex:Persona porque ex:Estudiante rdfs:subClassOf ex:Persona y más tarde aparece ex:maria rdf:type ex:Estudiante, ¿invalida la inferencia anterior?**

No la invalida; al contrario, si María es ex:Estudiante y ex:Estudiante es subclase de ex:Persona, entonces María sigue siendo ex:Persona.

**Parte 3 — Tabla comparativa (completa tú)**

| Pregunta | Web de documentos | SQL típico | RDF + SPARQL |
|---|---|---|---|
| Unidad básica | Documento o página HTML | Tabla, fila o registro | Triple: sujeto, predicado y objeto |
| ¿Ausencia de dato implica falsedad? | No necesariamente; puede que la página no lo mencione | Generalmente sí, porque trabaja como mundo cerrado | No; en mundo abierto solo significa que no se sabe |
| Identificador global típico | URL | Clave primaria o ID local | URI / IRI |
| Consulta declarativa | Búsqueda web o extracción del contenido | SQL, por ejemplo `SELECT` | SPARQL, por ejemplo `SELECT` sobre triples |

## Misión C: Escribir Turtle y ver inferencia RDFS

**Tarea C1 — Archivo Turtle**
Crea mentalmente o en un bloque Org el grafo en Turtle (mínimo 8 triples explícitos + tipos). Usa:

@prefix ex: <http://ejemplo.org/uni#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

**Clases y jerarquía**
ex:Profesor rdfs:subClassOf ex:Persona .
ex:Estudiante rdfs:subClassOf ex:Persona .

**Propiedad enseñar**
ex:enseña rdfs:domain ex:Profesor .
ex:enseña rdfs:range ex:Asignatura .

**Personas**
ex:Alicia rdf:type ex:Profesor ;
    ex:nombre "Alicia García"@es ;
    ex:enseña ex:MatematicasI .

ex:Bob rdf:type ex:Estudiante ;
    ex:nombre "Bob"@es .

**Asignatura**
ex:MatematicasI rdfs:label "Matemáticas I"@es.

**Tarea C2 — Inferencia en papel**
Lista al menos 3 triples que un motor RDFS inferiría sin que los hayas escrito a mano (herencia de tipos, dominio/rango). Explica cada uno: «por regla X del documento, se deduce Y».

**ex:Alicia rdf:type ex:Persona .
ex:Bob rdf:type ex:Persona .
ex:MatematicasI rdf:type ex:Asignatura .**

**ex:Alicia rdf:type ex:Persona.** Explicación: Por la regla de herencia de tipos con rdfs:subClassOf, si ex:Alicia es ex:Profesor y ex:Profesor es subclase de ex:Persona, entonces ex:Alicia también es ex:Persona.

**ex:Bob rdf:type ex:Persona.** Por la regla de herencia de tipos con rdfs:subClassOf, si ex:Bob es ex:Estudiante y ex:Estudiante es subclase de ex:Persona, entonces ex:Bob también es ex:Persona. 

**ex:MatematicasI rdf:type ex:Asignatura.** Por la regla de rango rdfs:range, si ex:Alicia ex:enseña ex:MatematicasI y ex:enseña tiene rango ex:Asignatura, entonces el objeto ex:MatematicasI es una ex:Asignatura.

También se podría decir que, por dominio rdfs:domain, cualquier sujeto que use ex:enseña queda clasificado como ex:Profesor; en este caso reforzaría que ex:Alicia rdf:type ex:Profesor.

**Tarea C3 — Validación con rdflib (opcional recomendado)**

Poner rdfs:subClassOf en el TBox es definir una regla general del “plano del conocimiento”: por ejemplo, decir que todo Profesor es una Persona.

Poner rdf:type ex:Profesor en el ABox es registrar un hecho concreto del mundo: por ejemplo, decir que Alicia es Profesora.

En otras palabras: el TBox describe la estructura o reglas del dominio, mientras que el ABox guarda los datos específicos de individuos reales o instancias.

## Misión D: Consultas SPARQL

**D1 — Sobre tu grafo de la Misión C (local)**
Escribe tres consultas y resultado esperado en prosa (no hace falta ejecutar si no tienes rdflib):

**Consulta 1 — SELECT: nombres de todas las Personas**
PREFIX ex: <http://ejemplo.org/uni#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?persona ?nombre
WHERE {
  ?persona rdf:type/rdfs:subClassOf* ex:Persona .
  ?persona ex:nombre ?nombre .
}

**Consulta 2 — ASK: ¿Bob es Persona?**
PREFIX ex: <http://ejemplo.org/uni#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ASK
WHERE {
  ex:Bob rdf:type/rdfs:subClassOf* ex:Persona .
}

**Consulta 3 — SELECT con FILTER: profesores con nombre en español**

PREFIX ex: <http://ejemplo.org/uni#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?profesor ?nombre
WHERE {
  ?profesor rdf:type/rdfs:subClassOf* ex:Profesor .
  ?profesor ex:nombre ?nombre .
  FILTER(LANGMATCHES(LANG(?nombre), "es"))
}

**D2 — Wikidata Query Service (en línea)**
Abre https://query.wikidata.org/ y ejecuta una consulta que devuelva al menos 5 filas. Opciones (elige una):

Museos en México con coordenadas.
Películas de un director que elijas.
Ciudades que son capital de un país de América Latina.

PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>

SELECT ?pais ?paisLabel ?capital ?capitalLabel
WHERE {
  VALUES ?pais {
    wd:Q96     # México
    wd:Q414    # Argentina
    wd:Q739    # Colombia
    wd:Q419    # Perú
    wd:Q298    # Chile
    wd:Q155    # Brasil
    wd:Q750    # Bolivia
    wd:Q241    # Cuba
    wd:Q77     # Uruguay
    wd:Q800    # Costa Rica
  }

  ?pais wdt:P36 ?capital .

  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "es,en" .
  }
}
LIMIT 10

**Captura o descripción de 2 columnas del resultado.**
El nombre legible del país, por ejemplo: México, Argentina, Colombia.

**Captura o descripción de 2 columnas del resultado.**

**paisLabel**: El nombre legible del país, por ejemplo: México, Argentina, Colombia.

**capitalLabel**: El nombre legible de su capital, por ejemplo: Ciudad de México, Buenos Aires, Bogotá.

**paisLabel**	**capitalLabel**
México	    Ciudad de México
Argentina	Buenos Aires
Colombia	Bogotá
Perú	    Lima
Chile	    Santiago de Chile

**¿Qué IRIs ves en la respuesta (ej. wd:Q...)? ¿Por qué Wikidata usa URIs y no solo nombres?**

wd:Q96   → México
wd:Q1489 → Ciudad de México
wd:Q414  → Argentina
wd:Q1486 → Buenos Aires
wd:Q739  → Colombia
wd:Q2841 → Bogotá

**D3 — Puente con la actividad previa**

Reescribe en SPARQL real la «Tarea A» de la Misión 3 de web_semantica_actividad_previa.org (autores de ex:libro42). Compara con tu función consulta_simple: ¿qué cláusula SPARQL no implementaste en Python?

PREFIX ex: <http://ejemplo.org/biblio#>

SELECT ?autor
WHERE {
  ex:libro42 ex:tieneAutor ?autor .
}

## Misión E: Linked Data, JSON-LD y datos abiertos

**E1 — Cuatro principios en la práctica**
Para un dataset hipotético «Bibliotecas de México»:

| Principio Linked Data | ¿Cómo lo cumplirías? (1 línea) | ¿Qué pasa si NO lo cumples? |
|---|---|---|
| 1. URIs como nombres | Asignaría una URI única a cada biblioteca, libro, autor o ciudad, por ejemplo `http://datos.ejemplo.mx/biblioteca/itm`. | Los recursos pueden confundirse si solo se usan nombres comunes o repetidos. |
| 2. URIs HTTP | Usaría URIs HTTP accesibles desde la web, como `https://datos.ejemplo.mx/bibliotecas/123`. | Otros sistemas no podrían consultar o reutilizar fácilmente la información. |
| 3. Content negotiation | Haría que la misma URI devuelva HTML para humanos y RDF/JSON-LD para máquinas según la petición. | La información sería menos útil porque solo serviría para personas o solo para aplicaciones. |
| 4. Enlaces a otros LOD | Enlazaría ciudades, autores o instituciones con Wikidata, DBpedia u otros datasets abiertos. | El dataset quedaría aislado y perdería contexto semántico externo. |

**E2 — Subir en las 5 estrellas**
Un municipio publica un PDF con tabla escaneada de presupuesto. Clasifica en ★ a ★★★★★ y propón dos pasos concretos para subir al menos dos estrellas.

| Situación | Clasificación |
|---|---|
| PDF escaneado con tabla de presupuesto | ★ |
| Motivo | Está publicado, pero no es estructurado ni reutilizable fácilmente por computadora. |

Se clasificaría como **★ (una estrella)**, siempre que el PDF esté disponible en la web y tenga una licencia abierta.

Aunque contiene datos públicos, al ser una **tabla escaneada**, no permite trabajar fácilmente con la información mediante programas o herramientas de análisis.

### Pasos para subir al menos dos estrellas

1. **Convertir la tabla escaneada a datos estructurados**  
   Usaría OCR y revisión manual para transformar la tabla en columnas claras, por ejemplo: `partida`, `concepto`, `monto`, `año` y `municipio`.

2. **Publicar los datos en un formato abierto no propietario**  
   Publicaría la información en formatos como **CSV** o **JSON**, junto con una licencia abierta.

**E3 — JSON-LD embebido (lectura)**
Pega un fragmento inventado de <script type"application/ld+json">= para un evento cultural (usa @context con schema.org). Indica qué triples RDF equivaldrían (sujeto, predicado, objeto en español).

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@id": "https://ejemplo.org/eventos/feria-del-libro-2026",
  "@type": "Event",
  "name": "Feria del Libro",
  "startDate": "2026-11-01",
  "location": {
    "@id": "https://ejemplo.org/lugares/centro-historico",
    "@type": "Place",
    "name": "Centro Histórico"
  }
}
</script>
```

**Pregunta E3: ¿El @context cumple la misma función que PREFIX en Turtle? Explica en 2–3 líneas.**

Sí, se parecen porque ambos sirven para abreviar vocabularios y convertir nombres cortos en IRIs completas.


## Misión F: Diseño TBox / ABox (mini ontología)

Escenario
Una app de recomendación de cursos en línea necesita interoperar con otra universidad. Diseña en papel (o Turtle solo TBox) lo siguiente:

Al menos 3 clases con jerarquía (rdfs:subClassOf).
Al menos 2 propiedades con rdfs:domain y rdfs:range.
Una restricción que solo se puede expresar bien en OWL, no en RDFS puro (ej. owl:FunctionalProperty, cardinalidad min 1). Escríbela en Turtle con prefijo owl:.
Escribe 5 triples ABox de individuos ficticios que respeten tu TBox.

@prefix ex: <http://ejemplo.org/cursos#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

**=========================
TBox: clases y jerarquía
=========================**

ex:Persona rdf:type rdfs:Class .
ex:Estudiante rdf:type rdfs:Class ;
    rdfs:subClassOf ex:Persona .

ex:Profesor rdf:type rdfs:Class ;
    rdfs:subClassOf ex:Persona .

ex:Curso rdf:type rdfs:Class .
ex:CursoEnLinea rdf:type rdfs:Class ;
    rdfs:subClassOf ex:Curso .

ex:AreaConocimiento rdf:type rdfs:Class .

**=========================
TBox: propiedades
=========================**

ex:inscritoEn rdf:type rdf:Property ;
    rdfs:domain ex:Estudiante ;
    rdfs:range ex:Curso .

ex:impartidoPor rdf:type rdf:Property ;
    rdfs:domain ex:Curso ;
    rdfs:range ex:Profesor .

ex:perteneceArea rdf:type rdf:Property ;
    rdfs:domain ex:Curso ;
    rdfs:range ex:AreaConocimiento .

**=========================
Restricción OWL
=========================**

ex:tieneCodigoCurso rdf:type owl:FunctionalProperty ;
    rdfs:domain ex:Curso ;
    rdfs:range xsd:string .

**=========================
ABox: individuos ficticios
=========================*

ex:Ana rdf:type ex:Estudiante .
ex:DrLopez rdf:type ex:Profesor .
ex:PythonBasico rdf:type ex:CursoEnLinea .
ex:PythonBasico ex:impartidoPor ex:DrLopez .
ex:Ana ex:inscritoEn ex:PythonBasico .
ex:PythonBasico ex:tieneCodigoCurso "PY-101" .
ex:Programacion rdf:type ex:AreaConocimiento .
ex:PythonBasico ex:perteneceArea ex:Programacion .

**Pregunta F
¿Qué vocabulario reutilizarías del documento (schema.org, FOAF, DCAT, SKOS) y para qué campo concreto de tu app? Mínimo dos vocabularios con justificación.**

Usaría **schema.org** para describir los cursos mediante `schema:Course`, porque permite representar nombre, descripción, proveedor y modalidad del curso de forma estándar.

También usaría **FOAF** para representar estudiantes y profesores con campos como `foaf:name` o `foaf:mbox`, ya que facilita identificar personas entre distintas universidades.

Además, podría usar **SKOS** para clasificar cursos por áreas de conocimiento como “Programación” o “Inteligencia Artificial”.

## Misión G: SHACL vs Reasoner (conceptual + mini ejercicio)

**G1 — Diferencia en criollo
Completa:**

El reasoner OWL/RDFS añade conocimiento porque aplica reglas semánticas sobre lo que ya existe, por ejemplo: si Profesor es subclase de Persona y Alicia es Profesor, entonces puede inferir que Alicia es Persona.

SHACL no inventa triples; en su lugar revisa si los datos cumplen ciertas reglas o restricciones, por ejemplo: “todo curso debe tener nombre” o “todo estudiante debe tener matrícula”. Si algo no cumple, lo marca como error o advertencia.

**G2 — Detecta el error
Este grafo dice:**

**ex:ana rdf:type ex:Persona .
ex:ana ex:email "ana@uni.edu" .
ex:ana ex:email "ana.personal@gmail.com" .
Y la forma SHACL dice: «cada ex:Persona tiene como máximo un ex:email».**

**1. ¿El grafo viola SHACL?**
Sí. Viola la regla porque ex:ana es ex:Persona y tiene dos valores para ex:email, cuando la forma SHACL permite máximo uno.

**2. ¿Un reasoner RDFS inferiría algo sobre los dos emails?**
No. RDFS no entiende restricciones de máximo uno ni propiedades funcionales; solo maneja cosas como rdfs:subClassOf, rdfs:domain y rdfs:range.

**3.¿Qué herramienta usarías antes de publicar el dataset en un portal LOD?**

Usaría un validador SHACL, por ejemplo pySHACL, para revisar que los datos cumplan las restricciones antes de publicarlos.

## Misión H: Proyecto integrador «Del dato abierto al grafo»

**1. Diseño de IRIs propuestas**

| Nombre legible | Tipo | IRI propuesta |
|---|---|---|
| Dr. Luis Méndez | Profesor | `ex:profesorP1` |
| Dra. Carmen Ruiz | Profesor | `ex:profesorP2` |
| Física I | Materia | `ex:fisicaI` |
| Química | Materia | `ex:quimica` |
| Aula 301 | Aula | `edif:aula301` |
| Edificio Norte | Edificio | `edif:edificioNorte` |

---

**2. Triples Turtle unificados**

```turtle
@prefix ex: <http://campus.ejemplo/recursos#> .
@prefix edif: <http://campus.ejemplo/edificios#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix wd: <http://www.wikidata.org/entity/> .

# Clases
ex:Profesor rdf:type rdfs:Class .
ex:Materia rdf:type rdfs:Class .
ex:Aula rdf:type rdfs:Class .
ex:Edificio rdf:type rdfs:Class .

# Profesores
ex:profesorP1 rdf:type ex:Profesor ;
    ex:idInterno "P1" ;
    ex:nombre "Dr. Luis Méndez"@es ;
    ex:enseña ex:fisicaI .

ex:profesorP2 rdf:type ex:Profesor ;
    ex:idInterno "P2" ;
    ex:nombre "Dra. Carmen Ruiz"@es ;
    ex:enseña ex:quimica .

# Materias
ex:fisicaI rdf:type ex:Materia ;
    ex:nombre "Física I"@es ;
    ex:seImparteEn edif:aula301 .

ex:quimica rdf:type ex:Materia ;
    ex:nombre "Química"@es ;
    ex:seImparteEn edif:aula301 ;
    skos:exactMatch wd:Q2329 .

# Fragmento RDF de edificios integrado
edif:edificioNorte rdf:type ex:Edificio ;
    edif:tieneNombre "Edificio Norte"@es .

edif:aula301 rdf:type ex:Aula ;
    edif:tieneNombre "Aula 301"@es ;
    edif:estaEn edif:edificioNorte .
```

---

**3. Enlace LOD**

```turtle
ex:quimica skos:exactMatch wd:Q2329 .
```

En este caso, `wd:Q2329` representa el concepto de **Química** en Wikidata.

---

**4. Consulta SPARQL**

**Pregunta:** ¿Qué materias se imparten en el Edificio Norte?

```sparql
PREFIX ex: <http://campus.ejemplo/recursos#>
PREFIX edif: <http://campus.ejemplo/edificios#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?materia ?nombreMateria ?aula
WHERE {
  ?materia rdf:type ex:Materia ;
           ex:nombre ?nombreMateria ;
           ex:seImparteEn ?aula .

  ?aula edif:estaEn edif:edificioNorte .
}
```

**Resultado esperado en prosa:**  
La consulta devolvería las materias **Física I** y **Química**, porque ambas se enlazaron con `edif:aula301`, y esa aula está ubicada en `edif:edificioNorte`.

---

**5. Reflexión**

Con solo búsqueda por keywords en HTML sería difícil descubrir relaciones indirectas entre datos de distintas fuentes.

La tabla original solo indica qué profesor enseña qué materia, pero no menciona edificios.

El fragmento RDF, por separado, solo describe el aula y el edificio donde se encuentra.

Al convertir ambos datos a RDF, se pueden unir mediante IRIs comunes como `edif:aula301`.

Así, una consulta puede responder qué materias se imparten en un edificio, aunque esa relación no estuviera escrita literalmente en la tabla.

La búsqueda por palabras clave encontraría textos parecidos, pero no entendería claramente las relaciones entre sujeto, predicado y objeto.

Tampoco distinguiría fácilmente si “Norte” es un edificio, una zona o parte de otro nombre.

RDF permite integrar datos heterogéneos y consultar relaciones semánticas de forma precisa.

Además, con enlaces LOD como Wikidata, el dataset puede conectarse con conocimiento externo reutilizable.

## Síntesis final (obligatoria)
**Responde: «Si mañana desaparecieran los estándares W3C de RDF/SPARQL, ¿qué perdería concretamente
el proyecto de la Misión H que sí tendría con solo APIs REST + JSON?»**

Si mañana desaparecieran los estándares W3C de RDF/SPARQL, el proyecto de la Misión H perdería principalmente la capacidad de integrar datos con significado común entre fuentes distintas. Con solo APIs REST + JSON, todavía podría enviar y recibir datos, pero cada sistema tendría que interpretar manualmente qué significa profesor, materia, aula o edificio.

También se perdería el uso de IRIs estándar para identificar entidades de forma global y reutilizable. La relación indirecta “materia → aula → edificio” tendría que programarse con lógica específica en la API, en vez de consultarse semánticamente con SPARQL. Además, no sería tan natural enlazar el dataset con Wikidata mediante skos:exactMatch u owl:sameAs.

En resumen, REST + JSON serviría para transportar información, pero RDF/SPARQL aporta interoperabilidad semántica, consultas flexibles, enlaces LOD y una forma común de entender las relaciones entre datos de distintas fuentes.