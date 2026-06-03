# Reporte Final Automático - SIMANW

**Generado:** 2026-06-03T02:54:03  
**Proyecto:** Sistema Inteligente de Monitoreo y Análisis de Noticias Web  

## 1. Resumen ejecutivo
- Noticias procesadas: **1364**
- Triples RDF en Knowledge Graph: **35444**
- Categorías detectadas: **6**
- Fuentes detectadas: **31**
- Tono general: **negativo**
- Sentimiento promedio: **-0.056**

## 2. Distribución por categoría
| Categoría | Noticias |
|---|---:|
| ciencia | 309 |
| economia | 295 |
| tecnologia | 293 |
| deportes | 263 |
| gobierno | 127 |
| mundo | 77 |

## 3. Análisis de sentimiento
| Sentimiento | Noticias |
|---|---:|
| neutral | 727 |
| negativo | 360 |
| positivo | 277 |

### Noticias más negativas
- **-0.995** — Tras probarlos, los expertos de Xataka coinciden: estos son los mejores móviles de 2026
- **-0.989** — El problema no es que los cargos intermedios se estén jubilando en masa. Es que la generación Z no quiere su puesto
- **-0.987** — Estamos obsesionados con el magnesio como suplemento a la dieta. Su "sobredosis" tiene un nombre: hipermagnesemia
- **-0.986** — ‘Minecraft’ no parece el mejor sitio para calcular pi: dos investigadores han encontrado cómo aproximarlo dentro del juego
- **-0.986** — iPhone 18 Pro y iPhone 18 Pro Max: todo lo que creemos saber sobre los nuevos móviles de Apple

### Noticias más positivas
- **+0.920** — La presa Hoover, una maravilla de la ingeniería vista en 3D detalle a detalle
- **+0.872** — "Con todo el respeto para los colegas y las autoridades, creo que la última jornada fue un poco rara"
- **+0.866** — El CEO de Randstad afirma que el teletrabajo ahora se reserva solo para talentos "muy especiales" y explica quién tiene este perfil
- **+0.856** — Esta versión de Microsoft Office dejará de funcionar muy pronto: adiós a usar Word, Excel o PowerPoint aunque hayas pagado
- **+0.852** — Un cohete New Glenn explota en la plataforma de lanzamiento durante una prueba de encendido de sus motores

## 4. Búsqueda y chatbot
- Modelo ganador en AC-5: **N/D**
- F1 vectorial: **0.2452**
- Preguntas demo Fase 5: **8**
- Confianza promedio chatbot: **0.6752**

## 5. Knowledge Graph
- Triples RDF: **35444**
- Validación AC-13: **OK**
- Enlaces externos AC-13: **10**

## 6. Capacidades demostradas
| Estado | Capacidad | Descripción |
|---|---|---|
| OK | Rastreo Web | Extracción automática y corpus maestro |
| OK | Control de calidad | Validación y depuración del corpus |
| OK | NLP | Procesamiento textual del corpus |
| OK | Clasificación | Categorización automática |
| OK | Sentimientos | Análisis de polaridad |
| OK | Búsqueda | Índice invertido y ranking vectorial |
| OK | Evaluación IR | Comparación booleano vs vectorial |
| OK | Chatbot | Q&A y conversación |
| OK | Alertas | Consultas guardadas y deduplicación |
| OK | Knowledge Graph | RDF, ontología y SPARQL |
| OK | Publicación semántica | Paquete RDF documentado |
| OK | Trazabilidad | Manifiesto reproducible |
| OK | Reportes | Reporte final automático |

## 7. Artefactos principales
| Estado | Archivo |
|---|---|
| OK | `config/fuentes_rss.json` |
| OK | `datos/dataset_maestro.json` |
| OK | `datos/dataset_nlp.json` |
| OK | `datos/dataset_analizado.json` |
| OK | `datos/dataset_depurado_ac8.json` |
| OK | `indices/indice_invertido.json` |
| OK | `indices/metadatos_busqueda.json` |
| OK | `reportes/reporte_fase4_busqueda.json` |
| OK | `reportes/reporte_fase5_conversacion.json` |
| OK | `reportes/reporte_fase6_kg.json` |
| OK | `reportes/ac5_comparador_busqueda.json` |
| OK | `reportes/ac8_control_calidad_corpus.json` |
| OK | `reportes/ac9_tendencias_temporales.json` |
| OK | `reportes/ac10_reporte_alertas.json` |
| OK | `knowledge_graph/simanw.ttl` |
| OK | `knowledge_graph/simanw.rdf` |
| OK | `knowledge_graph/simanw.jsonld` |
| OK | `knowledge_graph/publicacion/manifiesto_publicacion.json` |
| OK | `evidencia/ac12_manifiesto_ejecucion.json` |

## 8. Conclusión final
El sistema SIMANW procesó 1364 noticias y consolidó un flujo completo de recuperación web, NLP, análisis, búsqueda, conversación, Knowledge Graph y reportes. La categoría con mayor presencia fue ciencia, mientras que el sentimiento más frecuente fue neutral. El tono promedio del corpus se clasificó como negativo. Además, el grafo semántico generado contiene 35444 triples RDF, lo que permite consultar las noticias mediante SPARQL y reutilizarlas como datos enlazados. La integración de reportes, alertas, evaluación de búsqueda y trazabilidad demuestra que el proyecto es funcional, auditable y preparado para una interfaz gráfica final.
