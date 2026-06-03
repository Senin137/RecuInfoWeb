
"""
SIMANW - AC-12: Trazabilidad y reproducibilidad del pipeline
============================================================

Complemento de Fases 1-7.

Objetivo:
    Demostrar que el SIMANW es reproducible y trazable: qué datos entraron,
    qué versión del entorno se usó y qué artefactos se generaron.

Cumple:
- Manifiesto por ejecución.
- Fecha y hora.
- Versión del proyecto.
- Fuente de noticias.
- Número de documentos por etapa.
- Referencias a archivos principales.
- Log estructurado del pipeline completo.
- Procedimiento reproducible documentado.
- Checklist firmado por el alumno.
- Anexo de limitaciones conocidas.

Uso:
    python fases/AC12_TrazabilidadPipeline.py

Salidas:
    evidencia/ac12_manifiesto_ejecucion.json
    evidencia/ac12_log_pipeline.json
    evidencia/ac12_procedimiento_reproduccion.md
    evidencia/ac12_checklist.md
    evidencia/ac12_limitaciones.md
"""

import json
import os
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from rdflib import Graph
except Exception:
    Graph = None


ALUMNO = "Eladio Martinez Ambriz"
VERSION_PROYECTO = "SIMANW 1.0 - Enero Junio 2026"


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


class InspectorArtefactos:
    def __init__(self, root):
        self.root = Path(root)

    def inspeccionar_archivo(self, ruta_relativa):
        ruta = self.root / ruta_relativa
        info = {
            "ruta": ruta_relativa,
            "existe": ruta.exists(),
            "tamano_bytes": ruta.stat().st_size if ruta.exists() else 0,
            "modificado": datetime.fromtimestamp(ruta.stat().st_mtime).isoformat(timespec="seconds") if ruta.exists() else None,
        }

        if ruta.exists() and ruta.suffix.lower() == ".json":
            info.update(self._info_json(ruta))

        if ruta.exists() and ruta.suffix.lower() in {".ttl", ".rdf", ".xml", ".jsonld"}:
            info.update(self._info_rdf(ruta))

        return info

    def _info_json(self, ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return {
                    "tipo_contenido": "lista_json",
                    "registros": len(data),
                }

            if isinstance(data, dict):
                return {
                    "tipo_contenido": "objeto_json",
                    "claves_principales": list(data.keys())[:20],
                    "registros": self._inferir_registros_dict(data),
                }

            return {"tipo_contenido": type(data).__name__}
        except Exception as exc:
            return {
                "tipo_contenido": "json_no_leible",
                "error_lectura": str(exc),
            }

    def _inferir_registros_dict(self, data):
        posibles = [
            "total_noticias",
            "noticias",
            "documentos",
            "documentos_indexados",
            "total_registros",
            "validos",
        ]

        for clave in posibles:
            valor = data.get(clave)
            if isinstance(valor, int):
                return valor
            if isinstance(valor, list):
                return len(valor)

        if "info_indice" in data and isinstance(data["info_indice"], dict):
            return data["info_indice"].get("documentos_indexados") or data["info_indice"].get("documentos")

        if "estadisticas" in data and isinstance(data["estadisticas"], dict):
            return data["estadisticas"].get("total_registros")

        return None

    def _info_rdf(self, ruta):
        if Graph is None:
            return {
                "tipo_contenido": "rdf",
                "triples": None,
                "nota": "rdflib no disponible para contar triples.",
            }

        formato = self._formato_rdf(ruta)
        try:
            g = Graph()
            g.parse(str(ruta), format=formato)
            return {
                "tipo_contenido": "rdf",
                "formato_rdf": formato,
                "triples": len(g),
            }
        except Exception as exc:
            return {
                "tipo_contenido": "rdf_no_leible",
                "formato_rdf": formato,
                "triples": None,
                "error_lectura": str(exc),
            }

    def _formato_rdf(self, ruta):
        sufijo = ruta.suffix.lower()
        if sufijo == ".ttl":
            return "turtle"
        if sufijo in {".rdf", ".xml"}:
            return "xml"
        if sufijo == ".jsonld":
            return "json-ld"
        return None


class AC12TrazabilidadPipeline:
    def __init__(self, root=None):
        self.root = Path(root) if root else ROOT
        self.evidencia = self.root / "evidencia"
        self.inspector = InspectorArtefactos(self.root)

        self.ruta_manifiesto = self.evidencia / "ac12_manifiesto_ejecucion.json"
        self.ruta_log = self.evidencia / "ac12_log_pipeline.json"
        self.ruta_procedimiento = self.evidencia / "ac12_procedimiento_reproduccion.md"
        self.ruta_checklist = self.evidencia / "ac12_checklist.md"
        self.ruta_limitaciones = self.evidencia / "ac12_limitaciones.md"

    def ejecutar(self):
        self.evidencia.mkdir(parents=True, exist_ok=True)

        artefactos = self._inspeccionar_artefactos()
        manifiesto = self._crear_manifiesto(artefactos)
        log_pipeline = self._crear_log_pipeline(artefactos)
        procedimiento = self._crear_procedimiento()
        checklist = self._crear_checklist(artefactos)
        limitaciones = self._crear_limitaciones()

        self._guardar_json(self.ruta_manifiesto, manifiesto)
        self._guardar_json(self.ruta_log, log_pipeline)
        self._guardar_texto(self.ruta_procedimiento, procedimiento)
        self._guardar_texto(self.ruta_checklist, checklist)
        self._guardar_texto(self.ruta_limitaciones, limitaciones)

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-12 — Trazabilidad y reproducibilidad    ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Alumno          : {ALUMNO}")
        print(f"  Raíz proyecto   : {self.root}")
        print(f"  Versión         : {VERSION_PROYECTO}")
        print(f"  Python          : {platform.python_version()}")
        print(f"  Sistema         : {platform.system()} {platform.release()}")
        print()

        print("  Artefactos principales:")
        for nombre, info in artefactos.items():
            estado = "OK" if info["existe"] else "FALTA"
            extra = ""
            if info.get("registros") is not None:
                extra = f" | registros={info['registros']}"
            if info.get("triples") is not None:
                extra = f" | triples={info['triples']}"
            print(f"   - [{estado}] {info['ruta']}{extra}")

        print()
        print("  Log estructurado:")
        for paso in log_pipeline["pasos"]:
            print(f"   - {paso['fase']}: {paso['estado']} → {paso['artefacto_principal']}")

        print()
        print("  Archivos generados:")
        print("   -", self.ruta_manifiesto)
        print("   -", self.ruta_log)
        print("   -", self.ruta_procedimiento)
        print("   -", self.ruta_checklist)
        print("   -", self.ruta_limitaciones)

        return {
            "manifiesto": manifiesto,
            "log_pipeline": log_pipeline,
            "archivos": {
                "manifiesto": str(self.ruta_manifiesto),
                "log": str(self.ruta_log),
                "procedimiento": str(self.ruta_procedimiento),
                "checklist": str(self.ruta_checklist),
                "limitaciones": str(self.ruta_limitaciones),
            }
        }

    def _inspeccionar_artefactos(self):
        rutas = {
            "fuentes_rss": "config/fuentes_rss.json",
            "dataset_maestro": "datos/dataset_maestro.json",
            "dataset_nlp": "datos/dataset_nlp.json",
            "dataset_analizado": "datos/dataset_analizado.json",
            "dataset_depurado_ac8": "datos/dataset_depurado_ac8.json",
            "rastreo_paginado_ac1": "datos/ac1_rastreo_paginado.json",
            "indice_invertido": "indices/indice_invertido.json",
            "metadata_busqueda": "indices/metadatos_busqueda.json",
            "reporte_fase4": "reportes/reporte_fase4_busqueda.json",
            "reporte_fase5": "reportes/reporte_fase5_conversacion.json",
            "reporte_fase6": "reportes/reporte_fase6_kg.json",
            "reporte_ac5": "reportes/ac5_comparador_busqueda.json",
            "reporte_ac8": "reportes/ac8_control_calidad_corpus.json",
            "reporte_ac9": "reportes/ac9_tendencias_temporales.json",
            "reporte_ac10": "reportes/ac10_reporte_alertas.json",
            "grafo_ttl": "knowledge_graph/simanw.ttl",
            "grafo_rdf": "knowledge_graph/simanw.rdf",
            "grafo_jsonld": "knowledge_graph/simanw.jsonld",
        }

        return {
            nombre: self.inspector.inspeccionar_archivo(ruta)
            for nombre, ruta in rutas.items()
        }

    def _crear_manifiesto(self, artefactos):
        return {
            "actividad": "AC-12 Trazabilidad y reproducibilidad del pipeline",
            "alumno": ALUMNO,
            "fecha_ejecucion": datetime.now().isoformat(timespec="seconds"),
            "version_proyecto": VERSION_PROYECTO,
            "version_python": platform.python_version(),
            "ejecutable_python": sys.executable,
            "sistema_operativo": {
                "sistema": platform.system(),
                "version": platform.release(),
                "arquitectura": platform.machine(),
            },
            "git": self._git_info(),
            "fuentes_noticias": self._fuentes_noticias(artefactos),
            "conteo_documentos_por_etapa": {
                "fase_1_dataset_maestro": artefactos["dataset_maestro"].get("registros"),
                "fase_2_dataset_nlp": artefactos["dataset_nlp"].get("registros"),
                "fase_3_dataset_analizado": artefactos["dataset_analizado"].get("registros"),
                "ac8_dataset_depurado": artefactos["dataset_depurado_ac8"].get("registros"),
                "ac1_rastreo_paginado": artefactos["rastreo_paginado_ac1"].get("registros"),
            },
            "knowledge_graph": {
                "ttl": artefactos["grafo_ttl"],
                "rdf": artefactos["grafo_rdf"],
                "jsonld": artefactos["grafo_jsonld"],
                "triples_detectados": (
                    artefactos["grafo_ttl"].get("triples")
                    or artefactos["grafo_rdf"].get("triples")
                    or artefactos["grafo_jsonld"].get("triples")
                ),
            },
            "artefactos": artefactos,
        }

    def _crear_log_pipeline(self, artefactos):
        pasos = [
            {
                "fase": "Fase 1",
                "nombre": "Rastreo de noticias",
                "script": "fases/Fase1_Rastreador.py",
                "artefacto_principal": "datos/dataset_maestro.json",
                "estado": self._estado_archivo(artefactos["dataset_maestro"]),
                "documentos": artefactos["dataset_maestro"].get("registros"),
            },
            {
                "fase": "AC-1",
                "nombre": "Rastreo real con paginación",
                "script": "fases/AC1_RastreadorPaginado.py",
                "artefacto_principal": "datos/ac1_rastreo_paginado.json",
                "estado": self._estado_archivo(artefactos["rastreo_paginado_ac1"]),
                "documentos": artefactos["rastreo_paginado_ac1"].get("registros"),
            },
            {
                "fase": "AC-8",
                "nombre": "Control de calidad del corpus",
                "script": "fases/AC8_ControlCalidadCorpus.py",
                "artefacto_principal": "datos/dataset_depurado_ac8.json",
                "estado": self._estado_archivo(artefactos["dataset_depurado_ac8"]),
                "documentos": artefactos["dataset_depurado_ac8"].get("registros"),
            },
            {
                "fase": "Fase 2",
                "nombre": "Procesamiento NLP",
                "script": "fases/Fase2_Pipeline.py",
                "artefacto_principal": "datos/dataset_nlp.json",
                "estado": self._estado_archivo(artefactos["dataset_nlp"]),
                "documentos": artefactos["dataset_nlp"].get("registros"),
            },
            {
                "fase": "Fase 3",
                "nombre": "Clasificación y análisis",
                "script": "fases/Fase3_Clasificador.py",
                "artefacto_principal": "datos/dataset_analizado.json",
                "estado": self._estado_archivo(artefactos["dataset_analizado"]),
                "documentos": artefactos["dataset_analizado"].get("registros"),
            },
            {
                "fase": "Fase 4",
                "nombre": "Motor de búsqueda",
                "script": "fases/Fase4_Busqueda.py",
                "artefacto_principal": "indices/indice_invertido.json",
                "estado": self._estado_archivo(artefactos["indice_invertido"]),
                "documentos": artefactos["metadata_busqueda"].get("registros"),
            },
            {
                "fase": "Fase 5",
                "nombre": "Chatbot y Q&A",
                "script": "fases/Fase5_Conversacion.py",
                "artefacto_principal": "reportes/reporte_fase5_conversacion.json",
                "estado": self._estado_archivo(artefactos["reporte_fase5"]),
                "documentos": artefactos["reporte_fase5"].get("registros"),
            },
            {
                "fase": "Fase 6",
                "nombre": "Knowledge Graph semántico",
                "script": "fases/Fase6_KnowledgeGraph.py",
                "artefacto_principal": "knowledge_graph/simanw.ttl",
                "estado": self._estado_archivo(artefactos["grafo_ttl"]),
                "triples": artefactos["grafo_ttl"].get("triples"),
            },
            {
                "fase": "AC-9",
                "nombre": "Línea de tiempo y tendencias",
                "script": "fases/AC9_LineaTiempoTendencias.py",
                "artefacto_principal": "reportes/ac9_tendencias_temporales.json",
                "estado": self._estado_archivo(artefactos["reporte_ac9"]),
            },
            {
                "fase": "AC-10",
                "nombre": "Alertas por consulta guardada",
                "script": "fases/AC10_SistemaAlertas.py",
                "artefacto_principal": "reportes/ac10_reporte_alertas.json",
                "estado": self._estado_archivo(artefactos["reporte_ac10"]),
            },
        ]

        return {
            "actividad": "AC-12 Log estructurado del pipeline",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "alumno": ALUMNO,
            "pasos": pasos,
        }

    def _crear_procedimiento(self):
        return f"""# AC-12: Procedimiento de reproducción del SIMANW

**Alumno:** {ALUMNO}  
**Proyecto:** {VERSION_PROYECTO}  
**Fecha de generación:** {datetime.now().isoformat(timespec="seconds")}

## 1. Preparar entorno

Desde la raíz del proyecto:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Si no existe `requirements.txt`, instalar las dependencias base:

```bash
pip install nltk scikit-learn numpy pandas beautifulsoup4 requests scrapy rdflib SPARQLWrapper transformers matplotlib
```

## 2. Datos de entrada versionados

El pipeline puede reproducirse usando los archivos incluidos en la carpeta `datos/` y la configuración en `config/`.

Archivos principales:

```txt
config/fuentes_rss.json
datos/dataset_maestro.json
datos/dataset_nlp.json
datos/dataset_analizado.json
```

## 3. Ejecutar fases principales

```bash
python fases/Fase1_Rastreador.py
python fases/Fase2_Pipeline.py
python fases/Fase3_Clasificador.py
python fases/Fase4_Busqueda.py
python fases/Fase5_Conversacion.py
python fases/Fase6_KnowledgeGraph.py
```

## 4. Ejecutar actividades complementarias

```bash
python fases/AC1_RastreadorPaginado.py
python fases/AC2_AnalisisDiscurso.py
python fases/AC3_SelectorMultimodelo.py
python fases/AC4_AnalisisHilos.py
python fases/AC5_ComparadorBusqueda.py
python fases/AC6_ChatbotContextual.py
python fases/AC8_ControlCalidadCorpus.py
python fases/AC9_LineaTiempoTendencias.py
python fases/AC10_SistemaAlertas.py
python fases/AC12_TrazabilidadPipeline.py
python fases/AC13_PublicacionSemantica.py
```

## 5. Artefactos esperados

```txt
datos/dataset_maestro.json
datos/dataset_nlp.json
datos/dataset_analizado.json
indices/indice_invertido.json
reportes/reporte_fase5_conversacion.json
knowledge_graph/simanw.ttl
knowledge_graph/simanw.rdf
knowledge_graph/simanw.jsonld
evidencia/ac12_manifiesto_ejecucion.json
```

## 6. Criterio de reproducibilidad

La ejecución es reproducible si, usando los mismos datos de entrada versionados, se generan los mismos archivos principales y se mantiene el mismo número de documentos por etapa. Las fases que consultan Internet pueden variar por cambios externos; por eso se recomienda conservar copias JSON de los datos rastreados.
"""

    def _crear_checklist(self, artefactos):
        items = [
            ("Fuente RSS configurada", artefactos["fuentes_rss"]["existe"]),
            ("Dataset maestro generado", artefactos["dataset_maestro"]["existe"]),
            ("Dataset NLP generado", artefactos["dataset_nlp"]["existe"]),
            ("Dataset analizado generado", artefactos["dataset_analizado"]["existe"]),
            ("Corpus depurado AC-8 generado", artefactos["dataset_depurado_ac8"]["existe"]),
            ("Rastreo paginado AC-1 generado", artefactos["rastreo_paginado_ac1"]["existe"]),
            ("Índice invertido generado", artefactos["indice_invertido"]["existe"]),
            ("Reporte de Fase 5 generado", artefactos["reporte_fase5"]["existe"]),
            ("Reporte de Fase 6 generado", artefactos["reporte_fase6"]["existe"]),
            ("Knowledge Graph TTL generado", artefactos["grafo_ttl"]["existe"]),
            ("Knowledge Graph RDF/XML generado", artefactos["grafo_rdf"]["existe"]),
            ("Knowledge Graph JSON-LD generado", artefactos["grafo_jsonld"]["existe"]),
            ("Reporte AC-9 generado", artefactos["reporte_ac9"]["existe"]),
            ("Reporte AC-10 generado", artefactos["reporte_ac10"]["existe"]),
        ]

        lineas = [
            "# AC-12: Checklist firmado de ejecución",
            "",
            f"**Alumno:** {ALUMNO}",
            f"**Proyecto:** {VERSION_PROYECTO}",
            f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Pasos y artefactos verificados",
            "",
        ]

        for texto, ok in items:
            marca = "X" if ok else " "
            lineas.append(f"- [{marca}] {texto}")

        lineas.extend([
            "",
            "## Firma",
            "",
            f"Alumno: **{ALUMNO}**",
            "",
            "Firma: ________________________________",
            "",
        ])

        return "\n".join(lineas)

    def _crear_limitaciones(self):
        return f"""# AC-12: Anexo de limitaciones conocidas

**Alumno:** {ALUMNO}  
**Proyecto:** {VERSION_PROYECTO}

## Limitaciones técnicas

1. **Cambios en sitios rastreados:** los portales de noticias pueden modificar su estructura HTML, sus selectores, su paginación o su archivo `robots.txt`, lo que puede afectar el rastreo real.
2. **Dependencia de conexión a Internet:** las fases que consultan RSS, sitios web o endpoints externos dependen de la disponibilidad de red.
3. **Disponibilidad de fuentes externas:** servicios como Wikidata, DBpedia o portales de datos abiertos pueden limitar peticiones, cambiar respuestas o estar temporalmente fuera de servicio.
4. **Variación temporal del corpus:** si se vuelve a rastrear en otra fecha, las noticias disponibles pueden cambiar. Por eso se conservan datasets JSON versionados.
5. **Calidad de los textos rastreados:** algunas noticias pueden tener cuerpos cortos, metadatos incompletos o contenido duplicado.
6. **Clasificación automática:** los modelos de clasificación dependen de los datos de entrenamiento y pueden cometer errores en noticias ambiguas o multitemáticas.
7. **Análisis de sentimiento:** VADER y técnicas léxicas pueden no capturar ironía, sarcasmo o contexto político complejo.
8. **Knowledge Graph:** los enlaces semánticos externos pueden ser aproximados y requieren revisión si se usa el sistema en producción.

## Mitigaciones aplicadas

- Se genera un corpus depurado con AC-8.
- Se guarda historial de alertas para evitar duplicados en AC-10.
- Se exportan artefactos RDF en varios formatos.
- Se registra un manifiesto por ejecución con versiones, archivos y conteos.
- Se conserva un procedimiento reproducible para ejecutar el pipeline desde datos versionados.
"""

    def _fuentes_noticias(self, artefactos):
        ruta = self.root / "config" / "fuentes_rss.json"

        if not ruta.exists():
            return {
                "archivo": "config/fuentes_rss.json",
                "existe": False,
                "fuentes": [],
            }

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)

            fuentes = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        fuentes.append(item.get("nombre") or item.get("name") or item.get("url") or "fuente_sin_nombre")
                    else:
                        fuentes.append(str(item))
            elif isinstance(data, dict):
                for clave, valor in data.items():
                    if isinstance(valor, list):
                        fuentes.extend([str(v.get("nombre", v.get("url", clave))) if isinstance(v, dict) else str(v) for v in valor])
                    else:
                        fuentes.append(str(clave))

            return {
                "archivo": "config/fuentes_rss.json",
                "existe": True,
                "total_fuentes_detectadas": len(fuentes),
                "fuentes": fuentes[:30],
            }
        except Exception as exc:
            return {
                "archivo": "config/fuentes_rss.json",
                "existe": True,
                "error": str(exc),
                "fuentes": [],
            }

    def _git_info(self):
        try:
            commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=self.root, stderr=subprocess.DEVNULL).decode().strip()
            branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=self.root, stderr=subprocess.DEVNULL).decode().strip()
            dirty = subprocess.call(["git", "diff", "--quiet"], cwd=self.root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0
            return {
                "disponible": True,
                "commit": commit,
                "branch": branch,
                "cambios_sin_commit": dirty,
            }
        except Exception:
            return {
                "disponible": False,
                "nota": "No se detectó repositorio Git o Git no está disponible.",
            }

    def _estado_archivo(self, info):
        return "OK" if info.get("existe") else "FALTA"

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
    AC12TrazabilidadPipeline().ejecutar()
