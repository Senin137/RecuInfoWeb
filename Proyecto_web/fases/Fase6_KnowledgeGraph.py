"""
SIMANW - Sistema Inteligente de Monitoreo y Análisis de Noticias Web
=====================================================================
FASE 6: Knowledge Graph Semántico

Construye un grafo RDF a partir del dataset analizado del SIMANW, permite
consultas SPARQL locales, enlaza categorías con conceptos externos y exporta
el grafo en distintos formatos semánticos.

Entrada:
    datos/dataset_analizado.json

Salidas:
    knowledge_graph/simanw.ttl
    knowledge_graph/simanw.rdf
    knowledge_graph/simanw.jsonld
    reportes/reporte_fase6_kg.json

Uso:
    python fases/Fase6_KnowledgeGraph.py
"""

import json
import os
import re
import hashlib
from datetime import datetime
from urllib.parse import quote

from rdflib import Graph, Namespace, Literal, URIRef, RDF, RDFS, OWL, XSD
from rdflib.namespace import DC, DCTERMS, FOAF, SKOS


class UtilidadesKG:
    @staticmethod
    def slug(texto: str, limite: int = 80) -> str:
        texto = (texto or "desconocido").lower().strip()
        texto = re.sub(r"[^a-záéíóúñü0-9]+", "_", texto)
        texto = re.sub(r"_+", "_", texto).strip("_")
        return quote(texto[:limite] or "desconocido")

    @staticmethod
    def hash_corto(texto: str) -> str:
        return hashlib.sha1((texto or "").encode("utf-8")).hexdigest()[:10]

    @staticmethod
    def literal_fecha(fecha: str):
        if not fecha:
            return Literal("sin_fecha")
        return Literal(str(fecha))


class KnowledgeGraphSIMANW:
    def __init__(self):
        self.g = Graph()

        self.SIMANW = Namespace("https://simanw.local/ontology#")
        self.DATA = Namespace("https://simanw.local/recurso/")
        self.WD = Namespace("http://www.wikidata.org/entity/")
        self.SCHEMA = Namespace("https://schema.org/")

        self._bind()
        self._crear_ontologia()

    def _bind(self):
        self.g.bind("simanw", self.SIMANW)
        self.g.bind("data", self.DATA)
        self.g.bind("schema", self.SCHEMA)
        self.g.bind("dc", DC)
        self.g.bind("dcterms", DCTERMS)
        self.g.bind("foaf", FOAF)
        self.g.bind("skos", SKOS)
        self.g.bind("owl", OWL)

    def _crear_ontologia(self):
        clases = ["Noticia", "Categoria", "Fuente", "Autor", "Sentimiento", "Entidad", "DatasetAbierto"]
        for clase in clases:
            self.g.add((self.SIMANW[clase], RDF.type, OWL.Class))

        object_properties = [
            ("tieneCategoria", "Noticia", "Categoria"),
            ("publicadaPor", "Noticia", "Fuente"),
            ("escritaPor", "Noticia", "Autor"),
            ("tieneSentimiento", "Noticia", "Sentimiento"),
            ("mencionaEntidad", "Noticia", "Entidad"),
            ("relacionadaConDataset", "Noticia", "DatasetAbierto"),
        ]

        for nombre, dominio, rango in object_properties:
            prop = self.SIMANW[nombre]
            self.g.add((prop, RDF.type, OWL.ObjectProperty))
            self.g.add((prop, RDFS.domain, self.SIMANW[dominio]))
            self.g.add((prop, RDFS.range, self.SIMANW[rango]))

        data_properties = [
            "titulo", "resumen", "url", "fechaPublicacion", "categoriaTexto",
            "sentimientoEtiqueta", "sentimientoScore", "tokensClave", "fuenteTexto"
        ]

        for nombre in data_properties:
            self.g.add((self.SIMANW[nombre], RDF.type, OWL.DatatypeProperty))

    def agregar_noticias(self, noticias: list[dict]):
        for i, noticia in enumerate(noticias, start=1):
            self.agregar_noticia(noticia, i)

    def agregar_noticia(self, noticia: dict, indice: int):
        titulo = noticia.get("titulo", f"Noticia {indice}")
        cuerpo = noticia.get("cuerpo", "")
        url = noticia.get("url", "")
        categoria = self._categoria(noticia)
        fuente = self._fuente(noticia)
        autor = noticia.get("autor") or "Autor no identificado"
        sentimiento = self._sentimiento(noticia)

        noticia_uri = self.DATA[f"noticia_{indice}_{UtilidadesKG.hash_corto(url or titulo)}"]
        categoria_uri = self.DATA[f"categoria_{UtilidadesKG.slug(categoria)}"]
        fuente_uri = self.DATA[f"fuente_{UtilidadesKG.slug(fuente)}"]
        autor_uri = self.DATA[f"autor_{UtilidadesKG.slug(autor)}"]
        sentimiento_uri = self.DATA[f"sentimiento_{UtilidadesKG.slug(sentimiento['etiqueta'])}"]

        self.g.add((noticia_uri, RDF.type, self.SIMANW.Noticia))
        self.g.add((noticia_uri, RDF.type, self.SCHEMA.NewsArticle))
        self.g.add((noticia_uri, self.SIMANW.titulo, Literal(titulo, lang="es")))
        self.g.add((noticia_uri, DC.title, Literal(titulo, lang="es")))
        self.g.add((noticia_uri, self.SIMANW.resumen, Literal(cuerpo[:350], lang="es")))
        self.g.add((noticia_uri, DC.description, Literal(cuerpo[:350], lang="es")))

        if url:
            self.g.add((noticia_uri, self.SIMANW.url, URIRef(url)))
            self.g.add((noticia_uri, DCTERMS.identifier, Literal(url)))

        self.g.add((noticia_uri, self.SIMANW.fechaPublicacion, UtilidadesKG.literal_fecha(noticia.get("fecha", ""))))

        self.g.add((categoria_uri, RDF.type, self.SIMANW.Categoria))
        self.g.add((categoria_uri, RDFS.label, Literal(categoria, lang="es")))
        self.g.add((categoria_uri, SKOS.prefLabel, Literal(categoria, lang="es")))
        self.g.add((noticia_uri, self.SIMANW.tieneCategoria, categoria_uri))
        self.g.add((noticia_uri, self.SIMANW.categoriaTexto, Literal(categoria, lang="es")))

        self.g.add((fuente_uri, RDF.type, self.SIMANW.Fuente))
        self.g.add((fuente_uri, RDFS.label, Literal(fuente, lang="es")))
        self.g.add((noticia_uri, self.SIMANW.publicadaPor, fuente_uri))
        self.g.add((noticia_uri, self.SIMANW.fuenteTexto, Literal(fuente, lang="es")))

        self.g.add((autor_uri, RDF.type, self.SIMANW.Autor))
        self.g.add((autor_uri, FOAF.name, Literal(autor, lang="es")))
        self.g.add((noticia_uri, self.SIMANW.escritaPor, autor_uri))

        self.g.add((sentimiento_uri, RDF.type, self.SIMANW.Sentimiento))
        self.g.add((sentimiento_uri, RDFS.label, Literal(sentimiento["etiqueta"], lang="es")))
        self.g.add((noticia_uri, self.SIMANW.tieneSentimiento, sentimiento_uri))
        self.g.add((noticia_uri, self.SIMANW.sentimientoEtiqueta, Literal(sentimiento["etiqueta"], lang="es")))
        self.g.add((noticia_uri, self.SIMANW.sentimientoScore, Literal(sentimiento["compound"], datatype=XSD.float)))

        tokens = noticia.get("nlp", {}).get("tokens_repr", [])
        if tokens:
            self.g.add((noticia_uri, self.SIMANW.tokensClave, Literal(", ".join(tokens[:15]), lang="es")))

        for entidad in self._entidades_aproximadas(titulo + " " + cuerpo):
            entidad_uri = self.DATA[f"entidad_{UtilidadesKG.slug(entidad)}"]
            self.g.add((entidad_uri, RDF.type, self.SIMANW.Entidad))
            self.g.add((entidad_uri, RDFS.label, Literal(entidad, lang="es")))
            self.g.add((noticia_uri, self.SIMANW.mencionaEntidad, entidad_uri))

    def enlazar_categorias_base(self):
        enlaces = {
            "tecnologia": ("Q11016", "tecnología"),
            "ciencia": ("Q336", "ciencia"),
            "economia": ("Q8134", "economía"),
            "gobierno": ("Q7188", "gobierno"),
            "mundo": ("Q16502", "mundo"),
        }

        for categoria, (qid, etiqueta) in enlaces.items():
            cat_uri = self.DATA[f"categoria_{categoria}"]
            wd_uri = self.WD[qid]
            self.g.add((cat_uri, OWL.sameAs, wd_uri))
            self.g.add((cat_uri, SKOS.exactMatch, wd_uri))
            self.g.add((wd_uri, RDFS.label, Literal(etiqueta, lang="es")))

    def cargar_datasets_abiertos_demo(self):
        datasets = [
            {
                "id": "indicadores_economia_mx",
                "titulo": "Indicadores económicos de México",
                "tema": "economia",
                "publicador": "INEGI / Banco de México",
                "descripcion": "Dataset simulado para vincular noticias económicas con indicadores públicos.",
            },
            {
                "id": "emisiones_clima_mx",
                "titulo": "Emisiones y cambio climático",
                "tema": "ciencia",
                "publicador": "SEMARNAT",
                "descripcion": "Dataset simulado sobre emisiones y medio ambiente.",
            },
            {
                "id": "agenda_digital_publica",
                "titulo": "Agenda digital pública",
                "tema": "tecnologia",
                "publicador": "Gobierno de México",
                "descripcion": "Dataset simulado sobre infraestructura digital y servicios tecnológicos.",
            },
        ]

        for ds in datasets:
            ds_uri = self.DATA[f"dataset_{ds['id']}"]
            cat_uri = self.DATA[f"categoria_{ds['tema']}"]

            self.g.add((ds_uri, RDF.type, self.SIMANW.DatasetAbierto))
            self.g.add((ds_uri, DC.title, Literal(ds["titulo"], lang="es")))
            self.g.add((ds_uri, DC.publisher, Literal(ds["publicador"], lang="es")))
            self.g.add((ds_uri, DC.description, Literal(ds["descripcion"], lang="es")))
            self.g.add((ds_uri, self.SIMANW.categoriaTexto, Literal(ds["tema"], lang="es")))

            query = f"""
            PREFIX simanw: <https://simanw.local/ontology#>
            SELECT ?noticia WHERE {{
                ?noticia a simanw:Noticia ;
                         simanw:tieneCategoria <{cat_uri}> .
            }}
            LIMIT 10
            """

            for row in self.g.query(query):
                self.g.add((row.noticia, self.SIMANW.relacionadaConDataset, ds_uri))

    def consultas_demo(self) -> dict:
        consultas = {
            "conteo_por_categoria": """
            PREFIX simanw: <https://simanw.local/ontology#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?categoria (COUNT(?noticia) AS ?total)
            WHERE {
                ?noticia a simanw:Noticia ;
                         simanw:tieneCategoria ?cat .
                ?cat rdfs:label ?categoria .
            }
            GROUP BY ?categoria
            ORDER BY DESC(?total)
            """,
            "noticias_negativas": """
            PREFIX simanw: <https://simanw.local/ontology#>
            SELECT ?titulo ?score
            WHERE {
                ?n a simanw:Noticia ;
                   simanw:titulo ?titulo ;
                   simanw:sentimientoScore ?score .
                FILTER(?score < -0.05)
            }
            ORDER BY ASC(?score)
            LIMIT 10
            """,
            "categorias_enlazadas": """
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?categoria ?wikidata ?etiqueta
            WHERE {
                ?categoria owl:sameAs ?wikidata .
                OPTIONAL { ?wikidata rdfs:label ?etiqueta . }
            }
            """,
            "noticias_con_datos_abiertos": """
            PREFIX simanw: <https://simanw.local/ontology#>
            PREFIX dc: <http://purl.org/dc/elements/1.1/>
            SELECT ?titulo ?dataset
            WHERE {
                ?n simanw:titulo ?titulo ;
                   simanw:relacionadaConDataset ?ds .
                ?ds dc:title ?dataset .
            }
            LIMIT 15
            """,
        }

        salida = {}
        for nombre, query in consultas.items():
            salida[nombre] = [self._fila_a_dict(row) for row in self.g.query(query)]
        return salida

    def validar_minimo(self) -> dict:
        query = """
        PREFIX simanw: <https://simanw.local/ontology#>
        SELECT ?n ?titulo ?url WHERE {
            ?n a simanw:Noticia .
            OPTIONAL { ?n simanw:titulo ?titulo . }
            OPTIONAL { ?n simanw:url ?url . }
        }
        """

        total = 0
        sin_titulo = 0
        sin_url = 0

        for row in self.g.query(query):
            total += 1
            if row.titulo is None:
                sin_titulo += 1
            if row.url is None:
                sin_url += 1

        return {
            "conforms": sin_titulo == 0 and sin_url == 0,
            "noticias_validadas": total,
            "sin_titulo": sin_titulo,
            "sin_url": sin_url,
            "criterio": "Cada simanw:Noticia debe tener simanw:titulo y simanw:url.",
        }

    def exportar(self, ruta_ttl: str, ruta_rdf: str, ruta_jsonld: str):
        os.makedirs(os.path.dirname(ruta_ttl), exist_ok=True)
        self.g.serialize(destination=ruta_ttl, format="turtle")
        self.g.serialize(destination=ruta_rdf, format="xml")
        self.g.serialize(destination=ruta_jsonld, format="json-ld", indent=2)

    def total_triples(self) -> int:
        return len(self.g)

    def _categoria(self, noticia: dict) -> str:
        return (
            noticia.get("categoria_predicha")
            or noticia.get("categoria")
            or noticia.get("categoria_original")
            or "general"
        ).lower()

    def _fuente(self, noticia: dict) -> str:
        fuente = noticia.get("fuente") or noticia.get("source") or ""
        if fuente:
            return str(fuente)
        url = noticia.get("url", "")
        match = re.search(r"https?://(?:www\.)?([^/]+)", url)
        return match.group(1) if match else "fuente_desconocida"

    def _sentimiento(self, noticia: dict) -> dict:
        sent = noticia.get("sentimiento", {})
        if isinstance(sent, dict):
            return {
                "etiqueta": sent.get("etiqueta", "desconocido"),
                "compound": float(sent.get("compound", 0.0)),
            }
        return {"etiqueta": str(sent or "desconocido"), "compound": 0.0}

    def _entidades_aproximadas(self, texto: str) -> list[str]:
        patron = r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,2}"
        entidades = re.findall(patron, texto or "")
        descartes = {"El", "La", "Los", "Las", "Un", "Una", "Para", "Por", "Con"}
        limpias = []
        for e in entidades:
            if e not in descartes and len(e) > 3 and e not in limpias:
                limpias.append(e)
        return limpias[:5]

    def _fila_a_dict(self, row) -> dict:
        return {str(var): str(row[var]) for var in row.labels}


class Fase6KnowledgeGraph:
    def __init__(
        self,
        ruta_dataset: str = "datos/dataset_analizado.json",
        ruta_ttl: str = "knowledge_graph/simanw.ttl",
        ruta_rdf: str = "knowledge_graph/simanw.rdf",
        ruta_jsonld: str = "knowledge_graph/simanw.jsonld",
        ruta_reporte: str = "reportes/reporte_fase6_kg.json",
    ):
        self.ruta_dataset = ruta_dataset
        self.ruta_ttl = ruta_ttl
        self.ruta_rdf = ruta_rdf
        self.ruta_jsonld = ruta_jsonld
        self.ruta_reporte = ruta_reporte
        self.kg = KnowledgeGraphSIMANW()

    def ejecutar(self) -> dict:
        noticias = self._cargar_dataset()

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 6 — Knowledge Graph Semántico         ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Dataset fuente : {self.ruta_dataset}")
        print(f"  Noticias       : {len(noticias)}\n")

        print("  ▶ 6.1 Construyendo grafo RDF...")
        self.kg.agregar_noticias(noticias)
        self.kg.enlazar_categorias_base()
        print(f"     Triples iniciales: {self.kg.total_triples()}")

        print("\n  ▶ 6.2 Integrando datasets abiertos simulados...")
        self.kg.cargar_datasets_abiertos_demo()
        print(f"     Triples con datos abiertos: {self.kg.total_triples()}")

        print("\n  ▶ 6.3 Ejecutando consultas SPARQL locales...")
        consultas = self.kg.consultas_demo()
        for nombre, filas in consultas.items():
            print(f"     {nombre}: {len(filas)} resultado(s)")

        print("\n  ▶ 6.4 Validación mínima del grafo...")
        validacion = self.kg.validar_minimo()
        print(f"     Conforms: {validacion['conforms']}")
        print(f"     Noticias validadas: {validacion['noticias_validadas']}")

        self.kg.exportar(self.ruta_ttl, self.ruta_rdf, self.ruta_jsonld)

        reporte = {
            "fase": "Fase 6 - Knowledge Graph Semántico",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "entrada": self.ruta_dataset,
            "total_noticias": len(noticias),
            "total_triples": self.kg.total_triples(),
            "salidas": {
                "turtle": self.ruta_ttl,
                "rdf_xml": self.ruta_rdf,
                "json_ld": self.ruta_jsonld,
                "reporte": self.ruta_reporte,
            },
            "consultas_sparql": consultas,
            "validacion": validacion,
        }

        self._guardar_json(self.ruta_reporte, reporte)

        print("\n  [TTL]     Guardado →", self.ruta_ttl)
        print("  [RDF/XML] Guardado →", self.ruta_rdf)
        print("  [JSON-LD] Guardado →", self.ruta_jsonld)
        print("  [Reporte] Guardado →", self.ruta_reporte)

        return reporte

    def _cargar_dataset(self) -> list[dict]:
        if not os.path.exists(self.ruta_dataset):
            raise FileNotFoundError(f"No se encontró {self.ruta_dataset}. Ejecuta primero la Fase 3.")
        with open(self.ruta_dataset, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if not isinstance(datos, list):
            raise ValueError("El dataset debe ser una lista de noticias.")
        return datos

    def _guardar_json(self, ruta: str, contenido: dict):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import os as _os
    _BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

    Fase6KnowledgeGraph(
        ruta_dataset=_os.path.join(_BASE, "datos",           "dataset_analizado.json"),
        ruta_ttl    =_os.path.join(_BASE, "knowledge_graph", "simanw.ttl"),
        ruta_rdf    =_os.path.join(_BASE, "knowledge_graph", "simanw.rdf"),
        ruta_jsonld =_os.path.join(_BASE, "knowledge_graph", "simanw.jsonld"),
        ruta_reporte=_os.path.join(_BASE, "reportes",        "reporte_fase6_kg.json"),
    ).ejecutar()
