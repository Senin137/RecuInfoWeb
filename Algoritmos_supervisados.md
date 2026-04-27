

# Algoritmos supervisados

## Naive Bayes
El clasificador Naïve Bayes es un algoritmo de aprendizaje automático supervisado que se utiliza para tareas de clasificación, como la clasificación de texto. Utiliza principios de probabilidad para realizar tareas de clasificación.

El teorema de Bayes establece la siguiente relación, dada la variable de clase y vector de características dependientes $X_1$ a través de $X_n$ :

$$
P(y \mid x_1, \ldots, x_n) =
\frac{P(y)P(x_1, \ldots, x_n \mid y)}
{P(x_1, \ldots, x_n)}
$$

La función de clasificación ingenua de Bayes se encuentra en varias librerías de R: `naivebayes`, en el paquete `e1071` y en otros.

El modelo bayesiano de probabilidad condicionada se representa como:

$$
P(A \mid B) = \frac{P(A \cap B)}{P(B)}
$$

Es decir, la probabilidad de que se dé el caso $A$ dado $B$ es igual a la probabilidad de la intersección $A$ con $B$, es decir, $A \cap B$, partida entre la probabilidad de $B$.

Estirando esta formulación, llegaríamos al teorema de Bayes, cuya expresión más típica es la siguiente:

$$
P(A \mid B) = \frac{P(B \mid A) \cdot P(A)}{P(B)}
$$

### Tipos de clasificadores Naive Bayes
No hay un solo tipo de clasificador Naïve Bayes. Los tipos más populares difieren en función de las distribuciones de los valores de las características. Por ejemplo:

Naïve Bayes gaussiano (GaussianNB): esta es una variante del clasificador Naïve Bayes, que se utiliza con distribuciones gaussianas, es decir, distribuciones normales, y variables continuas. Este modelo se ajusta encontrando la media y la desviación estándar de cada clase.
Naïve Bayes multinomial (MultinomialNB): este tipo de clasificador Naïve Bayes supone que las características provienen de distribuciones multinomiales. Esta variante es útil cuando se utilizan datos discretos, como recuentos de frecuencia, y normalmente se aplica dentro de casos de uso de procesamiento de lenguaje natural, como la clasificación de spam.
Naïve Bayes para modelos Bernoulli (BernoulliNB): esta es otra variante del clasificador Naïve Bayes, que se utiliza con variables booleanas, es decir, variables con dos valores, como Verdadero y Falso o 1 y 0.

Ahora, imaginemos un caso de uso de **clasificación de texto** para ilustrar cómo funciona el algoritmo **Naïve Bayes**.

Imagina un proveedor de correo electrónico que busca mejorar su filtro de spam. Los datos de entrenamiento consistirían en palabras de correos electrónicos que se han clasificado como **"spam"** o **"no spam"**. A partir de ahí, se calculan las probabilidades condicionales de clase y las probabilidades previas para obtener la **probabilidad posterior**.

El clasificador **Naïve Bayes** operará devolviendo la clase que tiene la máxima probabilidad posterior de un grupo de clases (es decir, **"spam"** o **"no spam"**) para un correo electrónico determinado.

Este cálculo se representa con la siguiente fórmula:

$$
\hat{y} = \arg\max_{y \in Y} P(y \mid x)
= \arg\max \frac{P(x \mid y)P(y)}{P(x)}
$$

**Probabilidades condicionales de clase**
Para desglosar esto un poco más, profundizaremos un nivel más en las partes individuales que componen esta fórmula. Las probabilidades condicionales de clase son las probabilidades individuales de cada palabra en un correo electrónico. Se calculan determinando la frecuencia de cada palabra para em categoría, es decir, “spam” o “not spam”, que también se conoce como estimación de máxima verosimilitud (MLE). En este ejemplo, si estuviéramos examinando la frase "Estimado señor", simplemente calcularíamos la frecuencia con la que esas palabras aparecen en todo el correo electrónico spam y no spam. Esto se puede representar mediante la siguiente fórmula, donde y es "Estimado señor" y x es "spam".

## Máquinas de Vectores de Soporte (SVM)

Una máquina de vectores de soporte (SVM) es un algoritmo de aprendizaje automático supervisado que clasifica los datos al encontrar una línea o hiperplano óptimo que maximice la distancia entre cada clase en un espacio N-dimensional.

Las SVM fueron desarrolladas en la década de 1990 por Vladimir N. Vapnik y sus colegas, y publicaron este trabajo en un artículo titulado "Support Vector Method for Function Approximation, Regression Estimation, and Signal Processing"1 en 1995.

Las SVM se emplean comúnmente en problemas de clasificación. Distinguen entre dos clases encontrando el hiperplano óptimo que maximiza el margen entre los puntos de datos más cercanos de clases opuestas. El número de características en los datos de entrada determina si el hiperplano es una línea en un espacio bidimensional o un plano en un espacio n-dimensional. Dado que se pueden encontrar múltiples hiperplanos para diferenciar clases, la maximización del margen entre puntos permite al algoritmo encontrar la mejor frontera de decisión entre clases. Esto, a su vez, le permite generalizar bien nuevos datos y hacer predicciones de clasificación precisas. Las líneas adyacentes al hiperplano óptimo se conocen como vectores de soporte, ya que estos vectores atraviesan los puntos de datos que determinan el margen máximo.

El algoritmo SVM se emplea ampliamente en el aprendizaje automático ya que puede manejar tareas de clasificación tanto lineales como no lineales. Sin embargo, cuando los datos no son separables linealmente, las funciones del kernel se utilizan para transformar el espacio multidimensional de los datos y permitir la separación lineal. A esta aplicación de las funciones del kernel (o núcleo) se le conoce como el “truco del kernel”, y la elección de funciones del kernel, como núcleos lineales, núcleos polinomiales, núcleos de función de base radial (RBF, sigla en inglés de radial basis function) o núcleos sigmoides, depende de las características de los datos y del caso de uso específico.

## Regresión logística
La regresión logística es un algoritmo de aprendizaje supervisado de machine learning en ciencia de datos. Es un tipo de algoritmo de clasificación que predice un resultado discreto o categórico. Por ejemplo, podemos utilizar un modelo de clasificación para determinar si un préstamo se aprueba o no en función de predictores como la cantidad de ahorros, los ingresos y la puntuación crediticia.

En este artículo, nos sumergimos en las matemáticas detrás de la regresión logística, uno de los algoritmos de clasificación más utilizados en el machine learning y la inteligencia artificial (IA). También profundizaremos en los detalles del análisis de regresión, los casos de uso y los diferentes tipos de regresiones logísticas. En la era de la IA generativa, los cimientos que sustentan la regresión logística siguen desempeñando un papel crítico en la orquestación de modelos complejos de Neural Networks. La regresión logística también sigue siendo muy relevante para realizar pruebas estadísticas en el contexto de la investigación en ciencias sociales y del comportamiento, y en el campo de la ciencia de datos en general. Podemos implementar la regresión logística fácilmente mediante el uso del módulo scikit-learn en Python.  

## Random Forest
Random forest, o bosque aleatorio, es un algoritmo de aprendizaje automático de uso común, registrado por Leo Breiman y Adele Cutler, que combina el resultado de múltiples árboles de decisión para llegar a un resultado único. Su facilidad de uso y flexibilidad han impulsado su adopción, ya que maneja problemas de clasificación y regresión.

**Árboles de decisión**
Dado que el modelo de bosque aleatorio se compone de varios árboles de decisión, sería útil empezar describiendo brevemente el algoritmo del árbol de decisión. Los árboles de decisión comienzan con una pregunta básica, como "¿Debería navegar?" A partir de ahí, puede hacer una serie de preguntas para determinar una respuesta, como "¿El oleaje es prolongado?" o "¿Hay viento en alta mar?". Estas preguntas constituyen los nodos de decisión en el árbol, que funcionan como un medio para dividir los datos. Cada pregunta ayuda a un individuo a llegar a una decisión final, que sería señalada por el nodo hoja. Las observaciones que cumplan con los criterios seguirán el ramal "Sí" y las que no, seguirán la ruta alternativa. Los árboles de decisión buscan encontrar la mejor división para los subconjuntos de datos y, por lo general, se entrenan a través del algoritmo del árbol de clasificación y regresión (CART). Las métricas, como la impureza de Gini, la ganancia de información o el error cuadrático medio (MSE), pueden utilizarse para evaluar la calidad de la división.

Este árbol de decisión es un ejemplo de un problema de clasificación, donde las etiquetas de clase son "navegar" y "no navegar".

Si bien los árboles de decisión son algoritmos comunes de aprendizaje supervisado, pueden ser proclives a presentar problemas, como sesgos y sobreajuste. Sin embargo, cuando varios árboles de decisión forman un conjunto en el algoritmo de bosque aleatorio, predicen resultados más precisos, en especial cuando los árboles de decisión individuales no están correlacionados entre sí.

**Métodos de conjunto**
Los métodos de aprendizaje por conjuntos se componen de un conjunto de clasificadores, por ejemplo árboles de decisión, y sus predicciones se agregan para identificar el resultado más popular. Los métodos de conjunto más conocidos son el bagging (embolsado), también conocido como bootstrapping (o agregación de arranque), y el boostin (o estímulo). En 1996, Leo Breiman introdujo el método de embolsado; en este método, se selecciona una muestra aleatoria de datos en un conjunto de entrenamiento con reemplazo, lo que significa que los puntos de datos individuales se pueden elegir más de una vez. Después de generar varias muestras de datos, estos modelos se entrenan de forma independiente y en función del tipo de tarea, es decir. regresión o clasificación: el promedio o la mayoría de esas predicciones arrojan una estimación más precisa. Este enfoque se utiliza comúnmente para reducir la varianza dentro de un conjunto de datos ruidoso.

**¿Cómo Funciona?**
Los algoritmos de bosque aleatorio tienen tres hiperparámetros principales, que deben configurarse antes del entrenamiento. Estos incluyen el tamaño del nodo, la cantidad de árboles y la cantidad de características muestreadas. A partir de ahí, el clasificador de bosque aleatorio se puede utilizar para resolver problemas de regresión o clasificación.

El algoritmo de bosque aleatorio se compone de una colección de árboles de decisión y cada árbol en el conjunto está compuesto por una muestra de datos extraída de un conjunto de entrenamiento con reemplazo, llamado bootstrapping. De esa muestra de entrenamiento, un tercio de ella se reserva como datos de prueba, lo que se conoce como la muestra fuera de bolsa (oob), a la que volveremos más adelante. Luego, se inyecta otra instancia de aleatoriedad mediante el embolsado de características, lo que agrega más diversidad al conjunto de datos y reduce la correlación entre los árboles de decisión. Dependiendo del tipo de problema, la determinación de la predicción variará. Para una tarea de regresión, se promediarán los árboles de decisión individuales, y para una tarea de clasificación, el voto mayoritario, es decir, la variable categórica más frecuente, arrojará la clase prevista. Finalmente, la muestra fuera de la bolsa (oob) se utiliza para la validación cruzada, finalizando esa predicción.

## k-nearest neighbors

**¿Qué es el algoritmo KNN?**
El algoritmo de k-nearest neighbors (KNN) es un clasificador de aprendizaje supervisado no paramétrico, que emplea la proximidad para realizar clasificaciones o predicciones sobre la agrupación de un punto de datos individual. Es uno de los clasificadores de clasificación y regression más populares y sencillos que se emplean actualmente en machine learning.

Si bien el algoritmo KNN se puede usar para problemas de regresión o clasificación, generalmente se usa como un algoritmo de clasificación, partiendo del supuesto de que se pueden encontrar puntos similares cerca uno del otro.

En los problemas de clasificación, la etiqueta de clase se asigna por mayoría de votos, es decir, se emplea la etiqueta que se representa con más frecuencia en torno a un punto de datos determinado. Aunque técnicamente se considera "votación por pluralidad", el término "votación por mayoría" se emplea más comúnmente en las publicaciones al respecto. La distinción entre estas terminologías es que la "votación por mayoría" requiere técnicamente una mayoría superior al 50%, lo que funciona sobre todo cuando sólo hay dos categorías. Cuando hay varias clases, por ejemplo, cuatro categorías, usted no requiere necesariamente el 50% de los votos para llegar a una conclusión sobre una clase, ya que podría asignar una etiqueta de clase con un voto superior al 25%. 

Los problemas de regression emplean un concepto similar al de los problemas de clasificación, pero en este caso se toma el promedio de los 'k-nearest neighbors' para hacer una predicción sobre una clasificación. La principal distinción es que la clasificación se emplea para valores discretos, mientras que regression se emplea con valores continuos. Sin embargo, antes de hacer una clasificación, hay que definir la distancia. La distancia euclidiana es la más empleada, en la que profundizaremos más adelante.

Cabe señalar que el algoritmo KNN también forma parte de una familia de modelos de "aprendizaje perezoso", lo que significa que sólo almacena un conjunto de datos de entrenamiento en lugar de someterse a una fase de entrenamiento. Esto también significa que todo el cálculo se produce cuando se realiza una clasificación o predicción. Dado que depende en gran medida de la memoria para almacenar todos sus datos de entrenamiento, también se denomina método de aprendizaje basado en instancias o en la memoria.

**K-vecinos más cercanos y Python**
Para profundizar, puede aprender más sobre el algoritmo k-NN empleando Python y scikit-learn (también conocido como sklearn). Nuestro tutorial en Watson Studio lo ayuda a aprender la sintaxis básica de esta biblioteca, que también contiene otras bibliotecas populares, como NumPy, pandas y Matplotlib. El siguiente código es un ejemplo de cómo crear y predecir con un modelo KNN:

from sklearn.neighbors import KNeighborsClassifier

model_name = ‘K-Nearest Neighbor Classifier’

knnClassifier = KNeighborsClassifier(n_neighbors = 5, metric = ‘minkowski’, p=2)

knn_model = Pipeline(steps=[(‘preprocessor’, preprocessorForFeatures), (‘classifier’ , knnClassifier)])

knn_model.fit(X_train, y_train)

y_pred = knn_model.predict(X_test)

# Algoritmos Semisupervisado

## Self-Training (Autoentrenamiento)
El autoaprendizaje es una técnica de aprendizaje semisupervisado en la que un modelo se entrena inicialmente con un pequeño conjunto de datos etiquetados y luego se refina iterativamente utilizando sus propias predicciones.

En cada iteración, el modelo etiqueta las predicciones más fiables sobre los datos sin etiquetar, tratándolas como datos de referencia, y las incluye en el conjunto de entrenamiento.
Este proceso continúa hasta que no se logra ninguna mejora significativa o se utilizan todos los datos sin etiquetar.
El autoaprendizaje resulta especialmente útil cuando la adquisición de datos etiquetados es costosa o difícil, ya que permite aprovechar grandes cantidades de datos sin etiquetar para mejorar el rendimiento del modelo.

**Pasos para el autoaprendizaje**
Entrenamiento con datos etiquetados: Comience con un modelo entrenado con un pequeño conjunto de datos etiquetados.
Generar pseudoetiquetas: Utilice el modelo entrenado para predecir etiquetas para los datos sin etiquetar. Filtre estas predicciones por umbrales de confianza (por ejemplo, acepte solo predicciones con altas probabilidades).
Ampliar los datos de entrenamiento: Añada las muestras pseudoetiquetadas al conjunto de datos etiquetados original.
Refinamiento iterativo: Reentrene el modelo con el conjunto de datos aumentado. Repita el proceso hasta que el rendimiento del modelo converja o se alcance un número predefinido de iteraciones.

**Importancia del autoaprendizaje**
El autoaprendizaje es popular por su simplicidad y eficacia. No requiere modificaciones a los algoritmos de aprendizaje automático existentes y puede implementarse con un mínimo esfuerzo. Entre sus principales ventajas se incluyen:

Utilización de datos sin etiquetar: Aprovecha grandes volúmenes de datos sin etiquetar para mejorar la generalización del modelo.
Independencia de dominio: Funciona en diversos dominios y tareas.
Eficiencia: Puede reducir la necesidad de un etiquetado manual extenso.

**El autoaprendizaje funciona en la práctica.**
Para ilustrar el autoaprendizaje, consideremos una tarea de clasificación binaria:

Se etiqueta un pequeño subconjunto de los datos (por ejemplo, el 10% del conjunto de datos).
Se entrena un modelo de regresión logística con estos datos etiquetados.
El modelo se utiliza para predecir las etiquetas de los datos restantes que no están etiquetados.
Las predicciones con un alto grado de confianza (por ejemplo, aquellas con probabilidades superiores al 95%) se añaden al conjunto de entrenamiento.
El modelo se vuelve a entrenar con el conjunto de datos ampliado y el proceso se repite.

**Implementación del autoaprendizaje en Python**
A continuación se muestra una implementación paso a paso del autoaprendizaje mediante un clasificador de Bosque Aleatorio . El proceso consiste en entrenar un modelo con un pequeño conjunto de datos etiquetados, realizar predicciones con datos sin etiquetar y añadir iterativamente predicciones de alta confianza al conjunto de datos etiquetados.

## Algoritmo de propagación de etiquetas 
El algoritmo de propagación de etiquetas es un algoritmo de gran utilidad que permite encontrar comunidades dentro de un grafo de forma muy veloz. Este detecta las comunidades utilizando la red estructural del grafo como una guía sin necesidad de determinar de forma la información que contienen los miembros de la comunidad a detectar.

Una de las características más interesantes del algoritmo de propagación de etiquetas es que pueden asignarse de forma preliminar algunas etiquetas que nos pueden indicar el rango de soluciones que posee el nodo. Esto significa que pueden utilizarse como un método semi-estructurado para conseguir comunidades especificas y seleccionables para su estudio.

**Características del algoritmo de propagación de etiquetas**
El algoritmo de propagación de etiquetas es de muy reciente data. Este funciona propagando etiquetas asignadas a nodos o vértices dentro de un grafo y conformando comunidades basándose en el proceso de propagación de etiquetas. El algoritmo al funcionar de esta manera permite que una sola etiqueta pueda convertirse rápidamente en un factor dominante dentro de los nodos que están densamente conectados.

El proceso mediante el cual funciona el algoritmo inicia con una etiqueta de una comunidad única que cumple la función de indicador. Estas etiquetas se propagan a través de la red. En cada iteración de propagación cada uno de los nodos del grafo actualiza su etiqueta a la que pertenece el número máximo de vecinos en la estructura. Las conexiones se establecen y cesan de forma uniforme y aleatoria. Este algoritmo alcanza totalmente la convergencia cuando cada nodo posee una etiqueta correspondiente al vértice más cercano o vecino.

**Casos de uso**
Uno de los usos más importantes que puede otorgarse al  algoritmo de propagación de etiquetas se puede encontrar en la red social de microbloggin Twitter. La propagación de etiquetas puede asignarse al estudio de la polaridad de los tweets determinando gustos y preferencias de forma eficiente en base a las reacciones del usuario.

Adicionalmente la propagación de etiquetas se utiliza para estimar combinaciones de elementos que pueden representar contradicciones de asignaciones de información, por ejemplo, puede estudiarse la asignación de tratamiento de fármacos que  con combinaciones potencialmente peligrosas para el paciente basándose en algunos criterios especiales.

## Label Spreading (Difusión de Etiquetas)

El Label Spreading (Difusión de Etiquetas) es un algoritmo de aprendizaje semisupervisado basado en grafos. Su objetivo principal es aprovechar la estructura de los datos para asignar etiquetas a ejemplos que no las tienen, partiendo de un pequeño conjunto de datos que sí están etiquetados.

A diferencia del aprendizaje supervisado tradicional, donde ignoras los datos sin etiqueta, el Label Spreading utiliza la "forma" de la nube de datos para inferir a qué clase pertenecen.

**¿Cómo funciona? El proceso de "Contagio"**
Imagina que tienes una red de puntos. Algunos tienen color (etiquetados) y la gran mayoría son grises (no etiquetados). El Label Spreading funciona bajo la premisa de que puntos cercanos deben tener la misma etiqueta.

Construcción del Grafo: El algoritmo conecta todos los puntos entre sí. La fuerza de la conexión (peso) depende de la similitud; los puntos muy cercanos tienen una conexión fuerte, mientras que los lejanos tienen una conexión casi inexistente.

Matriz de Similitud: Se calcula una matriz de afinidad, comúnmente usando una función de base radial (RBF) o el algoritmo de k-vecinos más cercanos.

Difusión (Iteración): Las etiquetas "se propagan" a través de las conexiones. Un punto etiquetado le "pasa" su color a sus vecinos grises. En la siguiente iteración, esos nuevos puntos coloreados le pasan el color a sus propios vecinos.

Sujeción (Clamping): A diferencia de otros algoritmos (como Label Propagation), el Label Spreading permite que la etiqueta original de un punto cambie ligeramente si el entorno sugiere que es un error (un "ruido"). Esto lo hace más robusto.

**Diferencias clave: Label Spreading vs. Label Propagation**
Aunque ambos son algoritmos de difusión en grafos, el Label Spreading introduce mejoras técnicas importantes:

Regularización: Utiliza una matriz de afinidad normalizada, lo que ayuda a que el algoritmo sea más estable frente a datos con mucho ruido o valores atípicos (outliers).

Flexibilidad de las etiquetas iniciales: Mientras que el Label Propagation suele mantener las etiquetas iniciales fijas (clamping duro), el Label Spreading aplica una pérdida suave, permitiendo que el algoritmo sea menos sensible a errores previos de etiquetado.

## Co-Training (Coentrenamiento)

**¿Qué es la formación conjunta?**
En esencia, el entrenamiento conjunto es una estrategia ingeniosa diseñada para mejorar el rendimiento de los modelos de aprendizaje automático aprovechando múltiples perspectivas de los mismos datos. Imagina que intentas entrenar un modelo para que reconozca si un correo electrónico es spam o no. Normalmente, te basarías en un único conjunto de características, como la frecuencia de las palabras, para determinarlo. Pero ¿qué pasaría si tuvieras información adicional y distinta sobre cada correo electrónico, como el remitente o el asunto? El entrenamiento conjunto te permite utilizar estas diferentes piezas de información (perspectivas) para entrenar múltiples modelos que se ayudan mutuamente a mejorar con el tiempo.

**¿Cómo funciona la formación conjunta?**
La formación conjunta se basa en un principio sencillo pero poderoso: las diferentes perspectivas de los datos pueden proporcionar información complementaria. A continuación, se presenta un desglose paso a paso del proceso de formación conjunta:

Inicializar clasificadores : Divida sus datos en diferentes vistas o conjuntos de características. Por ejemplo, en una tarea de clasificación de texto, una vista podría ser el contenido del correo electrónico, mientras que otra podría ser los metadatos (remitente, fecha y hora, etc.). Entrene clasificadores separados para cada vista utilizando los datos etiquetados disponibles.
Autoaprendizaje : Cada clasificador realiza predicciones sobre los datos sin etiquetar. Se seleccionan las predicciones más fiables y se utilizan como pseudoetiquetas.
Entrenamiento conjunto : Las predicciones fiables de un clasificador se añaden al conjunto de entrenamiento del otro clasificador. A continuación, ambos clasificadores se vuelven a entrenar con estos nuevos ejemplos pseudoetiquetados.
Iterar : Este proceso de autoaprendizaje y coaprendizaje continúa hasta que los modelos convergen o hasta que la mejora se estanca.
Evaluación : Finalmente, evalúe el rendimiento de los clasificadores en un conjunto de prueba independiente para determinar qué tan bien ha funcionado el enfoque de entrenamiento conjunto.

**Por qué la formación conjunta supone un cambio radical**
Entonces, ¿por qué debería entusiasmarte la formación conjunta? Aquí tienes algunas razones convincentes:

Maximiza el uso de datos sin etiquetar : En muchos escenarios reales, obtener datos etiquetados es costoso y requiere mucho tiempo, mientras que los datos sin etiquetar son abundantes. El co-entrenamiento permite aprovechar al máximo estos abundantes datos sin etiquetar, utilizándolos para mejorar el rendimiento del modelo.
Mejora el rendimiento : Al utilizar múltiples vistas de los datos, el entrenamiento conjunto suele lograr un mejor rendimiento que un clasificador único entrenado con una sola vista. La naturaleza complementaria de las vistas contribuye a crear modelos más robustos y precisos.
Mejora la robustez : El entrenamiento conjunto puede ser más resistente a datos etiquetados ruidosos o incompletos. Dado que cada clasificador ayuda a corregir los errores del otro, el sistema en su conjunto se vuelve más robusto.

## Clasificadores basados en SVM

Las S3VM (Semi-Supervised Support Vector Machines), también conocidas como Transductive SVM (TSVM), son una extensión del algoritmo SVM tradicional diseñada para aprovechar tanto los datos etiquetados como los no etiquetados en la construcción del hiperplano de separación.

Su filosofía principal es la Asunción de Bajo Densidad: el hiperplano debe pasar por una región donde haya pocos datos (un "hueco" entre clústeres), asumiendo que los datos de una misma clase tienden a agruparse.

¿En qué se diferencia de una SVM convencional?
En una SVM supervisada, solo buscas maximizar el margen entre las clases etiquetadas. Si tienes pocos datos, el margen puede ser muy estrecho o estar mal orientado.

En una S3VM, el algoritmo intenta encontrar una posición para el hiperplano que:

Maximice el margen respecto a los datos etiquetados.

Mantenga el hiperplano lejos de las zonas de alta densidad de los datos no etiquetados.

El Proceso de Optimización
El funcionamiento matemático es más complejo que el de una SVM estándar porque se convierte en un problema de optimización combinatoria. Los pasos conceptuales son:

Entrenamiento Inicial: Se entrena una SVM estándar usando solo los pocos datos etiquetados disponibles.

Etiquetado Tentativo: El modelo predice etiquetas para los datos no etiquetados basándose en su posición respecto al hiperplano inicial.

Ajuste del Hiperplano: El algoritmo mueve el hiperplano para maximizar el margen total, tratando las etiquetas tentativas como si fueran reales, pero permitiendo que cambien si eso mejora el margen global.

Iteración: Se repite el proceso (usualmente mediante algoritmos como Local Search o Branch and Bound) hasta que las etiquetas de los datos no etiquetados se estabilizan.

# ¿Cual de estos usaría Netflix para su algortimo de recomendación?

El motor de recomendaciones de Netflix se basa fundamentalmente en el Filtrado Colaborativo. La premisa de este método es exactamente la misma que la de KNN: "Dime quiénes son tus vecinos (usuarios similares) y te diré qué te va a gustar".

**Proximidad de Usuarios**: KNN identifica usuarios que han visto y calificado las mismas películas que tú. Si el "Usuario A" y el "Usuario B" tienen gustos casi idénticos (están "cerca" en el espacio de datos), el sistema te recomendará lo que el otro ya vio.

**Proximidad de Contenido**: También funciona para encontrar películas similares. Si te gustó Stranger Things, el algoritmo busca los "vecinos más cercanos" en términos de género, etiquetas y comportamiento de otros usuarios.