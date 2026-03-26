from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def cargar_documentos(directorio: str):
    """Carga todos los .txt de un directorio y devuelve rutas y contenidos."""
    base_path = Path(directorio)
    filepaths = sorted(base_path.glob("*.txt"))

    documentos = []
    nombres = []

    for path in filepaths:
        texto = path.read_text(encoding="utf-8", errors="ignore")
        documentos.append(texto)
        nombres.append(path.name)

    return nombres, documentos


def calcular_tfidf(documentos):
    """Calcula la matriz TF-IDF a partir de una lista de textos."""
    vectorizador = TfidfVectorizer(
        lowercase=True,      # pasar todo a minúsculas
        stop_words=None # eliminar stopwords en español (siempre opcional)
    )
    matriz_tfidf = vectorizador.fit_transform(documentos)
    return matriz_tfidf, vectorizador


def matriz_similitud_coseno(matriz_tfidf):
    """Devuelve la matriz de similitud de coseno entre todos los documentos."""
    return cosine_similarity(matriz_tfidf)


if __name__ == "__main__":
    # 1. Cargar documentos
    nombres, documentos = cargar_documentos("textos")

    # 2. Calcular TF-IDF
    matriz_tfidf, vectorizador = calcular_tfidf(documentos)

    # 3. Calcular similitud de coseno entre todos los pares de documentos
    sim_matrix = matriz_similitud_coseno(matriz_tfidf)

    # 4. Mostrar resultados
    print("Documentos cargados:")
    for i, nombre in enumerate(nombres):
        print(f"{i}: {nombre}")

    print("\nMatriz de similitud de coseno:")
    print(sim_matrix)

    # Ejemplo: similitud entre el documento 0 y el 1
    if len(nombres) >= 2:
        print(
            f"\nSimilitud de coseno entre '{nombres[0]}' y '{nombres[1]}': "
            f"{sim_matrix[0, 1]:.4f}"
        )