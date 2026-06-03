"""
SIMANW - AC7: Enriquecimiento externo del Knowledge Graph

Módulo opcional para enriquecer categorías locales con conceptos de Wikidata.
Tiene modo seguro: si no hay internet o Wikidata falla, usa una caché académica
mínima para que la práctica siga siendo reproducible.
"""

import time
from rdflib import Namespace, Literal, URIRef, RDFS
from rdflib.namespace import OWL, SKOS, DC
from SPARQLWrapper import SPARQLWrapper, JSON


class EnriquecedorExternoSIMANW:
    def __init__(self, graph):
        self.g = graph
        self.WD = Namespace("http://www.wikidata.org/entity/")
        self.WDT = Namespace("http://www.wikidata.org/prop/direct/")
        self.g.bind("wd", self.WD)
        self.g.bind("wdt", self.WDT)
        self.g.bind("skos", SKOS)
        self.enlaces = []

    def enriquecer_categoria(self, categoria_uri, categoria: str, usar_internet: bool = False):
        datos = self._consultar_wikidata(categoria) if usar_internet else None
        if not datos:
            datos = self._fallback(categoria)

        for item in datos:
            wd_uri = URIRef(item["uri"])
            etiqueta = item["label"]
            descripcion = item.get("description", "Concepto relacionado")

            self.g.add((categoria_uri, SKOS.related, wd_uri))
            self.g.add((categoria_uri, OWL.sameAs, wd_uri))
            self.g.add((wd_uri, RDFS.label, Literal(etiqueta, lang="es")))
            self.g.add((wd_uri, DC.description, Literal(descripcion, lang="es")))

            self.enlaces.append({
                "categoria_local": str(categoria_uri),
                "wikidata": str(wd_uri),
                "etiqueta": etiqueta,
                "descripcion": descripcion,
            })

        return self.enlaces

    def _consultar_wikidata(self, categoria: str):
        qids = {
            "tecnologia": "Q11016",
            "ciencia": "Q336",
            "economia": "Q8134",
            "gobierno": "Q7188",
            "mundo": "Q16502",
        }

        qid = qids.get(categoria.lower())
        if not qid:
            return []

        query = f"""
        SELECT ?item ?itemLabel ?itemDescription WHERE {{
          wd:{qid} wdt:P279* ?item .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }}
        }}
        LIMIT 5
        """

        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.addCustomHttpHeader("User-Agent", "SIMANW-Academic-Project/1.0")
        sparql.setReturnFormat(JSON)
        sparql.setQuery(query)

        for intento in range(3):
            try:
                raw = sparql.query().convert()
                salida = []
                for row in raw["results"]["bindings"]:
                    salida.append({
                        "uri": row["item"]["value"],
                        "label": row.get("itemLabel", {}).get("value", "sin etiqueta"),
                        "description": row.get("itemDescription", {}).get("value", "sin descripción"),
                    })
                return salida
            except Exception:
                time.sleep(2 + intento)

        return []

    def _fallback(self, categoria: str):
        cache = {
            "tecnologia": [
                {"uri": "http://www.wikidata.org/entity/Q11016", "label": "tecnología", "description": "aplicación de conocimiento técnico"},
                {"uri": "http://www.wikidata.org/entity/Q11660", "label": "inteligencia artificial", "description": "campo de estudio de sistemas inteligentes"},
            ],
            "ciencia": [
                {"uri": "http://www.wikidata.org/entity/Q336", "label": "ciencia", "description": "sistema de conocimiento verificable"},
                {"uri": "http://www.wikidata.org/entity/Q125928", "label": "investigación científica", "description": "proceso sistemático de investigación"},
            ],
            "economia": [
                {"uri": "http://www.wikidata.org/entity/Q8134", "label": "economía", "description": "ciencia social de producción y consumo"},
                {"uri": "http://www.wikidata.org/entity/Q43015", "label": "finanzas", "description": "gestión de dinero y activos"},
            ],
            "gobierno": [
                {"uri": "http://www.wikidata.org/entity/Q7188", "label": "gobierno", "description": "sistema que administra un Estado"},
                {"uri": "http://www.wikidata.org/entity/Q7163", "label": "política", "description": "actividad relacionada con decisiones colectivas"},
            ],
            "mundo": [
                {"uri": "http://www.wikidata.org/entity/Q16502", "label": "mundo", "description": "conjunto global de países y sociedades"},
                {"uri": "http://www.wikidata.org/entity/Q6256", "label": "país", "description": "territorio político definido"},
            ],
        }
        return cache.get(categoria.lower(), [])