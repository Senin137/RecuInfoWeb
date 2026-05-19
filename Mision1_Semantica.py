html_informe = """
<article id="persona-alicia">
  <h1>Alicia García</h1>
  <p class="rol">Profesora de Matemáticas en la UNAM</p>
  <p>Conoce a <a href="/personas/bob">Bob Martínez</a>, coautor del artículo
     <cite>Redes y Grafos</cite>.</p>
</article>
"""

json_biblioteca = {
    "libro_id": "L-42",
    "titulo": "Introducción a la Web Semántica",
    "autores": ["Alicia García", "Bob Martínez"],
    "anio": 2019,
    "isbn": "978-3-030-00000-0",
}

triples_html = [
    ("ex:alicia", "tieneNombre", "Alicia García"),
    ("ex:alicia", "tieneRol", "Profesora de Matemáticas en la UNAM"),
    ("ex:alicia", "conoce", "ex:bob"),
    ("ex:bob", "tieneNombre", "Bob Martínez"),
    ("ex:alicia", "coautorDe", "ex:articulo_redes"),
    ("ex:bob", "coautorDe", "ex:articulo_redes"),
    ("ex:articulo_redes", "titulo", "Redes y Grafos")
]

triples_json = [
    ("ex:libro_L42", "titulo", "Introducción a la Web Semántica"),
    ("ex:libro_L42", "tieneAutor", "Alicia García"),
    ("ex:libro_L42", "tieneAutor", "Bob Martínez"),
    ("ex:libro_L42", "publicadoEn", 2019),
    ("ex:libro_L42", "isbn", "978-3-030-00000-0")
]

# Si no unificamos los criterios ni usamos URIs globales, 
# las dos fuentes generan datos desconectados. Observa estos dos triples:
triples_similares = [
("ex:alicia", "tieneNombre", "Alicia García"),
("ex:libro_L42", "tieneAutor", "Alicia García")
]

def cubre(triples, predicados_esperados):
    preds = {p for _, p, _ in triples}
    faltan = set(predicados_esperados) - preds
    print("Predicados presentes:", sorted(preds))
    print("Faltan:", sorted(faltan) if faltan else "ninguno")

cubre(triples_html, {"tieneNombre", "tieneRol", "conoce", "coautorDe"})
cubre(triples_json, {"titulo", "tieneAutor", "publicadoEn"})