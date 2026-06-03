
"""
SIMANW - Interfaz gráfica del pipeline completo
===============================================

Aplicación Streamlit para ejecutar, visualizar y auditar el proyecto SIMANW.

Uso:
    streamlit run app_simanw.py

Desde la raíz del proyecto:
    /home/yayo/Documentos/Proyecto_web

Características:
- Dashboard general.
- Ejecución de fases y actividades complementarias.
- Visualización de datasets, reportes y Knowledge Graph.
- Buscador local sobre dataset_analizado.json.
- Chatbot básico sobre el corpus.
- Trazabilidad y entrega final.

Requiere:
    pip install streamlit plotly pandas scikit-learn rdflib
"""

import json
import os
import re
import unicodedata
import subprocess
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

try:
    import plotly.express as px
except Exception:
    px = None

try:
    from rdflib import Graph
except Exception:
    Graph = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None


APP_TITLE = "SIMANW — Sistema Inteligente de Monitoreo y Análisis de Noticias Web"


def root_project() -> Path:
    actual = Path.cwd().resolve()

    if (actual / "datos").exists() and (actual / "fases").exists():
        return actual

    if actual.name.lower() == "fases" and (actual.parent / "datos").exists():
        return actual.parent

    archivo = Path(__file__).resolve()
    if (archivo.parent / "datos").exists() and (archivo.parent / "fases").exists():
        return archivo.parent

    return actual


ROOT = root_project()


def normalizar_texto(texto: str) -> str:
    texto = str(texto or "").lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"https?://\S+", " ", texto)
    texto = re.sub(r"www\.\S+", " ", texto)
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"\d+", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


ARTEFACTOS = {
    "Dataset maestro": "datos/dataset_maestro.json",
    "Dataset NLP": "datos/dataset_nlp.json",
    "Dataset analizado": "datos/dataset_analizado.json",
    "Corpus depurado AC8": "datos/dataset_depurado_ac8.json",
    "Índice invertido": "indices/indice_invertido.json",
    "Reporte Fase 5": "reportes/reporte_fase5_conversacion.json",
    "Reporte Fase 6": "reportes/reporte_fase6_kg.json",
    "Reporte Fase 7": "reportes/reporte_final_simanw.json",
    "AC5 búsqueda": "reportes/ac5_comparador_busqueda.json",
    "AC8 calidad": "reportes/ac8_control_calidad_corpus.json",
    "AC9 tendencias": "reportes/ac9_tendencias_temporales.json",
    "AC10 alertas": "reportes/ac10_reporte_alertas.json",
    "AC12 manifiesto": "evidencia/ac12_manifiesto_ejecucion.json",
    "AC13 publicación": "knowledge_graph/publicacion/manifiesto_publicacion.json",
    "KG Turtle": "knowledge_graph/simanw.ttl",
    "KG RDF/XML": "knowledge_graph/simanw.rdf",
    "KG JSON-LD": "knowledge_graph/simanw.jsonld",
}


SCRIPTS = {
    "Fase 1 — Rastreo RSS": "fases/Fase1_Rastreador.py",
    "AC1 — Rastreo paginado": "fases/AC1_RastreadorPaginado.py",
    "AC8 — Control calidad": "fases/AC8_ControlCalidadCorpus.py",
    "Fase 2 — Pipeline NLP": "fases/Fase2_Pipeline.py",
    "AC2 — Análisis discurso": "fases/AC2_AnalisisDiscurso.py",
    "Fase 3 — Clasificador": "fases/Fase3_Clasificador.py",
    "AC3 — Selector multimodelo": "fases/AC3_SelectorMultimodelo.py",
    "AC4 — Hilos discusión": "fases/AC4_AnalisisHilos.py",
    "Fase 4 — Motor búsqueda": "fases/Fase4_Busqueda.py",
    "AC5 — Comparador búsqueda": "fases/AC5_ComparadorBusqueda.py",
    "Fase 5 — Chatbot": "fases/Fase5_Conversacion.py",
    "AC6 — Chatbot contextual": "fases/AC6_ChatbotContextual.py",
    "Fase 6 — Knowledge Graph": "fases/Fase6_KnowledgeGraph.py",
    "AC7 — Enriquecimiento externo": "fases/AC7_EnriquecimientoExterno.py",
    "AC9 — Tendencias temporales": "fases/AC9_LineaTiempoTendencias.py",
    "AC10 — Alertas": "fases/AC10_SistemaAlertas.py",
    "AC11 — Usabilidad": "fases/AC11_EstudioUsabilidad.py",
    "AC12 — Trazabilidad": "fases/AC12_TrazabilidadPipeline.py",
    "AC13 — Publicación semántica": "fases/AC13_PublicacionSemantica.py",
    "Fase 7 — Reportes finales": "fases/Fase7_Reportes.py",
}


def setup_page():
    st.set_page_config(
        page_title="SIMANW",
        page_icon="📰",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        :root {
            --bg: #0e0e0f;
            --bg2: #161618;
            --bg3: #1e1e21;
            --border: #2e2e33;
            --text: #e8e8ec;
            --muted: #9898a8;
            --accent: #4af0b0;
            --info: #4ab8f0;
            --warn: #f0a84a;
            --danger: #f06060;
            --purple: #a88afc;
        }

        .stApp {
            background: var(--bg);
            color: var(--text);
        }

        section[data-testid="stSidebar"] {
            background: var(--bg2);
            border-right: 1px solid var(--border);
        }

        section[data-testid="stSidebar"] * {
            color: var(--text);
        }

        h1, h2, h3 {
            color: var(--text);
            font-weight: 500;
        }

        div[data-testid="stMetric"] {
            background: var(--bg2);
            border: 1px solid var(--border);
            padding: 16px;
            border-radius: 8px;
        }

        div[data-testid="stMetric"] label {
            color: var(--muted) !important;
        }

        div[data-testid="stMetricValue"] {
            color: var(--accent);
        }

        .simanw-card {
            background: var(--bg2);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 14px;
        }

        .simanw-title {
            font-size: 26px;
            font-weight: 600;
            color: var(--accent);
            letter-spacing: .03em;
        }

        .simanw-subtitle {
            color: var(--muted);
            font-size: 14px;
            margin-top: -8px;
            margin-bottom: 20px;
        }

        .ok { color: var(--accent); font-weight: 600; }
        .warn { color: var(--warn); font-weight: 600; }
        .bad { color: var(--danger); font-weight: 600; }
        .muted { color: var(--muted); }

        .status-pill {
            display: inline-block;
            padding: 3px 9px;
            border-radius: 4px;
            font-size: 12px;
            font-family: monospace;
            border: 1px solid var(--border);
            margin-right: 4px;
        }

        .pill-ok {
            background: rgba(74,240,176,.08);
            color: var(--accent);
            border-color: rgba(74,240,176,.25);
        }

        .pill-missing {
            background: rgba(240,168,74,.08);
            color: var(--warn);
            border-color: rgba(240,168,74,.25);
        }

        .small-mono {
            font-family: monospace;
            font-size: 12px;
            color: var(--muted);
        }

        .stButton > button {
            background: var(--accent);
            color: #06140d;
            border: none;
            font-weight: 600;
        }

        .stButton > button:hover {
            background: #1fd88a;
            color: #06140d;
            border: none;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 8px;
        }

        textarea, input {
            background-color: var(--bg2) !important;
            color: var(--text) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_json(relative_path: str, default=None):
    path = ROOT / relative_path
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def load_text(relative_path: str, default=""):
    path = ROOT / relative_path
    if not path.exists():
        return default

    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return default


def save_session_log(name: str, output: str):
    logs_dir = ROOT / "logs_ui"
    logs_dir.mkdir(exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", name)
    path = logs_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_name}.txt"
    path.write_text(output, encoding="utf-8")
    return path


def run_script(label: str, relative_script: str):
    script_path = ROOT / relative_script

    if not script_path.exists():
        st.error(f"No se encontró el script: {relative_script}")
        return None

    with st.spinner(f"Ejecutando {label}..."):
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=300,
            )

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += "\n--- STDERR ---\n" + result.stderr

            log_path = save_session_log(label, output)

            if result.returncode == 0:
                st.success(f"{label} ejecutado correctamente.")
            else:
                st.error(f"{label} terminó con código {result.returncode}.")

            st.caption(f"Log guardado en: {log_path.relative_to(ROOT)}")
            st.code(output or "Sin salida.", language="bash")
            return result.returncode

        except subprocess.TimeoutExpired:
            st.error("La ejecución tardó demasiado y fue detenida.")
        except Exception as exc:
            st.error(f"Error al ejecutar: {exc}")

    return None


def count_json_records(relative_path: str):
    data = load_json(relative_path)

    if isinstance(data, list):
        return len(data)

    if isinstance(data, dict):
        for key in ("total_noticias", "total_registros", "validos", "noticias", "documentos"):
            value = data.get(key)
            if isinstance(value, int):
                return value
            if isinstance(value, list):
                return len(value)

        if "estadisticas" in data and isinstance(data["estadisticas"], dict):
            return data["estadisticas"].get("total_registros")

    return 0


def count_triples():
    ttl = ROOT / "knowledge_graph" / "simanw.ttl"

    if ttl.exists() and Graph is not None:
        try:
            g = Graph()
            g.parse(str(ttl), format="turtle")
            return len(g)
        except Exception:
            pass

    reporte = load_json("reportes/reporte_fase6_kg.json", {})
    for key in ("total_triples", "triples", "triples_finales"):
        if isinstance(reporte.get(key), int):
            return reporte[key]

    return 0


def get_noticias():
    noticias = load_json("datos/dataset_analizado.json", [])
    if not isinstance(noticias, list):
        return []
    return noticias


def categoria(noticia):
    return (
        noticia.get("categoria_predicha")
        or noticia.get("categoria")
        or noticia.get("categoria_original")
        or "general"
    )


def sentimiento(noticia):
    sent = noticia.get("sentimiento", {})
    if isinstance(sent, dict):
        return sent.get("etiqueta", "desconocido")
    return str(sent or "desconocido")


def sentiment_score(noticia):
    sent = noticia.get("sentimiento", {})
    if isinstance(sent, dict):
        try:
            return float(sent.get("compound", 0))
        except Exception:
            return 0.0
    return 0.0


def noticia_texto(noticia):
    return " ".join([
        str(noticia.get("titulo", "")),
        str(noticia.get("cuerpo", "")),
        str(noticia.get("resumen", "")),
        str(categoria(noticia)),
    ])


def artifact_status_table():
    rows = []
    for name, rel in ARTEFACTOS.items():
        path = ROOT / rel
        rows.append({
            "Artefacto": name,
            "Ruta": rel,
            "Estado": "OK" if path.exists() else "FALTA",
            "Tamaño KB": round(path.stat().st_size / 1024, 2) if path.exists() else 0,
        })
    return pd.DataFrame(rows)


def pipeline_status():
    rows = []
    for name, rel in SCRIPTS.items():
        path = ROOT / rel
        rows.append({
            "Módulo": name,
            "Script": rel,
            "Estado": "OK" if path.exists() else "FALTA",
        })
    return pd.DataFrame(rows)


def search_corpus(query: str, category_filter: str = "", top_k: int = 8):
    noticias = get_noticias()
    if not query.strip() or not noticias:
        return []

    if TfidfVectorizer is None or cosine_similarity is None:
        return []

    textos = [normalizar_texto(noticia_texto(n)) for n in noticias]
    query_normalizada = normalizar_texto(query)
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), lowercase=True)
    matrix = vectorizer.fit_transform(textos)
    q_vec = vectorizer.transform([query_normalizada])
    sims = cosine_similarity(q_vec, matrix)[0]
    order = sims.argsort()[::-1]

    results = []
    for idx in order:
        score = float(sims[idx])
        if score <= 0:
            continue

        n = noticias[int(idx)]
        cat = categoria(n)
        if category_filter and cat != category_filter:
            continue

        cuerpo = re.sub(r"\s+", " ", n.get("cuerpo", "")).strip()
        results.append({
            "idx": int(idx),
            "titulo": n.get("titulo", "Sin título"),
            "categoria": cat,
            "sentimiento": sentimiento(n),
            "score": round(score, 4),
            "url": n.get("url", ""),
            "snippet": cuerpo[:240] + ("..." if len(cuerpo) > 240 else ""),
        })

        if len(results) >= top_k:
            break

    return results


def simple_chat_response(question: str):
    q = normalizar_texto(question)
    noticias = get_noticias()

    if not noticias:
        return "No encontré el dataset analizado. Ejecuta primero las fases 1–3.", []

    if any(w in q for w in ["cuantas", "cuantos", "total"]):
        cats = Counter(categoria(n) for n in noticias)
        sents = Counter(sentimiento(n) for n in noticias)
        response = (
            f"Tengo {len(noticias)} noticias procesadas. "
            f"Por categoría: {', '.join(f'{k}: {v}' for k, v in cats.most_common())}. "
            f"Por sentimiento: {', '.join(f'{k}: {v}' for k, v in sents.most_common())}."
        )
        return response, []

    if any(w in q for w in ["sentimiento", "tono", "positivo", "negativo", "neutral"]):
        scores = [sentiment_score(n) for n in noticias]
        avg = sum(scores) / max(len(scores), 1)
        tono = "positivo" if avg > 0.05 else "negativo" if avg < -0.05 else "neutral"
        dist = Counter(sentimiento(n) for n in noticias)
        return f"El tono general del corpus es {tono}. Compound promedio: {avg:+.3f}. Distribución: {dict(dist)}.", []

    results = search_corpus(question, top_k=3)
    if not results:
        return "No encontré resultados claros para esa consulta.", []

    top = results[0]
    response = (
        f"La noticia más relacionada es: {top['titulo']}. "
        f"Categoría: {top['categoria']} | Sentimiento: {top['sentimiento']} | Score: {top['score']}."
    )
    return response, results


def render_header():
    st.markdown(
        f"""
        <div class="simanw-title">SIMANW <span style="color:#9898a8;font-size:16px;">v1.0</span></div>
        <div class="simanw-subtitle">Sistema Inteligente de Monitoreo y Análisis de Noticias Web · Enero–Junio 2026</div>
        """,
        unsafe_allow_html=True,
    )


def view_dashboard():
    render_header()
    st.subheader("Dashboard general")

    noticias = get_noticias()
    cats = Counter(categoria(n) for n in noticias)
    sents = Counter(sentimiento(n) for n in noticias)
    scores = [sentiment_score(n) for n in noticias]
    avg = sum(scores) / max(len(scores), 1)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Noticias", len(noticias))
    c2.metric("Triples RDF", count_triples())
    c3.metric("Categorías", len(cats))
    c4.metric("Sent. promedio", f"{avg:+.3f}")
    c5.metric("Artefactos OK", int((artifact_status_table()["Estado"] == "OK").sum()))

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Distribución por categoría")
        if cats:
            df = pd.DataFrame(cats.items(), columns=["Categoría", "Noticias"]).sort_values("Noticias", ascending=False)
            if px:
                st.plotly_chart(px.bar(df, x="Categoría", y="Noticias"), use_container_width=True)
            else:
                st.bar_chart(df.set_index("Categoría"))
        else:
            st.info("Aún no hay dataset analizado.")

    with col_b:
        st.markdown("### Distribución de sentimiento")
        if sents:
            df = pd.DataFrame(sents.items(), columns=["Sentimiento", "Noticias"]).sort_values("Noticias", ascending=False)
            if px:
                st.plotly_chart(px.pie(df, values="Noticias", names="Sentimiento"), use_container_width=True)
            else:
                st.bar_chart(df.set_index("Sentimiento"))
        else:
            st.info("Aún no hay sentimientos procesados.")

    st.markdown("### Estado del pipeline")
    st.dataframe(pipeline_status(), use_container_width=True, hide_index=True)

    with st.expander("Artefactos detectados"):
        st.dataframe(artifact_status_table(), use_container_width=True, hide_index=True)


def view_ejecucion():
    render_header()
    st.subheader("Ejecución del pipeline")

    st.warning(
        "Ejecuta las fases en orden. Algunas fases dependen de archivos generados por fases anteriores."
    )

    ordered = [
        "Fase 1 — Rastreo RSS",
        "AC1 — Rastreo paginado",
        "AC8 — Control calidad",
        "Fase 2 — Pipeline NLP",
        "AC2 — Análisis discurso",
        "Fase 3 — Clasificador",
        "AC3 — Selector multimodelo",
        "AC4 — Hilos discusión",
        "Fase 4 — Motor búsqueda",
        "AC5 — Comparador búsqueda",
        "Fase 5 — Chatbot",
        "AC6 — Chatbot contextual",
        "Fase 6 — Knowledge Graph",
        "AC7 — Enriquecimiento externo",
        "AC9 — Tendencias temporales",
        "AC10 — Alertas",
        "AC12 — Trazabilidad",
        "AC13 — Publicación semántica",
        "Fase 7 — Reportes finales",
    ]

    for name in ordered:
        script = SCRIPTS.get(name)
        exists = (ROOT / script).exists() if script else False

        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 2, 1])
            col1.markdown(f"**{name}**")
            col2.code(script or "N/D", language="text")
            col3.markdown("✅ OK" if exists else "⚠️ Falta")

            if exists:
                if st.button(f"Ejecutar {name}", key=f"run_{name}"):
                    run_script(name, script)


def view_rastreo():
    render_header()
    st.subheader("Fase 1 + AC1 + AC8 — Rastreo y calidad del corpus")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dataset maestro", count_json_records("datos/dataset_maestro.json"))
    c2.metric("Rastreo paginado", count_json_records("datos/ac1_rastreo_paginado.json"))
    c3.metric("Depurado AC8", count_json_records("datos/dataset_depurado_ac8.json"))

    ac8 = load_json("reportes/ac8_control_calidad_corpus.json", {})
    stats = ac8.get("estadisticas", {})
    c4.metric("Rechazados", stats.get("rechazados", 0))

    st.markdown("### Noticias del dataset maestro")
    data = load_json("datos/dataset_maestro.json", [])
    if isinstance(data, list) and data:
        rows = []
        for n in data[:100]:
            rows.append({
                "Título": n.get("titulo", ""),
                "Fuente": n.get("fuente", ""),
                "Fecha": n.get("fecha", ""),
                "Categoría": n.get("categoria", ""),
                "URL": n.get("url", ""),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No se encontró datos/dataset_maestro.json.")

    with st.expander("Reporte AC8"):
        st.json(ac8)


def view_nlp_clasificacion():
    render_header()
    st.subheader("Fase 2–3 + AC2–AC4 — NLP, clasificación y análisis")

    noticias = get_noticias()
    cats = Counter(categoria(n) for n in noticias)
    sents = Counter(sentimiento(n) for n in noticias)

    c1, c2, c3 = st.columns(3)
    c1.metric("Noticias analizadas", len(noticias))
    c2.metric("Categorías", len(cats))
    c3.metric("Sentimientos", len(sents))

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### Categorías")
        if cats:
            st.dataframe(pd.DataFrame(cats.most_common(), columns=["Categoría", "Total"]), use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("### Sentimientos")
        if sents:
            st.dataframe(pd.DataFrame(sents.most_common(), columns=["Sentimiento", "Total"]), use_container_width=True, hide_index=True)

    st.markdown("### AC3 — Comparación multimodelo")
    ac3 = load_json("reportes/ac3_selector_multimodelo.json", {})
    modelos = ac3.get("modelos_evaluados", {})
    if modelos:
        rows = []
        for name, result in modelos.items():
            rows.append({
                "Modelo": name,
                "Accuracy media": result.get("accuracy_media"),
                "Std": result.get("desviacion_estandar"),
                "Folds": result.get("folds_usados"),
                "Estado": "Ganador" if name == ac3.get("modelo_seleccionado") else "",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Ejecuta AC3 para ver comparación multimodelo.")

    with st.expander("AC4 — Análisis de hilos"):
        st.json(load_json("reportes/ac4_analisis_hilo.json", {}))


def view_busqueda():
    render_header()
    st.subheader("Fase 4 + AC5 — Motor de búsqueda")

    query = st.text_input("Consulta", value="inteligencia artificial")
    cats = sorted({categoria(n) for n in get_noticias()})
    cat_filter = st.selectbox("Categoría", [""] + cats, format_func=lambda x: "Todas" if x == "" else x)
    top_k = st.slider("Top K", 3, 20, 8)

    if st.button("Buscar"):
        results = search_corpus(query, cat_filter, top_k)
        if not results:
            st.warning("Sin resultados.")
        for r in results:
            with st.container(border=True):
                st.markdown(f"### {r['titulo']}")
                st.caption(f"Categoría: {r['categoria']} · Sentimiento: {r['sentimiento']} · Score: {r['score']}")
                st.write(r["snippet"])
                if r["url"]:
                    st.code(r["url"], language="text")

    st.markdown("### AC5 — Booleano vs Vectorial")
    ac5 = load_json("reportes/ac5_comparador_busqueda.json", {})
    promedios = ac5.get("promedios", {})
    if promedios:
        rows = []
        for modelo, vals in promedios.items():
            row = {"Modelo": modelo}
            row.update(vals)
            rows.append(row)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.success(ac5.get("conclusion", ""))
    else:
        st.info("Ejecuta AC5 para generar la evaluación.")


def view_chatbot():
    render_header()
    st.subheader("Fase 5 + AC6 — Chatbot y Q&A")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    question = st.chat_input("Pregunta algo sobre el corpus...")
    if question:
        response, evidence = simple_chat_response(question)
        st.session_state.chat_history.append(("user", question, []))
        st.session_state.chat_history.append(("assistant", response, evidence))

    for role, msg, evidence in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(msg)
            if evidence:
                with st.expander("Evidencias"):
                    st.dataframe(pd.DataFrame(evidence), use_container_width=True, hide_index=True)

    with st.expander("Reporte Fase 5"):
        st.json(load_json("reportes/reporte_fase5_conversacion.json", {}))

    with st.expander("Reporte AC6"):
        st.json(load_json("reportes/ac6_chatbot_contextual.json", {}))


def view_kg():
    render_header()
    st.subheader("Fase 6 + AC7 + AC13 — Knowledge Graph semántico")

    c1, c2, c3 = st.columns(3)
    c1.metric("Triples RDF", count_triples())

    ac13 = load_json("knowledge_graph/publicacion/manifiesto_publicacion.json", {})
    c2.metric("Enlaces externos", ac13.get("enlaces_externos_detectados", 0))
    validacion = ac13.get("validacion", {})
    c3.metric("Validación", "OK" if validacion.get("conforms") else "N/D")

    st.markdown("### Serializaciones")
    files = [
        "knowledge_graph/simanw.ttl",
        "knowledge_graph/simanw.rdf",
        "knowledge_graph/simanw.jsonld",
        "knowledge_graph/publicacion/simanw_publicado.ttl",
        "knowledge_graph/publicacion/simanw_publicado.rdf",
        "knowledge_graph/publicacion/simanw_publicado.jsonld",
    ]
    st.dataframe(
        pd.DataFrame([
            {"Archivo": f, "Estado": "OK" if (ROOT / f).exists() else "FALTA", "KB": round((ROOT / f).stat().st_size / 1024, 2) if (ROOT / f).exists() else 0}
            for f in files
        ]),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### Consultas SPARQL documentadas")
    consultas = load_json("knowledge_graph/publicacion/consultas_sparql.json", [])
    if consultas:
        names = [f"{c.get('id', '')} — {c.get('nombre', '')}" for c in consultas]
        idx = st.selectbox("Consulta", range(len(names)), format_func=lambda i: names[i])
        st.code(consultas[idx].get("sparql", ""), language="sparql")
    else:
        st.info("Ejecuta AC13 para generar consultas documentadas.")

    with st.expander("Glosario de ontología"):
        st.markdown(load_text("knowledge_graph/publicacion/glosario_ontologia.md", "No disponible."))


def view_tendencias_alertas():
    render_header()
    st.subheader("AC9 + AC10 — Tendencias temporales y alertas")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### AC9 — Tendencias")
        ac9 = load_json("reportes/ac9_tendencias_temporales.json", {})
        st.metric("Granularidad", ac9.get("granularidad", "N/D"))
        st.metric("Periodos", len(ac9.get("periodos", [])) if isinstance(ac9.get("periodos"), list) else 0)

        tabla = ac9.get("tabla_resumen", [])
        if tabla:
            st.dataframe(pd.DataFrame(tabla), use_container_width=True, hide_index=True)

    with col_b:
        st.markdown("### AC10 — Alertas")
        ac10 = load_json("reportes/ac10_reporte_alertas.json", {})
        ejecuciones = ac10.get("ejecuciones", [])
        total_alertas = sum(len(e.get("alertas_generadas", [])) for e in ejecuciones)
        st.metric("Consultas guardadas", len(ac10.get("consultas_guardadas", [])))
        st.metric("Alertas generadas", total_alertas)

        alerts = []
        for e in ejecuciones:
            alerts.extend(e.get("alertas_generadas", []))
        if alerts:
            st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)


def view_trazabilidad_entrega():
    render_header()
    st.subheader("AC12 + Fase 7 — Trazabilidad y entrega final")

    c1, c2, c3 = st.columns(3)
    c1.metric("Artefactos OK", int((artifact_status_table()["Estado"] == "OK").sum()))
    c2.metric("Scripts OK", int((pipeline_status()["Estado"] == "OK").sum()))
    c3.metric("Triples RDF", count_triples())

    st.markdown("### Artefactos")
    st.dataframe(artifact_status_table(), use_container_width=True, hide_index=True)

    st.markdown("### Checklist AC12")
    checklist = load_text("evidencia/ac12_checklist.md", "")
    if checklist:
        st.markdown(checklist)
    else:
        st.info("Ejecuta AC12 para generar checklist.")

    st.markdown("### Reporte final")
    reporte = load_text("reportes/reporte_final_simanw.md", "")
    if reporte:
        st.markdown(reporte)
    else:
        st.info("Ejecuta Fase 7 para generar reporte final.")


def view_ac11():
    render_header()
    st.subheader("AC11 — Estudio de usabilidad")

    st.info("Esta sección queda lista para leer reportes de AC11 cuando generemos/ejecutemos el módulo.")

    ac11 = load_json("reportes/ac11_estudio_usabilidad.json", {})
    if ac11:
        st.json(ac11)
    else:
        st.warning("Aún no existe reportes/ac11_estudio_usabilidad.json.")

    st.markdown("### Requisitos AC11")
    st.markdown(
        """
        - Guion con 5 tareas.
        - Cuestionario con 8 ítems.
        - Mínimo 3 participantes.
        - Resultados anonimizados.
        - 5 problemas detectados con mejora.
        - Reflexión sobre consentimiento informado.
        """
    )


def main():
    setup_page()

    st.sidebar.markdown("## SIMANW")
    st.sidebar.caption(f"Raíz: `{ROOT}`")

    view = st.sidebar.radio(
        "Navegación",
        [
            "Dashboard",
            "Ejecución",
            "Rastreo y calidad",
            "NLP y clasificación",
            "Búsqueda",
            "Chatbot",
            "Knowledge Graph",
            "Tendencias y alertas",
            "Trazabilidad y entrega",
            "AC11 Usabilidad",
        ],
    )

    if view == "Dashboard":
        view_dashboard()
    elif view == "Ejecución":
        view_ejecucion()
    elif view == "Rastreo y calidad":
        view_rastreo()
    elif view == "NLP y clasificación":
        view_nlp_clasificacion()
    elif view == "Búsqueda":
        view_busqueda()
    elif view == "Chatbot":
        view_chatbot()
    elif view == "Knowledge Graph":
        view_kg()
    elif view == "Tendencias y alertas":
        view_tendencias_alertas()
    elif view == "Trazabilidad y entrega":
        view_trazabilidad_entrega()
    elif view == "AC11 Usabilidad":
        view_ac11()


if __name__ == "__main__":
    main()