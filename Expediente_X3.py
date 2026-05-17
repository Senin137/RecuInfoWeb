from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documentos_mision3 = [
    {"doc_id": "x1", "nivel": "PUBLICO", "texto": "Boletín de prensa sobre obras en la avenida central y tráfico lento."},
    {"doc_id": "x2", "nivel": "SIGILO", "texto": "Rumor operativo: el contacto cambió frecuencia; verificar handoff nocturno. ###FIN###"},
    {"doc_id": "x3", "nivel": "PUBLICO", "texto": "Convocatoria a curso de primeros auxilios para voluntarios municipales."},
    {"doc_id": "x4", "nivel": "SIGILO", "texto": "Inventario de papelería y tóner para el almacén B del cuartel general."},
    {"doc_id": "x5", "nivel": "RESERVADO", "texto": "Lista de proveedores homologados para catering y cafetería interna."},
]

consulta_mision3 = "contacto frecuencia operativo handoff nocturno"

# 1. Filtrar documentos por nivel de clasificación (SIGILO)

documentos_filtrados = [doc for doc in documentos_mision3 if doc["nivel"] == "SIGILO"]

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
ranking = sorted(zip(documentos_filtrados, similitudes), key=lambda x: x[1], reverse=True)

top_1_doc, top_1_score = ranking[0]

top_id = top_1_doc["doc_id"]
texto_completo = top_1_doc["texto"]

recorte = texto_completo[:120]

print(f"Identificador: {top_id}")
print(f"Similitud:     {top_1_score:.4f}")
print(f"Recorte texto: {recorte}")
