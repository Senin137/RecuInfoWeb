"""
SIMANW - Sistema Inteligente de Monitoreo y Análisis de Noticias Web
=====================================================================
FASE 3: Clasificación y Análisis Automático

Descripción:
    Recibe el dataset enriquecido de la Fase 2 y aplica cuatro tipos de
    análisis inteligente sobre cada noticia:

      3.1 Clasificación automática  → asigna categoría mediante ML supervisado
      3.2 Análisis de sentimientos  → detecta tono positivo/negativo/neutral
      3.3 Recomendación de contenido→ sugiere noticias relacionadas por similitud
      3.4 Detección de temas en chat→ identifica tema de conversación para publicidad

    La novedad respecto a un clasificador simple es que el sistema evalúa
    múltiples algoritmos de ML y selecciona automáticamente el más preciso
    antes de hacer predicciones. Esto hace el pipeline adaptable a distintos
    tipos de corpus sin intervención manual.

Componentes:
    - SelectorModelo          : Compara algoritmos y elige el mejor (3.1)
    - AnalizadorSentimientos  : Calcula tono con VADER adaptado al español (3.2)
    - SistemaRecomendacion    : Sugiere noticias por similitud de contenido (3.3)
    - DetectorTemasChat       : Detecta tema dominante en conversaciones (3.4)
    - AnalizadorCorpus        : Orquesta las 4 etapas sobre el dataset completo

Uso:
    python fase3_clasificador.py
    (requiere datos/dataset_nlp.json generado por la Fase 2)
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import json
import os
import random
from collections import Counter

import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics.pairwise import cosine_similarity

for recurso in ('stopwords', 'vader_lexicon'):
    nltk.download(recurso, quiet=True)

# ── Stopwords extendidas (stopwords estándar + ruido detectado en Fase 2) ────
_SW_BASE = set(stopwords.words('spanish'))
_SW_EXTRA = {
    'nbsp', 'solo', 'mejor', 'vez', 'hace', 'año', 'años', 'ser',
    'puede', 'parte', 'dos', 'tres', 'gran', 'mismo', 'misma',
    'así', 'cada', 'menos', 'después', 'ahora', 'según', 'sino',
    'además', 'también', 'aunque', 'mientras', 'durante', 'través',
}
STOPWORDS_COMPLETAS = list(_SW_BASE | _SW_EXTRA)


# ═════════════════════════════════════════════════════════════════════════════
# 3.1  SELECTOR DE MODELO
#      Evalúa cuatro algoritmos de clasificación con validación cruzada
#      estratificada y selecciona automáticamente el más preciso.
#      Usar StratifiedKFold garantiza que cada fold tenga la misma
#      proporción de categorías que el dataset original.
# ═════════════════════════════════════════════════════════════════════════════

class SelectorModelo:
    """
    Evalúa múltiples clasificadores y selecciona el mejor automáticamente.

    Algoritmos evaluados:
      - Naive Bayes Multinomial : rápido, funciona bien con texto disperso
      - SVM Lineal              : excelente para espacios de alta dimensión
      - Regresión Logística     : probabilístico, interpretable
      - Random Forest           : robusto, maneja ruido bien

    Args:
        max_features : Tamaño máximo del vocabulario TF-IDF.
        cv_folds     : Número de folds para validación cruzada.
    """

    CANDIDATOS = {
        'Naive Bayes':        MultinomialNB(alpha=0.1),
        'SVM Lineal':         LinearSVC(max_iter=3000, C=1.0, dual=False),
        'Regresion Logistica':LogisticRegression(max_iter=1000, C=1.0),
        'Random Forest':      RandomForestClassifier(n_estimators=100, random_state=42),
    }

    def __init__(self, max_features: int = 3000, cv_folds: int = 5):
        self.cv_folds     = cv_folds
        self.vectorizer   = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            stop_words=STOPWORDS_COMPLETAS,
            sublinear_tf=True,
        )
        self._resultados: dict  = {}
        self._mejor_nombre: str = ''
        self._mejor_modelo      = None
        self._matriz_X          = None

    # ── API pública ──────────────────────────────────────────────────────────

    def entrenar(self, textos: list[str], etiquetas: list[str]) -> dict:
        """
        Vectoriza el corpus, evalúa todos los candidatos con validación
        cruzada y entrena el ganador con el dataset completo.

        Retorna un dict con los resultados comparativos.
        """
        # Ajustamos folds al mínimo de muestras por clase para evitar errores
        min_clase = min(Counter(etiquetas).values())
        folds = min(self.cv_folds, min_clase)

        self._matriz_X = self.vectorizer.fit_transform(textos)
        cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)

        for nombre, modelo in self.CANDIDATOS.items():
            try:
                scores = cross_val_score(
                    modelo, self._matriz_X, etiquetas,
                    cv=cv, scoring='accuracy'
                )
                self._resultados[nombre] = {
                    'accuracy_media': round(float(scores.mean()), 4),
                    'desv_estandar':  round(float(scores.std()), 4),
                    'scores_por_fold': [round(float(s), 4) for s in scores],
                }
            except Exception as e:
                self._resultados[nombre] = {'error': str(e)}

        # Seleccionamos el modelo con mayor accuracy media
        validos = {k: v for k, v in self._resultados.items()
                   if 'accuracy_media' in v}
        if validos:
            self._mejor_nombre = max(validos, key=lambda k: validos[k]['accuracy_media'])
            self._mejor_modelo = self.CANDIDATOS[self._mejor_nombre]
            self._mejor_modelo.fit(self._matriz_X, etiquetas)

        return self._resultados

    def predecir(self, textos: list[str]) -> list[str]:
        """Predice categorías usando el mejor modelo seleccionado."""
        if not self._mejor_modelo:
            raise RuntimeError("Llama primero a entrenar()")
        X = self.vectorizer.transform(textos)
        return list(self._mejor_modelo.predict(X))

    def predecir_con_scores(self, texto: str) -> tuple[str, dict]:
        """
        Predice la categoría de un texto y devuelve los scores de decisión
        de cada clase para mostrar el nivel de confianza.
        """
        if not self._mejor_modelo:
            raise RuntimeError("Llama primero a entrenar()")
        X = self.vectorizer.transform([texto])
        prediccion = self._mejor_modelo.predict(X)[0]

        # decision_function disponible en SVM y Logística; para los demás
        # usamos predict_proba si está disponible
        scores = {}
        if hasattr(self._mejor_modelo, 'decision_function'):
            raw = self._mejor_modelo.decision_function(X)[0]
            clases = self._mejor_modelo.classes_
            scores = {c: round(float(s), 4) for c, s in zip(clases, raw)}
        elif hasattr(self._mejor_modelo, 'predict_proba'):
            raw = self._mejor_modelo.predict_proba(X)[0]
            clases = self._mejor_modelo.classes_
            scores = {c: round(float(s), 4) for c, s in zip(clases, raw)}

        return prediccion, scores

    def reporte_comparativo(self) -> str:
        """Tabla de texto con el ranking de modelos evaluados."""
        lineas = [
            "\n  Modelo                   │ Accuracy  │ Desv. Est.",
            "  " + "─" * 52,
        ]
        ordenados = sorted(
            self._resultados.items(),
            key=lambda x: x[1].get('accuracy_media', 0),
            reverse=True
        )
        for nombre, res in ordenados:
            if 'accuracy_media' in res:
                marca = "  ★ GANADOR" if nombre == self._mejor_nombre else ""
                lineas.append(
                    f"  {nombre:<24} │  {res['accuracy_media']:.4f}   │  {res['desv_estandar']:.4f}{marca}"
                )
            else:
                lineas.append(f"  {nombre:<24} │  ERROR    │  {res.get('error','')[:20]}")
        return "\n".join(lineas)

    @property
    def mejor_nombre(self) -> str:
        return self._mejor_nombre


# ═════════════════════════════════════════════════════════════════════════════
# 3.2  ANALIZADOR DE SENTIMIENTOS
#      Usa VADER (Valence Aware Dictionary and sEntiment Reasoner).
#      Aunque VADER fue diseñado para inglés, el score compound funciona
#      razonablemente en español para textos de noticias.
#      El compound va de -1 (muy negativo) a +1 (muy positivo).
# ═════════════════════════════════════════════════════════════════════════════

class AnalizadorSentimientos:
    """
    Determina el tono emocional de cada noticia.

    Umbrales estándar de VADER:
      compound ≥  0.05  →  positivo
      compound ≤ -0.05  →  negativo
      entre ambos       →  neutral

    Args:
        umbral_positivo : Score mínimo para clasificar como positivo.
        umbral_negativo : Score máximo para clasificar como negativo.
    """

    def __init__(self, umbral_positivo: float = 0.05, umbral_negativo: float = -0.05):
        self.sia               = SentimentIntensityAnalyzer()
        self.umbral_positivo   = umbral_positivo
        self.umbral_negativo   = umbral_negativo

    # ── API pública ──────────────────────────────────────────────────────────

    def analizar(self, texto: str) -> dict:
        """Analiza el sentimiento de un texto individual."""
        scores   = self.sia.polarity_scores(texto)
        compound = scores['compound']

        if compound >= self.umbral_positivo:
            etiqueta = 'positivo'
        elif compound <= self.umbral_negativo:
            etiqueta = 'negativo'
        else:
            etiqueta = 'neutral'

        return {
            'etiqueta':  etiqueta,
            'compound':  round(compound, 4),
            'positivo':  round(scores['pos'], 4),
            'negativo':  round(scores['neg'], 4),
            'neutral':   round(scores['neu'], 4),
        }

    def analizar_corpus(self, textos: list[str]) -> tuple[list[dict], dict]:
        """
        Analiza sentimiento de un corpus completo.
        Retorna la lista de resultados individuales y un resumen global.
        """
        resultados   = [self.analizar(t) for t in textos]
        distribucion = Counter(r['etiqueta'] for r in resultados)
        promedio     = sum(r['compound'] for r in resultados) / max(len(resultados), 1)

        resumen = {
            'distribucion':          dict(distribucion),
            'compound_promedio':     round(promedio, 4),
            'tono_general':          (
                'positivo' if promedio >= self.umbral_positivo
                else 'negativo' if promedio <= self.umbral_negativo
                else 'neutral'
            ),
        }
        return resultados, resumen


# ═════════════════════════════════════════════════════════════════════════════
# 3.3  SISTEMA DE RECOMENDACIÓN
#      Usa la matriz de similitud coseno construida en la Fase 2 para
#      sugerir noticias relacionadas. Soporta recomendación simple (por una
#      noticia) y por perfil (por múltiples noticias leídas).
# ═════════════════════════════════════════════════════════════════════════════

class SistemaRecomendacion:
    """
    Recomienda noticias similares basándose en la distancia coseno
    entre sus vectores TF-IDF.

    Args:
        noticias       : Lista de dicts del dataset enriquecido.
        matriz_tfidf   : Matriz dispersa de la Fase 2 (RepresentacionVectorial).
    """

    def __init__(self, noticias: list[dict], matriz_tfidf):
        self.noticias    = noticias
        self._sim_matrix = cosine_similarity(matriz_tfidf).tolist()

    # ── API pública ──────────────────────────────────────────────────────────

    def recomendar(self, idx: int, top_n: int = 3,
                   distinta_categoria: bool = False) -> list[tuple[int, float]]:
        """
        Retorna los top_n índices más similares al documento idx.

        Args:
            distinta_categoria : Si True, solo recomienda de otras categorías.
        """
        cat_base   = self.noticias[idx].get('categoria', '')
        similitudes = self._sim_matrix[idx]

        candidatos = [
            (i, round(sim, 4))
            for i, sim in enumerate(similitudes)
            if i != idx and (
                not distinta_categoria
                or self.noticias[i].get('categoria', '') != cat_base
            )
        ]
        candidatos.sort(key=lambda x: -x[1])
        return candidatos[:top_n]

    def recomendar_por_perfil(self, indices_leidos: list[int],
                              top_n: int = 3) -> list[tuple[int, float]]:
        """
        Genera recomendaciones basadas en múltiples noticias leídas.
        Acumula similitudes de todas las noticias del perfil y filtra
        las ya leídas.
        """
        n           = len(self.noticias)
        acumulado   = [0.0] * n

        for idx in indices_leidos:
            for j, sim in enumerate(self._sim_matrix[idx]):
                acumulado[j] += sim

        # Excluimos las ya leídas
        for idx in indices_leidos:
            acumulado[idx] = 0.0

        ordenados = sorted(enumerate(acumulado), key=lambda x: -x[1])
        return [(i, round(s, 4)) for i, s in ordenados[:top_n] if s > 0]


# ═════════════════════════════════════════════════════════════════════════════
# 3.4  DETECTOR DE TEMAS EN CHAT
#      Analiza el historial reciente de una conversación y detecta el tema
#      dominante para personalizar publicidad. La detección usa similitud
#      coseno entre el texto acumulado y perfiles temáticos predefinidos.
# ═════════════════════════════════════════════════════════════════════════════

class DetectorTemasChat:
    """
    Detecta el tema dominante en una conversación en tiempo real
    y selecciona publicidad contextual.

    El detector mantiene un historial de mensajes y analiza una ventana
    deslizante de los últimos N mensajes para capturar cambios de tema.

    Args:
        ventana : Número de mensajes recientes a considerar.
    """

    PERFILES_TEMATICOS = {
        'tecnologia': (
            "inteligencia artificial programación software apps tecnología "
            "computadora robot digital innovación algoritmo datos"
        ),
        'economia': (
            "dinero inversión mercado bolsa finanzas banco economía "
            "empleo trabajo inflación tasas crédito empresas"
        ),
        'ciencia': (
            "investigación científico descubrimiento estudio laboratorio "
            "clima universo espacio biología física química"
        ),
        'gobierno': (
            "gobierno elecciones presidente ley congreso partido "
            "democracia política pública decreto legislación"
        ),
        'mundo': (
            "internacional conflicto guerra diplomacia países tratado "
            "naciones unidas europa asia migración"
        ),
    }

    CATALOGO_PUBLICIDAD = {
        'tecnologia': [
            "Curso de IA y Machine Learning — 50% descuento",
            "Laptop para desarrolladores: i9 + 32 GB RAM",
            "Conferencia Tech 2026 — Boletos disponibles",
        ],
        'economia': [
            "App de inversiones — Comienza con $100",
            "Curso de finanzas personales gratuito",
            "Tarjeta de crédito sin anualidad",
        ],
        'ciencia': [
            "Suscripción a revista científica digital",
            "Telescopio astronómico con envío gratis",
            "Curso de ciencia de datos en línea",
        ],
        'gobierno': [
            "Portal de transparencia gubernamental",
            "Alertas de cambios legislativos en tiempo real",
            "Foro de participación ciudadana",
        ],
        'mundo': [
            "Suscripción premium a noticias internacionales",
            "Curso de relaciones internacionales",
            "VPN para acceder a medios globales",
        ],
    }

    def __init__(self, ventana: int = 5):
        self.ventana    = ventana
        self._historial: list[dict] = []
        self._vectorizer = TfidfVectorizer()
        # Construimos la matriz de perfiles temáticos una sola vez
        self._temas       = list(self.PERFILES_TEMATICOS.keys())
        self._matriz_temas = self._vectorizer.fit_transform(
            list(self.PERFILES_TEMATICOS.values())
        )

    # ── API pública ──────────────────────────────────────────────────────────

    def agregar_mensaje(self, usuario: str, texto: str):
        """Añade un mensaje al historial de conversación."""
        self._historial.append({'usuario': usuario, 'texto': texto})

    def detectar_tema(self) -> tuple[str, float]:
        """
        Detecta el tema dominante en la ventana de mensajes recientes.
        Retorna (tema, confianza).
        """
        if not self._historial:
            return 'general', 0.0

        ultimos   = self._historial[-self.ventana:]
        texto_ven = ' '.join(m['texto'] for m in ultimos)

        vec_conv  = self._vectorizer.transform([texto_ven])
        sims      = cosine_similarity(vec_conv, self._matriz_temas)[0]

        mejor_idx = int(sims.argmax())
        return self._temas[mejor_idx], round(float(sims[mejor_idx]), 4)

    def obtener_publicidad(self, tema: str) -> str:
        """Selecciona aleatoriamente un anuncio del catálogo para el tema."""
        opciones = self.CATALOGO_PUBLICIDAD.get(tema, ["Descubre las mejores ofertas del día"])
        return random.choice(opciones)

    def simular_chat(self, conversacion: list[tuple[str, str]]) -> list[dict]:
        """
        Procesa una lista de (usuario, mensaje), detecta el tema
        tras cada mensaje y asigna publicidad.
        """
        resultados = []
        for usuario, mensaje in conversacion:
            self.agregar_mensaje(usuario, mensaje)
            tema, confianza = self.detectar_tema()
            resultados.append({
                'usuario':    usuario,
                'mensaje':    mensaje,
                'tema':       tema,
                'confianza':  confianza,
                'publicidad': self.obtener_publicidad(tema),
            })
        return resultados


# ═════════════════════════════════════════════════════════════════════════════
# ORQUESTADOR
# ═════════════════════════════════════════════════════════════════════════════

class AnalizadorCorpus:
    """
    Orquesta las 4 etapas de la Fase 3 sobre el dataset del SIMANW.

    Carga el JSON de la Fase 2, aplica clasificación, sentimiento,
    recomendación y detección de temas, y exporta el dataset final
    enriquecido para las fases siguientes.

    Args:
        ruta_dataset : Ruta al dataset_nlp.json de la Fase 2.
    """

    # Datos de entrenamiento base para el clasificador
    # En producción se reemplaza por el corpus acumulado de rastreos anteriores
    TEXTOS_BASE = [
        "inteligencia artificial machine learning algoritmos redes neuronales deep learning modelos",
        "nuevo procesador computadora software desarrollo programación tecnología aplicaciones",
        "startup tecnológica lanza aplicación innovadora plataforma digital usuarios",
        "robot automatización industria software empresa tecnología manufactura proceso",
        "mercados financieros bolsa acciones inversión capital rendimiento portafolio",
        "inflación economía banco central tasas interés política monetaria precios",
        "desempleo crisis económica recesión PIB crecimiento producto interno bruto",
        "comercio internacional exportaciones importaciones aranceles tratado libre",
        "estudio científico investigadores descubrimiento laboratorio publicación revista",
        "cambio climático calentamiento global temperatura emisiones carbono gases efecto",
        "vacuna tratamiento médico salud enfermedad hospital pacientes investigación",
        "espacio NASA cohete satélite misión exploración astronauta universo planetas",
        "elecciones candidato presidente congreso voto democracia partido campaña",
        "gobierno ley reforma política pública decreto legislación parlamento",
        "seguridad pública policía crimen delito justicia tribunal sentencia",
        "presupuesto gasto público programa social gobierno federal recursos",
        "conflicto internacional guerra diplomacia países tratado naciones unidas",
        "migración refugiados fronteras acuerdos internacionales derechos humanos",
    ]

    ETIQUETAS_BASE = [
        'tecnologia', 'tecnologia', 'tecnologia', 'tecnologia',
        'economia',   'economia',   'economia',   'economia',
        'ciencia',    'ciencia',    'ciencia',    'ciencia',
        'gobierno',   'gobierno',   'gobierno',   'gobierno',
        'mundo',      'mundo',
    ]

    def __init__(self, ruta_dataset: str):
        self.ruta_dataset = ruta_dataset
        self.noticias: list[dict] = []

    # ── API pública ──────────────────────────────────────────────────────────

    def ejecutar(self) -> list[dict]:
        """Corre las 4 etapas de análisis sobre el corpus completo."""
        self._cargar_dataset()
        if not self.noticias:
            return []

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 3 — Clasificación y Análisis          ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Noticias a analizar : {len(self.noticias)}\n")

        textos = [f"{n['titulo']}. {n['cuerpo']}" for n in self.noticias]

        # ── 3.1 Clasificación ────────────────────────────────────────────────
        self._fase_clasificacion(textos)

        # ── 3.2 Sentimientos ────────────────────────────────────────────────
        self._fase_sentimientos(textos)

        # ── 3.3 Recomendación ───────────────────────────────────────────────
        self._fase_recomendacion(textos)

        # ── 3.4 Detección de temas ──────────────────────────────────────────
        self._fase_deteccion_temas()

        return self.noticias

    def guardar_resultados(self, ruta_salida: str):
        """Exporta el dataset enriquecido con los resultados de la Fase 3."""
        if not self.noticias:
            return
        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        with open(ruta_salida, 'w', encoding='utf-8') as f:
            json.dump(self.noticias, f, ensure_ascii=False, indent=2)
        print(f"\n  [Dataset F3] {len(self.noticias)} noticias → {ruta_salida}")

    # ── Etapas internas ──────────────────────────────────────────────────────

    def _fase_clasificacion(self, textos: list[str]):
        print("  ▶ 3.1 Clasificación automática...")

        # Combinamos datos base con el corpus real para mejor cobertura
        etiquetas_reales = [n.get('categoria', 'general') for n in self.noticias]
        textos_train     = self.TEXTOS_BASE + textos
        etiquetas_train  = self.ETIQUETAS_BASE + etiquetas_reales

        selector = SelectorModelo(max_features=3000, cv_folds=5)
        selector.entrenar(textos_train, etiquetas_train)

        print(selector.reporte_comparativo())
        print(f"\n     Modelo seleccionado : {selector.mejor_nombre}")

        # Predicción sobre el corpus real
        predicciones = selector.predecir(textos)
        for noticia, pred in zip(self.noticias, predicciones):
            noticia['categoria_predicha'] = pred

        # Muestra las primeras 5 predicciones con scores
        print("\n     Muestra de predicciones:")
        for i, noticia in enumerate(self.noticias[:5]):
            pred, scores = selector.predecir_con_scores(
                f"{noticia['titulo']}. {noticia['cuerpo']}"
            )
            cat_orig = noticia.get('categoria', '?')
            coincide = "✓" if pred == cat_orig else "✗"
            print(f"     {coincide} [{cat_orig}→{pred}] {noticia['titulo'][:50]}...")
            if scores:
                top = sorted(scores.items(), key=lambda x: -x[1])[:3]
                print(f"       scores: {', '.join(f'{c}={s:.2f}' for c,s in top)}")

    def _fase_sentimientos(self, textos: list[str]):
        print("\n  ▶ 3.2 Análisis de sentimientos...")
        analizador = AnalizadorSentimientos()
        resultados, resumen = analizador.analizar_corpus(textos)

        for noticia, sent in zip(self.noticias, resultados):
            noticia['sentimiento'] = sent

        print(f"     Distribución  : {resumen['distribucion']}")
        print(f"     Compound prom : {resumen['compound_promedio']:+.4f}")
        print(f"     Tono general  : {resumen['tono_general'].upper()}")

        iconos = {'positivo': '↑', 'negativo': '↓', 'neutral': '→'}
        print("\n     Por noticia:")
        for noticia in self.noticias:
            sent = noticia['sentimiento']
            icono = iconos.get(sent['etiqueta'], '?')
            print(f"     {icono} [{sent['compound']:+.3f}] {noticia['titulo'][:55]}...")

    def _fase_recomendacion(self, textos: list[str]):
        print("\n  ▶ 3.3 Sistema de recomendación...")

        # Construimos vectores TF-IDF internos para la similitud
        vec   = TfidfVectorizer(max_features=2000, ngram_range=(1, 2),
                                stop_words=STOPWORDS_COMPLETAS)
        matriz = vec.fit_transform(textos)

        recomendador = SistemaRecomendacion(self.noticias, matriz)

        print("     Si leíste esta noticia, te recomendamos:")
        for i in range(min(3, len(self.noticias))):
            recs = recomendador.recomendar(i, top_n=2)
            print(f"\n     ▸ '{self.noticias[i]['titulo'][:50]}...'")
            for j, sim in recs:
                print(f"       → [{sim:.3f}] {self.noticias[j]['titulo'][:50]}...")

        # Recomendación por perfil (primeras 2 noticias como historial)
        if len(self.noticias) >= 3:
            perfil = recomendador.recomendar_por_perfil([0, 1], top_n=2)
            print("\n     Recomendaciones por perfil (leyó noticias 1 y 2):")
            for j, score in perfil:
                print(f"       → [{score:.3f}] {self.noticias[j]['titulo'][:55]}...")

    def _fase_deteccion_temas(self):
        print("\n  ▶ 3.4 Detección de temas en chat...")
        detector = DetectorTemasChat(ventana=5)

        conversacion = [
            ("Laura",   "¿Vieron la noticia sobre la nueva IA de Google?"),
            ("Miguel",  "Sí, dicen que puede programar mejor que muchos desarrolladores"),
            ("Laura",   "Me preocupa el futuro del trabajo en tecnología"),
            ("Roberto", "Hay que aprender machine learning, es una oportunidad"),
            ("Miguel",  "Cambiando de tema, ¿cómo ven los mercados este trimestre?"),
            ("Laura",   "Los mercados están muy volátiles, mis inversiones bajaron"),
            ("Roberto", "El banco central anunció que subirá las tasas de interés"),
            ("Miguel",  "Mejor diversificar, quizá invertir en fondos indexados"),
        ]

        print("     Simulación de chat con publicidad contextual:")
        print("     " + "─" * 60)
        resultados = detector.simular_chat(conversacion)

        for r in resultados:
            print(f"     [{r['usuario']}]: {r['mensaje']}")
            print(f"       Tema: {r['tema'].upper()} (confianza: {r['confianza']:.3f})")
            print(f"       Publicidad: {r['publicidad']}\n")

        temas_detectados = Counter(r['tema'] for r in resultados)
        print(f"     Resumen de temas: {dict(temas_detectados)}")

    # ── Métodos internos ─────────────────────────────────────────────────────

    def _cargar_dataset(self):
        try:
            with open(self.ruta_dataset, 'r', encoding='utf-8') as f:
                self.noticias = json.load(f)
        except FileNotFoundError:
            print(f"  [F3] ✗ No se encontró {self.ruta_dataset}")
            print("        Ejecuta primero fase2_nlp.py")
            self.noticias = []


# ═════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':

    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    analizador = AnalizadorCorpus(
        ruta_dataset=os.path.join(BASE, 'datos', 'dataset_nlp.json'),
    )

    analizador.ejecutar()

    analizador.guardar_resultados(
        ruta_salida=os.path.join(BASE, 'datos', 'dataset_analizado.json'),
    )