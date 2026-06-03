"""
SIMANW - Sistema Inteligente de Monitoreo y Análisis de Noticias Web
=====================================================================
FASE 1: Rastreador de Noticias vía RSS

Descripción:
    Este módulo construye el pipeline de entrada del sistema. Su responsabilidad
    es conectarse a feeds RSS de portales de noticias, extraer artículos de forma
    estructurada, validar su calidad y consolidar un dataset maestro listo para
    el procesamiento NLP de las fases siguientes.

    Se eligió RSS sobre scraping directo por tres razones:
      1. Los portales ofrecen RSS precisamente para ser leídos por máquinas.
      2. Elimina el riesgo de baneo por comportamiento de bot.
      3. Los datos ya vienen semi-estructurados (título, fecha, autor, resumen).

Componentes:
    - ParserDOM        : Demuestra la navegación del DOM con BeautifulSoup (1.1)
    - FiltroCalidad    : Valida y descarta noticias de baja calidad (1.2)
    - ControlRastreo   : Administra el alcance y límites del rastreo (1.3)
    - RastreadorRSS    : Orquesta la extracción completa del pipeline (1.4)

Uso:
    python fase1_rastreador.py
"""

# ── Imports ──────────────────────────────────────────────────────────────────
import json
import re
import os
import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse
from collections import deque
from bs4 import BeautifulSoup


# ═════════════════════════════════════════════════════════════════════════════
# 1.1  PARSER DEL DOM
#      Muestra cómo navegar la jerarquía HTML de un portal de noticias.
#      En el pipeline real los datos vienen de RSS; este componente sirve
#      para entender la estructura subyacente de los portales.
# ═════════════════════════════════════════════════════════════════════════════

HTML_DEMO = """
<!DOCTYPE html>
<html>
<head><title>Portal de Noticias - SIMANW</title></head>
<body>
  <nav>
    <a href="/">Inicio</a>
    <a href="/tech">Tecnología</a>
    <a href="/ciencia">Ciencia</a>
  </nav>
  <main id="contenido">
    <h1>Últimas Noticias</h1>
    <article class="noticia" data-categoria="tecnologia">
      <h2>Avances en IA Generativa revolucionan la industria</h2>
      <p class="cuerpo">Los nuevos modelos de inteligencia artificial generativa
      están transformando múltiples industrias. Empresas de todo el mundo adoptan
      estas tecnologías para automatizar procesos creativos y analíticos.</p>
      <div class="meta">
        <span class="fecha">2026-05-10</span>
        <span class="autor">María García</span>
        <a href="/noticias/ia-generativa-2026" class="leer-mas">Leer más</a>
      </div>
    </article>
    <article class="noticia" data-categoria="economia">
      <h2>Mercados financieros muestran volatilidad ante incertidumbre global</h2>
      <p class="cuerpo">Los principales índices bursátiles registraron caídas
      significativas. Analistas señalan que la inflación persistente y las
      tensiones geopolíticas generan preocupación entre los inversores.</p>
      <div class="meta">
        <span class="fecha">2026-05-09</span>
        <span class="autor">Carlos Ruiz</span>
        <a href="/noticias/mercados-volatilidad" class="leer-mas">Leer más</a>
      </div>
    </article>
  </main>
  <aside>
    <h3>Tendencias</h3>
    <ul>
      <li><a href="/trend/1">#InteligenciaArtificial</a></li>
      <li><a href="/trend/2">#Python</a></li>
    </ul>
  </aside>
</body>
</html>
"""


class ParserDOM:
    """
    Navega y analiza la estructura jerárquica de un documento HTML.

    Aunque el SIMANW usa RSS como fuente principal, entender el DOM
    es fundamental para comprender cómo están organizados los portales
    y para casos donde se requiera scraping complementario.
    """

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'html.parser')

    def extraer_articulos(self) -> list[dict]:
        """Extrae artículos estructurados desde el árbol DOM."""
        articulos = []
        for art in self.soup.find_all('article', class_='noticia'):
            try:
                articulos.append({
                    'titulo':    art.find('h2').get_text(strip=True),
                    'cuerpo':    art.find('p', class_='cuerpo').get_text(strip=True),
                    'fecha':     art.find('span', class_='fecha').get_text(strip=True),
                    'autor':     art.find('span', class_='autor').get_text(strip=True),
                    'categoria': art.get('data-categoria', 'general'),
                    'url':       art.find('a', class_='leer-mas')['href'],
                })
            except (AttributeError, TypeError):
                continue  # Artículo incompleto, se ignora
        return articulos

    def mapa_estructura(self) -> dict:
        """Devuelve un resumen de la estructura del documento."""
        return {
            'titulo':      self.soup.title.string if self.soup.title else 'Sin título',
            'navegacion':  [a.get_text() for a in self.soup.nav.find_all('a')] if self.soup.nav else [],
            'articulos':   len(self.soup.find_all('article')),
            'tendencias':  [li.get_text() for li in self.soup.select('aside li')] if self.soup.aside else [],
        }

    def mostrar_demo(self):
        mapa = self.mapa_estructura()
        arts = self.extraer_articulos()

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 1.1 — Parser del DOM                  ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Portal        : {mapa['titulo']}")
        print(f"  Navegación    : {mapa['navegacion']}")
        print(f"  Tendencias    : {mapa['tendencias']}")
        print(f"  Artículos DOM : {mapa['articulos']}\n")

        for i, a in enumerate(arts, 1):
            print(f"  [{i}] [{a['categoria']}] {a['titulo']}")
            print(f"       {a['fecha']} · {a['autor']}\n")


# ═════════════════════════════════════════════════════════════════════════════
# 1.2  FILTRO DE CALIDAD
#      Evalúa cada noticia candidata antes de incorporarla al corpus.
#      Descarta duplicados, contenido vacío, URLs inválidas y artículos
#      caducados (si el filtro de tiempo está activo).
# ═════════════════════════════════════════════════════════════════════════════

class FiltroCalidad:
    """
    Valida la integridad de cada noticia antes de incorporarla al corpus.

    Reglas de validación:
      1. Todos los campos críticos deben estar presentes.
      2. El cuerpo debe tener al menos MIN_CUERPO caracteres.
      3. La URL debe tener formato válido (http/https).
      4. No se admiten duplicados (por URL ni por título).
      5. Opcional: noticias mayores a MESES_LIMITE meses son descartadas.

    Args:
        filtro_tiempo  : Activa/desactiva la regla de caducidad.
        meses_limite   : Antigüedad máxima permitida (en meses).
    """

    MIN_CUERPO = 50  # caracteres mínimos en el cuerpo

    def __init__(self, filtro_tiempo: bool = False, meses_limite: int = 6):
        self.filtro_tiempo = filtro_tiempo
        self.dias_limite   = meses_limite * 30
        self._urls_vistas    = set()
        self._titulos_vistos = set()
        self.rechazados    = []
        self.total_evaluados = 0

    # ── API pública ──────────────────────────────────────────────────────────

    def validar(self, noticia: dict) -> bool:
        """Devuelve True si la noticia pasa todos los filtros."""
        self.total_evaluados += 1

        titulo = noticia.get('titulo', '') or ''
        cuerpo = noticia.get('cuerpo', '') or ''
        url    = str(noticia.get('url', '') or '')

        # Regla 1 — Campos mínimos presentes
        if not titulo.strip() or not url.strip():
            return self._rechazar(noticia, "Título o URL vacíos")

        # Regla 2 — Cuerpo con suficiente contenido
        if len(cuerpo.strip()) < self.MIN_CUERPO:
            return self._rechazar(noticia, f"Cuerpo insuficiente ({len(cuerpo.strip())} chars < {self.MIN_CUERPO})")

        # Regla 3 — URL con esquema válido
        if not url.startswith(('http://', 'https://')):
            return self._rechazar(noticia, "URL sin esquema http/https")

        # Regla 4 — Sin duplicados
        url_clave    = url.split('?')[0].rstrip('/')
        titulo_clave = titulo.strip().lower()

        if url_clave in self._urls_vistas:
            return self._rechazar(noticia, "Duplicado — URL ya registrada")

        if titulo_clave in self._titulos_vistos:
            return self._rechazar(noticia, "Duplicado — Título ya registrado")

        # Regla 5 — Caducidad (opcional)
        if self.filtro_tiempo:
            resultado = self._validar_fecha(noticia)
            if resultado is not True:
                return self._rechazar(noticia, resultado)

        # ✓ Noticia aprobada
        self._urls_vistas.add(url_clave)
        self._titulos_vistos.add(titulo_clave)
        return True

    def estadisticas(self) -> dict:
        aprobadas = self.total_evaluados - len(self.rechazados)
        return {
            'evaluadas':  self.total_evaluados,
            'aprobadas':  aprobadas,
            'rechazadas': len(self.rechazados),
            'tasa_exito': round(aprobadas / max(self.total_evaluados, 1) * 100, 1),
        }

    def exportar_reporte(self, ruta: str):
        """Guarda un reporte de texto con las noticias rechazadas."""
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        stats = self.estadisticas()
        estado_tiempo = "ACTIVO" if self.filtro_tiempo else "INACTIVO"

        with open(ruta, 'w', encoding='utf-8') as f:
            f.write("═" * 60 + "\n")
            f.write("  REPORTE DE CONTROL DE CALIDAD — SIMANW Fase 1\n")
            f.write("═" * 60 + "\n\n")
            f.write(f"  Total evaluadas  : {stats['evaluadas']}\n")
            f.write(f"  Aprobadas        : {stats['aprobadas']}\n")
            f.write(f"  Rechazadas       : {stats['rechazadas']}\n")
            f.write(f"  Tasa de éxito    : {stats['tasa_exito']}%\n")
            f.write(f"  Filtro de tiempo : {estado_tiempo}\n\n")
            f.write("DETALLE DE RECHAZOS:\n")
            f.write("─" * 60 + "\n")

            for i, r in enumerate(self.rechazados, 1):
                f.write(f"\n{i}. ✗ {r['motivo']}\n")
                f.write(f"   Título : {r['titulo']}\n")
                f.write(f"   URL    : {r['url']}\n")

        print(f"  [Reporte] Exportado → {ruta}")

    # ── Métodos internos ─────────────────────────────────────────────────────

    def _rechazar(self, noticia: dict, motivo: str) -> bool:
        self.rechazados.append({
            'titulo': noticia.get('titulo', 'SIN TÍTULO'),
            'url':    noticia.get('url', 'SIN URL'),
            'motivo': motivo,
        })
        return False

    def _validar_fecha(self, noticia: dict):
        """Valida que la noticia no supere el límite de antigüedad."""
        fecha_str = noticia.get('fecha', '')
        try:
            fecha_dt = parsedate_to_datetime(fecha_str)
            if fecha_dt.tzinfo is not None:
                fecha_dt = fecha_dt.astimezone().replace(tzinfo=None)
            diferencia = datetime.now() - fecha_dt
            if diferencia.days > self.dias_limite:
                return f"Caducada ({diferencia.days} días > límite {self.dias_limite})"
            return True
        except Exception:
            return "Fecha en formato no reconocido"


# ═════════════════════════════════════════════════════════════════════════════
# 1.3  CONTROL DE RASTREO
#      Define el alcance del rastreador: qué URLs puede visitar,
#      cuántas páginas procesar y en qué orden.
# ═════════════════════════════════════════════════════════════════════════════

class ControlRastreo:
    """
    Administra la política y los límites del proceso de rastreo.

    Modos de alcance:
      - 'dominio'    : Solo URLs del mismo dominio exacto.
      - 'subdominio' : Dominio principal y cualquier subdominio.
      - 'directorio' : Solo URLs bajo el mismo path de la semilla.

    Args:
        url_semilla  : URL inicial del rastreo.
        modo         : Política de alcance ('dominio', 'subdominio', 'directorio').
        max_paginas  : Límite de páginas a visitar.
        delay_seg    : Pausa (en segundos) entre peticiones para no sobrecargar servidores.
    """

    def __init__(self, url_semilla: str, modo: str = 'dominio',
                 max_paginas: int = 50, delay_seg: float = 2.0):
        self.url_semilla  = url_semilla
        self.modo         = modo
        self.max_paginas  = max_paginas
        self.delay_seg    = delay_seg
        self._dominio     = urlparse(url_semilla).netloc
        self._visitadas   = set()
        self._cola        = deque([url_semilla])
        self._rechazadas  = []

    # ── API pública ──────────────────────────────────────────────────────────

    def permitida(self, url: str) -> bool:
        """Verifica si una URL está dentro del alcance configurado."""
        p = urlparse(url)
        if self.modo == 'dominio':
            return p.netloc == self._dominio
        elif self.modo == 'subdominio':
            raiz = self._dominio.split('.', 1)[-1]
            return p.netloc.endswith(raiz)
        elif self.modo == 'directorio':
            base = urlparse(self.url_semilla).path.rsplit('/', 1)[0]
            return p.netloc == self._dominio and p.path.startswith(base)
        return False

    def encolar(self, urls: list[str]) -> int:
        """Añade a la cola las URLs válidas que no han sido visitadas."""
        nuevas = 0
        for url in urls:
            if url not in self._visitadas and self.permitida(url):
                self._cola.append(url)
                nuevas += 1
            else:
                self._rechazadas.append(url)
        return nuevas

    def siguiente(self) -> str | None:
        """Retorna la siguiente URL a procesar, o None si se alcanzó el límite."""
        if self._cola and len(self._visitadas) < self.max_paginas:
            url = self._cola.popleft()
            self._visitadas.add(url)
            return url
        return None

    def estado(self) -> dict:
        return {
            'visitadas':   len(self._visitadas),
            'en_cola':     len(self._cola),
            'rechazadas':  len(self._rechazadas),
            'completado':  len(self._visitadas) >= self.max_paginas or not self._cola,
        }

    def mostrar_demo(self):
        """Simula un rastreo con URLs de prueba para demostrar el control de alcance."""
        urls_prueba = [
            "/noticias/tecnologia/ia-2026",
            "/noticias/economia/mercados",
            "/deportes/futbol",
            "https://otro-sitio.com/articulo",
            "/noticias/ciencia/clima",
        ]

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 1.3 — Control de Rastreo              ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Semilla  : {self.url_semilla}")
        print(f"  Modo     : {self.modo}")
        print(f"  Límite   : {self.max_paginas} páginas\n")

        from urllib.parse import urljoin
        urls_abs = [urljoin(self.url_semilla, u) for u in urls_prueba]
        encoladas = self.encolar(urls_abs)

        print(f"  Candidatas : {len(urls_abs)}")
        print(f"  Encoladas  : {encoladas}")
        print(f"  Rechazadas : {len(self._rechazadas)}\n")

        print("  Simulación de visitas:")
        while True:
            url = self.siguiente()
            if not url:
                break
            print(f"    ✓ {url}")

        print(f"\n  Estado final: {self.estado()}")


# ═════════════════════════════════════════════════════════════════════════════
# 1.4  RASTREADOR RSS  (pipeline principal)
#      Orquesta la extracción completa: lee el archivo de configuración,
#      conecta con cada feed, filtra con FiltroCalidad y construye el dataset.
# ═════════════════════════════════════════════════════════════════════════════

class RastreadorRSS:
    """
    Pipeline principal de la Fase 1.

    Lee feeds RSS de múltiples portales, extrae noticias estructuradas,
    las filtra con FiltroCalidad y genera el dataset maestro para las
    fases posteriores de NLP y análisis.

    Args:
        config_rss      : Ruta al JSON con la configuración de fuentes RSS.
        max_por_cat     : Número máximo de noticias válidas por categoría.
        filtro_tiempo   : Activa la regla de caducidad en FiltroCalidad.
        meses_limite    : Antigüedad máxima de noticias (si filtro_tiempo=True).
    """

    def __init__(self, config_rss: str, max_por_cat: int = 900,
                 filtro_tiempo: bool = False, meses_limite: int = 6):
        self.config_rss    = config_rss
        self.max_por_cat   = max_por_cat
        self.dataset: list[dict] = []
        self.filtro        = FiltroCalidad(filtro_tiempo, meses_limite)
        self._stats_feeds  = {}   # estadísticas por feed individual

    # ── API pública ──────────────────────────────────────────────────────────

    def ejecutar(self) -> list[dict]:
        """Ejecuta el pipeline completo de extracción."""
        fuentes = self._cargar_config()

        print("╔══════════════════════════════════════════════╗")
        print("║   FASE 1.4 — Rastreador RSS                  ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Categorías  : {len(fuentes)}")
        print(f"  Límite/cat  : {self.max_por_cat}")
        print(f"  Filtro tiempo: {'ON' if self.filtro.filtro_tiempo else 'OFF'}\n")

        for categoria, urls in fuentes.items():
            self._procesar_categoria(categoria, urls)

        stats = self.filtro.estadisticas()
        print("\n  ── Resumen global ──────────────────────────")
        print(f"  Noticias en dataset : {len(self.dataset)}")
        print(f"  Evaluadas           : {stats['evaluadas']}")
        print(f"  Tasa de éxito       : {stats['tasa_exito']}%")
        print(f"  Rechazadas          : {stats['rechazadas']}")

        return self.dataset

    def guardar_dataset(self, ruta: str):
        """Serializa el dataset en JSON con formato legible."""
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, ensure_ascii=False, indent=2)
        print(f"\n  [Dataset] {len(self.dataset)} noticias → {ruta}")

    def exportar_reporte(self, ruta: str):
        """Genera el reporte de control de calidad."""
        self.filtro.exportar_reporte(ruta)

    # ── Métodos internos ─────────────────────────────────────────────────────

    def _cargar_config(self) -> dict:
        with open(self.config_rss, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _procesar_categoria(self, categoria: str, urls: list[str]):
        """Itera los feeds de una categoría hasta alcanzar el límite."""
        validas = 0
        print(f"  ▶ {categoria.upper()} (objetivo: {self.max_por_cat})")

        for url_feed in urls:
            if validas >= self.max_por_cat:
                break

            print(f"    ↳ {url_feed}")
            try:
                feed = feedparser.parse(url_feed)
                print(f"       entries encontradas: {len(feed.entries)}")

                encontradas_feed = 0

                for entry in feed.entries:
                    if validas >= self.max_por_cat:
                        break

                    candidata = self._construir_noticia(entry, categoria, url_feed)

                    if self.filtro.validar(candidata):
                        self.dataset.append(candidata)
                        validas += 1
                        encontradas_feed += 1

                print(f"       +{encontradas_feed} válidas  (total cat: {validas})")
                self._stats_feeds[url_feed] = encontradas_feed

            except Exception as e:
                print(f"       [!] Error: {e}")

    def _construir_noticia(self, entry, categoria: str, url_feed: str) -> dict:
        """Construye un dict normalizado a partir de una entrada RSS."""
        cuerpo_crudo = entry.get('summary', entry.get('description', ''))
        return {
            'titulo':     entry.get('title', ''),
            'cuerpo':     self._limpiar_html(cuerpo_crudo),
            'fecha':      entry.get('published', datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")),
            'autor':      entry.get('author', entry.get('publisher', 'Desconocido')),
            'url':        entry.get('link', ''),
            'categoria':  categoria,
            'fuente':     url_feed,
            'ts_captura': datetime.now().isoformat(),
        }

    @staticmethod
    def _limpiar_html(texto: str) -> str:
        """Elimina etiquetas HTML de un texto."""
        if not texto:
            return ''
        return re.sub(r'<[^>]+>', '', texto).strip()


# ═════════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':

    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ── 1.1 Demo del Parser DOM ──────────────────────────────────────────────
    parser = ParserDOM(HTML_DEMO)
    parser.mostrar_demo()
    print()

    # ── 1.3 Demo del Control de Rastreo ─────────────────────────────────────
    control = ControlRastreo(
        url_semilla='https://portal-noticias.com/noticias/',
        modo='directorio',
        max_paginas=10
    )
    control.mostrar_demo()
    print()

    # ── 1.4 Pipeline RSS ─────────────────────────────────────────────────────
    rastreador = RastreadorRSS(
        config_rss=os.path.join(BASE, 'config', 'fuentes_rss.json'),
        max_por_cat=900,
        filtro_tiempo=False,
    )

    dataset = rastreador.ejecutar()

    rastreador.guardar_dataset(
        os.path.join(BASE, 'datos', 'dataset_maestro.json')
    )
    rastreador.exportar_reporte(
        os.path.join(BASE, 'reportes', 'reporte_fase1_calidad.txt')
    )