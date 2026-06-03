
"""
SIMANW - AC-9: Línea de tiempo y tendencias por tema
====================================================

Complemento de Fases 2-3.

Objetivo:
    Analizar cómo cambian los temas/categorías del corpus a través del tiempo.

Cumple:
- Agrupa noticias por periodo semanal o mensual.
- Justifica la granularidad elegida.
- Analiza al menos tres categorías.
- Cuenta noticias por periodo.
- Detecta términos que suben o bajan entre primer y último periodo.
- Identifica picos o caídas apoyándose en títulos reales.
- Exporta tabla resumen CSV/JSON.
- Genera visualización con matplotlib.
- Redacta conclusión de una página en Markdown.

Uso:
    python fases/AC9_LineaTiempoTendencias.py

Entrada:
    datos/dataset_analizado.json

Salidas:
    reportes/ac9_tendencias_temporales.json
    reportes/ac9_tabla_resumen_tendencias.csv
    reportes/ac9_conclusion_tendencias.md
    graficos/ac9_tendencias_por_categoria.png
"""

import csv
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams


for recurso in ("stopwords",):
    nltk.download(recurso, quiet=True)


STOPWORDS_ES = set(stopwords.words("spanish")) | {
    "nbsp", "solo", "vez", "hace", "año", "años", "ser", "puede",
    "parte", "gran", "mismo", "misma", "además", "también", "tras",
    "según", "aunque", "mientras", "durante", "través", "nuevo", "nueva"
}


def resolver_raiz_proyecto():
    actual = Path.cwd().resolve()

    if (actual / "datos").exists():
        return actual

    if actual.name.lower() == "fases" and (actual.parent / "datos").exists():
        return actual.parent

    archivo = Path(__file__).resolve()
    if (archivo.parent.parent / "datos").exists():
        return archivo.parent.parent

    return actual


ROOT = resolver_raiz_proyecto()


class AnalizadorTendenciasTemporales:
    def __init__(self, noticias, granularidad="auto"):
        self.noticias = self._normalizar_fechas(noticias)
        self.granularidad = self._elegir_granularidad(granularidad)
        self.justificacion = self._justificar_granularidad()

    def analizar(self, top_categorias=5):
        categorias = self._categorias_principales(top_categorias)
        periodos = sorted({n["periodo"] for n in self.noticias if n.get("periodo")})

        conteos = self._conteos_por_periodo(categorias, periodos)
        tendencias = self._tendencias_terminos(categorias, periodos)
        picos_caidas = self._detectar_picos_caidas(categorias, conteos, periodos)
        tabla = self._tabla_resumen(categorias, conteos, tendencias, picos_caidas)

        return {
            "granularidad": self.granularidad,
            "justificacion_granularidad": self.justificacion,
            "periodos": periodos,
            "categorias_analizadas": categorias,
            "conteos_por_periodo": conteos,
            "tendencias_terminos": tendencias,
            "picos_y_caidas": picos_caidas,
            "tabla_resumen": tabla,
            "conclusion": self._conclusion(categorias, periodos, conteos, tendencias, picos_caidas),
        }

    def _normalizar_fechas(self, noticias):
        normalizadas = []
        for i, noticia in enumerate(noticias):
            item = dict(noticia)
            fecha = self._parse_fecha(item.get("fecha") or item.get("fecha_publicacion") or item.get("published") or "")

            if fecha is None:
                fecha = datetime.now()

            item["_fecha_dt"] = fecha
            normalizadas.append(item)

        return normalizadas

    def _parse_fecha(self, valor):
        if not valor:
            return None

        texto = str(valor).strip()

        formatos = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%d/%m/%Y",
            "%d-%m-%Y",
        ]

        for formato in formatos:
            try:
                return datetime.strptime(texto[:19], formato)
            except ValueError:
                pass

        try:
            return parsedate_to_datetime(texto).replace(tzinfo=None)
        except Exception:
            pass

        match = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", texto)
        if match:
            try:
                return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
            except ValueError:
                return None

        return None

    def _elegir_granularidad(self, granularidad):
        if granularidad in {"semana", "mes"}:
            elegido = granularidad
        else:
            fechas = [n["_fecha_dt"] for n in self.noticias]
            if not fechas:
                elegido = "mes"
            else:
                rango_dias = (max(fechas) - min(fechas)).days
                elegido = "semana" if rango_dias <= 90 else "mes"

        for noticia in self.noticias:
            noticia["periodo"] = self._periodo(noticia["_fecha_dt"], elegido)

        return elegido

    def _periodo(self, fecha, granularidad):
        if granularidad == "semana":
            iso = fecha.isocalendar()
            return f"{iso.year}-S{iso.week:02d}"

        return f"{fecha.year}-{fecha.month:02d}"

    def _justificar_granularidad(self):
        fechas = [n["_fecha_dt"] for n in self.noticias]
        if not fechas:
            return "Se usó agrupación mensual por ausencia de fechas válidas suficientes."

        rango_dias = (max(fechas) - min(fechas)).days
        if self.granularidad == "semana":
            return (
                f"Se eligió granularidad semanal porque el rango temporal del corpus es de {rango_dias} días; "
                "esto permite observar variaciones finas sin fragmentar demasiado los datos."
            )

        return (
            f"Se eligió granularidad mensual porque el rango temporal del corpus es de {rango_dias} días; "
            "esto reduce ruido y permite comparar tendencias agregadas con mayor estabilidad."
        )

    def _categorias_principales(self, top_n):
        conteo = Counter(self._categoria(n) for n in self.noticias)
        return [cat for cat, _ in conteo.most_common(max(top_n, 3))]

    def _conteos_por_periodo(self, categorias, periodos):
        conteos = {
            cat: {periodo: 0 for periodo in periodos}
            for cat in categorias
        }

        for noticia in self.noticias:
            cat = self._categoria(noticia)
            periodo = noticia.get("periodo")

            if cat in conteos and periodo in conteos[cat]:
                conteos[cat][periodo] += 1

        return conteos

    def _tendencias_terminos(self, categorias, periodos):
        if not periodos:
            return {}

        primer_periodo = periodos[0]
        ultimo_periodo = periodos[-1]
        salida = {}

        for categoria in categorias:
            textos_inicio = [
                self._texto(n)
                for n in self.noticias
                if self._categoria(n) == categoria and n.get("periodo") == primer_periodo
            ]
            textos_final = [
                self._texto(n)
                for n in self.noticias
                if self._categoria(n) == categoria and n.get("periodo") == ultimo_periodo
            ]

            freq_inicio = self._frecuencias_expresiones(" ".join(textos_inicio))
            freq_final = self._frecuencias_expresiones(" ".join(textos_final))

            todos = set(freq_inicio) | set(freq_final)
            cambios = []
            for termino in todos:
                inicial = freq_inicio.get(termino, 0)
                final = freq_final.get(termino, 0)
                cambios.append({
                    "termino": termino,
                    "frecuencia_inicio": inicial,
                    "frecuencia_final": final,
                    "cambio": final - inicial,
                })

            suben = sorted(cambios, key=lambda x: x["cambio"], reverse=True)[:8]
            bajan = sorted(cambios, key=lambda x: x["cambio"])[:8]

            salida[categoria] = {
                "primer_periodo": primer_periodo,
                "ultimo_periodo": ultimo_periodo,
                "terminos_aumentan": [x for x in suben if x["cambio"] > 0],
                "terminos_disminuyen": [x for x in bajan if x["cambio"] < 0],
            }

        return salida

    def _detectar_picos_caidas(self, categorias, conteos, periodos):
        salida = {}

        for categoria in categorias:
            serie = conteos.get(categoria, {})
            if not serie:
                continue

            periodo_pico = max(periodos, key=lambda p: serie.get(p, 0))
            periodo_min = min(periodos, key=lambda p: serie.get(p, 0))

            titulos_pico = [
                n.get("titulo", "")
                for n in self.noticias
                if self._categoria(n) == categoria and n.get("periodo") == periodo_pico
            ][:5]

            titulos_min = [
                n.get("titulo", "")
                for n in self.noticias
                if self._categoria(n) == categoria and n.get("periodo") == periodo_min
            ][:5]

            salida[categoria] = {
                "pico": {
                    "periodo": periodo_pico,
                    "conteo": serie.get(periodo_pico, 0),
                    "titulos_reales": titulos_pico,
                },
                "caida": {
                    "periodo": periodo_min,
                    "conteo": serie.get(periodo_min, 0),
                    "titulos_reales": titulos_min,
                },
                "variacion_pico_caida": serie.get(periodo_pico, 0) - serie.get(periodo_min, 0),
            }

        return salida

    def _tabla_resumen(self, categorias, conteos, tendencias, picos_caidas):
        tabla = []

        for categoria in categorias:
            total = sum(conteos[categoria].values())
            pico = picos_caidas.get(categoria, {}).get("pico", {})
            caida = picos_caidas.get(categoria, {}).get("caida", {})
            suben = tendencias.get(categoria, {}).get("terminos_aumentan", [])
            bajan = tendencias.get(categoria, {}).get("terminos_disminuyen", [])

            tabla.append({
                "categoria": categoria,
                "total_noticias": total,
                "periodo_pico": pico.get("periodo", ""),
                "conteo_pico": pico.get("conteo", 0),
                "periodo_caida": caida.get("periodo", ""),
                "conteo_caida": caida.get("conteo", 0),
                "terminos_suben": ", ".join(t["termino"] for t in suben[:5]),
                "terminos_bajan": ", ".join(t["termino"] for t in bajan[:5]),
            })

        return tabla

    def _conclusion(self, categorias, periodos, conteos, tendencias, picos_caidas):
        if not categorias or not periodos:
            return "No fue posible generar conclusión porque el corpus no contiene suficientes fechas o categorías."

        dominante = max(categorias, key=lambda c: sum(conteos[c].values()))
        total_dom = sum(conteos[dominante].values())

        partes = [
            "# Conclusión AC-9: Línea de tiempo y tendencias por tema",
            "",
            f"El análisis temporal se realizó con granularidad **{self.granularidad}**. {self.justificacion}",
            "",
            f"El corpus analizado cubre **{len(periodos)} periodos** y las categorías principales fueron: "
            + ", ".join(categorias)
            + ".",
            "",
            f"La categoría con mayor presencia acumulada fue **{dominante}**, con **{total_dom} noticias**.",
            "",
        ]

        for categoria in categorias[:5]:
            pico = picos_caidas.get(categoria, {}).get("pico", {})
            caida = picos_caidas.get(categoria, {}).get("caida", {})
            suben = tendencias.get(categoria, {}).get("terminos_aumentan", [])
            bajan = tendencias.get(categoria, {}).get("terminos_disminuyen", [])

            partes.append(f"## Categoría: {categoria}")
            partes.append(
                f"Su punto más alto ocurrió en **{pico.get('periodo', 'N/D')}** con "
                f"**{pico.get('conteo', 0)} noticias**, mientras que su nivel más bajo apareció en "
                f"**{caida.get('periodo', 'N/D')}** con **{caida.get('conteo', 0)} noticias**."
            )

            if suben:
                partes.append(
                    "Las expresiones que más aumentaron fueron: "
                    + ", ".join(f"**{x['termino']}**" for x in suben[:5])
                    + "."
                )

            if bajan:
                partes.append(
                    "Las expresiones que más disminuyeron fueron: "
                    + ", ".join(f"**{x['termino']}**" for x in bajan[:5])
                    + "."
                )

            titulos = pico.get("titulos_reales", [])
            if titulos:
                partes.append(
                    "El pico se apoya en títulos reales como: "
                    + "; ".join(f"“{t[:90]}”" for t in titulos[:3])
                    + "."
                )

            partes.append("")

        partes.append(
            "En conjunto, la línea de tiempo permite observar que el SIMANW no solo clasifica noticias de forma estática, "
            "sino que también puede detectar variaciones de presencia temática. Esto es útil para identificar momentos de "
            "mayor cobertura, cambios de agenda informativa y términos emergentes dentro del corpus."
        )

        return "\n".join(partes)

    def _frecuencias_expresiones(self, texto):
        tokens = self._tokens(texto)
        expresiones = Counter(tokens)

        for n in (2, 3):
            for grama in ngrams(tokens, n):
                expresiones[" ".join(grama)] += 1

        return expresiones

    def _tokens(self, texto):
        texto = (texto or "").lower()
        texto = re.sub(r"https?://\S+", " ", texto)
        texto = re.sub(r"[^\w\sáéíóúñü]", " ", texto)
        texto = re.sub(r"\d+", " ", texto)
        return [
            t for t in texto.split()
            if len(t) > 2 and t not in STOPWORDS_ES
        ]

    def _texto(self, noticia):
        return " ".join([
            str(noticia.get("titulo", "")),
            str(noticia.get("cuerpo", "")),
        ])

    def _categoria(self, noticia):
        return (
            noticia.get("categoria_predicha")
            or noticia.get("categoria")
            or noticia.get("categoria_original")
            or "general"
        ).lower()


class AC9LineaTiempoTendencias:
    def __init__(
        self,
        ruta_dataset=None,
        ruta_reporte=None,
        ruta_csv=None,
        ruta_md=None,
        ruta_grafico=None,
    ):
        self.ruta_dataset = Path(ruta_dataset) if ruta_dataset else ROOT / "datos" / "dataset_analizado.json"
        self.ruta_reporte = Path(ruta_reporte) if ruta_reporte else ROOT / "reportes" / "ac9_tendencias_temporales.json"
        self.ruta_csv = Path(ruta_csv) if ruta_csv else ROOT / "reportes" / "ac9_tabla_resumen_tendencias.csv"
        self.ruta_md = Path(ruta_md) if ruta_md else ROOT / "reportes" / "ac9_conclusion_tendencias.md"
        self.ruta_grafico = Path(ruta_grafico) if ruta_grafico else ROOT / "graficos" / "ac9_tendencias_por_categoria.png"

    def ejecutar(self):
        noticias = self._cargar_noticias()
        analizador = AnalizadorTendenciasTemporales(noticias, granularidad="auto")
        resultado = analizador.analizar(top_categorias=5)

        self._guardar_json(self.ruta_reporte, resultado)
        self._guardar_csv(self.ruta_csv, resultado["tabla_resumen"])
        self._guardar_texto(self.ruta_md, resultado["conclusion"])
        self._generar_grafico(resultado)

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-9 — Línea de tiempo y tendencias        ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Dataset       : {self.ruta_dataset}")
        print(f"  Noticias      : {len(noticias)}")
        print(f"  Granularidad  : {resultado['granularidad']}")
        print(f"  Periodos      : {len(resultado['periodos'])}")
        print(f"  Categorías    : {', '.join(resultado['categorias_analizadas'])}")
        print()
        print("  Justificación:")
        print("  " + resultado["justificacion_granularidad"])
        print()
        print("  Tabla resumen:")
        for fila in resultado["tabla_resumen"]:
            print(
                f"   - {fila['categoria']}: total={fila['total_noticias']}, "
                f"pico={fila['periodo_pico']} ({fila['conteo_pico']}), "
                f"caída={fila['periodo_caida']} ({fila['conteo_caida']})"
            )

        print()
        print("  [Reporte JSON] Guardado →", self.ruta_reporte)
        print("  [Tabla CSV]    Guardada →", self.ruta_csv)
        print("  [Conclusión]   Guardada →", self.ruta_md)
        print("  [Gráfico]      Guardado →", self.ruta_grafico)

        return resultado

    def _cargar_noticias(self):
        if not self.ruta_dataset.exists():
            raise FileNotFoundError(f"No se encontró el dataset: {self.ruta_dataset}")

        with open(self.ruta_dataset, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not isinstance(datos, list) or not datos:
            raise ValueError("El dataset debe ser una lista de noticias no vacía.")

        return datos

    def _generar_grafico(self, resultado):
        periodos = resultado["periodos"]
        conteos = resultado["conteos_por_periodo"]

        self.ruta_grafico.parent.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(12, 6))

        for categoria in resultado["categorias_analizadas"]:
            valores = [conteos[categoria].get(p, 0) for p in periodos]
            plt.plot(periodos, valores, marker="o", label=categoria)

        plt.title("AC-9: Tendencias temporales por categoría")
        plt.xlabel("Periodo")
        plt.ylabel("Cantidad de noticias")
        plt.xticks(rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.savefig(self.ruta_grafico, dpi=150)
        plt.close()

    def _guardar_json(self, ruta, contenido):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)

    def _guardar_csv(self, ruta, filas):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        if not filas:
            return

        with open(ruta, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
            writer.writeheader()
            writer.writerows(filas)

    def _guardar_texto(self, ruta, texto):
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)


if __name__ == "__main__":
    AC9LineaTiempoTendencias().ejecutar()
