# Asegúrate de haber ejecutado: pip install rdflib
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

# 1. Configurar el grafo y el espacio de nombres (Namespace)
EX = Namespace("http://ejemplo.org/")
g = Graph()

# Opcional: Vincular el prefijo para que al exportar el grafo sea legible
g.bind("ex", EX)

# 2. Cargar triples basados en la Misión 1
# Datos extraídos del HTML (usando URIs para entidades y Literales para texto)
g.add((EX.alicia, EX.tieneNombre, Literal("Alicia García", lang="es")))
g.add((EX.alicia, EX.tieneRol, Literal("Profesora de Matemáticas en la UNAM", lang="es")))
g.add((EX.alicia, EX.conoce, EX.bob))
g.add((EX.bob, EX.tieneNombre, Literal("Bob Martínez", lang="es")))
g.add((EX.alicia, EX.coautorDe, EX.articulo_redes))
g.add((EX.bob, EX.coautorDe, EX.articulo_redes))
g.add((EX.articulo_redes, EX.titulo, Literal("Redes y Grafos", lang="es")))

# Datos extraídos del JSON (conectando el libro con las URIs de los autores)
g.add((EX.libro42, RDF.type, EX.Libro))
g.add((EX.libro42, EX.titulo, Literal("Introducción a la Web Semántica", lang="es")))
g.add((EX.libro42, EX.autor, EX.alicia)) # Aquí unificamos la identidad
g.add((EX.libro42, EX.autor, EX.bob))   # Aquí también
g.add((EX.libro42, EX.anio, Literal(2019, datatype=XSD.gYear)))
g.add((EX.libro42, EX.isbn, Literal("978-3-030-00000-0")))

print(f"Grafo inicializado con {len(g)} triples.\n")

# =====================================================================
# CONSULTA 1: ¿Quiénes son autores del libro42? (Tarea A en SPARQL Real)
# =====================================================================
print("--- Ejecutando Consulta de Autores ---")
consulta_autores = """
PREFIX ex: <http://ejemplo.org/>
SELECT ?persona ?nombre
WHERE {
    ex:libro42 ex:autor ?persona .
    ?persona ex:tieneNombre ?nombre .
}
"""

for row in g.query(consulta_autores):
    print(f"URI: {row.persona} | Nombre: {row.nombre}")


# =====================================================================
# CONSULTA 2: Buscar pares (persona, nombre) (Tarea B en SPARQL Real)
# =====================================================================
print("\n--- Ejecutando Consulta de Personas y Nombres ---")
# Gracias a SPARQL, aquí sí podemos hacer el JOIN (intersección) de triples
consulta_personas = """
PREFIX ex: <http://ejemplo.org/>
SELECT ?persona ?nombre
WHERE {
    ?persona ex:tieneNombre ?nombre .
    # Evaluamos si la entidad está involucrada en roles humanos para asegurar el contexto
    { ?persona ex:tieneRol ?rol } UNION { ?persona ex:conoce ?alguien }
}
"""

for row in g.query(consulta_personas):
    print(f"Identificador: {row.persona} -> {row.nombre}")