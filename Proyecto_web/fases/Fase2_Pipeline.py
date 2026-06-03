"""
SIMANW - Sistema Inteligente de Monitoreo y Análisis de Noticias Web
=====================================================================
FASE 2: Procesamiento de Lenguaje Natural (NLP)

Descripción:
    Recibe el dataset crudo de la Fase 1 y lo transforma en representaciones
    computables. El pipeline cubre cuatro etapas progresivas:

      2.1 Pre-procesamiento  → limpieza, tokenización, stemming, n-gramas
      2.2 Análisis léxico    → frecuencias, riqueza léxica, entidades nombradas
      2.3 Vectorización      → matriz TF-IDF lista para ML
      2.4 Similitud          → distancia coseno entre documentos

    La salida de esta fase (vectores + metadatos NLP) alimenta directamente
    la Fase 3 (clasificación y análisis de sentimiento).

Componentes:
    - PipelineNLP           : Pre-procesa texto individual (2.1)
    - AnalizadorLexico      : Estadísticas, n-gramas y entidades del corpus (2.2)
    - RepresentacionVectorial: Construye la matriz TF-IDF (2.3)
    - CalculadorSimilitud   : Similitud coseno entre documentos (2.4)
    - ProcesadorCorpus      : Orquesta las 4 etapas sobre el dataset completo

Uso:
    python fase2_nlp.py
    (requiere datos/dataset_maestro.json generado por la Fase 1)
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import json
import re
import os
from collections import Counter

import nltk
import numpy as np
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Descarga silenciosa de recursos NLTK necesarios
for recurso in ('punkt', 'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger'):
    nltk.download(recurso, quiet=True)


# ── Palabras basura adicionales (más allá de stopwords estándar) ─────────────
BASURA_EXTRA = {
    'nbsp', 'solo', 'mejor', 'vez', 'cómo', 'hace', 'año', 'años',
    'ser', 'puede', 'parte', 'dos', 'tres', 'gran', 'mismo', 'misma',
    'así', 'cada', 'menos', 'después', 'ahora', 'según', 'sino',
    'además', 'también', 'aunque', 'mientras', 'durante', 'través',
}


# ═════════════════════════════════════════════════════════════════════════════
# 2.1  PIPELINE DE PRE-PROCESAMIENTO
#      Transforma texto crudo en tokens limpios y sus raíces (stems).
#      Es el primer paso obligatorio antes de cualquier análisis cuantitativo.
# ═════════════════════════════════════════════════════════════════════════════

class PipelineNLP:
    """
    Aplica el pipeline estándar de pre-procesamiento NLP a un texto.

    Pasos en orden:
      1. Limpieza   — minúsculas, quita puntuación y dígitos
      2. Tokenización — divide en palabras individuales
      3. Filtrado   — elimina stopwords y tokens muy cortos
      4. Stemming   — reduce cada token a su raíz morfológica

    Args:
        idioma : Idioma para stemmer y stopwords (default: 'spanish').
    """

    def __init__(self, idioma: str = 'spanish'):
        self.idioma     = idioma
        self.stemmer    = SnowballStemmer(idioma)
        self.stopwords  = set(stopwords.words(idioma)) | BASURA_EXTRA

    # ── Pasos individuales ───────────────────────────────────────────────────

    def limpiar(self, texto: str) -> str:
        """Normaliza el texto: minúsculas, sin puntuación ni dígitos."""
        texto = texto.lower()
        texto = re.sub(r'[^\w\sáéíóúñü]', ' ', texto)  # quita puntuación
        texto = re.sub(r'\d+', '', texto)                # quita números
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    def tokenizar(self, texto: str) -> list[str]:
        """Divide el texto en tokens individuales."""
        return word_tokenize(texto, language=self.idioma)

    def filtrar(self, tokens: list[str]) -> list[str]:
        """Elimina stopwords y tokens con menos de 3 caracteres."""
        return [t for t in tokens if t not in self.stopwords and len(t) > 2]

    def aplicar_stemming(self, tokens: list[str]) -> list[str]:
        """Reduce cada token a su raíz morfológica."""
        return [self.stemmer.stem(t) for t in tokens]

    # ── Pipeline completo ────────────────────────────────────────────────────

    def procesar(self, texto: str) -> dict:
        """
        Ejecuta los 4 pasos sobre un texto y retorna un dict con
        los resultados de cada etapa más métricas derivadas.
        """
        limpio      = self.limpiar(texto)
        tokens      = self.tokenizar(limpio)
        filtrados   = self.filtrar(tokens)
        stems       = self.aplicar_stemming(filtrados)
        oraciones   = sent_tokenize(texto, language=self.idioma)

        return {
            'original':        texto,
            'limpio':          limpio,
            'tokens':          tokens,
            'filtrados':       filtrados,   # sin stopwords
            'stems':           stems,
            'num_oraciones':   len(oraciones),
            'num_tokens':      len(tokens),
            'num_filtrados':   len(filtrados),
            'vocabulario':     len(set(filtrados)),
            # Riqueza léxica: qué tan variado es el vocabulario (0–1)
            'riqueza_lexica':  round(len(set(filtrados)) / max(len(filtrados), 1), 4),
        }

    def procesar_corpus(self, textos: list[str]) -> list[dict]:
        """Aplica procesar() a cada texto de una lista."""
        return [self.procesar(t) for t in textos]


# ═════════════════════════════════════════════════════════════════════════════
# 2.2  ANALIZADOR LÉXICO
#      Calcula estadísticas globales y por categoría sobre el corpus ya
#      tokenizado: frecuencias, n-gramas y extracción de entidades nombradas
#      mediante heurística de mayúsculas (sin modelo externo).
# ═════════════════════════════════════════════════════════════════════════════

class AnalizadorLexico:
    """
    Genera métricas léxicas y estadísticas sobre el corpus procesado.

    Incluye:
      - Frecuencias de unigramas, bigramas y trigramas
      - Riqueza léxica promedio del corpus
      - Entidades nombradas (heurística por mayúsculas)
      - Nubes de palabras por categoría (si wordcloud está disponible)

    Args:
        stopwords_extra : Conjunto adicional de palabras a ignorar.
    """

    def __init__(self, stopwords_extra: set = None):
        self._sw_base = set(stopwords.words('spanish')) | BASURA_EXTRA
        if stopwords_extra:
            self._sw_base |= stopwords_extra

    # ── API pública ──────────────────────────────────────────────────────────

    def estadisticas_globales(self, resultados_nlp: list[dict]) -> dict:
        """
        Calcula métricas sobre el corpus completo a partir de los
        dicts devueltos por PipelineNLP.procesar().
        """
        todos_tokens = []
        todos_stems  = []
        for r in resultados_nlp:
            todos_tokens.extend(r['filtrados'])
            todos_stems.extend(r['stems'])

        return {
            'total_documentos':      len(resultados_nlp),
            'total_tokens':          len(todos_tokens),
            'vocabulario_unico':     len(set(todos_tokens)),
            'stems_unicos':          len(set(todos_stems)),
            'promedio_tokens_doc':   round(len(todos_tokens) / max(len(resultados_nlp), 1), 1),
            'riqueza_lexica_prom':   round(
                sum(r['riqueza_lexica'] for r in resultados_nlp) / max(len(resultados_nlp), 1), 4
            ),
            'unigramas_top10':  self._top_ngrams(todos_tokens, 1, 10),
            'bigramas_top10':   self._top_ngrams(todos_tokens, 2, 10),
            'trigramas_top5':   self._top_ngrams(todos_tokens, 3, 5),
        }

    def estadisticas_por_categoria(self, noticias: list[dict],
                                   resultados_nlp: list[dict]) -> dict:
        """
        Agrupa los tokens por categoría y calcula métricas independientes
        para cada una.
        """
        grupos: dict[str, list[str]] = {}
        for noticia, resultado in zip(noticias, resultados_nlp):
            cat = noticia.get('categoria', 'general').lower()
            grupos.setdefault(cat, []).extend(resultado['filtrados'])

        stats = {}
        for cat, tokens in grupos.items():
            if not tokens:
                continue
            stats[cat] = {
                'total_tokens':    len(tokens),
                'vocabulario':     len(set(tokens)),
                'riqueza_lexica':  round(len(set(tokens)) / len(tokens), 4),
                'unigramas_top5':  self._top_ngrams(tokens, 1, 5),
                'bigramas_top5':   self._top_ngrams(tokens, 2, 5),
                'trigramas_top3':  self._top_ngrams(tokens, 3, 3),
            }
        return stats

    def extraer_entidades(self, textos_originales: list[str], top_n: int = 15) -> list[str]:
        """
        Extrae candidatos a entidades nombradas mediante heurística:
        secuencias de palabras que comienzan con mayúscula y no son
        stopwords. Sin dependencia de modelos externos.
        """
        texto_unido = ' '.join(textos_originales)
        # Captura secuencias de 1-3 palabras con mayúscula inicial
        patron = r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,2}'
        candidatos = re.findall(patron, texto_unido)
        # Filtra stopwords y tokens demasiado cortos
        sw = set(stopwords.words('spanish'))
        validos = [e for e in candidatos if e.lower() not in sw and len(e) > 3]
        return [ent for ent, _ in Counter(validos).most_common(top_n)]

    def generar_nubes(self, noticias: list[dict], resultados_nlp: list[dict],
                      ruta_salida: str):
        """
        Genera nubes de palabras globales y por categoría.
        Si wordcloud no está instalado, omite silenciosamente.
        """
        try:
            from wordcloud import WordCloud
        except ImportError:
            print("  [NLP] wordcloud no instalado — se omiten nubes de palabras.")
            return

        os.makedirs(ruta_salida, exist_ok=True)

        # Nube global
        todos = [t for r in resultados_nlp for t in r['filtrados']]
        self._guardar_nube(todos, os.path.join(ruta_salida, 'nube_global.png'), WordCloud)

        # Nubes por categoría
        grupos: dict[str, list[str]] = {}
        for noticia, resultado in zip(noticias, resultados_nlp):
            cat = noticia.get('categoria', 'general').lower()
            grupos.setdefault(cat, []).extend(resultado['filtrados'])

        for cat, tokens in grupos.items():
            if tokens:
                self._guardar_nube(
                    tokens,
                    os.path.join(ruta_salida, f'nube_{cat}.png'),
                    WordCloud
                )
        print(f"  [NLP] Nubes exportadas → {ruta_salida}")

    # ── Métodos internos ─────────────────────────────────────────────────────

    def _top_ngrams(self, tokens: list[str], n: int, top: int) -> list[str]:
        """Retorna los n-gramas más frecuentes como strings legibles."""
        if n == 1:
            conteo = Counter(tokens)
        else:
            conteo = Counter(ngrams(tokens, n))
        return [' '.join(gram) if n > 1 else gram
                for gram, _ in conteo.most_common(top)]

    @staticmethod
    def _guardar_nube(tokens: list[str], ruta: str, WordCloud):
        wc = WordCloud(
            width=800, height=400,
            background_color='#1a1a2e',
            colormap='Blues',
            max_words=80,
        ).generate(' '.join(tokens))
        wc.to_file(ruta)


# ═════════════════════════════════════════════════════════════════════════════
# 2.3  REPRESENTACIÓN VECTORIAL (TF-IDF)
#      Convierte los textos pre-procesados en una matriz numérica dispersa.
#      TF-IDF pondera cada término según su frecuencia en el documento (TF)
#      y su rareza en el corpus (IDF), resaltando términos discriminativos.
# ═════════════════════════════════════════════════════════════════════════════

class RepresentacionVectorial:
    """
    Construye y gestiona la matriz TF-IDF del corpus.

    Args:
        max_features  : Tamaño máximo del vocabulario a considerar.
        ngram_range   : Rango de n-gramas (unigrama + bigrama por defecto).
        sublinear_tf  : Aplica escala logarítmica a TF para suavizar frecuencias altas.
    """

    def __init__(self, max_features: int = 3000, ngram_range: tuple = (1, 2),
                 sublinear_tf: bool = True):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            sublinear_tf=sublinear_tf,
        )
        self.matriz    = None
        self._textos   = []

    # ── API pública ──────────────────────────────────────────────────────────

    def construir(self, resultados_nlp: list[dict]) -> 'RepresentacionVectorial':
        """
        Ajusta el vectorizador y construye la matriz TF-IDF.
        Recibe los dicts de PipelineNLP para usar los tokens filtrados.
        """
        # Reunimos los tokens filtrados en un string por documento
        self._textos = [' '.join(r['filtrados']) for r in resultados_nlp]
        self.matriz  = self.vectorizer.fit_transform(self._textos)
        return self  # permite encadenamiento

    def vocabulario(self) -> np.ndarray:
        """Array con todos los términos del vocabulario aprendido."""
        return self.vectorizer.get_feature_names_out()

    def terminos_relevantes(self, doc_idx: int, top_n: int = 8) -> list[tuple]:
        """Retorna los top_n términos más importantes de un documento."""
        vector    = self.matriz[doc_idx].toarray().flatten()
        terminos  = self.vocabulario()
        top_idx   = vector.argsort()[::-1][:top_n]
        return [(terminos[i], round(float(vector[i]), 4))
                for i in top_idx if vector[i] > 0]

    def info(self) -> dict:
        """Métricas de la matriz construida."""
        filas, cols = self.matriz.shape
        return {
            'documentos':          filas,
            'features':            cols,
            'terminos_no_cero':    self.matriz.nnz,
            'densidad':            round(self.matriz.nnz / (filas * cols), 6),
            'promedio_terms_doc':  round(self.matriz.nnz / max(filas, 1), 1),
        }


# ═════════════════════════════════════════════════════════════════════════════
# 2.4  CALCULADOR DE SIMILITUD
#      Usa la distancia coseno entre vectores TF-IDF para medir qué tan
#      parecidos son dos documentos. Cos(0°)=1 (idénticos), Cos(90°)=0
#      (sin términos en común).
# ═════════════════════════════════════════════════════════════════════════════

class CalculadorSimilitud:
    """
    Calcula y consulta la matriz de similitud coseno entre documentos.

    La similitud coseno es preferible a la distancia euclidiana para textos
    porque es invariante a la longitud del documento.

    Args:
        matriz_tfidf : Matriz dispersa generada por RepresentacionVectorial.
    """

    def __init__(self, matriz_tfidf):
        self._matriz_sim = cosine_similarity(matriz_tfidf)

    # ── API pública ──────────────────────────────────────────────────────────

    def similitud(self, i: int, j: int) -> float:
        """Similitud entre los documentos i y j (0–1)."""
        return round(float(self._matriz_sim[i][j]), 4)

    def mas_similares(self, doc_idx: int, top_n: int = 3) -> list[tuple]:
        """
        Retorna los top_n documentos más similares al documento dado,
        excluyendo el propio documento.
        """
        fila    = self._matriz_sim[doc_idx]
        indices = fila.argsort()[::-1]
        # Excluimos el doc mismo (similitud 1.0 consigo)
        resultado = [(int(i), round(float(fila[i]), 4))
                     for i in indices if i != doc_idx]
        return resultado[:top_n]

    def grupos_tematicos(self, umbral: float = 0.15) -> list[list[int]]:
        """
        Agrupa documentos con similitud ≥ umbral mediante búsqueda voraz.
        Útil para detectar noticias que cubren el mismo tema.
        """
        n         = len(self._matriz_sim)
        visitados = set()
        grupos    = []

        for i in range(n):
            if i in visitados:
                continue
            grupo = [i]
            visitados.add(i)
            for j in range(i + 1, n):
                if j not in visitados and self._matriz_sim[i][j] >= umbral:
                    grupo.append(j)
                    visitados.add(j)
            grupos.append(grupo)

        return grupos

    def matriz_como_lista(self) -> list[list[float]]:
        """Serializable: convierte la matriz a lista de listas."""
        return [[round(float(v), 4) for v in fila] for fila in self._matriz_sim]


# ═════════════════════════════════════════════════════════════════════════════
# ORQUESTADOR
# ═════════════════════════════════════════════════════════════════════════════

class ProcesadorCorpus:
    """
    Orquesta las 4 etapas NLP sobre el dataset completo del SIMANW.

    Lee el JSON de la Fase 1, aplica el pipeline a cada noticia,
    construye la representación vectorial y exporta los resultados
    enriquecidos listos para la Fase 3.

    Args:
        ruta_dataset : Ruta al dataset_maestro.json de la Fase 1.
    """

    def __init__(self, ruta_dataset: str):
        self.ruta_dataset = ruta_dataset
        self.noticias:    list[dict] = []
        self.resultados:  list[dict] = []
        self.vectores:    RepresentacionVectorial | None = None
        self.similitud:   CalculadorSimilitud | None = None

    # ── API pública ──────────────────────────────────────────────────────────

    def ejecutar(self) -> list[dict]:
        """Corre el pipeline NLP completo y retorna las noticias enriquecidas."""
        self._cargar_dataset()

        if not self.noticias:
            print("  [NLP] Dataset vacío — ejecuta primero la Fase 1.")
            return []

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 2 — Pipeline NLP                      ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Noticias a procesar : {len(self.noticias)}\n")

        # ── 2.1 Pre-procesamiento ────────────────────────────────────────────
        print("  ▶ 2.1 Pre-procesamiento...")
        pipeline = PipelineNLP()
        textos   = [f"{n['titulo']}. {n['cuerpo']}" for n in self.noticias]
        self.resultados = pipeline.procesar_corpus(textos)

        # Enriquecemos cada noticia con sus metadatos NLP
        for noticia, resultado in zip(self.noticias, self.resultados):
            noticia['nlp'] = {
                'num_tokens':     resultado['num_tokens'],
                'num_filtrados':  resultado['num_filtrados'],
                'vocabulario':    resultado['vocabulario'],
                'riqueza_lexica': resultado['riqueza_lexica'],
                'num_oraciones':  resultado['num_oraciones'],
                'tokens_repr':    resultado['filtrados'][:20],  # muestra compacta
            }

        # ── 2.2 Análisis léxico ──────────────────────────────────────────────
        print("  ▶ 2.2 Análisis léxico...")
        analizador = AnalizadorLexico()
        stats_globales = analizador.estadisticas_globales(self.resultados)
        stats_cat      = analizador.estadisticas_por_categoria(self.noticias, self.resultados)
        entidades      = analizador.extraer_entidades(textos)

        self._imprimir_estadisticas(stats_globales, stats_cat, entidades)

        # ── 2.3 Vectorización TF-IDF ─────────────────────────────────────────
        print("\n  ▶ 2.3 Vectorización TF-IDF...")
        self.vectores = RepresentacionVectorial(max_features=3000)
        self.vectores.construir(self.resultados)
        info_v = self.vectores.info()
        print(f"     Matriz: {info_v['documentos']} docs × {info_v['features']} features")
        print(f"     Densidad: {info_v['densidad']} | "
              f"Términos/doc (prom): {info_v['promedio_terms_doc']}")

        print("\n     Términos más relevantes por noticia:")
        for i, noticia in enumerate(self.noticias[:5]):   # muestra solo las 5 primeras
            cat = noticia.get('categoria', '?')
            titulo = noticia['titulo'][:45]
            top = self.vectores.terminos_relevantes(i, top_n=5)
            print(f"     [{cat}] {titulo}...")
            for termino, peso in top:
                print(f"       {termino:<25} {peso}")

        # ── 2.4 Similitud coseno ─────────────────────────────────────────────
        print("\n  ▶ 2.4 Similitud coseno...")
        self.similitud = CalculadorSimilitud(self.vectores.matriz)

        grupos = self.similitud.grupos_tematicos(umbral=0.15)
        grupos_multiples = [g for g in grupos if len(g) > 1]
        print(f"     Grupos temáticos detectados: {len(grupos_multiples)}")
        for idx, grupo in enumerate(grupos_multiples[:3], 1):   # muestra top 3
            print(f"     Grupo {idx}: {len(grupo)} noticias")
            for i in grupo[:3]:
                print(f"       · {self.noticias[i]['titulo'][:55]}...")

        return self.noticias

    def guardar_resultados(self, ruta_dataset_nlp: str, ruta_stats: str):
        """
        Exporta el dataset enriquecido con metadatos NLP y las estadísticas
        léxicas en archivos JSON para la Fase 3.
        """
        if not self.noticias:
            print("  [NLP] Nada que guardar.")
            return

        os.makedirs(os.path.dirname(ruta_dataset_nlp), exist_ok=True)
        os.makedirs(os.path.dirname(ruta_stats), exist_ok=True)

        # Dataset enriquecido (sin la matriz vectorial — demasiado grande para JSON)
        with open(ruta_dataset_nlp, 'w', encoding='utf-8') as f:
            json.dump(self.noticias, f, ensure_ascii=False, indent=2)
        print(f"\n  [Dataset NLP] {len(self.noticias)} noticias → {ruta_dataset_nlp}")

        # Estadísticas léxicas
        analizador = AnalizadorLexico()
        stats = {
            'globales':   analizador.estadisticas_globales(self.resultados),
            'categorias': analizador.estadisticas_por_categoria(self.noticias, self.resultados),
            'entidades':  analizador.extraer_entidades(
                [f"{n['titulo']}. {n['cuerpo']}" for n in self.noticias]
            ),
        }
        with open(ruta_stats, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        print(f"  [Stats NLP]   → {ruta_stats}")

    # ── Métodos internos ─────────────────────────────────────────────────────

    def _cargar_dataset(self):
        try:
            with open(self.ruta_dataset, 'r', encoding='utf-8') as f:
                self.noticias = json.load(f)
        except FileNotFoundError:
            print(f"  [NLP] ✗ No se encontró {self.ruta_dataset}")
            print("         Ejecuta primero fase1_rastreador.py")
            self.noticias = []

    @staticmethod
    def _imprimir_estadisticas(globales: dict, por_cat: dict, entidades: list):
        print(f"     Total documentos    : {globales['total_documentos']}")
        print(f"     Total tokens        : {globales['total_tokens']}")
        print(f"     Vocabulario único   : {globales['vocabulario_unico']}")
        print(f"     Riqueza léxica prom : {globales['riqueza_lexica_prom']}")
        print(f"     Tokens/doc (prom)   : {globales['promedio_tokens_doc']}")
        print(f"\n     Unigramas top-10    : {globales['unigramas_top10']}")
        print(f"     Bigramas top-10     : {globales['bigramas_top10']}")
        print(f"     Trigramas top-5     : {globales['trigramas_top5']}")
        print(f"\n     Entidades nombradas : {entidades}")

        print("\n     Por categoría:")
        for cat, s in por_cat.items():
            print(f"       [{cat}] {s['total_tokens']} tokens | "
                  f"vocab {s['vocabulario']} | riqueza {s['riqueza_lexica']}")
            print(f"         top: {s['unigramas_top5']}")


# ═════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':

    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    procesador = ProcesadorCorpus(
        ruta_dataset=os.path.join(BASE, 'datos', 'dataset_maestro.json'),
    )

    procesador.ejecutar()

    procesador.guardar_resultados(
        ruta_dataset_nlp=os.path.join(BASE, 'datos', 'dataset_nlp.json'),
        ruta_stats=os.path.join(BASE, 'reportes', 'estadisticas_nlp.json'),
    )