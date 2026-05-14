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

print(f"Documentos con '{termino1}': {docs_agente}")
print(f"Documentos con '{termino2}': {docs_red}")
print(f"---")
print(f"Resultado de la consulta ({termino1} AND {termino2}): {docs_interseccion}")

# 3) Imprimir doc_id coincidentes, ordenados

# Convertimos el set a una lista y la ordenamos alfabéticamente
lista_resultados = sorted(list(docs_interseccion))

if lista_resultados:
    print("Resultados de la búsqueda (Ordenados):")
    for doc_id in lista_resultados:
        print(f"-> {doc_id}")
else:
    print("La búsqueda no arrojó resultados coincidentes.")
