# Reporte de Misión: Búsqueda y Recuperación de Información

**Agente Especial:** Eladio Martinez Ambriz  
**Matrícula:** 22120687

---

## Misión 1

### Código

```python
import re
import pprint

corpus_mision1 = {
    "d1": "La red de agentes interceptó tráfico sospechoso en el nodo norte.",
    "d2": "El agente de campo reportó actividad normal en la red interna.",
    "d3": "Manual de procedimientos: la red no debe apagarse sin autorización.",
    "d4": "Mantenimiento programado del agente automático de respaldo.",
}

indice_invertido = {}

for doc_id, texto in corpus_mision1.items():
    texto_limpio = re.sub(r'[.:,]', '', texto.lower())
    tokens = texto_limpio.split()

    for termino in tokens:
        if termino not in indice_invertido:
            indice_invertido[termino] = []

        if doc_id not in indice_invertido[termino]:
            indice_invertido[termino].append(doc_id)

print("--- Índice Invertido de la Misión ---")
pprint.pprint(indice_invertido)

termino1 = "red"
termino2 = "agente"

docs_agente = set(indice_invertido.get(termino2, []))
docs_red = set(indice_invertido.get(termino1, []))

docs_interseccion = docs_agente.intersection(docs_red)

print(f"Documentos con '{termino1}': {docs_red}")
print(f"Documentos con '{termino2}': {docs_agente}")
print("---")
print(f"Resultado de la consulta ({termino1} AND {termino2}): {docs_interseccion}")

# 3) Imprimir doc_id coincidentes, ordenados

lista_resultados = sorted(list(docs_interseccion))

if lista_resultados:
    print("Resultados de la búsqueda (Ordenados):")
    for doc_id in lista_resultados:
        print(f"-> {doc_id}")
else:
    print("La búsqueda no arrojó resultados coincidentes.")
```

### Salida

```txt
Índice Invertido de la Misión
{'actividad': ['d2'],
 'agente': ['d2', 'd4'],
 'agentes': ['d1'],
 'apagarse': ['d3'],
 'automático': ['d4'],
 'autorización': ['d3'],
 'campo': ['d2'],
 'de': ['d1', 'd2', 'd3', 'd4'],
 'debe': ['d3'],
 'del': ['d4'],
 'el': ['d1', 'd2'],
 'en': ['d1', 'd2'],
 'interceptó': ['d1'],
 'interna': ['d2'],
 'la': ['d1', 'd2', 'd3'],
 'mantenimiento': ['d4'],
 'manual': ['d3'],
 'no': ['d3'],
 'nodo': ['d1'],
 'normal': ['d2'],
 'norte': ['d1'],
 'procedimientos': ['d3'],
 'programado': ['d4'],
 'red': ['d1', 'd2', 'd3'],
 'reportó': ['d2'],
 'respaldo': ['d4'],
 'sin': ['d3'],
 'sospechoso': ['d1'],
 'tráfico': ['d1']}

Documentos con 'red': {'d2', 'd1', 'd3'}
Documentos con 'agente': {'d2', 'd4'}

Resultado de la consulta (red AND agente): {'d2'}

Resultados de la búsqueda (Ordenados):
-> d2
```

---

## Misión 2

### Código

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

corpus_mision2 = {
    "a1": "Protocolo de evacuación silenciosa en instalaciones subterráneas.",
    "a2": "Guía de rutas de escape y puntos de reunión sin alarmas audibles.",
    "a3": "Receta de cocina: pasta con tomate y albahaca para el personal.",
    "a4": "Mapa de salidas de emergencia y señalética fotoluminiscente.",
    "a5": "Informe meteorológico: probabilidad de lluvia en la región este.",
}

consulta_mision2 = "evacuación silenciosa rutas de escape emergencia"

# 1. Vectorización del corpus y la consulta

docs_ids = list(corpus_mision2.keys())
textos_corpus = list(corpus_mision2.values())

vectorizador = TfidfVectorizer()
tfidf_corpus = vectorizador.fit_transform(textos_corpus)

tfidf_consulta = vectorizador.transform([consulta_mision2])

print(f"Vocabulario detectado ({len(vectorizador.get_feature_names_out())} términos únicos).")
print(f"Dimensión de la matriz del corpus: {tfidf_corpus.shape} (5 documentos, {tfidf_corpus.shape[1]} características)")
print(f"Dimensión del vector de consulta: {tfidf_consulta.shape} (1 consulta, {tfidf_consulta.shape[1]} características)")

# 2. Cálculo de similitud coseno

similitudes = cosine_similarity(tfidf_consulta, tfidf_corpus).flatten()

for doc_id, score in zip(docs_ids, similitudes):
    print(f"Similitud con {doc_id}: {score:.4f}")

# 3. Ordenar documentos por similitud

resultados_ordenados = list(zip(docs_ids, similitudes))
ranking = sorted(resultados_ordenados, key=lambda x: x[1], reverse=True)

for i, (doc_id, score) in enumerate(ranking[:3], start=1):
    print(f"{i}. {doc_id} -> Puntuación: {score:.4f}")
```

### Salida

```txt
Vocabulario detectado (36 términos únicos).

Dimensión de la matriz del corpus: (5, 36) (5 documentos, 36 características)
Dimensión del vector de consulta: (1, 36) (1 consulta, 36 características)

Similitud con a1: 0.4018
Similitud con a2: 0.3700
Similitud con a3: 0.0327
Similitud con a4: 0.2617
Similitud con a5: 0.0354

1. a1 -> Puntuación: 0.4018
2. a2 -> Puntuación: 0.3700
3. a4 -> Puntuación: 0.2617
```

---

## Misión 3

### Código

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documentos_mision3 = [
    {
        "doc_id": "x1",
        "nivel": "PUBLICO",
        "texto": "Boletín de prensa sobre obras en la avenida central y tráfico lento."
    },
    {
        "doc_id": "x2",
        "nivel": "SIGILO",
        "texto": "Rumor operativo: el contacto cambió frecuencia; verificar handoff nocturno. ###FIN###"
    },
    {
        "doc_id": "x3",
        "nivel": "PUBLICO",
        "texto": "Convocatoria a curso de primeros auxilios para voluntarios municipales."
    },
    {
        "doc_id": "x4",
        "nivel": "SIGILO",
        "texto": "Inventario de papelería y tóner para el almacén B del cuartel general."
    },
    {
        "doc_id": "x5",
        "nivel": "RESERVADO",
        "texto": "Lista de proveedores homologados para catering y cafetería interna."
    },
]

consulta_mision3 = "contacto frecuencia operativo handoff nocturno"

# 1. Filtrar documentos por nivel de clasificación (SIGILO)

documentos_filtrados = [
    doc for doc in documentos_mision3
    if doc["nivel"] == "SIGILO"
]

print("=== FASE 1: FILTRADO DE SEGURIDAD (NIVEL SIGILO) ===")

for doc in documentos_filtrados:
    print(f"ID: {doc['doc_id']} | Nivel: {doc['nivel']} | Texto: {doc['texto']}")

# 2. Vectorización del texto filtrado y la consulta

doc_ids_sigilo = [doc["doc_id"] for doc in documentos_filtrados]
textos_sigilo = [doc["texto"] for doc in documentos_filtrados]

vectorizador = TfidfVectorizer()

tfidf_corpus_m3 = vectorizador.fit_transform(textos_sigilo)
tfidf_consulta_m3 = vectorizador.transform([consulta_mision3])

similitudes = cosine_similarity(tfidf_consulta_m3, tfidf_corpus_m3).flatten()

for doc_id, score in zip(doc_ids_sigilo, similitudes):
    print(f"Similitud con {doc_id}: {score:.4f}")

# 3. Ordenar documentos por similitud

ranking = sorted(
    zip(documentos_filtrados, similitudes),
    key=lambda x: x[1],
    reverse=True
)

top_1_doc, top_1_score = ranking[0]

top_id = top_1_doc["doc_id"]
texto_completo = top_1_doc["texto"]

recorte = texto_completo[:120]

print(f"Identificador: {top_id}")
print(f"Similitud:     {top_1_score:.4f}")
print(f"Recorte texto: {recorte}")
```

### Salida

```txt
ID: x2 | Nivel: SIGILO | Texto: Rumor operativo: el contacto cambió frecuencia; verificar handoff nocturno. ###FIN###
ID: x4 | Nivel: SIGILO | Texto: Inventario de papelería y tóner para el almacén B del cuartel general.

Similitud con x2: 0.7252
Similitud con x4: 0.0000

Identificador: x2
Similitud:     0.7252
Recorte texto: Rumor operativo: el contacto cambió frecuencia; verificar handoff nocturno. ###FIN###
```

---

# Análisis del Analista

## Reflexiones Finales

### 1. Sobre la Investigación — Misión 1

**Pregunta:**  
Explica con tus propias palabras qué es un índice invertido y por qué la intersección de *postings* implementa un `AND` booleano en este modelo.

**Respuesta:**  
Un índice invertido es una estructura de datos que funciona de manera similar al índice analítico que aparece al final de un libro técnico. En lugar de tomar un documento y leerlo por completo para verificar qué palabras contiene mediante una búsqueda secuencial, el índice invertido mapea cada palabra única del vocabulario con una lista ordenada de los identificadores de los documentos donde aparece. Esta lista se conoce como *postings list*.

Cuando se ejecuta una consulta con el operador lógico `AND`, por ejemplo:

```txt
agente AND red
```

el sistema no vuelve a leer todos los textos. En su lugar, toma la lista de documentos donde aparece el término `agente` y la lista donde aparece el término `red`, para después buscar los elementos que se repiten en ambas.

Matemáticamente, este proceso corresponde a una **intersección de conjuntos**. Si un identificador de documento no está presente en ambas listas, se descarta. De esta forma, se garantiza que únicamente los reportes que contienen ambos términos sobrevivan al filtro.

---

### 2. Sobre TF-IDF — Misión 2

**Pregunta:**  
¿Por qué un término muy frecuente en todos los documentos suele discriminar peor que un término raro pero presente en pocos? Relaciona tu explicación con `idf`.

**Respuesta:**  
La capacidad de discriminación de una palabra depende de su rareza dentro de la colección de documentos. Si una palabra aparece en todos los documentos, como ocurre con preposiciones o términos demasiado genéricos, no ayuda realmente a distinguir cuál documento es más relevante para la búsqueda del usuario.

Por el contrario, un término raro, como `fotoluminiscente` o `evacuación`, puede funcionar como una firma más específica. Esto reduce el espacio de búsqueda y permite identificar con mayor precisión los documentos relevantes.

Este comportamiento se fundamenta en el componente `IDF`, es decir, *Inverse Document Frequency*. La fórmula del `IDF` calcula el logaritmo del total de documentos dividido entre la cantidad de documentos que contienen el término.

Por ejemplo, si una palabra aparece en los 5 documentos del corpus:

```txt
5 / 5 = 1
```

y el logaritmo de `1` es `0`, entonces el peso `IDF` de esa palabra se reduce considerablemente o se anula.

En cambio, si un término aparece en un solo documento, el denominador es pequeño, el resultado de la división es más alto y el `IDF` le asigna un peso mayor. Esto provoca que dicho término tenga más influencia al momento de calcular la relevancia del documento dentro del ranking.

---

### 3. Sobre la Lógica de Recuperación — Misión 3

**Pregunta:**  
Si aplicaras TF-IDF a toda la colección, sin filtrar por `SIGILO`, ¿cómo podría cambiar el documento top-1 y por qué el filtro actúa como una llave de acceso antes del ranking?

**Respuesta:**  
Si se omitiera el filtro de seguridad y se aplicara TF-IDF a toda la colección, el documento top-1 podría cambiar de manera significativa por coincidencias estadísticas. Por ejemplo, un documento de nivel `PUBLICO` o `RESERVADO` podría contener términos como `contacto` o `frecuencia` en un contexto completamente distinto.

Un documento público podría hablar de la frecuencia de paso de autobuses o de un teléfono de contacto, y aun así obtener una puntuación alta si comparte términos con la consulta. Si ese documento repitiera más veces esas palabras, su similitud coseno podría superar a la del documento realmente relevante de nivel `SIGILO`.

Por esta razón, el filtro por nivel actúa como una **llave de acceso** o una restricción estricta antes de que el algoritmo de ranking entre en funcionamiento. En sistemas reales de recuperación de información, la seguridad no debe depender de una puntuación de similitud, sino de una regla binaria.

El filtro reduce el espacio de búsqueda y asegura dos aspectos principales:

1. **Confidencialidad:**  
   Evita que un analista sin credenciales vea fragmentos de información sensible en los resultados.

2. **Precisión operativa:**  
   Permite que el algoritmo estadístico, en este caso TF-IDF, trabaje únicamente sobre el conjunto de datos que es legal, válido y relevante para la misión.

---