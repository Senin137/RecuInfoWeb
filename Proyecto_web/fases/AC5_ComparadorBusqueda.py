
"""
SIMANW - AC-5: Evaluación comparativa de modelos de búsqueda
============================================================

Complemento de la Fase 4.

Cumple:
- Implementa modelo booleano con índice invertido.
- Implementa modelo vectorial con TF-IDF + similitud coseno.
- Evalúa ambos modelos con las mismas consultas.
- Calcula precision, recall, F1 y precision@k.
- Usa ground truth dinámico por categoría completa.
- Detecta empates técnicos.
- Exporta reporte JSON.

Uso:
    python fases/AC5_ComparadorBusqueda.py
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


for recurso in ("stopwords",):
    nltk.download(recurso, quiet=True)


STOPWORDS_ES = list(set(stopwords.words("spanish")) | {
    "nbsp", "solo", "vez", "hace", "año", "años", "ser", "puede",
    "parte", "gran", "mismo", "misma", "además", "también"
})


class ComparadorModelosBusqueda:
    def __init__(self, documentos):
        self.documentos = documentos
        self.textos = [self._texto_documento(d) for d in documentos]
        self.indice = defaultdict(set)

        self.vectorizador = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words=STOPWORDS_ES,
            sublinear_tf=True,
        )
        self.matriz = self.vectorizador.fit_transform(self.textos) if self.textos else None
        self._construir_indice()

    def _construir_indice(self):
        for doc_id, texto in enumerate(self.textos):
            for token in self._tokens(texto):
                self.indice[token].add(doc_id)

    def busqueda_booleana(self, consulta, modo="AND"):
        terminos = self._tokens(consulta)

        if not terminos:
            return []

        conjuntos = [self.indice.get(t, set()) for t in terminos]

        if modo.upper() == "OR":
            resultado = set().union(*conjuntos)
        else:
            resultado = set.intersection(*conjuntos) if conjuntos else set()

        return sorted(resultado)

    def busqueda_vectorial(self, consulta, top_k=10):
        if self.matriz is None:
            return []

        q_vec = self.vectorizador.transform([consulta])
        sims = cosine_similarity(q_vec, self.matriz)[0]
        indices = sims.argsort()[::-1][:top_k]

        return [
            (int(i), round(float(sims[i]), 4))
            for i in indices
            if sims[i] > 0
        ]

    def evaluar_ambos(self, consulta, relevantes, top_k=10):
        relevantes = list(dict.fromkeys(relevantes))

        bool_and = self.busqueda_booleana(consulta, modo="AND")[:top_k]
        bool_or = self.busqueda_booleana(consulta, modo="OR")[:top_k]
        vectorial = [idx for idx, _ in self.busqueda_vectorial(consulta, top_k=top_k)]

        return {
            "consulta": consulta,
            "total_relevantes": len(relevantes),
            "booleano_and": self._metricas(bool_and, relevantes, top_k),
            "booleano_or": self._metricas(bool_or, relevantes, top_k),
            "vectorial": self._metricas(vectorial, relevantes, top_k),
            "resultados": {
                "booleano_and": self._describir_resultados(bool_and),
                "booleano_or": self._describir_resultados(bool_or),
                "vectorial": self._describir_resultados(vectorial),
            }
        }

    def info(self):
        postings = sum(len(v) for v in self.indice.values())
        return {
            "documentos": len(self.documentos),
            "terminos_indice": len(self.indice),
            "postings_totales": postings,
            "features_vectoriales": 0 if self.matriz is None else int(self.matriz.shape[1]),
        }

    def _metricas(self, recuperados, relevantes, k):
        recuperados_set = set(recuperados)
        relevantes_set = set(relevantes)

        tp = len(recuperados_set & relevantes_set)
        precision = tp / len(recuperados_set) if recuperados_set else 0.0
        recall = tp / len(relevantes_set) if relevantes_set else 0.0
        f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
        p_at_k = tp / k if k else 0.0

        return {
            "recuperados": len(recuperados),
            "relevantes_encontrados": tp,
            "ids_recuperados": recuperados,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "precision_at_k": round(p_at_k, 4),
        }

    def _describir_resultados(self, ids):
        salida = []
        for doc_id in ids:
            if doc_id >= len(self.documentos):
                continue
            doc = self.documentos[doc_id]
            salida.append({
                "doc_id": doc_id,
                "titulo": doc.get("titulo", "Sin título"),
                "categoria": self._categoria(doc),
                "url": doc.get("url", ""),
            })
        return salida

    def _tokens(self, texto):
        texto = (texto or "").lower()
        texto = re.sub(r"https?://\S+", " ", texto)
        texto = re.sub(r"[^\w\sáéíóúñü]", " ", texto)
        texto = re.sub(r"\d+", " ", texto)
        return [
            t for t in texto.split()
            if len(t) > 2 and t not in STOPWORDS_ES
        ]

    def _texto_documento(self, doc):
        return " ".join([
            str(doc.get("titulo", "")),
            str(doc.get("cuerpo", "")),
            str(doc.get("categoria", "")),
            str(doc.get("categoria_predicha", "")),
        ])

    def _categoria(self, doc):
        return (
            doc.get("categoria_predicha")
            or doc.get("categoria")
            or doc.get("categoria_original")
            or "general"
        )


class AC5ComparadorBusqueda:
    def __init__(
        self,
        ruta_dataset="datos/dataset_analizado.json",
        ruta_reporte="reportes/ac5_comparador_busqueda.json",
    ):
        self.ruta_dataset = ruta_dataset
        self.ruta_reporte = ruta_reporte

    def ejecutar(self):
        documentos, origen = self._cargar_documentos()
        comparador = ComparadorModelosBusqueda(documentos)
        consultas = self._crear_consultas_evaluacion(documentos)

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-5 — Booleano vs Vectorial               ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Origen       : {origen}")
        print(f"  Documentos   : {len(documentos)}")
        print(f"  Consultas    : {len(consultas)}")
        print(f"  Índice       : {comparador.info()}")
        print()

        evaluaciones = []
        acumulados = {
            "booleano_and": Counter(),
            "booleano_or": Counter(),
            "vectorial": Counter(),
        }

        print(f"{'Consulta':<34} | {'Modelo':<13} | {'Rec':>3} | {'Rel':>3} | {'Prec':>5} | {'Recall':>6} | {'F1':>5}")
        print("─" * 90)

        for caso in consultas:
            resultado = comparador.evaluar_ambos(
                consulta=caso["consulta"],
                relevantes=caso["relevantes"],
                top_k=10,
            )
            evaluaciones.append(resultado)

            for modelo in ["booleano_and", "booleano_or", "vectorial"]:
                m = resultado[modelo]
                acumulados[modelo]["precision"] += m["precision"]
                acumulados[modelo]["recall"] += m["recall"]
                acumulados[modelo]["f1"] += m["f1"]
                acumulados[modelo]["precision_at_k"] += m["precision_at_k"]

            self._imprimir_fila(caso["consulta"], "Booleano AND", resultado["booleano_and"])
            self._imprimir_fila("", "Booleano OR", resultado["booleano_or"])
            self._imprimir_fila("", "Vectorial", resultado["vectorial"])
            print()

        promedios = self._calcular_promedios(acumulados, len(consultas))
        ganadores = self._detectar_ganadores(promedios)
        conclusion = self._generar_conclusion(promedios, ganadores)

        print("─" * 90)
        print("PROMEDIOS")
        for modelo, datos in promedios.items():
            print(
                f"  {modelo:<13} "
                f"precision={datos['precision']:.3f} "
                f"recall={datos['recall']:.3f} "
                f"f1={datos['f1']:.3f} "
                f"p@10={datos['precision_at_k']:.3f}"
            )

        print()
        print("Conclusión:")
        print("  " + conclusion)

        reporte = {
            "actividad": "AC-5 Evaluación comparativa de modelos de búsqueda",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "origen_datos": origen,
            "info_indice": comparador.info(),
            "criterio_relevancia": "Un documento es relevante si pertenece a la categoría objetivo de la consulta.",
            "consultas": consultas,
            "evaluaciones": evaluaciones,
            "promedios": promedios,
            "modelos_ganadores": ganadores,
            "conclusion": conclusion,
        }

        self._guardar_json(self.ruta_reporte, reporte)
        print()
        print("  [Reporte] Guardado →", self.ruta_reporte)

        return reporte

    def _crear_consultas_evaluacion(self, documentos):
        plantillas = {
            "tecnologia": [
                "inteligencia artificial tecnología software",
                "programación datos aplicaciones digitales",
            ],
            "economia": [
                "economía mercados inflación finanzas",
                "banco inversión precios empresas",
            ],
            "ciencia": [
                "ciencia investigación cambio climático",
                "salud estudio científico laboratorio",
            ],
            "gobierno": [
                "gobierno elecciones ley política",
                "congreso reforma justicia pública",
            ],
            "mundo": [
                "internacional mundo conflicto países",
                "guerra migración europa diplomacia",
            ],
        }

        consultas = []
        for categoria, queries in plantillas.items():
            relevantes = [
                i for i, doc in enumerate(documentos)
                if self._categoria(doc).lower() == categoria
            ]

            if not relevantes:
                continue

            for consulta in queries:
                consultas.append({
                    "consulta": consulta,
                    "categoria_objetivo": categoria,
                    "relevantes": relevantes,
                    "total_relevantes": len(relevantes),
                })

        if consultas:
            return consultas

        return [
            {"consulta": "inteligencia artificial", "categoria_objetivo": "tecnologia", "relevantes": [0, 1], "total_relevantes": 2},
            {"consulta": "economía mercados", "categoria_objetivo": "economia", "relevantes": [2, 3], "total_relevantes": 2},
        ]

    def _cargar_documentos(self):
        if os.path.exists(self.ruta_dataset):
            with open(self.ruta_dataset, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, list) and datos:
                return datos, self.ruta_dataset

        return self._documentos_demo(), "datos_demo_ac5"

    def _documentos_demo(self):
        return [
            {"titulo": "Avance de inteligencia artificial", "cuerpo": "La IA mejora sistemas de búsqueda y software.", "categoria": "tecnologia"},
            {"titulo": "Nueva plataforma tecnológica", "cuerpo": "Empresas invierten en cloud y datos.", "categoria": "tecnologia"},
            {"titulo": "Mercados financieros caen", "cuerpo": "La inflación afecta las bolsas.", "categoria": "economia"},
            {"titulo": "Banco central sube tasas", "cuerpo": "Medida para contener inflación.", "categoria": "economia"},
        ]

    def _calcular_promedios(self, acumulados, total):
        promedios = {}
        for modelo, datos in acumulados.items():
            promedios[modelo] = {
                "precision": round(datos["precision"] / max(total, 1), 4),
                "recall": round(datos["recall"] / max(total, 1), 4),
                "f1": round(datos["f1"] / max(total, 1), 4),
                "precision_at_k": round(datos["precision_at_k"] / max(total, 1), 4),
            }
        return promedios

    def _detectar_ganadores(self, promedios):
        mejor_f1 = max(datos["f1"] for datos in promedios.values())
        tolerancia = 0.0001

        return [
            modelo for modelo, datos in promedios.items()
            if abs(datos["f1"] - mejor_f1) <= tolerancia
        ]

    def _generar_conclusion(self, promedios, ganadores):
        nombres = {
            "booleano_and": "modelo booleano AND",
            "booleano_or": "modelo booleano OR",
            "vectorial": "modelo vectorial",
        }

        if len(ganadores) > 1:
            lista = ", ".join(nombres[g] for g in ganadores)
            return (
                f"Hubo empate técnico entre {lista}. "
                "Esto indica que, con estas consultas y este corpus, varios enfoques recuperan una proporción similar "
                "de documentos relevantes. Aun así, el modelo vectorial suele ser más flexible porque ordena resultados "
                "por similitud y no depende de coincidencias exactas."
            )

        ganador = ganadores[0]

        if ganador == "vectorial":
            return (
                "El modelo vectorial obtuvo el mejor desempeño promedio. "
                "Esto ocurre porque TF-IDF con similitud coseno recupera documentos relacionados "
                "aunque no contengan exactamente todos los términos de la consulta."
            )

        if ganador == "booleano_and":
            return (
                "El modelo booleano AND obtuvo el mejor desempeño promedio. "
                "Esto indica que las consultas fueron muy específicas y los documentos relevantes "
                "contenían exactamente los términos buscados."
            )

        return (
            "El modelo booleano OR obtuvo el mejor desempeño promedio. "
            "Esto indica que recuperar documentos con coincidencias parciales fue más útil que exigir "
            "todos los términos de la consulta, aunque puede traer más ruido que el modelo vectorial."
        )

    def _imprimir_fila(self, consulta, modelo, metricas):
        print(
            f"{consulta:<34} | "
            f"{modelo:<13} | "
            f"{metricas['recuperados']:>3} | "
            f"{metricas['relevantes_encontrados']:>3} | "
            f"{metricas['precision']:>5.3f} | "
            f"{metricas['recall']:>6.3f} | "
            f"{metricas['f1']:>5.3f}"
        )

    def _categoria(self, doc):
        return (
            doc.get("categoria_predicha")
            or doc.get("categoria")
            or doc.get("categoria_original")
            or "general"
        )

    def _guardar_json(self, ruta, contenido):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    AC5ComparadorBusqueda().ejecutar()
