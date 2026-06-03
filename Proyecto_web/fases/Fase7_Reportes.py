
"""
SIMANW - Fase 7: Reportes automáticos y entrega final
=====================================================

Objetivo:
    Generar reportes finales automáticamente a partir de los artefactos
    producidos por las fases anteriores del SIMANW.

Integra:
- Dataset analizado.
- Reportes de búsqueda.
- Reportes del chatbot.
- Knowledge Graph RDF.
- Actividades complementarias AC-8, AC-9, AC-10, AC-12 y AC-13 si existen.

Uso:
    python fases/Fase7_Reportes.py

Salidas:
    reportes/reporte_final_simanw.txt
    reportes/reporte_final_simanw.md
    reportes/reporte_final_simanw.json
    entrega_final/resumen_entrega.json
"""

import json
import os
import platform
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

try:
    from rdflib import Graph
except Exception:
    Graph = None


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


class GeneradorReportesSIMANW:
    def __init__(
        self,
        ruta_dataset=None,
        ruta_reporte_txt=None,
        ruta_reporte_md=None,
        ruta_reporte_json=None,
        ruta_entrega=None,
    ):
        self.ruta_dataset = Path(ruta_dataset) if ruta_dataset else ROOT / "datos" / "dataset_analizado.json"
        self.ruta_reporte_txt = Path(ruta_reporte_txt) if ruta_reporte_txt else ROOT / "reportes" / "reporte_final_simanw.txt"
        self.ruta_reporte_md = Path(ruta_reporte_md) if ruta_reporte_md else ROOT / "reportes" / "reporte_final_simanw.md"
        self.ruta_reporte_json = Path(ruta_reporte_json) if ruta_reporte_json else ROOT / "reportes" / "reporte_final_simanw.json"
        self.ruta_entrega = Path(ruta_entrega) if ruta_entrega else ROOT / "entrega_final" / "resumen_entrega.json"

        self.noticias = self._cargar_json(self.ruta_dataset, default=[])
        self.reportes = self._cargar_reportes_disponibles()
        self.triples_kg = self._contar_triples_kg()

    def ejecutar(self):
        resumen = self._crear_resumen_estructurado()
        reporte_txt = self._reporte_texto(resumen)
        reporte_md = self._reporte_markdown(resumen)

        self._guardar_texto(self.ruta_reporte_txt, reporte_txt)
        self._guardar_texto(self.ruta_reporte_md, reporte_md)
        self._guardar_json(self.ruta_reporte_json, resumen)
        self._guardar_json(self.ruta_entrega, self._resumen_entrega(resumen))

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 7 — Reportes automáticos              ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Dataset             : {self.ruta_dataset}")
        print(f"  Noticias procesadas : {len(self.noticias)}")
        print(f"  Triples KG          : {self.triples_kg}")
        print(f"  Categorías          : {len(resumen['distribucion_categorias'])}")
        print(f"  Sentimiento promedio: {resumen['sentimiento']['promedio']:+.3f}")
        print()
        print("  Archivos generados:")
        print("   -", self.ruta_reporte_txt)
        print("   -", self.ruta_reporte_md)
        print("   -", self.ruta_reporte_json)
        print("   -", self.ruta_entrega)

        return resumen

    def _crear_resumen_estructurado(self):
        categorias = Counter(self._categoria(n) for n in self.noticias)
        sentimientos = Counter(self._sentimiento_etiqueta(n) for n in self.noticias)
        fuentes = Counter(n.get("fuente", "fuente_desconocida") for n in self.noticias)
        autores = Counter(n.get("autor", "No identificado") for n in self.noticias)
        scores = [self._sentimiento_score(n) for n in self.noticias if self._sentimiento_score(n) is not None]
        promedio_sent = sum(scores) / len(scores) if scores else 0.0

        noticias_extremas = self._noticias_extremas()
        artefactos = self._artefactos_principales()
        capacidades = self._capacidades_demostradas()

        return {
            "fase": "Fase 7 - Reportes automáticos y entrega final",
            "fecha_generacion": datetime.now().isoformat(timespec="seconds"),
            "raiz_proyecto": str(ROOT),
            "entorno": {
                "python": platform.python_version(),
                "sistema": platform.system(),
                "version_sistema": platform.release(),
            },
            "resumen_ejecutivo": {
                "noticias_procesadas": len(self.noticias),
                "triples_knowledge_graph": self.triples_kg,
                "categorias_detectadas": len(categorias),
                "fuentes_detectadas": len(fuentes),
                "reportes_integrados": list(self.reportes.keys()),
                "artefactos_principales_existentes": sum(1 for a in artefactos if a["existe"]),
            },
            "distribucion_categorias": dict(categorias.most_common()),
            "distribucion_sentimientos": dict(sentimientos.most_common()),
            "distribucion_fuentes": dict(fuentes.most_common(15)),
            "autores_principales": dict(autores.most_common(10)),
            "sentimiento": {
                "promedio": round(promedio_sent, 4),
                "tono_general": self._tono(promedio_sent),
                "noticias_mas_negativas": noticias_extremas["negativas"],
                "noticias_mas_positivas": noticias_extremas["positivas"],
            },
            "busqueda": self._resumen_busqueda(),
            "chatbot": self._resumen_chatbot(),
            "knowledge_graph": self._resumen_kg(),
            "tendencias": self._resumen_tendencias(),
            "alertas": self._resumen_alertas(),
            "control_calidad": self._resumen_control_calidad(),
            "capacidades_demostradas": capacidades,
            "artefactos_principales": artefactos,
            "conclusion_final": self._conclusion_final(categorias, sentimientos, promedio_sent),
        }

    def _reporte_texto(self, resumen):
        lineas = []
        lineas.append("=" * 78)
        lineas.append("  REPORTE AUTOMÁTICO - SISTEMA SIMANW")
        lineas.append(f"  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lineas.append("=" * 78)

        lineas.append("\n1. RESUMEN EJECUTIVO")
        lineas.append("─" * 50)
        ej = resumen["resumen_ejecutivo"]
        lineas.append(f"   Noticias procesadas: {ej['noticias_procesadas']}")
        lineas.append(f"   Triples en Knowledge Graph: {ej['triples_knowledge_graph']}")
        lineas.append(f"   Categorías detectadas: {ej['categorias_detectadas']}")
        lineas.append(f"   Fuentes detectadas: {ej['fuentes_detectadas']}")
        lineas.append(f"   Reportes integrados: {len(ej['reportes_integrados'])}")
        lineas.append(f"   Tono general: {resumen['sentimiento']['tono_general'].upper()}")
        lineas.append(f"   Sentimiento promedio: {resumen['sentimiento']['promedio']:+.3f}")

        lineas.append("\n2. DISTRIBUCIÓN POR CATEGORÍA")
        lineas.append("─" * 50)
        total = max(len(self.noticias), 1)
        for cat, count in resumen["distribucion_categorias"].items():
            pct = 100 * count / total
            barra = "█" * max(1, int(pct / 4))
            lineas.append(f"   {cat:<15} {barra:<25} {count:>4} ({pct:>5.1f}%)")

        lineas.append("\n3. ANÁLISIS DE SENTIMIENTO")
        lineas.append("─" * 50)
        for etiqueta, count in resumen["distribucion_sentimientos"].items():
            icono = "+" if etiqueta == "positivo" else "-" if etiqueta == "negativo" else "~"
            lineas.append(f"   [{icono}] {etiqueta:<12}: {count} noticia(s)")

        lineas.append("\n   Noticias más negativas:")
        for n in resumen["sentimiento"]["noticias_mas_negativas"][:5]:
            lineas.append(f"   [{n['score']:+.3f}] {n['titulo'][:90]}")

        lineas.append("\n   Noticias más positivas:")
        for n in resumen["sentimiento"]["noticias_mas_positivas"][:5]:
            lineas.append(f"   [{n['score']:+.3f}] {n['titulo'][:90]}")

        lineas.append("\n4. BUSCADOR Y CHATBOT")
        lineas.append("─" * 50)
        busq = resumen["busqueda"]
        lineas.append(f"   Modelo ganador AC-5: {busq.get('modelo_ganador', 'N/D')}")
        lineas.append(f"   F1 vectorial: {busq.get('f1_vectorial', 'N/D')}")
        chat = resumen["chatbot"]
        lineas.append(f"   Preguntas demo Fase 5: {chat.get('total_preguntas_demo', 'N/D')}")
        lineas.append(f"   Confianza promedio chatbot: {chat.get('confianza_promedio', 'N/D')}")

        lineas.append("\n5. KNOWLEDGE GRAPH Y WEB SEMÁNTICA")
        lineas.append("─" * 50)
        kg = resumen["knowledge_graph"]
        lineas.append(f"   Triples RDF: {kg.get('triples', 0)}")
        lineas.append(f"   Validación AC-13: {kg.get('validacion_ac13', 'N/D')}")
        lineas.append(f"   Enlaces externos AC-13: {kg.get('enlaces_externos', 'N/D')}")

        lineas.append("\n6. TENDENCIAS Y ALERTAS")
        lineas.append("─" * 50)
        tend = resumen["tendencias"]
        lineas.append(f"   Granularidad AC-9: {tend.get('granularidad', 'N/D')}")
        lineas.append(f"   Periodos analizados: {tend.get('periodos', 'N/D')}")
        alertas = resumen["alertas"]
        lineas.append(f"   Consultas guardadas AC-10: {alertas.get('consultas_guardadas', 'N/D')}")
        lineas.append(f"   Alertas generadas: {alertas.get('alertas_generadas', 'N/D')}")

        lineas.append("\n7. CAPACIDADES DEMOSTRADAS")
        lineas.append("─" * 50)
        for item in resumen["capacidades_demostradas"]:
            estado = "OK" if item["cumplida"] else "PENDIENTE"
            lineas.append(f"   [{estado}] {item['nombre']:<24} → {item['descripcion']}")

        lineas.append("\n8. ARTEFACTOS PRINCIPALES")
        lineas.append("─" * 50)
        for art in resumen["artefactos_principales"]:
            estado = "OK" if art["existe"] else "FALTA"
            lineas.append(f"   [{estado}] {art['ruta']}")

        lineas.append("\n9. CONCLUSIÓN FINAL")
        lineas.append("─" * 50)
        lineas.append("   " + resumen["conclusion_final"])

        lineas.append("\n" + "=" * 78)
        lineas.append("  FIN DEL REPORTE")
        lineas.append("=" * 78)

        return "\n".join(lineas)

    def _reporte_markdown(self, resumen):
        lineas = []
        lineas.append("# Reporte Final Automático - SIMANW")
        lineas.append("")
        lineas.append(f"**Generado:** {resumen['fecha_generacion']}  ")
        lineas.append(f"**Proyecto:** Sistema Inteligente de Monitoreo y Análisis de Noticias Web  ")
        lineas.append("")

        lineas.append("## 1. Resumen ejecutivo")
        ej = resumen["resumen_ejecutivo"]
        lineas.append(f"- Noticias procesadas: **{ej['noticias_procesadas']}**")
        lineas.append(f"- Triples RDF en Knowledge Graph: **{ej['triples_knowledge_graph']}**")
        lineas.append(f"- Categorías detectadas: **{ej['categorias_detectadas']}**")
        lineas.append(f"- Fuentes detectadas: **{ej['fuentes_detectadas']}**")
        lineas.append(f"- Tono general: **{resumen['sentimiento']['tono_general']}**")
        lineas.append(f"- Sentimiento promedio: **{resumen['sentimiento']['promedio']:+.3f}**")
        lineas.append("")

        lineas.append("## 2. Distribución por categoría")
        lineas.append("| Categoría | Noticias |")
        lineas.append("|---|---:|")
        for cat, count in resumen["distribucion_categorias"].items():
            lineas.append(f"| {cat} | {count} |")
        lineas.append("")

        lineas.append("## 3. Análisis de sentimiento")
        lineas.append("| Sentimiento | Noticias |")
        lineas.append("|---|---:|")
        for etiqueta, count in resumen["distribucion_sentimientos"].items():
            lineas.append(f"| {etiqueta} | {count} |")
        lineas.append("")

        lineas.append("### Noticias más negativas")
        for n in resumen["sentimiento"]["noticias_mas_negativas"][:5]:
            lineas.append(f"- **{n['score']:+.3f}** — {n['titulo']}")
        lineas.append("")

        lineas.append("### Noticias más positivas")
        for n in resumen["sentimiento"]["noticias_mas_positivas"][:5]:
            lineas.append(f"- **{n['score']:+.3f}** — {n['titulo']}")
        lineas.append("")

        lineas.append("## 4. Búsqueda y chatbot")
        lineas.append(f"- Modelo ganador en AC-5: **{resumen['busqueda'].get('modelo_ganador', 'N/D')}**")
        lineas.append(f"- F1 vectorial: **{resumen['busqueda'].get('f1_vectorial', 'N/D')}**")
        lineas.append(f"- Preguntas demo Fase 5: **{resumen['chatbot'].get('total_preguntas_demo', 'N/D')}**")
        lineas.append(f"- Confianza promedio chatbot: **{resumen['chatbot'].get('confianza_promedio', 'N/D')}**")
        lineas.append("")

        lineas.append("## 5. Knowledge Graph")
        lineas.append(f"- Triples RDF: **{resumen['knowledge_graph'].get('triples', 0)}**")
        lineas.append(f"- Validación AC-13: **{resumen['knowledge_graph'].get('validacion_ac13', 'N/D')}**")
        lineas.append(f"- Enlaces externos AC-13: **{resumen['knowledge_graph'].get('enlaces_externos', 'N/D')}**")
        lineas.append("")

        lineas.append("## 6. Capacidades demostradas")
        lineas.append("| Estado | Capacidad | Descripción |")
        lineas.append("|---|---|---|")
        for item in resumen["capacidades_demostradas"]:
            estado = "OK" if item["cumplida"] else "Pendiente"
            lineas.append(f"| {estado} | {item['nombre']} | {item['descripcion']} |")
        lineas.append("")

        lineas.append("## 7. Artefactos principales")
        lineas.append("| Estado | Archivo |")
        lineas.append("|---|---|")
        for art in resumen["artefactos_principales"]:
            estado = "OK" if art["existe"] else "FALTA"
            lineas.append(f"| {estado} | `{art['ruta']}` |")
        lineas.append("")

        lineas.append("## 8. Conclusión final")
        lineas.append(resumen["conclusion_final"])
        lineas.append("")

        return "\n".join(lineas)

    def _resumen_entrega(self, resumen):
        return {
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "estado": "entrega_final_generada",
            "noticias": len(self.noticias),
            "triples_kg": self.triples_kg,
            "reportes": {
                "txt": str(self.ruta_reporte_txt),
                "markdown": str(self.ruta_reporte_md),
                "json": str(self.ruta_reporte_json),
            },
            "artefactos_principales": resumen["artefactos_principales"],
        }

    def _cargar_reportes_disponibles(self):
        rutas = {
            "fase4": ROOT / "reportes" / "reporte_fase4_busqueda.json",
            "fase5": ROOT / "reportes" / "reporte_fase5_conversacion.json",
            "fase6": ROOT / "reportes" / "reporte_fase6_kg.json",
            "ac5": ROOT / "reportes" / "ac5_comparador_busqueda.json",
            "ac8": ROOT / "reportes" / "ac8_control_calidad_corpus.json",
            "ac9": ROOT / "reportes" / "ac9_tendencias_temporales.json",
            "ac10": ROOT / "reportes" / "ac10_reporte_alertas.json",
            "ac12": ROOT / "evidencia" / "ac12_manifiesto_ejecucion.json",
            "ac13": ROOT / "knowledge_graph" / "publicacion" / "manifiesto_publicacion.json",
        }

        return {
            nombre: self._cargar_json(ruta, default=None)
            for nombre, ruta in rutas.items()
            if ruta.exists()
        }

    def _contar_triples_kg(self):
        ruta_ttl = ROOT / "knowledge_graph" / "simanw.ttl"
        if not ruta_ttl.exists():
            return 0

        if Graph is None:
            fase6 = self._cargar_json(ROOT / "reportes" / "reporte_fase6_kg.json", default={})
            return fase6.get("total_triples", 0)

        try:
            g = Graph()
            g.parse(str(ruta_ttl), format="turtle")
            return len(g)
        except Exception:
            fase6 = self._cargar_json(ROOT / "reportes" / "reporte_fase6_kg.json", default={})
            return fase6.get("total_triples", 0)

    def _resumen_busqueda(self):
        ac5 = self.reportes.get("ac5", {})
        promedios = ac5.get("promedios", {})
        ganadores = ac5.get("modelos_ganadores") or [ac5.get("modelo_ganador")] if ac5.get("modelo_ganador") else []

        return {
            "modelo_ganador": ", ".join(g for g in ganadores if g) or "N/D",
            "f1_booleano_and": promedios.get("booleano_and", {}).get("f1"),
            "f1_booleano_or": promedios.get("booleano_or", {}).get("f1"),
            "f1_vectorial": promedios.get("vectorial", {}).get("f1"),
            "conclusion": ac5.get("conclusion", ""),
        }

    def _resumen_chatbot(self):
        fase5 = self.reportes.get("fase5", {})
        evaluacion = fase5.get("evaluacion_demo", {})
        return {
            "total_preguntas_demo": evaluacion.get("total_preguntas"),
            "confianza_promedio": evaluacion.get("confianza_promedio"),
            "intenciones_detectadas": evaluacion.get("intenciones_detectadas", {}),
            "capacidades": fase5.get("capacidades", []),
        }

    def _resumen_kg(self):
        fase6 = self.reportes.get("fase6", {})
        ac13 = self.reportes.get("ac13", {})
        validacion = ac13.get("validacion", {})

        return {
            "triples": self.triples_kg or fase6.get("total_triples", 0),
            "consultas_sparql_fase6": len(fase6.get("consultas_sparql", {})),
            "validacion_fase6": fase6.get("validacion", {}),
            "validacion_ac13": "OK" if validacion.get("conforms") else "N/D",
            "enlaces_externos": ac13.get("enlaces_externos_detectados"),
            "serializaciones": ac13.get("serializaciones", {}),
        }

    def _resumen_tendencias(self):
        ac9 = self.reportes.get("ac9", {})
        return {
            "granularidad": ac9.get("granularidad"),
            "periodos": len(ac9.get("periodos", [])) if isinstance(ac9.get("periodos"), list) else None,
            "categorias_analizadas": ac9.get("categorias_analizadas", []),
            "tabla_resumen": ac9.get("tabla_resumen", []),
        }

    def _resumen_alertas(self):
        ac10 = self.reportes.get("ac10", {})
        ejecuciones = ac10.get("ejecuciones", [])
        total_alertas = 0
        for e in ejecuciones:
            total_alertas += len(e.get("alertas_generadas", []))

        return {
            "consultas_guardadas": len(ac10.get("consultas_guardadas", [])),
            "ejecuciones": len(ejecuciones),
            "alertas_generadas": total_alertas,
            "historial": ac10.get("historial_alertas"),
        }

    def _resumen_control_calidad(self):
        ac8 = self.reportes.get("ac8", {})
        return {
            "estadisticas": ac8.get("estadisticas", {}),
            "resumen": ac8.get("resumen_200_palabras", ""),
        }

    def _capacidades_demostradas(self):
        checks = [
            ("Rastreo Web", "Extracción automática y corpus maestro", ROOT / "datos" / "dataset_maestro.json"),
            ("Control de calidad", "Validación y depuración del corpus", ROOT / "reportes" / "ac8_control_calidad_corpus.json"),
            ("NLP", "Procesamiento textual del corpus", ROOT / "datos" / "dataset_nlp.json"),
            ("Clasificación", "Categorización automática", ROOT / "datos" / "dataset_analizado.json"),
            ("Sentimientos", "Análisis de polaridad", ROOT / "datos" / "dataset_analizado.json"),
            ("Búsqueda", "Índice invertido y ranking vectorial", ROOT / "indices" / "indice_invertido.json"),
            ("Evaluación IR", "Comparación booleano vs vectorial", ROOT / "reportes" / "ac5_comparador_busqueda.json"),
            ("Chatbot", "Q&A y conversación", ROOT / "reportes" / "reporte_fase5_conversacion.json"),
            ("Alertas", "Consultas guardadas y deduplicación", ROOT / "reportes" / "ac10_reporte_alertas.json"),
            ("Knowledge Graph", "RDF, ontología y SPARQL", ROOT / "knowledge_graph" / "simanw.ttl"),
            ("Publicación semántica", "Paquete RDF documentado", ROOT / "knowledge_graph" / "publicacion" / "manifiesto_publicacion.json"),
            ("Trazabilidad", "Manifiesto reproducible", ROOT / "evidencia" / "ac12_manifiesto_ejecucion.json"),
            ("Reportes", "Reporte final automático", self.ruta_reporte_json),
        ]

        return [
            {
                "nombre": nombre,
                "descripcion": desc,
                "cumplida": ruta.exists(),
                "artefacto": str(ruta),
            }
            for nombre, desc, ruta in checks
        ]

    def _artefactos_principales(self):
        rutas = [
            "config/fuentes_rss.json",
            "datos/dataset_maestro.json",
            "datos/dataset_nlp.json",
            "datos/dataset_analizado.json",
            "datos/dataset_depurado_ac8.json",
            "indices/indice_invertido.json",
            "indices/metadatos_busqueda.json",
            "reportes/reporte_fase4_busqueda.json",
            "reportes/reporte_fase5_conversacion.json",
            "reportes/reporte_fase6_kg.json",
            "reportes/ac5_comparador_busqueda.json",
            "reportes/ac8_control_calidad_corpus.json",
            "reportes/ac9_tendencias_temporales.json",
            "reportes/ac10_reporte_alertas.json",
            "knowledge_graph/simanw.ttl",
            "knowledge_graph/simanw.rdf",
            "knowledge_graph/simanw.jsonld",
            "knowledge_graph/publicacion/manifiesto_publicacion.json",
            "evidencia/ac12_manifiesto_ejecucion.json",
        ]

        salida = []
        for ruta in rutas:
            path = ROOT / ruta
            salida.append({
                "ruta": ruta,
                "existe": path.exists(),
                "tamano_bytes": path.stat().st_size if path.exists() else 0,
            })
        return salida

    def _noticias_extremas(self):
        noticias_con_score = []
        for n in self.noticias:
            score = self._sentimiento_score(n)
            if score is None:
                continue
            noticias_con_score.append({
                "titulo": n.get("titulo", "Sin título"),
                "categoria": self._categoria(n),
                "score": round(score, 4),
                "url": n.get("url", ""),
            })

        ordenadas = sorted(noticias_con_score, key=lambda x: x["score"])
        return {
            "negativas": ordenadas[:10],
            "positivas": list(reversed(ordenadas[-10:])),
        }

    def _conclusion_final(self, categorias, sentimientos, promedio_sent):
        if not self.noticias:
            return "No se encontraron noticias procesadas para generar una conclusión final."

        cat_top = categorias.most_common(1)[0][0] if categorias else "sin categoría dominante"
        sent_top = sentimientos.most_common(1)[0][0] if sentimientos else "sin sentimiento dominante"
        tono = self._tono(promedio_sent)

        return (
            f"El sistema SIMANW procesó {len(self.noticias)} noticias y consolidó un flujo completo "
            f"de recuperación web, NLP, análisis, búsqueda, conversación, Knowledge Graph y reportes. "
            f"La categoría con mayor presencia fue {cat_top}, mientras que el sentimiento más frecuente fue "
            f"{sent_top}. El tono promedio del corpus se clasificó como {tono}. "
            f"Además, el grafo semántico generado contiene {self.triples_kg} triples RDF, lo que permite consultar "
            f"las noticias mediante SPARQL y reutilizarlas como datos enlazados. La integración de reportes, "
            f"alertas, evaluación de búsqueda y trazabilidad demuestra que el proyecto es funcional, auditable "
            f"y preparado para una interfaz gráfica final."
        )

    def _categoria(self, noticia):
        return (
            noticia.get("categoria_predicha")
            or noticia.get("categoria")
            or noticia.get("categoria_original")
            or "general"
        )

    def _sentimiento_etiqueta(self, noticia):
        sent = noticia.get("sentimiento", {})
        if isinstance(sent, dict):
            return sent.get("etiqueta", "desconocido")
        return str(sent or "desconocido")

    def _sentimiento_score(self, noticia):
        sent = noticia.get("sentimiento", {})
        if isinstance(sent, dict) and "compound" in sent:
            try:
                return float(sent["compound"])
            except Exception:
                return None
        return None

    def _tono(self, score):
        if score > 0.05:
            return "positivo"
        if score < -0.05:
            return "negativo"
        return "neutral"

    def _cargar_json(self, ruta, default):
        ruta = Path(ruta)
        if not ruta.exists():
            return default

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

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
    GeneradorReportesSIMANW().ejecutar()
