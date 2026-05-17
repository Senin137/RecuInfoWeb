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