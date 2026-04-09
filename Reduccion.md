# Reducción de Dimensionalidad en Recuperación de Información

## Parte 1: Reducción “a ojo”

| Documento | Palabras clave
| :--- | :---: |
|Doc 1|aprendizaje automático, artificial, computadoras,  sistemas, datos|
|Doc 2|salud pública, enfermedades, vacunación, sanitaria, epidemias|
|Doc 3|fútbol, habilidades físicas, equipo, estrategias, partidos|
|Doc 4|Inteligencia artificial, Análisis de datos, Patrones, Decisiones, Automatización|
|Doc 5|Educación moderna, Tecnologías digitales, Plataformas en línea, Simuladores, Recursos interactivos|
|Doc 6|Cambio climático, Ecosistemas, Fenómenos extremos, Sequías e inundaciones, Temperatura global|
|Doc 7|Inflación, Aumento de precios, Bienes y servicios, Economía, Periodo de tiempo|
|Doc 8|Redes neuronales profundas, Sistemas avanzados, Reconocimiento de imágenes, Procesamiento de lenguaje, Inteligencia artificial|
|Doc 9|Alimentación balanceada, Ejercicio regular,Prevención de enfermedades, Calidad de vida, Bienestar|
|Doc 10|Aprendizaje en línea, Crecimiento significativo, Acceso a internet, Plataformas digitales, Educación|

## Parte 2: Discusión

1. **¿Qué criterio utilizaste para seleccionar palabras?**
Simplemente saque las palabras más relevantes del tema en cuestión.

2. **¿Coincidiste con otros compañeros?** En algunas palabras si, digamos en la mayoría, en otros documentos no tanto, pero en lo general diría que si.

3. **¿Qué dificultades encontraste?** El elegir solamente 5, ya que habían palabras que podían ser relevantes tambien, un poco menos que las otras, pero tambien podían servir.

## Parte 5 Análisis
1. **¿Qué representan las nuevas dimensiones?**
La relavancia que tiene para el aprendizaje de modelo por las palabras restantes del vocabulario.

2. **¿Se agrupan documentos similares?**
Si, hay varios docuementos que se agrupan que son similares

3. **¿Qué diferencias hay respecto a la reducción manual?**
En si hay un mejor control de la información con la reducción automatica, obviamente es mas sencilla de hacer de manera automatica, igual tambien es un poco menos interpretable en un inicio, pero es más preciso.

## Parte 6: Comparación

| Aspecto       | Manual                          | TF-IDF + SVD                          |
|--------------|----------------------------------|---------------------------------------|
| Facilidad    | Alta (fácil de implementar)     | Media (requiere librerías y conceptos)|
| Precisión    | Baja a media                    | Alta (mejor representación del texto) |
| Escalabilidad| Baja (limitado con muchos datos)| Alta (maneja grandes volúmenes)       |
| Objetividad  | Baja (depende del criterio humano)| Alta (basado en cálculos matemáticos) |

## Reflexión final

1. **¿Qué método es más confiable?** Diría que el más confiable es el metodo con TF-IDF ya que es mas preciso y mas escalable.

2. **¿Cuál usarías en un sistema real?** Definitivamente el TF-IDF

3. **¿Se pierde información en ambos casos?** Si, pero en el TF-IDF se pierde de una forma controlada segun la configuración del algoritmo.