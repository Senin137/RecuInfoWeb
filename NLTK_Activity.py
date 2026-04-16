import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Descarga de recursos necesarios
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')

# 1. Definición del abstract (Mínimo 100 palabras)
abstract = """
La inteligencia artificial está cada vez más presente en nuestra vida diaria. Desde asistentes virtuales 
que nos ayudan a realizar tareas, hasta sistemas de conducción autónoma que nos brindan mayor seguridad 
en nuestras carreteras, su presencia es innegable. Esto es solo el comienzo, ya que su impacto en nuestra 
sociedad continuará creciendo en el futuro. La inteligencia artificial tiene el potencial de revolucionar 
la forma en que interactuamos con la tecnología y está cambiando la forma en que vivimos nuestras vidas. 
En el futuro, es posible que veamos más avances en la inteligencia artificial en áreas como la medicina, 
la educación y la industria. No hay límites para lo que la inteligencia artificial puede lograr y estamos 
presenciando cómo transforma nuestro mundo a cada paso.
"""

# 2. Pipeline de Procesamiento
# Tokenización original (incluye signos de puntuación)
tokens_originales = word_tokenize(abstract, language='spanish')
num_tokens_originales = len(tokens_originales)

# Carga de stopwords en español
vocabulario_stopwords = set(stopwords.words('spanish'))

# Procesamiento: Case folding + Filtrado de puntuación (.isalpha) + Eliminación de stopwords
tokens_procesados = [
    token.lower() for token in tokens_originales 
    if token.isalpha() and token.lower() not in vocabulario_stopwords
]

num_tokens_procesados = len(tokens_procesados)

# 3. Cálculos estadísticos
# Porcentaje de reducción de dimensionalidad
# Fórmula: ((Original - Procesado) / Original) * 100
reduccion = ((num_tokens_originales - num_tokens_procesados) / num_tokens_originales) * 100

# Distribución de frecuencias para los 5 términos más comunes
distribucion = nltk.FreqDist(tokens_procesados)
top_5 = distribucion.most_common(5)

# --- SALIDA ESTÁNDAR (stdout) ---
print("-" * 50)
print("RESULTADOS DEL ANÁLISIS")
print("-" * 50)
print(f"• Número total de tokens originales: {num_tokens_originales}")
print(f"• Número total de tokens tras pre-procesamiento: {num_tokens_procesados}")
print(f"• Porcentaje de reducción de dimensionalidad: {reduccion:.2f}%")
print("-" * 50)
print("• Los 5 términos más frecuentes:")
for termino, frecuencia in top_5:
    print(f"  - {termino}: {frecuencia}")
print("-" * 50)