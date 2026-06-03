
"""
SIMANW - AC-6: Interfaz conversacional con memoria de contexto
==============================================================

Complemento de la Fase 5.

Cumple:
- Chatbot con memoria de conversación.
- Uso de contexto para preguntas como "eso", "otra", "anterior".
- Perfil de temas de interés del usuario.
- Personalización de respuestas por tema frecuente.
- Registro de estadísticas de sesión.
- Exportación de historial y reporte JSON.

Uso:
    python fases/AC6_ChatbotContextual.py
"""

import json
import os
import re
from collections import Counter, deque
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


class MotorBusquedaContextual:
    def __init__(self, documentos):
        self.documentos = documentos
        self.textos = [self._texto_documento(d) for d in documentos]
        self.vectorizador = TfidfVectorizer(
            max_features=4000,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words=STOPWORDS_ES,
            sublinear_tf=True,
        )
        self.matriz = self.vectorizador.fit_transform(self.textos) if self.textos else None

    def buscar(self, consulta, top_k=5):
        if self.matriz is None:
            return []

        q_vec = self.vectorizador.transform([consulta])
        sims = cosine_similarity(q_vec, self.matriz)[0]
        indices = sims.argsort()[::-1][:top_k]

        resultados = []
        for idx in indices:
            score = float(sims[idx])
            if score <= 0:
                continue

            doc = self.documentos[int(idx)]
            resultados.append({
                "doc_id": int(idx),
                "titulo": doc.get("titulo", "Sin título"),
                "snippet": self._snippet(doc),
                "categoria": self._categoria(doc),
                "sentimiento": self._sentimiento(doc),
                "url": doc.get("url", ""),
                "relevancia": round(score, 4),
            })

        return resultados

    def _texto_documento(self, doc):
        return " ".join([
            str(doc.get("titulo", "")),
            str(doc.get("resumen", "")),
            str(doc.get("cuerpo", "")),
            str(doc.get("categoria", "")),
            str(doc.get("categoria_predicha", "")),
            str(doc.get("categoria_original", "")),
            str(doc.get("fuente", "")),
        ])

    def _categoria(self, doc):
        categoria = (
            doc.get("categoria_predicha")
            or doc.get("categoria")
            or doc.get("categoria_original")
            or "general"
        )
        categoria = str(categoria).lower().strip()
        if categoria in {"deporte", "sports", "sport"}:
            return "deportes"
        if categoria in {"politica", "política"}:
            return "gobierno"
        return categoria

    def _sentimiento(self, doc):
        sent = doc.get("sentimiento", {})
        if isinstance(sent, dict):
            return sent.get("etiqueta", "desconocido")
        return str(sent or "desconocido")

    def _snippet(self, doc, limite=180):
        cuerpo = re.sub(r"\s+", " ", doc.get("cuerpo", "")).strip()
        if len(cuerpo) <= limite:
            return cuerpo
        return cuerpo[:limite].rsplit(" ", 1)[0] + "..."


class ChatbotContextual:
    def __init__(self, noticias, motor_busqueda):
        self.noticias = noticias
        self.motor = motor_busqueda
        self.historial = deque(maxlen=12)
        self.contexto_temas = Counter()
        self.tipos_respuesta = Counter()
        self.ultimo_resultado = []
        self.usuario_preferencias = {
            "tema_favorito": None,
            "ultima_categoria": None,
            "ultima_consulta_expandida": None,
        }

    def responder(self, pregunta):
        pregunta_limpia = self._limpiar_pregunta(pregunta)
        es_referencia = self._es_referencia_contextual(pregunta)

        if es_referencia and self.historial:
            respuesta = self._responder_con_contexto(pregunta, pregunta_limpia)
        else:
            respuesta = self._responder_directo(pregunta, pregunta_limpia)

        self._registrar_interaccion(pregunta, respuesta)
        return respuesta["texto"], respuesta["tipo"], respuesta["confianza"]

    def _responder_con_contexto(self, pregunta, pregunta_limpia):
        ultima_pregunta = self.historial[-1]["pregunta"] if self.historial else ""
        ultimo_tema = self.usuario_preferencias.get("ultima_categoria") or self.tema_favorito()

        consulta_base = " ".join([
            ultima_pregunta,
            ultimo_tema or "",
            pregunta_limpia,
        ]).strip()
        consulta_expandida = self._expandir_consulta_por_tema(pregunta, consulta_base)

        resultados = self.motor.buscar(consulta_expandida, top_k=5)

        if "otra" in pregunta.lower() or "similar" in pregunta.lower():
            resultados = self._excluir_resultados_previos(resultados)

        if resultados:
            mejor = resultados[0]
            self.ultimo_resultado = resultados
            self.usuario_preferencias["ultima_categoria"] = mejor["categoria"]
            self.usuario_preferencias["ultima_consulta_expandida"] = consulta_expandida

            return {
                "tipo": "contextual",
                "confianza": mejor["relevancia"],
                "categoria": mejor["categoria"],
                "texto": (
                    "Tomando en cuenta lo anterior, encontré esta noticia: "
                    f"{mejor['titulo']}. {mejor['snippet']}"
                ),
                "evidencias": resultados,
            }

        return {
            "tipo": "fallback_contextual",
            "confianza": 0.0,
            "categoria": None,
            "texto": "Entiendo que te refieres a lo anterior, pero no encontré otra noticia relacionada.",
            "evidencias": [],
        }

    def _expandir_consulta_por_tema(self, pregunta, pregunta_limpia):
        texto = pregunta.lower()
        temas = {
            "deportes": [
                "deportes", "deporte", "fútbol", "futbol", "champions",
                "champions league", "psg", "paris saint germain", "real madrid",
                "barcelona", "messi", "mbappé", "mbappe", "liga", "partido",
                "gol", "goles", "mundial", "nba", "tenis", "f1", "formula 1"
            ],
            "tecnologia": [
                "tecnología", "tecnologia", "software", "programación", "programacion",
                "inteligencia artificial", "ia", "internet", "digital"
            ],
            "economia": [
                "economía", "economia", "mercado", "finanzas", "inflación", "inflacion",
                "banco", "inversión", "inversion"
            ],
            "ciencia": [
                "ciencia", "científico", "cientifico", "investigación", "investigacion",
                "salud", "clima", "espacio"
            ],
            "gobierno": [
                "gobierno", "política", "politica", "elecciones", "congreso", "ley", "reforma"
            ],
            "mundo": [
                "mundo", "internacional", "guerra", "países", "paises", "europa", "migración"
            ],
        }

        partes = [pregunta_limpia or pregunta]
        for categoria, claves in temas.items():
            if any(clave in texto for clave in claves):
                partes.append(categoria)
                partes.extend(claves[:8])
                break

        return " ".join(partes)


    def _responder_directo(self, pregunta, pregunta_limpia):
        resultados = self.motor.buscar(pregunta_limpia or pregunta, top_k=5)

        if not resultados:
            return {
                "tipo": "fallback",
                "confianza": 0.0,
                "categoria": None,
                "texto": "No encontré información específica. ¿Puedes darme más detalles?",
                "evidencias": [],
            }

        resultado = self._priorizar_por_preferencia(resultados)
        tipo = "personalizada" if resultado != resultados[0] else "directa"

        self.ultimo_resultado = resultados
        self.usuario_preferencias["ultima_categoria"] = resultado["categoria"]

        return {
            "tipo": tipo,
            "confianza": resultado["relevancia"],
            "categoria": resultado["categoria"],
            "texto": self._formatear_respuesta(resultado, tipo),
            "evidencias": resultados,
        }

    def _priorizar_por_preferencia(self, resultados):
        tema = self.tema_favorito()
        if not tema:
            return resultados[0]

        mejor = resultados[0]

        if mejor["relevancia"] >= 0.35:
            return mejor

        for resultado in resultados:
            if resultado["categoria"] == tema:
                return resultado

        return mejor

    def _registrar_interaccion(self, pregunta, respuesta):
        item = {
            "pregunta": pregunta,
            "tipo": respuesta["tipo"],
            "confianza": respuesta["confianza"],
            "categoria": respuesta.get("categoria"),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        self.historial.append(item)

        if respuesta.get("categoria"):
            self.contexto_temas[respuesta["categoria"]] += 1
            self.usuario_preferencias["tema_favorito"] = self.tema_favorito()

        self.tipos_respuesta[respuesta["tipo"]] += 1

    def tema_favorito(self):
        if not self.contexto_temas:
            return None
        return self.contexto_temas.most_common(1)[0][0]

    def estadisticas_sesion(self):
        return {
            "interacciones": len(self.historial),
            "temas_interes": dict(self.contexto_temas.most_common()),
            "tipos_respuesta": dict(self.tipos_respuesta.most_common()),
            "preferencias": self.usuario_preferencias,
            "historial": list(self.historial),
        }

    def _excluir_resultados_previos(self, resultados):
        ids_previos = {r["doc_id"] for r in self.ultimo_resultado}
        filtrados = [r for r in resultados if r["doc_id"] not in ids_previos]
        return filtrados or resultados

    def _es_referencia_contextual(self, pregunta):
        texto = pregunta.lower()
        referencias = [
            "eso", "esa", "ese", "anterior", "anteriores", "más sobre",
            "mas sobre", "otra", "similar", "de esas", "de esos",
            "la primera", "la segunda", "la tercera"
        ]
        return any(ref in texto for ref in referencias)

    def _limpiar_pregunta(self, pregunta):
        texto = pregunta.lower()
        ruido = r"\b(dame|busca|muéstrame|muestrame|quiero|necesito|noticia|noticias|sobre|algo|hay|qué|que|cuéntame|cuentame|más|mas)\b"
        texto = re.sub(ruido, " ", texto)
        texto = re.sub(r"[¿?¡!]", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    def _formatear_respuesta(self, resultado, tipo):
        if tipo == "personalizada":
            return (
                f"Como has mostrado interés en {resultado['categoria']}, "
                f"te puede servir esta noticia: {resultado['titulo']}. "
                f"{resultado['snippet']}"
            )

        return (
            f"{resultado['titulo']}. {resultado['snippet']} "
            f"Categoría: {resultado['categoria']} | Sentimiento: {resultado['sentimiento']}."
        )


class AC6ChatbotContextual:
    def __init__(
        self,
        ruta_dataset="datos/dataset_analizado.json",
        ruta_reporte="reportes/ac6_chatbot_contextual.json",
    ):
        self.ruta_dataset = ruta_dataset
        self.ruta_reporte = ruta_reporte

    def ejecutar(self):
        noticias, origen = self._cargar_noticias()
        motor = MotorBusquedaContextual(noticias)
        chatbot = ChatbotContextual(noticias, motor)

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-6 — Chatbot con memoria contextual      ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Origen     : {origen}")
        print(f"  Noticias   : {len(noticias)}")
        print()

        conversacion = [
            "¿Qué noticias hay de tecnología?",
            "Cuéntame más sobre eso",
            "¿Hay algo sobre inteligencia artificial?",
            "Dame otra noticia similar a la anterior",
            "Ahora quiero algo de economía",
            "¿Y otra relacionada con eso?",
            "¿Qué hay sobre ciencia?",
            "¿Qué noticias hay de deportes?",
            "Muéstrame noticias del PSG y la Champions",
            "Dame otra relacionada con eso",
        ]

        respuestas = []

        for pregunta in conversacion:
            respuesta, tipo, confianza = chatbot.responder(pregunta)
            fila = {
                "pregunta": pregunta,
                "respuesta": respuesta,
                "tipo": tipo,
                "confianza": round(float(confianza), 4),
            }
            respuestas.append(fila)

            print(f"  Usuario: {pregunta}")
            print(f"  Bot [{tipo}][{confianza:.2f}]: {respuesta[:130]}...")
            print()

        stats = chatbot.estadisticas_sesion()

        print("  Estadísticas de sesión:")
        print(f"   - Interacciones     : {stats['interacciones']}")
        print(f"   - Temas de interés  : {stats['temas_interes']}")
        print(f"   - Tipos de respuesta: {stats['tipos_respuesta']}")
        print(f"   - Tema favorito     : {stats['preferencias'].get('tema_favorito')}")

        reporte = {
            "actividad": "AC-6 Interfaz conversacional con memoria de contexto",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "origen_datos": origen,
            "conversacion_demo": respuestas,
            "estadisticas_sesion": stats,
        }

        self._guardar_json(self.ruta_reporte, reporte)
        print()
        print("  [Reporte] Guardado →", self.ruta_reporte)

        return reporte

    def _cargar_noticias(self):
        if os.path.exists(self.ruta_dataset):
            with open(self.ruta_dataset, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, list) and datos:
                return datos, self.ruta_dataset

        return self._noticias_demo(), "datos_demo_ac6"

    def _noticias_demo(self):
        return [
            {
                "titulo": "Nuevo avance de inteligencia artificial",
                "cuerpo": "La inteligencia artificial mejora la recuperación de información.",
                "categoria": "tecnologia",
                "sentimiento": {"etiqueta": "positivo"},
            },
            {
                "titulo": "Mercados financieros caen por inflación",
                "cuerpo": "La economía muestra señales de presión por tasas altas.",
                "categoria": "economia",
                "sentimiento": {"etiqueta": "negativo"},
            },
            {
                "titulo": "Investigadores estudian el cambio climático",
                "cuerpo": "La ciencia analiza emisiones y temperatura global.",
                "categoria": "ciencia",
                "sentimiento": {"etiqueta": "neutral"},
            },
            {
                "titulo": "PSG avanza en la Champions League",
                "cuerpo": "El equipo parisino ganó su partido con goles decisivos y se mantiene como candidato al título europeo.",
                "categoria": "deportes",
                "sentimiento": {"etiqueta": "positivo"},
            },
        ]

    def _guardar_json(self, ruta, contenido):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    AC6ChatbotContextual().ejecutar()
