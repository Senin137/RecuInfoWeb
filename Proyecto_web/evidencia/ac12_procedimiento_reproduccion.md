# AC-12: Procedimiento de reproducción del SIMANW

**Alumno:** Eladio Martinez Ambriz  
**Proyecto:** SIMANW 1.0 - Enero Junio 2026  
**Fecha de generación:** 2026-06-03T02:44:57

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
