"""
SIMANW - Sistema Inteligente de Monitoreo y Análisis de Noticias Web
=====================================================================
FASE 5: Conversación y Question Answering

Este módulo agrega una capa conversacional sobre las noticias ya procesadas.
Conserva contexto breve de la charla, clasifica la intención de la pregunta
y genera respuestas explicables usando recuperación de información.

Entrada esperada:
    datos/dataset_analizado.json

Salidas generadas:
    reportes/reporte_fase5_conversacion.json
    reportes/historial_chatbot.json

Uso:
    python fases/Fase5_Conversacion.py
"""

import json
import os
import re
from collections import Counter, deque
from dataclasses import dataclass
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
class RespuestaChat:
    pregunta: str
    intencion: str
    respuesta: str
    confianza: float
    evidencias: list[dict]

    def como_dict(self) -> dict:
        return {
            "pregunta": self.pregunta,
            "intencion": self.intencion,
            "respuesta": self.respuesta,
            "confianza": round(float(self.confianza), 4),
            "evidencias": self.evidencias,
        }


class BuscadorConversacional:
    def __init__(self, noticias: list[dict]):
        self.noticias = noticias
        self.vectorizador = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            strip_accents="unicode",
            lowercase=True,
            stop_words=list(STOPWORDS_ES),
            sublinear_tf=True,
        )
        self.textos = [self._texto_noticia(n) for n in noticias]
        self.matriz = self.vectorizador.fit_transform(self.textos) if self.textos else None

    def buscar(self, consulta: str, top_k: int = 5, filtros: dict | None = None) -> list[dict]:
        if self.matriz is None:
            return []

        filtros = filtros or {}
        q_vec = self.vectorizador.transform([consulta])
        sims = cosine_similarity(q_vec, self.matriz)[0]
        ranking = sims.argsort()[::-1]

        resultados = []
        for idx in ranking:
            score = float(sims[idx])
            if score <= 0:
                continue

            noticia = self.noticias[int(idx)]
            categoria = self._categoria(noticia)
            sentimiento = self._sentimiento(noticia)

            if filtros.get("categoria") and categoria != filtros["categoria"]:
                continue
            if filtros.get("sentimiento") and sentimiento != filtros["sentimiento"]:
                continue

            resultados.append({
                "doc_id": int(idx),
                "titulo": noticia.get("titulo", "Sin título"),
                "url": noticia.get("url", ""),
                "categoria": categoria,
                "sentimiento": sentimiento,
                "score": round(score, 4),
                "snippet": self._snippet(noticia),
            })

            if len(resultados) >= top_k:
                break

        return resultados

    def _texto_noticia(self, noticia: dict) -> str:
        campos = [
            noticia.get("titulo", ""),
            noticia.get("resumen", ""),
            noticia.get("cuerpo", ""),
            noticia.get("categoria", ""),
            noticia.get("categoria_predicha", ""),
            noticia.get("categoria_original", ""),
            noticia.get("fuente", ""),
        ]
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
        if categoria in {"deporte", "sports", "sport"}:
            return "deportes"
        if categoria in {"politica", "política"}:
            return "gobierno"
        return categoria

    def _sentimiento(self, noticia: dict) -> str:
        sent = noticia.get("sentimiento", {})
        return sent.get("etiqueta", "desconocido") if isinstance(sent, dict) else str(sent)

    def _snippet(self, noticia: dict, limite: int = 220) -> str:
        cuerpo = re.sub(r"\s+", " ", noticia.get("cuerpo", "")).strip()
        if len(cuerpo) <= limite:
            return cuerpo
        return cuerpo[:limite].rsplit(" ", 1)[0] + "..."


class MemoriaConversacional:
    def __init__(self, limite: int = 8):
        self.historial = deque(maxlen=limite)
        self.ultimo_resultado: list[dict] = []
        self.ultimo_tema: str | None = None

    def registrar(self, pregunta: str, respuesta: RespuestaChat):
        self.historial.append(respuesta.como_dict())
        if respuesta.evidencias:
            self.ultimo_resultado = respuesta.evidencias
            self.ultimo_tema = self._extraer_tema(pregunta)

    def _extraer_tema(self, texto: str) -> str | None:
        limpio = re.sub(r"[^\w\sáéíóúñ]", " ", texto.lower())
        tokens = [t for t in limpio.split() if len(t) > 3 and t not in STOPWORDS_ES]
        return " ".join(tokens[:5]) if tokens else None


class ClasificadorIntencion:
    CATEGORIAS = {
        "tecnologia": [
            "tecnología", "tecnologia", "software", "programación", "programacion",
            "ia", "inteligencia artificial", "apps", "internet", "digital"
        ],
        "ciencia": [
            "ciencia", "científico", "cientifico", "investigación", "investigacion",
            "salud", "clima", "espacio", "astronomía", "astronomia", "estudio"
        ],
        "economia": [
            "economía", "economia", "mercado", "mercados", "finanzas",
            "inflación", "inflacion", "dinero", "banco", "inversión", "inversion"
        ],
        "gobierno": [
            "gobierno", "política", "politica", "elecciones", "ley",
            "congreso", "presidente", "reforma", "justicia"
        ],
        "mundo": [
            "mundo", "internacional", "guerra", "países", "paises",
            "migración", "migracion", "europa", "asia", "américa", "america"
        ],
        "deportes": [
            "deportes", "deporte", "fútbol", "futbol", "champions",
            "champions league", "psg", "paris saint germain", "real madrid",
            "barcelona", "messi", "mbappé", "mbappe", "cristiano",
            "liga", "partido", "gol", "goles", "mundial", "selección",
            "seleccion", "nba", "tenis", "formula 1", "f1"
        ],
    }

    def analizar(self, pregunta: str) -> dict:
        texto = pregunta.lower()

        if any(p in texto for p in ["cuántas", "cuantas", "cuánto", "cuanto", "total", "número", "numero"]):
            intencion = "conteo"
        elif any(p in texto for p in ["resumen", "resume", "sintetiza"]):
            intencion = "resumen"
        elif any(p in texto for p in ["sentimiento", "tono", "positiv", "negativ", "neutral", "preocupante"]):
            intencion = "sentimiento"
        elif any(p in texto for p in ["categoría", "categoria", "tema", "tipo", "clasifica"]):
            intencion = "categoria"
        elif any(p in texto for p in ["recomienda", "recomendación", "sugiere", "similar", "relacionada"]):
            intencion = "recomendacion"
        elif any(p in texto for p in ["esas", "esos", "anterior", "anteriores", "primera", "segunda", "tercera"]):
            intencion = "seguimiento"
        else:
            intencion = "busqueda"

        return {
            "intencion": intencion,
            "filtros": {
                "categoria": self._detectar_categoria(texto),
                "sentimiento": self._detectar_sentimiento(texto),
            },
            "consulta_limpia": self._limpiar_consulta(texto),
        }

    def _detectar_categoria(self, texto: str) -> str | None:
        for categoria, alias in self.CATEGORIAS.items():
            if any(a in texto for a in alias):
                return categoria
        return None

    def _detectar_sentimiento(self, texto: str) -> str | None:
        if any(p in texto for p in ["positiva", "positivo", "optimista", "buena noticia"]):
            return "positivo"
        if any(p in texto for p in ["negativa", "negativo", "preocupante", "mala noticia", "crisis"]):
            return "negativo"
        if any(p in texto for p in ["neutral", "neutra", "informativa"]):
            return "neutral"
        return None

    def _limpiar_consulta(self, texto: str) -> str:
        ruido = r"\b(quiero|necesito|dame|muestra|muéstrame|busca|encuentra|noticias|información|sobre|hay|qué|que|cuál|cual)\b"
        texto = re.sub(ruido, " ", texto)
        texto = re.sub(r"[¿?¡!]", " ", texto)
        return re.sub(r"\s+", " ", texto).strip()


class ChatbotSIMANW:
    def __init__(self, noticias: list[dict]):
        self.noticias = noticias
        self.buscador = BuscadorConversacional(noticias)
        self.intenciones = ClasificadorIntencion()
        self.memoria = MemoriaConversacional()

    def responder(self, pregunta: str) -> RespuestaChat:
        analisis = self.intenciones.analizar(pregunta)
        intencion = analisis["intencion"]
        filtros = {k: v for k, v in analisis["filtros"].items() if v}

        if intencion == "conteo":
            respuesta = self._responder_conteo(filtros, pregunta)
        elif intencion == "resumen":
            respuesta = self._responder_resumen(filtros, pregunta, analisis["consulta_limpia"])
        elif intencion == "sentimiento":
            respuesta = self._responder_sentimiento(filtros, pregunta, analisis["consulta_limpia"])
        elif intencion == "categoria":
            respuesta = self._responder_categoria(filtros, pregunta)
        elif intencion == "recomendacion":
            respuesta = self._responder_recomendacion(filtros, pregunta, analisis["consulta_limpia"])
        elif intencion == "seguimiento":
            respuesta = self._responder_seguimiento(pregunta, filtros)
        else:
            respuesta = self._responder_busqueda(filtros, pregunta, analisis["consulta_limpia"])

        self.memoria.registrar(pregunta, respuesta)
        return respuesta

    def _filtrar_noticias(self, filtros: dict) -> list[dict]:
        filtradas = []
        for noticia in self.noticias:
            categoria = self.buscador._categoria(noticia)
            sentimiento = self.buscador._sentimiento(noticia)
            if filtros.get("categoria") and categoria != filtros["categoria"]:
                continue
            if filtros.get("sentimiento") and sentimiento != filtros["sentimiento"]:
                continue
            filtradas.append(noticia)
        return filtradas

    def _responder_conteo(self, filtros: dict, pregunta: str) -> RespuestaChat:
        noticias = self._filtrar_noticias(filtros)
        por_categoria = Counter(self.buscador._categoria(n) for n in noticias)
        por_sentimiento = Counter(self.buscador._sentimiento(n) for n in noticias)

        partes = [f"Tengo {len(noticias)} noticias que coinciden con tu consulta."]
        if por_categoria:
            partes.append("Por categoría: " + ", ".join(f"{k}: {v}" for k, v in por_categoria.most_common()))
        if por_sentimiento:
            partes.append("Por sentimiento: " + ", ".join(f"{k}: {v}" for k, v in por_sentimiento.most_common()))

        return RespuestaChat(pregunta, "conteo", " ".join(partes), 1.0, [])

    def _responder_resumen(self, filtros: dict, pregunta: str, consulta: str) -> RespuestaChat:
        evidencias = self.buscador.buscar(consulta or pregunta, top_k=5, filtros=filtros)
        if not evidencias:
            noticias = self._filtrar_noticias(filtros)[:5]
            evidencias = [self._evidencia_desde_noticia(i, n) for i, n in enumerate(noticias)]

        if not evidencias:
            return RespuestaChat(pregunta, "resumen", "No encontré noticias para resumir con esos filtros.", 0.0, [])

        lineas = ["Resumen de las noticias más relevantes:"]
        for ev in evidencias[:5]:
            lineas.append(f"- [{ev['categoria']}][{ev['sentimiento']}] {ev['titulo']}")

        return RespuestaChat(pregunta, "resumen", "\n".join(lineas), evidencias[0].get("score", 0.75), evidencias)

    def _responder_sentimiento(self, filtros: dict, pregunta: str, consulta: str) -> RespuestaChat:
        evidencias = self.buscador.buscar(consulta or pregunta, top_k=8, filtros={k: v for k, v in filtros.items() if k == "categoria"})
        noticias = [self.noticias[e["doc_id"]] for e in evidencias if e["doc_id"] < len(self.noticias)]

        if not noticias:
            noticias = self._filtrar_noticias({k: v for k, v in filtros.items() if k == "categoria"})

        sentimientos = Counter(self.buscador._sentimiento(n) for n in noticias)
        compuestos = [
            n.get("sentimiento", {}).get("compound")
            for n in noticias
            if isinstance(n.get("sentimiento", {}), dict) and "compound" in n.get("sentimiento", {})
        ]

        promedio = sum(compuestos) / len(compuestos) if compuestos else 0.0
        tono = "positivo" if promedio > 0.05 else "negativo" if promedio < -0.05 else "neutral"
        respuesta = f"El tono dominante es {tono}. Distribución encontrada: {dict(sentimientos)}. Compound promedio: {promedio:+.3f}."

        return RespuestaChat(pregunta, "sentimiento", respuesta, 0.9, evidencias[:5])

    def _responder_categoria(self, filtros: dict, pregunta: str) -> RespuestaChat:
        noticias = self._filtrar_noticias(filtros)
        categorias = Counter(self.buscador._categoria(n) for n in noticias)

        if not categorias:
            return RespuestaChat(pregunta, "categoria", "No encontré categorías para esa consulta.", 0.0, [])

        lineas = ["Categorías detectadas en el corpus:"]
        for categoria, total in categorias.most_common():
            ejemplo = next((n.get("titulo", "") for n in noticias if self.buscador._categoria(n) == categoria), "")
            lineas.append(f"- {categoria}: {total} noticias. Ejemplo: {ejemplo[:80]}")

        return RespuestaChat(pregunta, "categoria", "\n".join(lineas), 1.0, [])

    def _responder_recomendacion(self, filtros: dict, pregunta: str, consulta: str) -> RespuestaChat:
        evidencias = self.buscador.buscar(consulta or pregunta, top_k=4, filtros=filtros)
        if not evidencias:
            return RespuestaChat(pregunta, "recomendacion", "No encontré recomendaciones relevantes.", 0.0, [])

        lineas = ["Te recomiendo revisar estas noticias relacionadas:"]
        for ev in evidencias:
            lineas.append(f"- [{ev['score']:.2f}] {ev['titulo']} ({ev['categoria']}, {ev['sentimiento']})")

        return RespuestaChat(pregunta, "recomendacion", "\n".join(lineas), evidencias[0]["score"], evidencias)

    def _responder_seguimiento(self, pregunta: str, filtros: dict) -> RespuestaChat:
        if not self.memoria.ultimo_resultado:
            return RespuestaChat(pregunta, "seguimiento", "Todavía no tengo una búsqueda anterior clara. Haz primero una pregunta sobre algún tema.", 0.0, [])

        resultados = self.memoria.ultimo_resultado

        if filtros.get("sentimiento"):
            resultados = [r for r in resultados if r.get("sentimiento") == filtros["sentimiento"]]
        if filtros.get("categoria"):
            resultados = [r for r in resultados if r.get("categoria") == filtros["categoria"]]

        texto = pregunta.lower()
        if "primera" in texto and resultados:
            resultados = resultados[:1]
        elif "segunda" in texto and len(resultados) >= 2:
            resultados = [resultados[1]]
        elif "tercera" in texto and len(resultados) >= 3:
            resultados = [resultados[2]]

        if not resultados:
            return RespuestaChat(pregunta, "seguimiento", "No encontré coincidencias dentro del contexto anterior.", 0.2, [])

        lineas = ["Tomando como contexto la búsqueda anterior:"]
        for r in resultados[:4]:
            lineas.append(f"- {r['titulo']} — {r['snippet']}")

        return RespuestaChat(pregunta, "seguimiento", "\n".join(lineas), 0.85, resultados[:4])

    def _responder_busqueda(self, filtros: dict, pregunta: str, consulta: str) -> RespuestaChat:
        consulta_final = consulta or pregunta
        if self.memoria.ultimo_tema and len(consulta_final.split()) <= 2:
            consulta_final = f"{self.memoria.ultimo_tema} {consulta_final}"

        evidencias = self.buscador.buscar(consulta_final, top_k=4, filtros=filtros)
        if not evidencias:
            return RespuestaChat(pregunta, "busqueda", "No encontré información suficiente en las noticias procesadas.", 0.0, [])

        mejor = evidencias[0]
        respuesta = (
            f"La noticia más relacionada es: {mejor['titulo']}.\n"
            f"{mejor['snippet']}\n"
            f"Categoría: {mejor['categoria']} | Sentimiento: {mejor['sentimiento']}."
        )

        if len(evidencias) > 1:
            respuesta += "\nTambién encontré: " + "; ".join(e["titulo"][:70] for e in evidencias[1:3])

        return RespuestaChat(pregunta, "busqueda", respuesta, mejor["score"], evidencias)

    def _evidencia_desde_noticia(self, doc_id: int, noticia: dict) -> dict:
        return {
            "doc_id": doc_id,
            "titulo": noticia.get("titulo", "Sin título"),
            "url": noticia.get("url", ""),
            "categoria": self.buscador._categoria(noticia),
            "sentimiento": self.buscador._sentimiento(noticia),
            "score": 0.0,
            "snippet": self.buscador._snippet(noticia),
        }


class EvaluadorChatbot:
    def evaluar(self, chatbot: ChatbotSIMANW, preguntas: list[str]) -> dict:
        resultados = []
        for pregunta in preguntas:
            respuesta = chatbot.responder(pregunta)
            resultados.append(respuesta.como_dict())

        confianza_promedio = sum(r["confianza"] for r in resultados) / max(len(resultados), 1)
        intenciones = Counter(r["intencion"] for r in resultados)

        return {
            "total_preguntas": len(resultados),
            "confianza_promedio": round(confianza_promedio, 4),
            "intenciones_detectadas": dict(intenciones),
            "resultados": resultados,
        }


class Fase5Conversacion:
    def __init__(
        self,
        ruta_dataset: str = "datos/dataset_analizado.json",
        ruta_reporte: str = "reportes/reporte_fase5_conversacion.json",
        ruta_historial: str = "reportes/historial_chatbot.json",
    ):
        self.ruta_dataset = ruta_dataset
        self.ruta_reporte = ruta_reporte
        self.ruta_historial = ruta_historial
        self.noticias: list[dict] = []
        self.chatbot: ChatbotSIMANW | None = None

    def ejecutar_demo(self) -> dict:
        self.noticias = self._cargar_dataset()
        self.chatbot = ChatbotSIMANW(self.noticias)

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 5 — Conversación y Q&A                ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Dataset fuente : {self.ruta_dataset}")
        print(f"  Noticias       : {len(self.noticias)}\n")

        preguntas = [
            "¿Cuántas noticias tienes sobre tecnología?",
            "¿Cuántas noticias tienes sobre deportes?",
            "¿Cuál es el sentimiento general de las noticias?",
            "Muéstrame noticias sobre inteligencia artificial",
            "Muéstrame noticias sobre PSG y Champions",
            "¿Y de esas cuáles son negativas?",
            "Dame un resumen de economía",
            "Dame un resumen de deportes",
            "Recomiéndame noticias similares sobre ciencia",
            "¿Qué categorías hay en el corpus?",
            "¿Qué dice la primera?",
        ]

        evaluacion = EvaluadorChatbot().evaluar(self.chatbot, preguntas)

        for item in evaluacion["resultados"]:
            print(f"  Usuario: {item['pregunta']}")
            print(f"  Bot [{item['intencion']} | {item['confianza']:.3f}]:")
            print("  " + item["respuesta"].replace("\n", "\n  "))
            print()

        reporte = {
            "fase": "Fase 5 - Conversación y Question Answering",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "entrada": self.ruta_dataset,
            "total_noticias": len(self.noticias),
            "evaluacion_demo": evaluacion,
            "capacidades": [
                "búsqueda conversacional con TF-IDF",
                "clasificación de intención",
                "conteos por categoría y sentimiento",
                "resúmenes basados en evidencias",
                "recomendaciones",
                "preguntas de seguimiento con memoria breve",
            ],
        }

        self._guardar_json(self.ruta_reporte, reporte)
        self._guardar_json(self.ruta_historial, {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "historial": list(self.chatbot.memoria.historial),
        })

        print("  [Reporte]  Guardado →", self.ruta_reporte)
        print("  [Historial] Guardado →", self.ruta_historial)

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

    fase5 = Fase5Conversacion(
        ruta_dataset =_os.path.join(_BASE, "datos",    "dataset_analizado.json"),
        ruta_reporte =_os.path.join(_BASE, "reportes", "reporte_fase5_conversacion.json"),
        ruta_historial=_os.path.join(_BASE, "reportes", "historial_chatbot.json"),
    )
    fase5.ejecutar_demo()