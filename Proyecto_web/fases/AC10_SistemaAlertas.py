
"""
SIMANW - AC-10: Sistema de alertas por consulta guardada
========================================================

Complemento de Fases 1 y 4.

Objetivo:
    Permitir consultas permanentes y generar alertas cuando entren noticias
    nuevas que coincidan con esas consultas.

Cumple:
- Persiste al menos cinco consultas guardadas con nombre y fecha de creación.
- Al incorporar noticias nuevas, determina qué consultas se activan y con qué documentos.
- Mantiene historial de alertas: consulta, noticia, marca de tiempo.
- Demuestra dos ejecuciones:
    1) Sin noticias nuevas.
    2) Agregando al menos cinco noticias nuevas.
- Documenta cómo se evitan alertas duplicadas.

Uso:
    python fases/AC10_SistemaAlertas.py

Entradas:
    datos/dataset_analizado.json

Salidas:
    config/ac10_consultas_guardadas.json
    datos/ac10_noticias_nuevas_demo.json
    reportes/ac10_historial_alertas.json
    reportes/ac10_reporte_alertas.json
    reportes/ac10_documentacion_duplicados.md
"""

import json
import os
import re
import hashlib
from datetime import datetime
from pathlib import Path

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


class SistemaAlertasConsultaGuardada:
    def __init__(
        self,
        ruta_consultas=None,
        ruta_historial=None,
        umbral_similitud=0.12,
    ):
        self.ruta_consultas = Path(ruta_consultas) if ruta_consultas else ROOT / "config" / "ac10_consultas_guardadas.json"
        self.ruta_historial = Path(ruta_historial) if ruta_historial else ROOT / "reportes" / "ac10_historial_alertas.json"
        self.umbral_similitud = umbral_similitud

        self.consultas = self._cargar_o_crear_consultas()
        self.historial = self._cargar_historial()

    def evaluar_noticias(self, noticias, etiqueta_ejecucion):
        if not noticias:
            return {
                "etiqueta_ejecucion": etiqueta_ejecucion,
                "noticias_evaluadas": 0,
                "alertas_generadas": [],
                "alertas_omitidas_por_duplicado": 0,
            }

        textos_noticias = [self._texto_noticia(n) for n in noticias]
        textos_consultas = [c["query"] for c in self.consultas]

        vectorizador = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            lowercase=True,
            stop_words=STOPWORDS_ES,
            sublinear_tf=True,
        )

        matriz = vectorizador.fit_transform(textos_noticias + textos_consultas)
        matriz_noticias = matriz[:len(textos_noticias)]
        matriz_consultas = matriz[len(textos_noticias):]

        alertas = []
        duplicadas = 0

        for idx_consulta, consulta in enumerate(self.consultas):
            vector_consulta = matriz_consultas[idx_consulta]
            similitudes = cosine_similarity(vector_consulta, matriz_noticias)[0]

            for idx_noticia, score in enumerate(similitudes):
                if score < self.umbral_similitud:
                    continue

                noticia = noticias[idx_noticia]
                noticia_id = self._id_noticia(noticia)
                alerta_id = self._id_alerta(consulta["id"], noticia_id)

                if alerta_id in self.historial["alertas_emitidas"]:
                    duplicadas += 1
                    continue

                alerta = {
                    "alerta_id": alerta_id,
                    "consulta_id": consulta["id"],
                    "consulta_nombre": consulta["nombre"],
                    "query": consulta["query"],
                    "noticia_id": noticia_id,
                    "noticia_titulo": noticia.get("titulo", "Sin título"),
                    "noticia_url": noticia.get("url", ""),
                    "categoria": self._categoria(noticia),
                    "similitud": round(float(score), 4),
                    "marca_tiempo": datetime.now().isoformat(timespec="seconds"),
                    "ejecucion": etiqueta_ejecucion,
                }

                alertas.append(alerta)
                self.historial["alertas_emitidas"][alerta_id] = alerta
                self.historial["orden"].append(alerta_id)

        self._guardar_historial()

        return {
            "etiqueta_ejecucion": etiqueta_ejecucion,
            "noticias_evaluadas": len(noticias),
            "alertas_generadas": alertas,
            "alertas_omitidas_por_duplicado": duplicadas,
        }

    def _cargar_o_crear_consultas(self):
        if self.ruta_consultas.exists():
            with open(self.ruta_consultas, "r", encoding="utf-8") as f:
                return json.load(f)

        consultas = [
            {
                "id": "C001",
                "nombre": "Inteligencia artificial",
                "query": "inteligencia artificial machine learning modelos generativos",
                "fecha_creacion": datetime.now().isoformat(timespec="seconds"),
            },
            {
                "id": "C002",
                "nombre": "Economía e inflación",
                "query": "economía inflación mercados tasas banco inversión",
                "fecha_creacion": datetime.now().isoformat(timespec="seconds"),
            },
            {
                "id": "C003",
                "nombre": "Ciencia y clima",
                "query": "ciencia investigación cambio climático salud estudio científico",
                "fecha_creacion": datetime.now().isoformat(timespec="seconds"),
            },
            {
                "id": "C004",
                "nombre": "Gobierno y política",
                "query": "gobierno política elecciones congreso reforma ley justicia",
                "fecha_creacion": datetime.now().isoformat(timespec="seconds"),
            },
            {
                "id": "C005",
                "nombre": "Internacional y conflictos",
                "query": "internacional mundo guerra conflicto migración países diplomacia",
                "fecha_creacion": datetime.now().isoformat(timespec="seconds"),
            },
        ]

        self.ruta_consultas.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta_consultas, "w", encoding="utf-8") as f:
            json.dump(consultas, f, ensure_ascii=False, indent=2)

        return consultas

    def _cargar_historial(self):
        if self.ruta_historial.exists():
            with open(self.ruta_historial, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "alertas_emitidas" in data and "orden" in data:
                return data

        return {
            "creado": datetime.now().isoformat(timespec="seconds"),
            "alertas_emitidas": {},
            "orden": [],
        }

    def _guardar_historial(self):
        self.ruta_historial.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ruta_historial, "w", encoding="utf-8") as f:
            json.dump(self.historial, f, ensure_ascii=False, indent=2)

    def _texto_noticia(self, noticia):
        return " ".join([
            str(noticia.get("titulo", "")),
            str(noticia.get("cuerpo", "")),
            str(noticia.get("resumen", "")),
            str(noticia.get("categoria", "")),
            str(noticia.get("categoria_predicha", "")),
        ])

    def _id_noticia(self, noticia):
        base = noticia.get("url") or noticia.get("titulo") or json.dumps(noticia, ensure_ascii=False)
        return hashlib.sha1(str(base).encode("utf-8")).hexdigest()[:16]

    def _id_alerta(self, consulta_id, noticia_id):
        base = f"{consulta_id}|{noticia_id}"
        return hashlib.sha1(base.encode("utf-8")).hexdigest()[:20]

    def _categoria(self, noticia):
        return (
            noticia.get("categoria_predicha")
            or noticia.get("categoria")
            or noticia.get("categoria_original")
            or "general"
        )


class AC10SistemaAlertas:
    def __init__(
        self,
        ruta_dataset=None,
        ruta_nuevas=None,
        ruta_reporte=None,
        ruta_documentacion=None,
    ):
        self.ruta_dataset = Path(ruta_dataset) if ruta_dataset else ROOT / "datos" / "dataset_analizado.json"
        self.ruta_nuevas = Path(ruta_nuevas) if ruta_nuevas else ROOT / "datos" / "ac10_noticias_nuevas_demo.json"
        self.ruta_reporte = Path(ruta_reporte) if ruta_reporte else ROOT / "reportes" / "ac10_reporte_alertas.json"
        self.ruta_documentacion = Path(ruta_documentacion) if ruta_documentacion else ROOT / "reportes" / "ac10_documentacion_duplicados.md"
        self.sistema = SistemaAlertasConsultaGuardada()

    def ejecutar(self):
        corpus = self._cargar_corpus()
        nuevas = self._crear_noticias_nuevas_demo()
        self._guardar_json(self.ruta_nuevas, nuevas)

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-10 — Alertas por consulta guardada      ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Dataset base       : {self.ruta_dataset}")
        print(f"  Consultas guardadas: {len(self.sistema.consultas)}")
        print(f"  Umbral similitud   : {self.sistema.umbral_similitud}")
        print()

        print("  ▶ Ejecución 1: sin noticias nuevas")
        ejecucion_1 = self.sistema.evaluar_noticias([], "ejecucion_sin_noticias_nuevas")
        print(f"     Noticias evaluadas : {ejecucion_1['noticias_evaluadas']}")
        print(f"     Alertas generadas  : {len(ejecucion_1['alertas_generadas'])}")
        print()

        print("  ▶ Ejecución 2: agregando cinco noticias nuevas")
        ejecucion_2 = self.sistema.evaluar_noticias(nuevas, "ejecucion_con_5_noticias_nuevas")
        print(f"     Noticias evaluadas : {ejecucion_2['noticias_evaluadas']}")
        print(f"     Alertas generadas  : {len(ejecucion_2['alertas_generadas'])}")
        print(f"     Duplicadas omitidas: {ejecucion_2['alertas_omitidas_por_duplicado']}")
        for alerta in ejecucion_2["alertas_generadas"][:10]:
            print(
                f"       - [{alerta['consulta_nombre']}] "
                f"{alerta['noticia_titulo'][:70]} "
                f"(sim={alerta['similitud']})"
            )
        print()

        print("  ▶ Ejecución 3: repetir las mismas noticias para probar duplicados")
        ejecucion_3 = self.sistema.evaluar_noticias(nuevas, "ejecucion_repetida_control_duplicados")
        print(f"     Noticias evaluadas : {ejecucion_3['noticias_evaluadas']}")
        print(f"     Alertas generadas  : {len(ejecucion_3['alertas_generadas'])}")
        print(f"     Duplicadas omitidas: {ejecucion_3['alertas_omitidas_por_duplicado']}")

        documentacion = self._documentacion_duplicados()
        self._guardar_texto(self.ruta_documentacion, documentacion)

        reporte = {
            "actividad": "AC-10 Sistema de alertas por consulta guardada",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "dataset_base": str(self.ruta_dataset),
            "noticias_base_disponibles": len(corpus),
            "consultas_guardadas": self.sistema.consultas,
            "historial_alertas": str(self.sistema.ruta_historial),
            "noticias_nuevas_demo": str(self.ruta_nuevas),
            "ejecuciones": [ejecucion_1, ejecucion_2, ejecucion_3],
            "documentacion_duplicados": str(self.ruta_documentacion),
        }

        self._guardar_json(self.ruta_reporte, reporte)

        print()
        print("  [Consultas]      Guardadas →", self.sistema.ruta_consultas)
        print("  [Noticias demo]  Guardadas →", self.ruta_nuevas)
        print("  [Historial]      Guardado  →", self.sistema.ruta_historial)
        print("  [Reporte]        Guardado  →", self.ruta_reporte)
        print("  [Documentación]  Guardada  →", self.ruta_documentacion)

        return reporte

    def _cargar_corpus(self):
        if not self.ruta_dataset.exists():
            return []

        with open(self.ruta_dataset, "r", encoding="utf-8") as f:
            datos = json.load(f)

        return datos if isinstance(datos, list) else []

    def _crear_noticias_nuevas_demo(self):
        fecha = datetime.now().strftime("%Y-%m-%d")
        return [
            {
                "titulo": "Nuevo modelo de inteligencia artificial mejora la búsqueda de noticias",
                "cuerpo": "Investigadores presentaron un sistema de machine learning capaz de organizar grandes corpus informativos mediante recuperación semántica.",
                "url": "https://simanw.local/demo/ac10/ia-busqueda-noticias",
                "fecha": fecha,
                "fuente": "SIMANW Demo",
                "autor": "Sistema AC10",
                "categoria": "tecnologia",
            },
            {
                "titulo": "Mercados reaccionan a nuevas señales de inflación",
                "cuerpo": "Analistas financieros observaron cambios en tasas de interés, inversión y comportamiento de bancos centrales durante la semana.",
                "url": "https://simanw.local/demo/ac10/mercados-inflacion",
                "fecha": fecha,
                "fuente": "SIMANW Demo",
                "autor": "Sistema AC10",
                "categoria": "economia",
            },
            {
                "titulo": "Estudio científico advierte sobre cambio climático y salud pública",
                "cuerpo": "Un grupo de científicos publicó una investigación sobre temperatura global, emisiones y efectos en hospitales y comunidades vulnerables.",
                "url": "https://simanw.local/demo/ac10/ciencia-clima-salud",
                "fecha": fecha,
                "fuente": "SIMANW Demo",
                "autor": "Sistema AC10",
                "categoria": "ciencia",
            },
            {
                "titulo": "Congreso discute reforma de justicia y nueva ley electoral",
                "cuerpo": "El gobierno y legisladores debatieron cambios políticos relacionados con elecciones, justicia pública y funcionamiento del congreso.",
                "url": "https://simanw.local/demo/ac10/reforma-justicia-electoral",
                "fecha": fecha,
                "fuente": "SIMANW Demo",
                "autor": "Sistema AC10",
                "categoria": "gobierno",
            },
            {
                "titulo": "Conflicto internacional genera nueva ronda de diplomacia",
                "cuerpo": "Países europeos y organismos internacionales buscan acuerdos ante una crisis migratoria y tensiones diplomáticas crecientes.",
                "url": "https://simanw.local/demo/ac10/conflicto-diplomacia",
                "fecha": fecha,
                "fuente": "SIMANW Demo",
                "autor": "Sistema AC10",
                "categoria": "mundo",
            },
        ]

    def _documentacion_duplicados(self):
        return """# AC-10: Control de alertas duplicadas

El sistema evita alertas duplicadas mediante una llave única compuesta por la consulta guardada y la noticia detectada. Para cada noticia se genera un identificador estable a partir de su URL; si la URL no existe, se usa el título como respaldo. Después, se combina `consulta_id + noticia_id` y se calcula un hash SHA-1. Ese hash se guarda en `reportes/ac10_historial_alertas.json`.

Cuando se evalúan noticias nuevas, el sistema calcula la similitud entre cada consulta persistida y cada noticia. Si la similitud supera el umbral, antes de emitir la alerta revisa si la llave ya existe en el historial. Si existe, la alerta se omite y se contabiliza como duplicada. Si no existe, se registra con consulta, noticia, URL, categoría, similitud y marca de tiempo.

Con este mecanismo, una misma noticia puede activar diferentes consultas si realmente coincide con varias, pero la misma consulta no vuelve a alertar por la misma noticia en ejecuciones posteriores.
"""

    def _guardar_json(self, ruta, contenido):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)

    def _guardar_texto(self, ruta, contenido):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)


if __name__ == "__main__":
    AC10SistemaAlertas().ejecutar()
