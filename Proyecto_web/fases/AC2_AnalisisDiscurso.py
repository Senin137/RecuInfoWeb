
"""
SIMANW - AC-2: Nube de palabras y estadísticas de un discurso
=============================================================

Complemento de la Fase 2.

Cumple:
- Frecuencia de bigramas y trigramas.
- Riqueza léxica por secciones del texto.
- Identificación heurística de entidades nombradas.
- Comparación estadística entre múltiples textos.
- Exportación de resultados JSON.
- Generación opcional de nube de palabras si wordcloud está instalado.

Uso:
    python fases/AC2_AnalisisDiscurso.py
"""

import json
import os
import re
from collections import Counter
from datetime import datetime

import nltk
from nltk import bigrams, trigrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize


for recurso in ("punkt", "punkt_tab", "stopwords"):
    nltk.download(recurso, quiet=True)


BASURA_EXTRA = {
    "nbsp", "solo", "vez", "hace", "año", "años", "ser", "puede",
    "parte", "gran", "mismo", "misma", "además", "también", "aunque",
    "mientras", "durante", "través"
}


class AnalisisDiscurso:
    def __init__(self, idioma="spanish"):
        self.idioma = idioma
        self.stop_words = set(stopwords.words(idioma)) | BASURA_EXTRA

    def analizar(self, texto: str, titulo: str = "Documento", secciones: int = 4) -> dict:
        texto = texto.strip()
        oraciones = sent_tokenize(texto, language=self.idioma)
        tokens_originales = word_tokenize(texto, language=self.idioma)

        tokens_limpios = self._tokens_limpios(texto)
        bigramas = list(bigrams(tokens_limpios))
        trigramas = list(trigrams(tokens_limpios))

        riqueza_secciones = self._riqueza_por_secciones(tokens_limpios, secciones)
        entidades = self._extraer_entidades(texto)

        return {
            "titulo": titulo,
            "oraciones": len(oraciones),
            "palabras_totales": len([t for t in tokens_originales if t.isalpha()]),
            "tokens_utiles": len(tokens_limpios),
            "vocabulario_unico": len(set(tokens_limpios)),
            "riqueza_lexica_global": round(len(set(tokens_limpios)) / max(len(tokens_limpios), 1), 4),
            "riqueza_por_seccion": riqueza_secciones,
            "promedio_palabras_oracion": round(
                len([t for t in tokens_originales if t.isalpha()]) / max(len(oraciones), 1),
                2
            ),
            "top_unigramas": Counter(tokens_limpios).most_common(15),
            "top_bigramas": self._formatear_ngrams(Counter(bigramas).most_common(10)),
            "top_trigramas": self._formatear_ngrams(Counter(trigramas).most_common(8)),
            "entidades_nombradas": entidades,
        }

    def comparar_textos(self, analisis_lista: list[dict]) -> dict:
        filas = []
        for analisis in analisis_lista:
            filas.append({
                "titulo": analisis["titulo"],
                "palabras": analisis["palabras_totales"],
                "tokens_utiles": analisis["tokens_utiles"],
                "vocabulario": analisis["vocabulario_unico"],
                "riqueza": analisis["riqueza_lexica_global"],
                "promedio_oracion": analisis["promedio_palabras_oracion"],
                "entidades_detectadas": len(analisis["entidades_nombradas"]),
            })

        if not filas:
            return {"documentos": [], "mayor_riqueza": None, "mayor_extension": None}

        mayor_riqueza = max(filas, key=lambda x: x["riqueza"])
        mayor_extension = max(filas, key=lambda x: x["palabras"])

        return {
            "documentos": filas,
            "mayor_riqueza": mayor_riqueza["titulo"],
            "mayor_extension": mayor_extension["titulo"],
            "total_documentos": len(filas),
        }

    def generar_nube_palabras(self, texto: str, ruta_salida: str) -> bool:
        try:
            from wordcloud import WordCloud
        except ImportError:
            return False

        tokens = self._tokens_limpios(texto)
        if not tokens:
            return False

        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        nube = WordCloud(
            width=1000,
            height=500,
            background_color="white",
            max_words=120
        ).generate(" ".join(tokens))
        nube.to_file(ruta_salida)
        return True

    def _tokens_limpios(self, texto: str) -> list[str]:
        texto = texto.lower()
        texto = re.sub(r"https?://\S+", " ", texto)
        texto = re.sub(r"[^\w\sáéíóúñü]", " ", texto)
        texto = re.sub(r"\d+", " ", texto)
        tokens = word_tokenize(texto, language=self.idioma)
        return [
            t for t in tokens
            if t.isalpha() and len(t) > 2 and t not in self.stop_words
        ]

    def _riqueza_por_secciones(self, tokens: list[str], secciones: int) -> list[dict]:
        if not tokens:
            return []

        tamano = max(len(tokens) // secciones, 1)
        salida = []

        for i in range(secciones):
            inicio = i * tamano
            fin = (i + 1) * tamano if i < secciones - 1 else len(tokens)
            segmento = tokens[inicio:fin]

            if not segmento:
                continue

            salida.append({
                "seccion": i + 1,
                "tokens": len(segmento),
                "vocabulario": len(set(segmento)),
                "riqueza": round(len(set(segmento)) / max(len(segmento), 1), 4),
            })

        return salida

    def _extraer_entidades(self, texto: str) -> list[tuple[str, int]]:
        patron = r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3}"
        candidatas = re.findall(patron, texto)

        descartes = {
            "El", "La", "Los", "Las", "Un", "Una", "En", "Para", "Por",
            "Con", "Sin", "Del", "Al", "Este", "Esta", "Estos", "Estas"
        }

        entidades = []
        for entidad in candidatas:
            entidad = entidad.strip()
            if entidad in descartes:
                continue
            if entidad.lower() in self.stop_words:
                continue
            if len(entidad) < 4:
                continue
            entidades.append(entidad)

        return Counter(entidades).most_common(12)

    @staticmethod
    def _formatear_ngrams(ngrams_contados: list[tuple[tuple[str, ...], int]]) -> list[tuple[str, int]]:
        return [(" ".join(grama), frecuencia) for grama, frecuencia in ngrams_contados]


class AC2AnalisisDiscurso:
    def __init__(
        self,
        ruta_reporte: str = "reportes/ac2_analisis_discurso.json",
        ruta_nube: str = "graficos/ac2_nube_palabras.png",
    ):
        self.ruta_reporte = ruta_reporte
        self.ruta_nube = ruta_nube
        self.analizador = AnalisisDiscurso()

    def ejecutar_demo(self) -> dict:
        textos = self._textos_demo()

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-2 — Análisis estadístico de textos      ║")
        print("╚══════════════════════════════════════════════╝")

        analisis = []
        for titulo, texto in textos.items():
            resultado = self.analizador.analizar(texto, titulo)
            analisis.append(resultado)

            print(f"\n  ▶ {titulo}")
            print(f"     Oraciones              : {resultado['oraciones']}")
            print(f"     Palabras totales        : {resultado['palabras_totales']}")
            print(f"     Vocabulario único       : {resultado['vocabulario_unico']}")
            print(f"     Riqueza léxica global   : {resultado['riqueza_lexica_global']}")
            print(f"     Top bigramas            : {resultado['top_bigramas'][:3]}")
            print(f"     Top trigramas           : {resultado['top_trigramas'][:3]}")
            print(f"     Entidades detectadas    : {resultado['entidades_nombradas'][:5]}")

        comparativa = self.analizador.comparar_textos(analisis)
        nube_generada = self.analizador.generar_nube_palabras(
            " ".join(textos.values()),
            self.ruta_nube
        )

        reporte = {
            "actividad": "AC-2 Nube de palabras y estadísticas de un discurso",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "analisis": analisis,
            "comparativa": comparativa,
            "nube_palabras": self.ruta_nube if nube_generada else "No generada: instala wordcloud para habilitarla",
        }

        self._guardar_json(self.ruta_reporte, reporte)

        print("\n  ── Comparativa ─────────────────────────────")
        for fila in comparativa["documentos"]:
            print(
                f"  {fila['titulo']:<24} "
                f"palabras={fila['palabras']:<4} "
                f"riqueza={fila['riqueza']:<6} "
                f"entidades={fila['entidades_detectadas']}"
            )

        print("\n  [Reporte] Guardado →", self.ruta_reporte)
        if nube_generada:
            print("  [Nube]    Guardada →", self.ruta_nube)
        else:
            print("  [Nube]    No generada. Instala con: pip install wordcloud")

        return reporte

    def _guardar_json(self, ruta: str, contenido: dict):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)

    def _textos_demo(self) -> dict[str, str]:
        return {
            "Discurso educativo": """
            La educación es la herramienta más poderosa para transformar una sociedad.
            En México, la inversión en educación debe ser prioritaria para garantizar
            el desarrollo económico y social. Los jóvenes mexicanos merecen oportunidades
            de calidad en todos los niveles educativos. Las universidades tecnológicas y
            los institutos de investigación son pilares fundamentales para la innovación.
            La ciencia y la tecnología son motores del progreso nacional. El Instituto
            Tecnológico de Morelia ha formado generaciones de ingenieros que contribuyen
            al desarrollo del país. La inteligencia artificial y la programación son
            competencias esenciales para el futuro laboral. México necesita más profesionales
            en ciencias computacionales y recuperación de información.
            """,
            "Texto científico": """
            El procesamiento de lenguaje natural permite a las computadoras comprender
            y generar texto humano. Los modelos de aprendizaje profundo como BERT y GPT
            han revolucionado este campo. La representación vectorial de documentos mediante
            TF-IDF sigue siendo fundamental para sistemas de recuperación de información.
            Los algoritmos de clasificación como Naive Bayes y SVM logran alta precisión
            en categorización de texto. El análisis de sentimientos combina técnicas léxicas
            con aprendizaje automático para determinar la polaridad emocional de un texto.
            """,
            "Artículo tecnológico": """
            OpenAI, Google, Microsoft y Anthropic compiten por desarrollar modelos de
            inteligencia artificial más seguros y eficientes. En América Latina, empresas
            emergentes de México, Colombia y Argentina comienzan a integrar asistentes
            conversacionales en servicios financieros, educación y comercio electrónico.
            La recuperación de información se vuelve esencial para organizar grandes
            volúmenes de documentos, noticias y datos abiertos.
            """,
        }


if __name__ == "__main__":
    AC2AnalisisDiscurso().ejecutar_demo()
