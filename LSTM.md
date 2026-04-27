# Diferencias entre un LSTM y un RNN común

Una red de memoria a corto-largo plazo (LSTM) es un tipo de red neuronal recurrente (RNN). Las LSTM se utilizan principalmente para aprender, procesar y clasificar datos secuenciales, ya que pueden aprender dependencias a largo plazo entre unidades de tiempo de datos.

## Cómo funcionan las LSTM

**LSTM y RNN**
Las redes LSTM son una forma especializada de la arquitectura de RNN. Las RNN utilizan información anterior para mejorar el rendimiento de una red neuronal con entradas actuales y futuras. Contienen un estado oculto y bucles, que permiten que la red almacene información anterior en estado oculto y funcione con secuencias. Las RNN tienen dos conjuntos de pesos: uno para el vector del estado oculto y otro para las entradas. Durante el entrenamiento, la red aprende los pesos de las entradas y del estado oculto. Cuando se implementa, la salida se basa en la entrada actual y en el estado oculto, que a su vez se basa en entradas anteriores.

En la práctica, las RNN simples tienen una capacidad limitada para aprender dependencias a largo plazo. Las RNN se suelen entrenar mediante retropropagación, que puede provocar un problema de desvanecimiento o explosión de gradiente. Estos problemas hacen que los pesos de la red sean muy pequeños o muy grandes, lo que limita la eficacia en aplicaciones que requieren que la red aprenda relaciones a largo plazo.

**Arquitectura de capas de las LSTM**
Las capas de LSTM utilizan puertas adicionales para controlar qué información del estado oculto se exporta como salida y al siguiente estado oculto. Estas puertas adicionales solucionan el problema común de las RNN para aprender dependencias a largo plazo. Además del estado oculto de las RNN tradicionales, la arquitectura de un bloque de LSTM generalmente tiene una celda de memoria, puerta de entrada, puerta de salida y puerta de olvido. Las puertas adicionales permiten que la red aprenda relaciones de datos a largo plazo de manera más eficaz. Su menor sensibilidad al intervalo de tiempo hace que las redes LSTM sean mejores para analizar datos secuenciales que las RNN simples. 

Los pesos y sesgos de la puerta de entrada controlan cuánto fluye un nuevo valor en la unidad de LSTM. Del mismo modo, los pesos y sesgos de la puerta de olvido y la puerta de salida controlan cuánto permanece un valor en la unidad, y hasta qué punto se utiliza ese valor de unidad para calcular la activación de la salida del bloque de LSTM, respectivamente.

El siguiente diagrama ilustra el flujo de datos a través de una capa de LSTM con múltiples unidades de tiempo. El número de canales de la salida coincide con el número de unidades ocultas de la capa de LSTM.

## Arquitectura de redes LSTM
Las LSTM funcionan bien con datos de secuencias y series temporales para tareas de clasificación y regresión. También funcionan bien con vídeos, ya que son básicamente una secuencia de imágenes. Del mismo modo que cuando se trabaja con señales, es útil realizar extracción de características antes de suministrar la secuencia de imágenes a la capa de LSTM. Utilice redes neuronales convolucionales (CNN), como GoogLeNet, para extraer características de cada trama. 

## LSTM bidireccional
Una LSTM bidireccional (BiLSTM) aprende dependencias bidireccionales entre unidades de tiempo de datos de secuencias o series temporales. Estas dependencias pueden resultar útiles cuando desea que la red aprenda de la serie temporal completa en cada unidad de tiempo. Las redes BiLSTM permiten un entrenamiento adicional, ya que los datos de entrada se pasan a través de la capa de LSTM dos veces, lo que puede aumentar el rendimiento de la red.

Una BiLSTM consta de dos componentes de LSTM: forward LSTM y backward LSTM. Forward LSTM funciona desde la primera unidad de tiempo hasta la última unidad de tiempo. Backward LSTM funciona desde la última unidad de tiempo hasta la primera unidad de tiempo. Después de pasar los datos a través de los dos componentes de LSTM, la operación concatena las salidas a lo largo de la dimensión del canal.

## Aplicación de LSTM
Las LSTM son particularmente eficaces para trabajar con datos secuenciales, que pueden variar en longitud, y para aprender dependencias a largo plazo entre unidades de tiempo de esos datos. Entre las aplicaciones comunes de LSTM se incluyen análisis de sentimiento, modelado de lenguaje, reconocimiento de voz y análisis de vídeos.

Aplicaciones amplias de LSTM
Las RNN son una tecnología clave en las siguientes aplicaciones:

Procesamiento de señales. Las señales son básicamente datos secuenciales que a menudo se recopilan a partir de sensores a lo largo del tiempo. La clasificación y regresión automática con conjuntos de datos de señales de gran tamaño permiten realizar predicciones en tiempo real. Los datos de señales no procesados se pueden suministrar a redes profundas o preprocesarse para enfocarse en determinadas características, como componentes de frecuencia. La extracción de características puede mejorar enormemente el rendimiento de una red.
Procesamiento del lenguaje natural (PLN). El lenguaje es básicamente secuencial; los elementos de texto son de longitud variable. Las LSTM son una excelente herramienta para tareas de procesamiento del lenguaje natural, como clasificación de texto, generación de texto, traducción automática y análisis de sentimiento, ya que pueden aprender a contextualizar las palabras de una oración.
Pruebe los siguientes ejemplos para comenzar a aplicar redes LSTM a procesamiento de señales y procesamiento del lenguaje natural.
