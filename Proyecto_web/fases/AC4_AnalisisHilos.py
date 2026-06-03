
"""
SIMANW - AC-4: Análisis de hilos de discusión de red social
===========================================================

Complemento entre Fase 3 y Fase 4.

Cumple:
- Carga o simula un hilo de discusión.
- Analiza evolución del sentimiento con ventana móvil.
- Detecta subtemas usando TF-IDF + KMeans.
- Identifica usuarios más activos.
- Extrae hashtags y palabras clave.
- Genera resumen automático del hilo.
- Exporta reporte JSON.

Uso:
    python fases/AC4_AnalisisHilos.py
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


for recurso in ("vader_lexicon", "stopwords"):
    nltk.download(recurso, quiet=True)


STOPWORDS_ES_EN = list(set(stopwords.words("spanish") + stopwords.words("english")) | {
    "nbsp", "solo", "vez", "hace", "año", "años", "ser", "puede",
    "parte", "gran", "mismo", "misma", "además", "también",
    "ai", "ia", "thing", "really"
})


class AnalizadorHiloDiscusion:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.mensajes = []

    def cargar_hilo(self, mensajes):
        self.mensajes = []

        for i, mensaje in enumerate(mensajes, start=1):
            texto = mensaje.get("texto", "")
            score = self.sia.polarity_scores(texto)["compound"]

            item = {
                "id": i,
                "usuario": mensaje.get("usuario", "anonimo"),
                "texto": texto,
                "timestamp": mensaje.get("timestamp", ""),
                "sentimiento": round(float(score), 4),
                "tono": self._tono(score),
            }
            self.mensajes.append(item)

        return self.mensajes

    def evolucion_sentimiento(self, ventana=3):
        if not self.mensajes:
            return []

        evolucion = []
        sentimientos = [m["sentimiento"] for m in self.mensajes]

        for i, score in enumerate(sentimientos):
            inicio = max(0, i - ventana + 1)
            segmento = sentimientos[inicio:i + 1]
            tendencia = sum(segmento) / len(segmento)

            evolucion.append({
                "posicion": i + 1,
                "usuario": self.mensajes[i]["usuario"],
                "sentimiento_puntual": round(score, 4),
                "tendencia_ventana": round(tendencia, 4),
                "tono_puntual": self._tono(score),
                "tono_tendencia": self._tono(tendencia),
            })

        return evolucion

    def detectar_subtemas(self, n_clusters=3):
        if not self.mensajes:
            return {}

        textos = [m["texto"] for m in self.mensajes]
        n_clusters = max(1, min(n_clusters, len(textos)))

        vectorizador = TfidfVectorizer(
            max_features=700,
            ngram_range=(1, 2),
            stop_words=STOPWORDS_ES_EN,
            lowercase=True,
        )
        matriz = vectorizador.fit_transform(textos)

        if matriz.shape[0] < 2 or matriz.shape[1] == 0:
            return {
                "0": {
                    "keywords": [],
                    "n_mensajes": len(textos),
                    "mensajes_idx": list(range(len(textos))),
                    "usuarios": list({m["usuario"] for m in self.mensajes}),
                }
            }

        modelo = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = modelo.fit_predict(matriz)

        grupos = defaultdict(list)
        for idx, cluster_id in enumerate(clusters):
            grupos[int(cluster_id)].append(idx)

        terminos = vectorizador.get_feature_names_out()
        salida = {}

        for cluster_id, indices in grupos.items():
            centroide = modelo.cluster_centers_[cluster_id]
            top_idx = centroide.argsort()[-6:][::-1]
            keywords = [terminos[i] for i in top_idx if centroide[i] > 0]

            salida[str(cluster_id)] = {
                "keywords": keywords,
                "n_mensajes": len(indices),
                "mensajes_idx": indices,
                "usuarios": list({self.mensajes[i]["usuario"] for i in indices}),
                "ejemplos": [
                    self.mensajes[i]["texto"][:120]
                    for i in indices[:3]
                ],
            }

        return salida

    def usuarios_mas_activos(self, top_n=5):
        return Counter(m["usuario"] for m in self.mensajes).most_common(top_n)

    def hashtags_top(self, top_n=8):
        hashtags = Counter()
        for mensaje in self.mensajes:
            encontrados = re.findall(r"#(\w+)", mensaje["texto"])
            hashtags.update(tag.lower() for tag in encontrados)
        return hashtags.most_common(top_n)

    def resumen_hilo(self):
        total = len(self.mensajes)
        if total == 0:
            return {
                "total_mensajes": 0,
                "participantes": 0,
                "sentimiento_promedio": 0,
                "tono": "sin_datos",
                "positivos_pct": 0,
                "negativos_pct": 0,
                "neutrales_pct": 0,
                "hashtags_top": [],
                "usuarios_activos": [],
            }

        scores = [m["sentimiento"] for m in self.mensajes]
        promedio = sum(scores) / total

        positivos = sum(1 for s in scores if s > 0.05)
        negativos = sum(1 for s in scores if s < -0.05)
        neutrales = total - positivos - negativos

        return {
            "total_mensajes": total,
            "participantes": len(set(m["usuario"] for m in self.mensajes)),
            "sentimiento_promedio": round(promedio, 4),
            "tono": self._tono(promedio),
            "positivos_pct": round(100 * positivos / total, 2),
            "negativos_pct": round(100 * negativos / total, 2),
            "neutrales_pct": round(100 * neutrales / total, 2),
            "hashtags_top": self.hashtags_top(8),
            "usuarios_activos": self.usuarios_mas_activos(5),
        }

    def generar_resumen_automatico(self, subtemas):
        resumen = self.resumen_hilo()
        partes = []

        partes.append(
            f"El hilo contiene {resumen['total_mensajes']} mensajes escritos por "
            f"{resumen['participantes']} participantes."
        )

        partes.append(
            f"El tono general es {resumen['tono']} "
            f"(sentimiento promedio {resumen['sentimiento_promedio']:+.3f})."
        )

        partes.append(
            f"La distribución emocional fue: {resumen['positivos_pct']}% positivos, "
            f"{resumen['negativos_pct']}% negativos y {resumen['neutrales_pct']}% neutrales."
        )

        if resumen["usuarios_activos"]:
            usuarios = ", ".join(u for u, _ in resumen["usuarios_activos"][:3])
            partes.append(f"Los usuarios más activos fueron: {usuarios}.")

        if resumen["hashtags_top"]:
            tags = ", ".join("#" + tag for tag, _ in resumen["hashtags_top"][:5])
            partes.append(f"Los hashtags principales fueron: {tags}.")

        if subtemas:
            lista_subtemas = []
            for info in subtemas.values():
                if info["keywords"]:
                    lista_subtemas.append(", ".join(info["keywords"][:3]))
            if lista_subtemas:
                partes.append("Los subtemas dominantes fueron: " + " | ".join(lista_subtemas) + ".")

        return " ".join(partes)

    @staticmethod
    def _tono(score):
        if score > 0.05:
            return "positivo"
        if score < -0.05:
            return "negativo"
        return "neutral"


class AC4AnalisisHilos:
    def __init__(
        self,
        ruta_hilo=None,
        ruta_reporte="reportes/ac4_analisis_hilo.json",
    ):
        self.ruta_hilo = ruta_hilo
        self.ruta_reporte = ruta_reporte
        self.analizador = AnalizadorHiloDiscusion()

    def ejecutar(self):
        mensajes, origen = self._cargar_o_simular_hilo()
        self.analizador.cargar_hilo(mensajes)

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-4 — Análisis de hilo de discusión       ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Origen      : {origen}")
        print(f"  Mensajes    : {len(mensajes)}")
        print()

        resumen = self.analizador.resumen_hilo()
        evolucion = self.analizador.evolucion_sentimiento(ventana=3)
        subtemas = self.analizador.detectar_subtemas(n_clusters=3)
        resumen_auto = self.analizador.generar_resumen_automatico(subtemas)

        print("  ▶ Resumen del hilo")
        print(f"     Participantes       : {resumen['participantes']}")
        print(f"     Tono general        : {resumen['tono']} ({resumen['sentimiento_promedio']:+.3f})")
        print(f"     Positivos/Negativos : {resumen['positivos_pct']}% / {resumen['negativos_pct']}%")
        print(f"     Usuarios activos    : {resumen['usuarios_activos'][:3]}")
        print(f"     Hashtags            : {resumen['hashtags_top'][:5]}")

        print("\n  ▶ Evolución del sentimiento")
        for item in evolucion:
            barra = self._barra_sentimiento(item["tendencia_ventana"])
            print(
                f"     Msg {item['posicion']:>2} "
                f"[{item['sentimiento_puntual']:+.2f}] "
                f"tendencia={item['tendencia_ventana']:+.3f} {barra}"
            )

        print("\n  ▶ Subtemas detectados")
        for cluster_id, info in subtemas.items():
            print(
                f"     Subtema {int(cluster_id) + 1}: "
                f"{info['n_mensajes']} mensajes | keywords={info['keywords'][:5]}"
            )

        print("\n  ▶ Resumen automático")
        print("     " + resumen_auto)

        reporte = {
            "actividad": "AC-4 Análisis de hilos de discusión de red social",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "origen": origen,
            "mensajes_analizados": self.analizador.mensajes,
            "resumen": resumen,
            "evolucion_sentimiento": evolucion,
            "subtemas": subtemas,
            "resumen_automatico": resumen_auto,
        }

        self._guardar_json(self.ruta_reporte, reporte)
        print("\n  [Reporte] Guardado →", self.ruta_reporte)

        return reporte

    def _cargar_o_simular_hilo(self):
        if self.ruta_hilo and os.path.exists(self.ruta_hilo):
            with open(self.ruta_hilo, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, list):
                return datos, self.ruta_hilo
            if isinstance(datos, dict) and "mensajes" in datos:
                return datos["mensajes"], self.ruta_hilo

        return self._hilo_demo(), "hilo_demo_ia"

    def _hilo_demo(self):
        return [
            {"usuario": "@dev_laura", "texto": "Probé el nuevo asistente de IA para programar y me pareció impresionante. #IA #coding", "timestamp": "10:00"},
            {"usuario": "@tech_mike", "texto": "Estoy de acuerdo, las sugerencias de código son muy precisas y ahorran tiempo. #IA", "timestamp": "10:05"},
            {"usuario": "@skeptic_joe", "texto": "Pero me preocupa el desplazamiento laboral. Esta tecnología puede afectar a muchos trabajadores.", "timestamp": "10:08"},
            {"usuario": "@dev_laura", "texto": "Buen punto, pero lo veo como una herramienta y no como un reemplazo total. #AItools", "timestamp": "10:12"},
            {"usuario": "@data_sara", "texto": "El problema real está en los sesgos de los datos de entrenamiento. Se necesitan mejores datasets.", "timestamp": "10:15"},
            {"usuario": "@tech_mike", "texto": "El progreso es innegable. Es una etapa emocionante para la innovación tecnológica. #innovation", "timestamp": "10:20"},
            {"usuario": "@skeptic_joe", "texto": "Perdí un trabajo freelance por culpa de la IA. Esto es terrible para muchos trabajadores.", "timestamp": "10:25"},
            {"usuario": "@prof_chen", "texto": "La investigación muestra que la IA también puede crear nuevos empleos si hay capacitación.", "timestamp": "10:30"},
            {"usuario": "@data_sara", "texto": "Necesitamos regulación y lineamientos éticos urgentes. #AIethics", "timestamp": "10:35"},
            {"usuario": "@dev_laura", "texto": "Totalmente de acuerdo. El desarrollo responsable de IA es clave para evitar abusos. #responsible", "timestamp": "10:40"},
            {"usuario": "@tech_mike", "texto": "Las empresas deberían invertir en capacitación de empleados antes de automatizar procesos.", "timestamp": "10:45"},
            {"usuario": "@prof_chen", "texto": "Gran discusión. El futuro necesita innovación, responsabilidad y educación tecnológica.", "timestamp": "10:50"},
        ]

    def _guardar_json(self, ruta, contenido):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)

    @staticmethod
    def _barra_sentimiento(valor):
        if valor > 0:
            return "|" + "+" * int(valor * 20)
        if valor < 0:
            return "|" + "-" * int(abs(valor) * 20)
        return "|"


if __name__ == "__main__":
    AC4AnalisisHilos().ejecutar()
