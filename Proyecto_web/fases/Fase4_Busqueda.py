"""
SIMANW - Sistema Inteligente de Monitoreo y Análisis de Noticias Web
=====================================================================
FASE 4: Motor de Búsqueda Inteligente

Este módulo recibe el dataset analizado de la Fase 3 y construye un motor
de recuperación de información con tres capacidades principales:

  4.1 Índice invertido       -> búsqueda exacta por términos
  4.2 Ranking vectorial      -> búsqueda semántica con TF-IDF + coseno
  4.3 Lenguaje natural       -> interpretación de intención y filtros
  4.4 Evaluación IR          -> precision, recall, F1, P@K y MAP

Entrada esperada:
    datos/dataset_analizado.json

Salidas generadas:
    indices/indice_invertido.json
    indices/metadatos_busqueda.json
    reportes/reporte_fase4_busqueda.json

Uso:
    python fases/Fase4_Busqueda.py
"""

import json
import os
import re
import math
import unicodedata
from dataclasses import dataclass
from collections import Counter, defaultdict
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


for recurso in ("stopwords",):
    nltk.download(recurso, quiet=True)


STOPWORDS_ES = set(stopwords.words("spanish")) | {
    "nbsp", "solo", "vez", "hace", "año", "años", "ser", "puede",
    "parte", "gran", "mismo", "misma", "además", "también"
}


@dataclass
class ResultadoBusqueda:
    doc_id: int
    titulo: str
    url: str
    categoria: str
    sentimiento: str
    relevancia: float
    snippet: str
    metodo: str

    def como_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "titulo": self.titulo,
            "url": self.url,
            "categoria": self.categoria,
            "sentimiento": self.sentimiento,
            "relevancia": round(self.relevancia, 4),
            "snippet": self.snippet,
            "metodo": self.metodo,
        }


class NormalizadorTexto:
    def limpiar(self, texto: str) -> str:
        texto = str(texto or "").lower()
        texto = unicodedata.normalize("NFD", texto)
        texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
        texto = re.sub(r"https?://\S+", " ", texto)
        texto = re.sub(r"[^\w\s]", " ", texto)
        texto = re.sub(r"\d+", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    def tokens(self, texto: str) -> list[str]:
        limpio = self.limpiar(texto)
        stopwords_normalizadas = {self.limpiar(w) for w in STOPWORDS_ES}
        return [t for t in limpio.split() if len(t) > 2 and t not in stopwords_normalizadas]


class MotorBusquedaSIMANW:
    def __init__(self, max_features: int = 5000):
        self.normalizador = NormalizadorTexto()
        self.documentos: dict[int, dict] = {}
        self.indice_invertido: dict[str, dict[int, int]] = defaultdict(dict)
        self.longitudes: dict[int, int] = {}
        self.frecuencia_documental: dict[str, int] = {}
        self.total_documentos = 0

        stopwords_normalizadas = sorted({
            self.normalizador.limpiar(w)
            for w in STOPWORDS_ES
            if self.normalizador.limpiar(w)
        })

        self.vectorizador = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents="unicode",
            preprocessor=self.normalizador.limpiar,
            stop_words=stopwords_normalizadas,
            sublinear_tf=True,
        )
        self.matriz_tfidf = None
        self.textos_indexados: list[str] = []

    def indexar(self, noticias: list[dict]) -> dict:
        self.documentos.clear()
        self.indice_invertido.clear()
        self.longitudes.clear()
        self.frecuencia_documental.clear()
        self.textos_indexados.clear()

        for doc_id, noticia in enumerate(noticias):
            self.documentos[doc_id] = noticia
            texto = self._texto_documento(noticia)
            tokens = self.normalizador.tokens(texto)
            frecuencias = Counter(tokens)

            self.longitudes[doc_id] = len(tokens)
            self.textos_indexados.append(texto)

            for termino, frecuencia in frecuencias.items():
                self.indice_invertido[termino][doc_id] = frecuencia

        self.total_documentos = len(self.documentos)
        self.frecuencia_documental = {
            termino: len(postings)
            for termino, postings in self.indice_invertido.items()
        }

        if self.textos_indexados:
            self.matriz_tfidf = self.vectorizador.fit_transform(self.textos_indexados)

        return self.info()

    def buscar_booleana(self, consulta: str, modo: str = "AND", top_k: int = 10) -> list[dict]:
        terminos = self.normalizador.tokens(consulta)
        if not terminos:
            return []

        conjuntos = [
            set(self.indice_invertido.get(termino, {}).keys())
            for termino in terminos
        ]

        if modo.upper() == "OR":
            ids = set().union(*conjuntos)
        else:
            ids = set.intersection(*conjuntos) if conjuntos else set()

        resultados = []
        for doc_id in ids:
            score = self._score_bm25_simple(doc_id, terminos)
            resultados.append(self._crear_resultado(doc_id, score, "booleana").como_dict())

        resultados.sort(key=lambda r: r["relevancia"], reverse=True)
        return resultados[:top_k]

    def buscar_vectorial(self, consulta: str, top_k: int = 10) -> list[dict]:
        if self.matriz_tfidf is None or self.total_documentos == 0:
            return []

        vector_consulta = self.vectorizador.transform([self.normalizador.limpiar(consulta)])
        similitudes = cosine_similarity(vector_consulta, self.matriz_tfidf)[0]
        ranking = similitudes.argsort()[::-1]

        resultados = []
        for doc_id in ranking:
            score = float(similitudes[doc_id])
            if score <= 0:
                continue
            resultados.append(self._crear_resultado(int(doc_id), score, "vectorial").como_dict())
            if len(resultados) >= top_k:
                break

        return resultados

    def busqueda_hibrida(self, consulta: str, top_k: int = 10) -> list[dict]:
        vectoriales = self.buscar_vectorial(consulta, top_k=top_k * 2)
        booleanos = self.buscar_booleana(consulta, modo="OR", top_k=top_k * 2)

        acumulado: dict[int, dict] = {}

        for pos, item in enumerate(vectoriales):
            doc_id = item["doc_id"]
            item["relevancia"] = item["relevancia"] * 0.75 + (1 / (pos + 1)) * 0.15
            item["metodo"] = "hibrida"
            acumulado[doc_id] = item

        for pos, item in enumerate(booleanos):
            doc_id = item["doc_id"]
            bonus = min(item["relevancia"], 1.0) * 0.10 + (1 / (pos + 1)) * 0.05
            if doc_id in acumulado:
                acumulado[doc_id]["relevancia"] += bonus
            else:
                item["relevancia"] = bonus
                item["metodo"] = "hibrida"
                acumulado[doc_id] = item

        resultados = list(acumulado.values())
        resultados.sort(key=lambda r: r["relevancia"], reverse=True)
        for r in resultados:
            r["relevancia"] = round(float(r["relevancia"]), 4)
        return resultados[:top_k]

    def info(self) -> dict:
        postings = sum(len(v) for v in self.indice_invertido.values())
        return {
            "documentos_indexados": self.total_documentos,
            "terminos_unicos": len(self.indice_invertido),
            "postings_totales": postings,
            "postings_promedio": round(postings / max(len(self.indice_invertido), 1), 2),
            "longitud_promedio_doc": round(sum(self.longitudes.values()) / max(self.total_documentos, 1), 2),
            "features_tfidf": 0 if self.matriz_tfidf is None else int(self.matriz_tfidf.shape[1]),
        }

    def exportar_indice(self, ruta_indice: str, ruta_metadata: str):
        os.makedirs(os.path.dirname(ruta_indice), exist_ok=True)
        os.makedirs(os.path.dirname(ruta_metadata), exist_ok=True)

        indice_serializable = {
            termino: {str(doc_id): freq for doc_id, freq in postings.items()}
            for termino, postings in self.indice_invertido.items()
        }

        with open(ruta_indice, "w", encoding="utf-8") as f:
            json.dump(indice_serializable, f, ensure_ascii=False, indent=2)

        metadata = {
            "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
            "info": self.info(),
            "documentos": {
                str(doc_id): {
                    "titulo": doc.get("titulo", ""),
                    "url": doc.get("url", ""),
                    "categoria": self._categoria(doc),
                    "sentimiento": self._sentimiento(doc),
                }
                for doc_id, doc in self.documentos.items()
            },
        }

        with open(ruta_metadata, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def _texto_documento(self, noticia: dict) -> str:
        campos = [
            noticia.get("titulo", ""),
            noticia.get("resumen", ""),
            noticia.get("cuerpo", ""),
            noticia.get("categoria", ""),
            noticia.get("categoria_predicha", ""),
            noticia.get("categoria_original", ""),
            noticia.get("fuente", ""),
        ]

        categoria_norm = self._categoria(noticia)
        if categoria_norm == "deportes":
            campos.append(
                "deportes deporte futbol fútbol champions psg paris saint germain "
                "real madrid barcelona messi mbappe mbappé liga partido gol goles"
            )

        nlp = noticia.get("nlp", {})
        if isinstance(nlp, dict):
            campos.append(" ".join(nlp.get("tokens_repr", [])))
        return " ".join(str(c) for c in campos if c)

    def _categoria(self, noticia: dict) -> str:
        categoria = (
            noticia.get("categoria_predicha")
            or noticia.get("categoria")
            or noticia.get("categoria_original")
            or "general"
        )
        categoria = str(categoria).lower().strip()

        if categoria in {"deporte", "deportes", "sports", "sport"}:
            return "deportes"
        if categoria in {"política", "politica"}:
            return "gobierno"

        return categoria

    def _sentimiento(self, noticia: dict) -> str:
        sent = noticia.get("sentimiento", {})
        return sent.get("etiqueta", "desconocido") if isinstance(sent, dict) else str(sent)

    def _snippet(self, noticia: dict, limite: int = 180) -> str:
        cuerpo = re.sub(r"\s+", " ", noticia.get("cuerpo", "")).strip()
        if len(cuerpo) <= limite:
            return cuerpo
        return cuerpo[:limite].rsplit(" ", 1)[0] + "..."

    def _crear_resultado(self, doc_id: int, score: float, metodo: str) -> ResultadoBusqueda:
        noticia = self.documentos[doc_id]
        return ResultadoBusqueda(
            doc_id=doc_id,
            titulo=noticia.get("titulo", "Sin título"),
            url=noticia.get("url", ""),
            categoria=self._categoria(noticia),
            sentimiento=self._sentimiento(noticia),
            relevancia=float(score),
            snippet=self._snippet(noticia),
            metodo=metodo,
        )

    def _score_bm25_simple(self, doc_id: int, terminos: list[str]) -> float:
        score = 0.0
        for termino in terminos:
            tf = self.indice_invertido.get(termino, {}).get(doc_id, 0)
            if tf == 0:
                continue
            df = self.frecuencia_documental.get(termino, 0)
            idf = math.log((self.total_documentos + 1) / (df + 1)) + 1
            score += (1 + math.log(tf)) * idf
        return round(score, 4)


class BusquedaLenguajeNatural:
    def __init__(self, motor: MotorBusquedaSIMANW):
        self.motor = motor
        self.alias_categorias = {
            "tecnologia": [
                "tecnologia", "tecnología", "tecnológico", "tecnologico",
                "tech", "ia", "inteligencia artificial", "software", "programación", "programacion"
            ],
            "ciencia": [
                "ciencia", "científico", "cientifico", "investigación", "investigacion",
                "salud", "clima", "espacio", "estudio"
            ],
            "economia": [
                "economía", "economia", "mercados", "mercado", "finanzas",
                "inflación", "inflacion", "dinero", "banco", "inversión", "inversion"
            ],
            "gobierno": [
                "gobierno", "política", "politica", "elecciones", "ley",
                "congreso", "presidente", "reforma"
            ],
            "mundo": [
                "mundo", "internacional", "guerra", "países", "paises",
                "migración", "migracion", "europa", "américa", "america"
            ],
            "deportes": [
                "deportes", "deporte", "deportiva", "deportivas", "deportivo",
                "fútbol", "futbol", "champions", "champions league", "psg",
                "paris saint germain", "real madrid", "barcelona", "messi",
                "mbappé", "mbappe", "cristiano", "liga", "partido", "gol",
                "goles", "mundial", "selección", "seleccion", "nba", "tenis",
                "formula 1", "f1"
            ],
        }

    def interpretar(self, consulta: str) -> dict:
        texto = self.normalizador.limpiar(consulta)
        filtros = {
            "categoria": None,
            "sentimiento": None,
            "modo": "hibrida",
            "consulta_limpia": consulta,
        }

        if any(p in texto for p in ["positiva", "positivo", "optimista", "buena noticia", "buenas noticias"]):
            filtros["sentimiento"] = "positivo"
        elif any(p in texto for p in ["negativa", "negativo", "preocupante", "mala noticia", "crisis"]):
            filtros["sentimiento"] = "negativo"
        elif any(p in texto for p in ["neutral", "neutra", "informativa"]):
            filtros["sentimiento"] = "neutral"

        for categoria, alias in self.alias_categorias.items():
            alias_normalizados = [self.normalizador.limpiar(a) for a in alias]
            if any(a in texto for a in alias_normalizados):
                filtros["categoria"] = categoria
                break

        if any(p in texto for p in ["exactamente", "literal", "contenga", "mencione"]):
            filtros["modo"] = "booleana"

        filtros["consulta_limpia"] = self._quitar_ruido(texto)
        return filtros

    def buscar(self, consulta: str, top_k: int = 5) -> dict:
        filtros = self.interpretar(consulta)

        if filtros["modo"] == "booleana":
            resultados = self.motor.buscar_booleana(filtros["consulta_limpia"], modo="AND", top_k=top_k * 3)
        else:
            resultados = self.motor.busqueda_hibrida(filtros["consulta_limpia"], top_k=top_k * 3)

        filtrados = []
        for item in resultados:
            if filtros["categoria"] and item["categoria"] != filtros["categoria"]:
                continue
            if filtros["sentimiento"] and item["sentimiento"] != filtros["sentimiento"]:
                continue
            filtrados.append(item)

        if not filtrados and filtros["categoria"]:
            filtrados = [
                self.motor._crear_resultado(doc_id, 1.0, "categoria").como_dict()
                for doc_id, doc in self.motor.documentos.items()
                if self.motor._categoria(doc) == filtros["categoria"]
            ][:top_k]

        if not filtrados:
            filtrados = resultados[:top_k]

        return {
            "consulta_original": consulta,
            "interpretacion": filtros,
            "total_resultados": len(filtrados[:top_k]),
            "resultados": filtrados[:top_k],
        }

    def _quitar_ruido(self, texto: str) -> str:
        # El regex busca fronteras de palabras (\b) para remover adjetivos e intenciones
        patrones = [
            r"\b(mu[eé]strame|busca|buscar|quiero|necesito|dame|encuentra|hay|sobre|noticias?|informaci[oó]n)\b",
            r"\b(positivas?|positivos?|negativas?|negativos?|preocupante|neutrales?|neutras?|recientes?)\b",
            r"[¿?¡!]",
        ]
        limpio = texto
        for patron in patrones:
            limpio = re.sub(patron, " ", limpio)
        return re.sub(r"\s+", " ", limpio).strip()


class EvaluadorBusqueda:
    @staticmethod
    def precision(recuperados: list[int], relevantes: list[int]) -> float:
        recuperados_set = set(recuperados)
        relevantes_set = set(relevantes)
        return len(recuperados_set & relevantes_set) / len(recuperados_set) if recuperados_set else 0.0

    @staticmethod
    def recall(recuperados: list[int], relevantes: list[int]) -> float:
        recuperados_set = set(recuperados)
        relevantes_set = set(relevantes)
        return len(recuperados_set & relevantes_set) / len(relevantes_set) if relevantes_set else 0.0

    @staticmethod
    def f1(precision: float, recall: float) -> float:
        return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)

    @staticmethod
    def precision_at_k(ranking: list[int], relevantes: list[int], k: int) -> float:
        if k <= 0:
            return 0.0
        return len(set(ranking[:k]) & set(relevantes)) / k

    @staticmethod
    def average_precision(ranking: list[int], relevantes: list[int]) -> float:
        relevantes_set = set(relevantes)
        if not relevantes_set:
            return 0.0

        suma = 0.0
        encontrados = 0
        for posicion, doc_id in enumerate(ranking, start=1):
            if doc_id in relevantes_set:
                encontrados += 1
                suma += encontrados / posicion
        return suma / len(relevantes_set)

    def evaluar_consultas(self, motor: MotorBusquedaSIMANW, casos: list[dict], top_k: int = 5) -> dict:
        detalle = []
        map_total = 0.0

        for caso in casos:
            resultados = motor.busqueda_hibrida(caso["consulta"], top_k=top_k)
            ranking = [r["doc_id"] for r in resultados]
            relevantes = caso["relevantes"]

            p = self.precision(ranking, relevantes)
            r = self.recall(ranking, relevantes)
            f = self.f1(p, r)
            ap = self.average_precision(ranking, relevantes)
            map_total += ap

            detalle.append({
                "consulta": caso["consulta"],
                "recuperados": ranking,
                "relevantes": relevantes,
                "precision": round(p, 4),
                "recall": round(r, 4),
                "f1": round(f, 4),
                "p@3": round(self.precision_at_k(ranking, relevantes, 3), 4),
                "average_precision": round(ap, 4),
            })

        return {
            "consultas_evaluadas": len(casos),
            "map": round(map_total / max(len(casos), 1), 4),
            "detalle": detalle,
        }


class Fase4Busqueda:
    def __init__(
        self,
        ruta_dataset: str = "datos/dataset_analizado.json",
        ruta_indice: str = "indices/indice_invertido.json",
        ruta_metadata: str = "indices/metadatos_busqueda.json",
        ruta_reporte: str = "reportes/reporte_fase4_busqueda.json",
    ):
        self.ruta_dataset = ruta_dataset
        self.ruta_indice = ruta_indice
        self.ruta_metadata = ruta_metadata
        self.ruta_reporte = ruta_reporte
        self.motor = MotorBusquedaSIMANW()
        self.busqueda_natural = BusquedaLenguajeNatural(self.motor)

    def ejecutar(self) -> dict:
        noticias = self._cargar_dataset()

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 4 — Motor de Búsqueda Inteligente     ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Dataset fuente : {self.ruta_dataset}")
        print(f"  Noticias       : {len(noticias)}\n")

        info = self.motor.indexar(noticias)

        print("  ▶ 4.1 Índice invertido + TF-IDF")
        print(f"     Documentos indexados : {info['documentos_indexados']}")
        print(f"     Términos únicos      : {info['terminos_unicos']}")
        print(f"     Features TF-IDF      : {info['features_tfidf']}")

        consultas_demo = [
            "inteligencia artificial y tecnología",
            "mercados economía inflación",
            "cambio climático investigación científica",
            "gobierno elecciones ley",
            "noticias internacionales conflicto",
        ]

        print("\n  ▶ 4.2 Búsqueda híbrida")
        demostracion = []
        for consulta in consultas_demo:
            resultados = self.motor.busqueda_hibrida(consulta, top_k=3)
            demostracion.append({"consulta": consulta, "resultados": resultados})
            print(f"\n     Consulta: {consulta}")
            for r in resultados[:2]:
                print(f"       [{r['relevancia']:.3f}] {r['titulo'][:65]}...")

        print("\n  ▶ 4.3 Lenguaje natural")
        consultas_naturales = [
            "Muéstrame noticias positivas sobre tecnología",
            "Busco información preocupante sobre economía",
            "¿Qué hay sobre investigación científica?",
            "Encuentra noticias internacionales recientes",
        ]

        demo_natural = []
        for consulta in consultas_naturales:
            salida = self.busqueda_natural.buscar(consulta, top_k=2)
            demo_natural.append(salida)
            print(f"\n     Usuario: {consulta}")
            print(f"     Interpretación: {salida['interpretacion']}")
            for r in salida["resultados"]:
                print(f"       → [{r['relevancia']:.3f}] {r['titulo'][:60]}...")

        print("\n  ▶ 4.4 Evaluación automática")
        casos = self._crear_casos_evaluacion(noticias)
        evaluacion = EvaluadorBusqueda().evaluar_consultas(self.motor, casos, top_k=5)

        print(f"     Consultas evaluadas : {evaluacion['consultas_evaluadas']}")
        print(f"     MAP                 : {evaluacion['map']}")

        self.motor.exportar_indice(self.ruta_indice, self.ruta_metadata)

        reporte = {
            "fase": "Fase 4 - Motor de Búsqueda Inteligente",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "entrada": self.ruta_dataset,
            "salidas": {
                "indice": self.ruta_indice,
                "metadata": self.ruta_metadata,
                "reporte": self.ruta_reporte,
            },
            "info_indice": info,
            "demostracion_busqueda": demostracion,
            "demostracion_lenguaje_natural": demo_natural,
            "evaluacion": evaluacion,
        }

        self._guardar_json(self.ruta_reporte, reporte)

        print("\n  [Índice]  Guardado →", self.ruta_indice)
        print("  [Metadata] Guardada →", self.ruta_metadata)
        print("  [Reporte] Guardado →", self.ruta_reporte)

        return reporte

    def _cargar_dataset(self) -> list[dict]:
        if not os.path.exists(self.ruta_dataset):
            raise FileNotFoundError(
                f"No se encontró {self.ruta_dataset}. Ejecuta primero la Fase 3."
            )

        with open(self.ruta_dataset, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not isinstance(datos, list):
            raise ValueError("El dataset debe ser una lista de noticias.")

        return datos

    def _crear_casos_evaluacion(self, noticias: list[dict]) -> list[dict]:
        consultas = {
            "tecnologia": "inteligencia artificial tecnología software",
            "deportes": "psg champions deportes fútbol",
            "economia": "economía mercados inflación finanzas",
            "ciencia": "investigación ciencia clima salud",
            "gobierno": "gobierno política elecciones ley",
            "mundo": "internacional mundo conflicto países",
        }

        casos = []
        for categoria, consulta in consultas.items():
            relevantes = [
                i for i, n in enumerate(noticias)
                if (n.get("categoria_predicha") or n.get("categoria") or n.get("categoria_original") or "").lower() == categoria
            ][:5]

            if relevantes:
                casos.append({"consulta": consulta, "relevantes": relevantes})

        return casos

    def _guardar_json(self, ruta: str, contenido: dict):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import os as _os
    _BASE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

    fase4 = Fase4Busqueda(
        ruta_dataset =_os.path.join(_BASE, "datos",    "dataset_analizado.json"),
        ruta_indice  =_os.path.join(_BASE, "indices",  "indice_invertido.json"),
        ruta_metadata=_os.path.join(_BASE, "indices",  "metadatos_busqueda.json"),
        ruta_reporte =_os.path.join(_BASE, "reportes", "reporte_fase4_busqueda.json"),
    )
    fase4.ejecutar()