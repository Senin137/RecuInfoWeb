
"""
SIMANW - Generador de nubes de palabras por sección
===================================================

Objetivo:
    Generar una nube global y una nube por categoría/sección del corpus:
    tecnologia, ciencia, economia, gobierno, mundo y deportes.

Uso:
    python fases/AC2_NubesPorSeccion.py

Entradas:
    datos/dataset_analizado.json
    datos/dataset_maestro.json

Salidas:
    reportes/nubes/nube_global.png
    reportes/nubes/nube_tecnologia.png
    reportes/nubes/nube_ciencia.png
    reportes/nubes/nube_economia.png
    reportes/nubes/nube_gobierno.png
    reportes/nubes/nube_mundo.png
    reportes/nubes/nube_deportes.png
    reportes/nubes/reporte_nubes_por_seccion.json

Instalación si falta wordcloud:
    pip install wordcloud
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import nltk
from nltk.corpus import stopwords

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
except Exception as exc:
    WordCloud = None
    plt = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


for recurso in ("stopwords",):
    nltk.download(recurso, quiet=True)


def resolver_raiz_proyecto():
    actual = Path.cwd().resolve()

    if (actual / "datos").exists() and (actual / "fases").exists():
        return actual

    if actual.name.lower() == "fases" and (actual.parent / "datos").exists():
        return actual.parent

    archivo = Path(__file__).resolve()
    if (archivo.parent.parent / "datos").exists():
        return archivo.parent.parent

    return actual


ROOT = resolver_raiz_proyecto()

STOPWORDS_EXTRA = {
    "nbsp", "solo", "vez", "hace", "año", "años", "ser", "puede", "pueden",
    "parte", "gran", "mismo", "misma", "además", "también", "tras",
    "según", "aunque", "mientras", "durante", "través", "nuevo", "nueva",
    "noticia", "noticias", "dijo", "dice", "será", "sera", "haber",
    "hacer", "cada", "dos", "tres", "personas", "forma", "medio",
    "país", "pais", "méxico", "mexico", "españa", "espana"
}

STOPWORDS_ES = set(stopwords.words("spanish")) | STOPWORDS_EXTRA


class GeneradorNubesPorSeccion:
    def __init__(
        self,
        ruta_dataset=None,
        ruta_salida=None,
        max_words=120,
        width=1200,
        height=700,
    ):
        self.ruta_dataset = Path(ruta_dataset) if ruta_dataset else self._resolver_dataset()
        self.ruta_salida = Path(ruta_salida) if ruta_salida else ROOT / "reportes" / "nubes"
        self.max_words = max_words
        self.width = width
        self.height = height

    def ejecutar(self):
        if WordCloud is None:
            raise ImportError(
                "Falta instalar wordcloud. Ejecuta: pip install wordcloud"
            ) from IMPORT_ERROR

        noticias = self._cargar_noticias()
        self.ruta_salida.mkdir(parents=True, exist_ok=True)

        grupos = self._agrupar_textos(noticias)
        reporte = {
            "actividad": "Nubes de palabras por sección",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "dataset": str(self.ruta_dataset),
            "total_noticias": len(noticias),
            "salida": str(self.ruta_salida),
            "nubes": {},
        }

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-2 — Nubes de palabras por sección       ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Dataset      : {self.ruta_dataset}")
        print(f"  Noticias     : {len(noticias)}")
        print(f"  Carpeta      : {self.ruta_salida}")
        print()

        for nombre, textos in grupos.items():
            texto_total = " ".join(textos)
            frecuencias = self._frecuencias(texto_total)

            if not frecuencias:
                print(f"  [OMITIDA] {nombre}: sin texto suficiente")
                reporte["nubes"][nombre] = {
                    "estado": "omitida",
                    "motivo": "sin texto suficiente",
                    "noticias": len(textos),
                    "archivo": None,
                    "top_terminos": [],
                }
                continue

            archivo = self.ruta_salida / f"nube_{nombre}.png"
            self._crear_nube(frecuencias, archivo, titulo=f"SIMANW — {nombre}")

            reporte["nubes"][nombre] = {
                "estado": "generada",
                "noticias": len(textos),
                "archivo": str(archivo),
                "top_terminos": frecuencias.most_common(25),
            }

            print(f"  [OK] nube_{nombre}.png | noticias={len(textos)} | términos={len(frecuencias)}")

        ruta_reporte = self.ruta_salida / "reporte_nubes_por_seccion.json"
        with open(ruta_reporte, "w", encoding="utf-8") as f:
            json.dump(reporte, f, ensure_ascii=False, indent=2)

        print()
        print("  [Reporte] Guardado →", ruta_reporte)

        return reporte

    def _resolver_dataset(self):
        opciones = [
            ROOT / "datos" / "dataset_analizado.json",
            ROOT / "datos" / "dataset_depurado_ac8.json",
            ROOT / "datos" / "dataset_maestro.json",
        ]

        for ruta in opciones:
            if ruta.exists():
                return ruta

        return opciones[-1]

    def _cargar_noticias(self):
        if not self.ruta_dataset.exists():
            raise FileNotFoundError(f"No se encontró el dataset: {self.ruta_dataset}")

        with open(self.ruta_dataset, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not isinstance(datos, list):
            raise ValueError("El dataset debe ser una lista de noticias.")

        return datos

    def _agrupar_textos(self, noticias):
        grupos = defaultdict(list)

        for noticia in noticias:
            texto = self._texto_noticia(noticia)
            if not texto.strip():
                continue

            cat = self._categoria(noticia)
            grupos["global"].append(texto)
            grupos[cat].append(texto)

        orden = ["global", "tecnologia", "ciencia", "economia", "gobierno", "mundo", "deportes"]
        salida = {}

        for cat in orden:
            if cat in grupos:
                salida[cat] = grupos[cat]

        for cat, textos in grupos.items():
            if cat not in salida:
                salida[cat] = textos

        return salida

    def _texto_noticia(self, noticia):
        return " ".join([
            str(noticia.get("titulo", "")),
            str(noticia.get("resumen", "")),
            str(noticia.get("cuerpo", "")),
            str(noticia.get("categoria", "")),
            str(noticia.get("categoria_predicha", "")),
            str(noticia.get("categoria_original", "")),
        ])

    def _categoria(self, noticia):
        cat = (
            noticia.get("categoria_predicha")
            or noticia.get("categoria")
            or noticia.get("categoria_original")
            or "general"
        )
        cat = str(cat).lower().strip()
        cat = cat.replace("política", "gobierno").replace("politica", "gobierno")
        cat = cat.replace("deporte", "deportes").replace("sports", "deportes")
        cat = re.sub(r"[^a-záéíóúñü_]+", "_", cat)
        cat = cat.strip("_")
        return cat or "general"

    def _frecuencias(self, texto):
        texto = texto.lower()
        texto = re.sub(r"https?://\S+", " ", texto)
        texto = re.sub(r"www\.\S+", " ", texto)
        texto = re.sub(r"[^\w\sáéíóúñü]", " ", texto)
        texto = re.sub(r"\d+", " ", texto)
        tokens = [
            t for t in texto.split()
            if len(t) > 3 and t not in STOPWORDS_ES
        ]

        return Counter(tokens)

    def _crear_nube(self, frecuencias, archivo, titulo):
        wc = WordCloud(
            width=self.width,
            height=self.height,
            background_color="#0e0e0f",
            colormap="viridis",
            max_words=self.max_words,
            stopwords=STOPWORDS_ES,
            collocations=False,
            prefer_horizontal=0.9,
        ).generate_from_frequencies(frecuencias)

        plt.figure(figsize=(12, 7))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title(titulo, color="#e8e8ec", fontsize=18, pad=16)
        plt.tight_layout(pad=0)
        plt.savefig(archivo, dpi=160, facecolor="#0e0e0f", bbox_inches="tight")
        plt.close()


if __name__ == "__main__":
    GeneradorNubesPorSeccion().ejecutar()
