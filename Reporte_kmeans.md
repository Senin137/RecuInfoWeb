# Reporte: Agrupación de Tweets con K-Means y TF-IDF

## 1. Introducción

En esta práctica se implementó un modelo de agrupamiento utilizando **K-Means** para organizar tweets en diferentes grupos o *clusters*. El objetivo principal fue analizar si el modelo podía separar correctamente textos relacionados con cuatro temas principales:

- Deportes
- Tecnología
- Comida
- Entretenimiento

Para transformar los textos en datos numéricos, se utilizó **TF-IDF** mediante `TfidfVectorizer`. Posteriormente, los vectores generados fueron procesados por el algoritmo **K-Means**, configurado para crear cuatro clusters.

Es importante mencionar que K-Means es un modelo de aprendizaje no supervisado. Esto significa que el modelo no recibe etiquetas reales durante el entrenamiento, sino que intenta encontrar patrones o similitudes entre los textos a partir de sus características numéricas.

Por esta razón, aunque en el reporte se utilice la palabra “clasificar” para describir el resultado esperado, técnicamente el modelo no clasifica como lo haría un algoritmo supervisado. En realidad, **K-Means agrupa los textos en clusters** y después estos clusters pueden ser interpretados por el usuario.

---

## 2. Descripción general del código

El código se divide en varias etapas principales:

1. Importación de librerías.
2. Carga de stopwords en español.
3. Creación del corpus de tweets.
4. Vectorización de los textos con TF-IDF.
5. Aplicación del algoritmo K-Means.
6. Visualización de los resultados.
7. Análisis de palabras clave por cluster.

---

## 3. Importación de librerías

Primero se importaron las librerías necesarias para procesar texto, aplicar el modelo de agrupamiento y graficar los resultados.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
```

También se descargaron las stopwords en español mediante NLTK:

```python
nltk.download('stopwords')

stopwords_es = stopwords.words('spanish')
```

Las **stopwords** son palabras comunes del idioma, como:

```text
de, la, el, con, para, que, es, en
```

Estas palabras normalmente no aportan demasiado significado temático en una tarea de análisis de texto, por lo que suelen eliminarse para reducir ruido.

---

## 4. Creación del corpus

El corpus inicial estaba formado por 24 tweets divididos manualmente en cuatro grupos:

```text
6 tweets de deportes
6 tweets de tecnología
6 tweets de comida
6 tweets de entretenimiento
```

Aunque estas categorías eran claras para una persona, esto no significa que fueran igual de claras para el modelo. K-Means no entiende directamente que un texto pertenece a “deportes”, “tecnología”, “comida” o “entretenimiento”. El algoritmo únicamente analiza las palabras que aparecen en cada tweet y calcula similitudes entre los vectores numéricos generados.

El corpus original contenía ejemplos como:

```text
Gran partido de fútbol ayer, el gol fue increíble
Python es el mejor lenguaje para aprender a programar
Las tacos de pastor de aquí son los mejores
La nueva película de Marvel es espectacular
```

Para una persona, estos textos pertenecen a categorías distintas. Sin embargo, para el modelo, la separación depende de las palabras que comparten entre sí y de la forma en que TF-IDF representa esas palabras.

---

## 5. Vectorización con TF-IDF

Para convertir los tweets en datos numéricos, se utilizó `TfidfVectorizer`.

```python
vectorizador = TfidfVectorizer(
    stop_words=stopwords_es,
    max_features=100,
    lowercase=True
)
```

TF-IDF significa **Term Frequency - Inverse Document Frequency**. Esta técnica asigna un peso a cada palabra dependiendo de dos factores:

- Qué tan frecuente es una palabra dentro de un documento.
- Qué tan rara o común es esa palabra dentro del corpus completo.

El resultado es una matriz donde:

- Cada fila representa un tweet.
- Cada columna representa una palabra o característica textual.
- Cada valor representa el peso TF-IDF de esa palabra en ese tweet.

Por ejemplo, si la palabra `fútbol` aparece en varios tweets deportivos, puede ayudar a que esos textos sean considerados similares. En cambio, si los tweets de una misma categoría no comparten palabras importantes, el modelo tendrá dificultades para agruparlos correctamente.

---

## 6. Aplicación de K-Means

Después de convertir los textos en vectores numéricos, se aplicó el algoritmo K-Means.

```python
k = 4

kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
kmeans.fit(X)

etiquetas = kmeans.labels_
```

El parámetro:

```python
n_clusters=4
```

indica que el modelo debe formar cuatro grupos. Sin embargo, esto no significa que el modelo sepa que esos grupos deben corresponder a:

```text
Deportes
Tecnología
Comida
Entretenimiento
```

K-Means solamente intenta formar cuatro agrupaciones basándose en la distancia entre los vectores. Por lo tanto, los números de cluster son arbitrarios.

Por ejemplo:

```text
Cluster 0
Cluster 1
Cluster 2
Cluster 3
```

no tienen un significado fijo. Un cluster puede contener textos de comida, deportes o una mezcla de varias categorías, dependiendo de la similitud calculada por el modelo.

---

## 7. Visualización de los resultados

Para poder graficar los resultados, se redujo la dimensionalidad de los datos usando `TruncatedSVD`.

```python
from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=2, random_state=42)
X_2d = svd.fit_transform(X)
```

Esto permitió representar los tweets en una gráfica de dos dimensiones.

En la gráfica:

- Cada punto representa un tweet.
- El color representa el cluster asignado por K-Means.
- La posición del punto depende de la representación reducida de los vectores TF-IDF.

Es importante aclarar que la gráfica es una proyección en 2D. El modelo realmente trabaja con vectores de muchas dimensiones, por lo que la visualización no representa perfectamente todas las distancias originales. Sin embargo, sirve para observar tendencias generales en la agrupación de los textos.

---

## 8. Problema principal detectado

El modelo no agrupaba correctamente los tweets porque el problema principal no estaba en la ejecución del algoritmo, sino en el corpus utilizado.

El corpus original contenía textos muy cortos y con poco vocabulario compartido dentro de una misma categoría. Esto afectó directamente la forma en que TF-IDF generó los vectores.

Por ejemplo, en la categoría de entretenimiento se incluyeron tweets sobre:

```text
Marvel
Stranger Things
Conciertos
The Crown
Pink Floyd
Dune
```

Para una persona, todos estos elementos pueden pertenecer a la categoría “entretenimiento”. Sin embargo, para TF-IDF son palabras muy diferentes. El modelo no comprende que Marvel, Dune, Pink Floyd y Stranger Things pertenecen al mismo campo semántico.

K-Means no trabaja con significado profundo, sino con vectores numéricos. Por lo tanto, si los textos de una misma categoría no comparten palabras similares, el modelo puede interpretarlos como textos no relacionados.

---

## 9. Por qué K-Means no agrupaba correctamente

Aunque se buscaba que el modelo separara los tweets en categorías claras, K-Means no realiza clasificación supervisada. El algoritmo no conoce las etiquetas reales de los textos.

Indicar:

```python
n_clusters = 4
```

solo significa que el modelo debe crear cuatro grupos. No significa que esos grupos correspondan automáticamente a:

```text
Cluster 0 = Deportes
Cluster 1 = Tecnología
Cluster 2 = Comida
Cluster 3 = Entretenimiento
```

El problema se debe principalmente a los siguientes factores:

1. Los tweets eran demasiado cortos.
2. Había pocos ejemplos por categoría.
3. Las categorías no compartían suficiente vocabulario interno.
4. Algunas palabras aparecían en varios contextos.
5. TF-IDF analiza palabras, no significado semántico profundo.
6. K-Means agrupa por distancia numérica, no por categorías humanas.
7. Los números de cluster son arbitrarios y deben interpretarse después del entrenamiento.

---

## 10. Importancia del corpus

El corpus es una parte fundamental en los modelos de procesamiento de lenguaje natural. En este caso, el desempeño del modelo dependió directamente de la calidad de los textos utilizados.

El dataset original estaba organizado de acuerdo con categorías humanas, pero no necesariamente de acuerdo con similitud léxica.

Es decir, las categorías tenían sentido para una persona, pero no necesariamente para un algoritmo basado en TF-IDF.

Por ejemplo:

```text
Marvel
Dune
Pink Floyd
Stranger Things
```

pueden pertenecer a entretenimiento, pero no comparten suficientes palabras entre sí. Por eso el modelo puede separarlos en clusters diferentes.

En cambio, al agregar palabras como:

```text
entretenimiento
cine
serie
música
libro
```

los textos comienzan a compartir señales más claras y el algoritmo puede agruparlos mejor.

---

## 11. Comparación de resultados

Se realizaron tres pruebas principales para analizar el comportamiento del modelo:

1. Dataset original con stopwords en español.
2. Dataset original sin stopwords.
3. Dataset corregido con palabras clave y stopwords.

---

## 11.1 Primera prueba: dataset original con stopwords en español

En la primera gráfica se utilizó el dataset original y se eliminaron las stopwords en español.

![Primera prueba: dataset original con stopwords](./images/prueba1.png)

El resultado mostró clusters poco coherentes. Algunos textos de diferentes categorías aparecieron mezclados en una misma zona de la gráfica. También se observaron puntos aislados, como tweets relacionados con Pink Floyd, Dune, Messi o procesadores.

Esto ocurrió porque, aunque se eliminaron palabras comunes del español, el corpus seguía sin tener suficiente vocabulario compartido por categoría.

Por ejemplo, dentro de entretenimiento había textos sobre:

```text
Películas
Series
Música
Libros
Conciertos
```

Aunque todos pertenecen a entretenimiento desde una perspectiva humana, para el modelo son documentos distintos porque contienen palabras diferentes.

En esta primera prueba, el modelo intentó agrupar los tweets por palabras específicas, no por el tema general esperado.

---

## 11.2 Segunda prueba: dataset original sin stopwords

En la segunda gráfica se utilizó el mismo dataset original, pero sin eliminar stopwords.

![Segunda prueba: dataset original sin stopwords](./images/prueba2.png)

El resultado tampoco mejoró. Al conservar palabras comunes como:

```text
de
la
el
con
para
que
es
```

el modelo también las consideró dentro del cálculo TF-IDF. Estas palabras no aportan mucho significado temático, pero pueden aparecer en muchos textos de distintas categorías.

Esto puede provocar similitudes artificiales entre tweets que realmente no tratan del mismo tema. Por ejemplo, dos textos de categorías distintas pueden parecer cercanos porque comparten palabras comunes del idioma, no porque pertenezcan al mismo grupo temático.

En esta prueba, los puntos se distribuyeron de forma diferente, pero los clusters siguieron mezclando categorías como deportes, tecnología, comida y entretenimiento.

Esto demuestra que quitar o dejar stopwords no soluciona el problema si el corpus no tiene señales temáticas claras.

---

## 11.3 Tercera prueba: dataset corregido con palabras clave y stopwords

En la tercera gráfica se utilizó un dataset modificado. A cada grupo se le agregaron palabras clave o palabras ancla para reforzar la relación entre los textos de una misma categoría.

![Tercera prueba: dataset corregido con palabras clave](./images/prueba3.png)

Algunos ejemplos de palabras agregadas fueron:

```text
Fútbol deporte
Tecnología software
Tecnología hardware
Comida cocina
Comida restaurante
Entretenimiento cine
Entretenimiento serie
Entretenimiento música
```

Esta modificación permitió que los textos de una misma categoría compartieran vocabulario más representativo.

El resultado fue mucho más coherente. En la gráfica se observaron grupos mejor separados:

```text
Los textos de deportes se agruparon en una zona similar.
Los textos de entretenimiento se concentraron en otra región.
Los textos de tecnología quedaron más cercanos entre sí.
Los textos de comida formaron un grupo más definido.
```

Esto ocurrió porque TF-IDF ahora podía generar vectores más parecidos entre textos de la misma categoría. Al existir palabras clave repetidas dentro de cada tema, K-Means pudo calcular mejor la similitud entre los documentos.

---

## 12. Interpretación de las gráficas

Las gráficas muestran una proyección en dos dimensiones de los vectores generados por TF-IDF. Para poder visualizar los datos, se utilizó una reducción de dimensionalidad mediante SVD.

En las primeras dos gráficas, los clusters aparecen mezclados porque el corpus original no ofrecía suficientes señales lingüísticas. Los textos estaban organizados por categorías humanas, pero no compartían suficiente vocabulario temático.

En la tercera gráfica se observa una separación más clara porque el corpus fue reforzado con palabras representativas de cada categoría.

Esto demuestra que el rendimiento del modelo no depende únicamente del algoritmo, sino también de cómo se construye y representa el conjunto de datos.

---

## 13. Diferencia entre stopwords y palabras clave

La eliminación de stopwords ayuda a reducir ruido, pero no garantiza que los clusters sean correctos.

Por ejemplo, eliminar palabras como:

```text
de, la, el, con, para
```

puede mejorar la limpieza del texto, pero si los textos de una misma categoría no comparten palabras relevantes, el modelo seguirá teniendo problemas para agruparlos.

Por otro lado, agregar palabras clave como:

```text
fútbol
deporte
tecnología
software
comida
cocina
entretenimiento
cine
```

sí ayuda directamente a que los textos de una misma categoría tengan una representación más parecida.

Por eso, la tercera prueba obtuvo mejores resultados que las dos primeras.

---

## 14. Mejoras aplicadas

Para mejorar los resultados del modelo se propusieron varias modificaciones.

---

### 14.1 Agregar palabras ancla

Se agregaron términos representativos a cada categoría, como:

```text
Fútbol deporte
Tecnología software
Comida cocina
Entretenimiento cine
```

Esto permitió aumentar la similitud entre textos de una misma categoría.

---

### 14.2 Usar n-gramas

También se recomendó usar:

```python
ngram_range=(1, 2)
```

Esto permite que el vectorizador considere palabras individuales y combinaciones de dos palabras.

Por ejemplo:

```text
machine learning
inteligencia artificial
obra maestra
salsa tomate
```

Estas combinaciones pueden aportar más información que las palabras aisladas.

---

### 14.3 Normalizar el texto

También se recomendó normalizar los textos para reducir variaciones innecesarias.

Por ejemplo:

```text
Actualizé → actualice
fútbol → futbol
```

La normalización ayuda a que palabras con acentos o pequeñas variaciones no sean tratadas como términos completamente diferentes.

---

### 14.4 Aumentar la cantidad de ejemplos

El corpus original tenía únicamente seis tweets por categoría, lo cual es poco para que un modelo no supervisado encuentre patrones sólidos.

Una mejora importante sería utilizar más ejemplos por categoría, idealmente entre 30 y 50 textos como mínimo por tema.

---

### 14.5 Interpretar los clusters después del entrenamiento

Debido a que K-Means no asigna nombres a los clusters, es necesario interpretar los resultados después del entrenamiento.

Esto puede hacerse revisando:

- Los textos dentro de cada cluster.
- Las palabras clave más importantes de cada cluster.
- La coherencia temática de los documentos agrupados.
- La comparación con las categorías esperadas, si se tienen como referencia.

---

## 15. Análisis de palabras clave por cluster

El código también permite mostrar las palabras más importantes de cada cluster.

```python
nombres_palabras = vectorizador.get_feature_names_out()
centroides = kmeans.cluster_centers_

for cluster_id in range(k):
    indices_top = centroides[cluster_id].argsort()[-5:][::-1]
    palabras_top = [nombres_palabras[i] for i in indices_top]
    print(f"Cluster {cluster_id}: {', '.join(palabras_top)}")
```

Este análisis es útil porque permite interpretar qué representa cada grupo.

Por ejemplo, si un cluster contiene palabras como:

```text
fútbol, gol, partido, liga, mundial
```

se puede interpretar que ese cluster probablemente corresponde a deportes.

Si otro cluster contiene palabras como:

```text
tecnología, software, python, laptop, procesador
```

se puede interpretar que ese grupo corresponde a tecnología.

---

## 16. Conclusión

El modelo de K-Means no agrupaba correctamente los clusters debido principalmente a la estructura del corpus original. Aunque los tweets estaban organizados en categorías claras para una persona, los textos no compartían suficiente vocabulario representativo dentro de cada grupo.

K-Means, al ser un algoritmo no supervisado, no conoce las categorías reales de los textos. El modelo únicamente agrupa documentos según la distancia entre sus vectores numéricos. Por esta razón, si los textos de una misma categoría tienen vocabulario muy diferente, el algoritmo puede separarlos o mezclarlos con otros grupos.

La comparación entre las tres pruebas permitió observar que eliminar stopwords no era suficiente para resolver el problema. El cambio más importante fue mejorar el corpus agregando palabras clave o palabras ancla que reforzaran la similitud entre textos de la misma categoría.

En la tercera prueba, al agregar términos como:

```text
Fútbol deporte
Tecnología software
Comida cocina
Entretenimiento cine
```

los clusters se agruparon de manera más coherente. Esto demuestra que, en modelos basados en TF-IDF y K-Means, la calidad del corpus y la presencia de vocabulario representativo son factores esenciales para obtener buenos resultados.

Por lo tanto, el algoritmo funcionaba correctamente, pero necesitaba un corpus mejor estructurado para poder formar clusters más cercanos a las categorías esperadas.

---

## 17. Recomendaciones finales

Para mejorar futuros resultados con K-Means en textos, se recomienda:

- Utilizar un corpus más grande.
- Asegurar que los textos de una misma categoría compartan palabras representativas.
- Eliminar stopwords para reducir ruido.
- Usar n-gramas para capturar frases importantes.
- Normalizar acentos, signos y mayúsculas.
- Interpretar los clusters después del entrenamiento.
- Recordar que K-Means no clasifica con etiquetas, sino que agrupa por similitud.
- Considerar embeddings semánticos si se desea capturar significado más profundo entre textos.

---

## 18. Reflexión final

Esta práctica permitió comprobar que el funcionamiento de un modelo de agrupamiento de texto no depende únicamente del algoritmo utilizado. También depende de la calidad del corpus, del preprocesamiento y de la representación numérica de los textos.

K-Means puede ser útil para descubrir grupos dentro de un conjunto de documentos, pero necesita que existan patrones claros en los datos. Cuando los textos son muy cortos, variados o con poco vocabulario compartido, el modelo puede generar clusters poco coherentes.

Por esta razón, antes de aplicar un algoritmo de clustering en procesamiento de lenguaje natural, es fundamental revisar el corpus, limpiar los datos y asegurarse de que los textos contengan señales suficientes para que el modelo pueda detectar similitudes reales.