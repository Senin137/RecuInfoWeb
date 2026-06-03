
"""
SIMANW - AC-3: Clasificador multimodelo con selección automática
================================================================

Complemento de la Fase 3.

Cumple:
- Entrena múltiples modelos de clasificación.
- Evalúa con validación cruzada estratificada.
- Selecciona automáticamente el mejor modelo.
- Entrena el ganador con todos los datos.
- Genera predicciones de prueba.
- Exporta reporte JSON.

Uso:
    python fases/AC3_SelectorMultimodelo.py
"""

import json
import os
from collections import Counter
from datetime import datetime

import nltk
from nltk.corpus import stopwords

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline


for recurso in ("stopwords",):
    nltk.download(recurso, quiet=True)


STOPWORDS_ES = list(set(stopwords.words("spanish")) | {
    "nbsp", "solo", "vez", "hace", "año", "años", "ser", "puede",
    "parte", "gran", "mismo", "misma", "además", "también"
})


class SelectorMultimodelo:
    def __init__(self, max_features=3000):
        self.max_features = max_features
        self.modelos = {
            "Naive Bayes": MultinomialNB(alpha=0.1),
            "SVM Lineal": LinearSVC(max_iter=4000, C=1.0, dual=False),
            "Regresión Logística": LogisticRegression(max_iter=1500, C=1.0),
            "Random Forest": RandomForestClassifier(
                n_estimators=120,
                random_state=42,
                class_weight="balanced"
            ),
        }
        self.resultados = {}
        self.mejor_nombre = None
        self.mejor_pipeline = None

    def _crear_pipeline(self, modelo):
        return Pipeline([
            ("tfidf", TfidfVectorizer(
                max_features=self.max_features,
                ngram_range=(1, 2),
                lowercase=True,
                stop_words=STOPWORDS_ES,
                sublinear_tf=True,
            )),
            ("modelo", modelo),
        ])

    def evaluar_todos(self, textos, etiquetas, cv_folds=3):
        if len(textos) != len(etiquetas):
            raise ValueError("textos y etiquetas deben tener la misma longitud.")

        conteo = Counter(etiquetas)
        min_clase = min(conteo.values())

        if min_clase < 2:
            raise ValueError("Cada clase necesita al menos 2 ejemplos para validación cruzada.")

        folds = min(cv_folds, min_clase)
        cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)

        self.resultados = {}

        for nombre, modelo in self.modelos.items():
            pipeline = self._crear_pipeline(modelo)

            try:
                scores = cross_val_score(
                    pipeline,
                    textos,
                    etiquetas,
                    cv=cv,
                    scoring="accuracy"
                )

                self.resultados[nombre] = {
                    "accuracy_media": round(float(scores.mean()), 4),
                    "desviacion_estandar": round(float(scores.std()), 4),
                    "scores_por_fold": [round(float(s), 4) for s in scores],
                    "folds_usados": folds,
                }
            except Exception as exc:
                self.resultados[nombre] = {"error": str(exc)}

        validos = {
            nombre: datos
            for nombre, datos in self.resultados.items()
            if "accuracy_media" in datos
        }

        if not validos:
            raise RuntimeError("Ningún modelo pudo entrenarse correctamente.")

        self.mejor_nombre = max(
            validos,
            key=lambda nombre: (
                validos[nombre]["accuracy_media"],
                -validos[nombre]["desviacion_estandar"]
            )
        )

        self.mejor_pipeline = self._crear_pipeline(self.modelos[self.mejor_nombre])
        self.mejor_pipeline.fit(textos, etiquetas)

        return self.resultados

    def predecir(self, textos):
        if self.mejor_pipeline is None:
            raise RuntimeError("Primero ejecuta evaluar_todos().")
        return list(self.mejor_pipeline.predict(textos))

    def reporte_texto(self):
        lineas = [
            "Modelo                  | Accuracy | Std Dev | Folds",
            "-" * 58,
        ]

        ordenados = sorted(
            self.resultados.items(),
            key=lambda item: item[1].get("accuracy_media", 0),
            reverse=True
        )

        for nombre, resultado in ordenados:
            if "accuracy_media" in resultado:
                marca = " ★ GANADOR" if nombre == self.mejor_nombre else ""
                lineas.append(
                    f"{nombre:<23} | "
                    f"{resultado['accuracy_media']:<8.4f} | "
                    f"{resultado['desviacion_estandar']:<7.4f} | "
                    f"{resultado['folds_usados']}{marca}"
                )
            else:
                lineas.append(f"{nombre:<23} | ERROR    | {resultado.get('error', '')[:25]}")

        return "\\n".join(lineas)


class AC3SelectorMultimodelo:
    def __init__(
        self,
        ruta_dataset="datos/dataset_analizado.json",
        ruta_reporte="reportes/ac3_selector_multimodelo.json",
    ):
        self.ruta_dataset = ruta_dataset
        self.ruta_reporte = ruta_reporte
        self.selector = SelectorMultimodelo()

    def ejecutar(self):
        textos, etiquetas, origen = self._preparar_datos()

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-3 — Clasificador multimodelo            ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Origen de datos : {origen}")
        print(f"  Textos          : {len(textos)}")
        print(f"  Clases          : {dict(Counter(etiquetas))}")
        print()

        resultados = self.selector.evaluar_todos(textos, etiquetas, cv_folds=3)

        print(self.selector.reporte_texto())
        print()
        print(f"  Modelo seleccionado: {self.selector.mejor_nombre}")

        textos_prueba = [
            "nueva aplicación de inteligencia artificial para detectar fraudes bancarios",
            "el gobierno anunció una reforma electoral y cambios en el congreso",
            "investigadores publican avance científico sobre cambio climático",
            "los mercados financieros cerraron con pérdidas por inflación",
        ]

        predicciones = self.selector.predecir(textos_prueba)

        print("\\n  Predicciones de prueba:")
        predicciones_formateadas = []
        for texto, pred in zip(textos_prueba, predicciones):
            fila = {
                "texto": texto,
                "prediccion": pred,
            }
            predicciones_formateadas.append(fila)
            print(f"   - [{pred}] {texto[:70]}...")

        reporte = {
            "actividad": "AC-3 Clasificador multimodelo con selección automática",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "origen_datos": origen,
            "total_textos": len(textos),
            "distribucion_clases": dict(Counter(etiquetas)),
            "modelos_evaluados": resultados,
            "modelo_seleccionado": self.selector.mejor_nombre,
            "predicciones_prueba": predicciones_formateadas,
        }

        self._guardar_json(self.ruta_reporte, reporte)
        print("\\n  [Reporte] Guardado →", self.ruta_reporte)

        return reporte

    def _preparar_datos(self):
        if os.path.exists(self.ruta_dataset):
            with open(self.ruta_dataset, "r", encoding="utf-8") as f:
                noticias = json.load(f)

            textos = []
            etiquetas = []

            for noticia in noticias:
                titulo = noticia.get("titulo", "")
                cuerpo = noticia.get("cuerpo", "")
                categoria = (
                    noticia.get("categoria")
                    or noticia.get("categoria_original")
                    or noticia.get("categoria_predicha")
                )

                if not titulo or not cuerpo or not categoria:
                    continue

                textos.append(f"{titulo}. {cuerpo}")
                etiquetas.append(categoria)

            conteo = Counter(etiquetas)
            clases_validas = {clase for clase, total in conteo.items() if total >= 3}

            textos_filtrados = []
            etiquetas_filtradas = []

            for texto, etiqueta in zip(textos, etiquetas):
                if etiqueta in clases_validas:
                    textos_filtrados.append(texto)
                    etiquetas_filtradas.append(etiqueta)

            if len(set(etiquetas_filtradas)) >= 2:
                return textos_filtrados, etiquetas_filtradas, self.ruta_dataset

        return self._datos_demo()

    def _datos_demo(self):
        textos = [
            "inteligencia artificial deep learning redes neuronales transformers",
            "programación software desarrollo aplicaciones web python javascript",
            "startup tecnológica innovación digital plataforma cloud",
            "ciberseguridad hackers vulnerabilidad protección datos privacidad",
            "inflación tasas interés banco central política monetaria",
            "bolsa acciones mercado valores inversión rendimiento portafolio",
            "desempleo recesión económica crisis laboral empleo informal",
            "comercio exportaciones importaciones balanza aranceles tratado",
            "investigación científica laboratorio experimento publicación revista",
            "cambio climático emisiones carbono calentamiento temperatura global",
            "vacuna medicamento ensayo clínico pacientes tratamiento hospital",
            "espacio cohete satélite misión astronauta exploración lunar",
            "elecciones presidente candidato partido campaña votación democracia",
            "congreso legisladores reforma ley aprobación dictamen senado",
            "seguridad policía crimen organizado justicia tribunal sentencia",
            "gobierno programa social presupuesto política pública decreto",
        ]

        etiquetas = [
            "tecnologia", "tecnologia", "tecnologia", "tecnologia",
            "economia", "economia", "economia", "economia",
            "ciencia", "ciencia", "ciencia", "ciencia",
            "gobierno", "gobierno", "gobierno", "gobierno",
        ]

        return textos, etiquetas, "datos_demo_ac3"

    def _guardar_json(self, ruta, contenido):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    AC3SelectorMultimodelo().ejecutar()
