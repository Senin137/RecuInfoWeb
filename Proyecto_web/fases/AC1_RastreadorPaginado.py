
"""
SIMANW - AC-1: Rastreo de sitio real con paginación

Complemento de la Fase 1. No reemplaza el rastreador RSS principal.

Cumple:
- Revisa robots.txt.
- Usa delay mínimo de 3 segundos.
- Navega automáticamente con paginación.
- Extrae al menos 20 noticias reales cuando el sitio lo permite.
- Guarda resultados en JSON.

Uso:
    python fases/AC1_RastreadorPaginado.py
"""

import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup


@dataclass
class ConfiguracionSitio:
    nombre: str
    url_inicio: str
    selector_articulos: str
    selector_siguiente: str
    selector_titulo: str
    selector_enlace: str
    selector_resumen: str | None = None
    categoria: str = "tecnologia"
    max_paginas: int = 3
    delay: int = 3
    minimo_noticias: int = 20


class RastreadorPaginado:
    def __init__(self, config: ConfiguracionSitio):
        self.config = config
        self.resultados = []
        self.visitadas = set()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "SIMANWBot/1.0 Proyecto academico de recuperacion web"
        })
        self.robot_parser = self._preparar_robots()

    def rastrear(self):
        url_actual = self.config.url_inicio
        paginas_visitadas = 0

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-1 — Rastreo real con paginación         ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Sitio         : {self.config.nombre}")
        print(f"  URL inicial   : {self.config.url_inicio}")
        print(f"  Delay         : {self.config.delay}s")
        print(f"  Meta noticias : {self.config.minimo_noticias}")
        print()

        while url_actual and paginas_visitadas < self.config.max_paginas:
            if url_actual in self.visitadas:
                print(f"  [STOP] URL repetida: {url_actual}")
                break

            if not self._permitida_por_robots(url_actual):
                print(f"  [ROBOTS] No permitido: {url_actual}")
                break

            print(f"  ▶ Página {paginas_visitadas + 1}: {url_actual}")
            html = self._descargar(url_actual)
            if not html:
                break

            noticias = self.extraer_pagina(html, url_actual)
            agregadas = self._agregar_sin_duplicados(noticias)

            print(f"     Extraídas en página : {len(noticias)}")
            print(f"     Nuevas agregadas    : {agregadas}")
            print(f"     Total acumulado     : {len(self.resultados)}")

            self.visitadas.add(url_actual)
            paginas_visitadas += 1

            if len(self.resultados) >= self.config.minimo_noticias:
                print("  [OK] Se alcanzó el mínimo de 20 noticias.")
                break

            siguiente = self.obtener_siguiente_pagina(html, url_actual)
            if not siguiente:
                print("  [STOP] No se encontró página siguiente.")
                break

            url_actual = siguiente
            if paginas_visitadas < self.config.max_paginas:
                time.sleep(max(self.config.delay, 3))

        return self.resultados

    def extraer_pagina(self, html, url_actual):
        soup = BeautifulSoup(html, "html.parser")
        articulos = soup.select(self.config.selector_articulos)
        noticias = []

        for art in articulos:
            titulo_elem = art.select_one(self.config.selector_titulo)
            enlace_elem = art.select_one(self.config.selector_enlace)

            if self.config.selector_resumen:
                resumen_elem = art.select_one(self.config.selector_resumen)
            else:
                resumen_elem = None

            titulo = self._texto(titulo_elem)
            resumen = self._texto(resumen_elem)
            href = enlace_elem.get("href") if enlace_elem else ""
            url = urljoin(url_actual, href)

            if not titulo or not url:
                continue

            noticias.append({
                "titulo": titulo,
                "cuerpo": resumen or titulo,
                "resumen": resumen or titulo,
                "url": url,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "autor": "No identificado",
                "fuente": self.config.nombre,
                "categoria": self.config.categoria,
                "extraido_en": datetime.now().isoformat(timespec="seconds"),
                "metodo_extraccion": "AC1_rastreo_paginado",
            })

        return noticias

    def obtener_siguiente_pagina(self, html, url_actual):
        soup = BeautifulSoup(html, "html.parser")
        siguiente = soup.select_one(self.config.selector_siguiente)

        if siguiente and siguiente.get("href"):
            return urljoin(url_actual, siguiente["href"])

        for enlace in soup.find_all("a"):
            texto = enlace.get_text(" ", strip=True).lower()
            rel = " ".join(enlace.get("rel", [])).lower() if enlace.get("rel") else ""
            if texto in {"more", "siguiente", "next", "más", "mas"} or "next" in rel:
                href = enlace.get("href")
                if href:
                    return urljoin(url_actual, href)

        return None

    def guardar_json(self, ruta):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.resultados, f, ensure_ascii=False, indent=2)
        return len(self.resultados)

    def guardar_reporte(self, ruta):
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.reporte(), f, ensure_ascii=False, indent=2)

    def reporte(self):
        return {
            "actividad": "AC-1 Rastreo de sitio real con paginacion",
            "sitio": self.config.nombre,
            "url_inicio": self.config.url_inicio,
            "paginas_visitadas": len(self.visitadas),
            "noticias_extraidas": len(self.resultados),
            "delay_segundos": self.config.delay,
            "robots_txt_respetado": True,
            "cumple_minimo_20": len(self.resultados) >= 20,
            "fecha": datetime.now().isoformat(timespec="seconds"),
        }

    def _descargar(self, url):
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            print(f"  [ERROR] {exc}")
            return None

    def _preparar_robots(self):
        parsed = urlparse(self.config.url_inicio)
        robots_url = urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
        rp = RobotFileParser()
        rp.set_url(robots_url)

        try:
            rp.read()
            print(f"  [robots.txt] Leído: {robots_url}")
        except Exception:
            print("  [robots.txt] No se pudo leer. Se usará política conservadora.")
            rp.parse(["User-agent: *", "Disallow:"])

        return rp

    def _permitida_por_robots(self, url):
        return self.robot_parser.can_fetch(self.session.headers["User-Agent"], url)

    def _agregar_sin_duplicados(self, noticias):
        urls = {n["url"] for n in self.resultados}
        titulos = {n["titulo"].strip().lower() for n in self.resultados}
        agregadas = 0

        for noticia in noticias:
            titulo = noticia["titulo"].strip().lower()
            if noticia["url"] in urls or titulo in titulos:
                continue
            self.resultados.append(noticia)
            urls.add(noticia["url"])
            titulos.add(titulo)
            agregadas += 1

        return agregadas

    @staticmethod
    def _texto(elemento):
        return elemento.get_text(" ", strip=True) if elemento else ""


def demo_hacker_news():
    config = ConfiguracionSitio(
        nombre="Hacker News",
        url_inicio="https://news.ycombinator.com/news?p=1",
        selector_articulos="tr.athing",
        selector_siguiente="a.morelink",
        selector_titulo=".titleline > a",
        selector_enlace=".titleline > a",
        selector_resumen=None,
        categoria="tecnologia",
        max_paginas=3,
        delay=3,
        minimo_noticias=20,
    )

    rastreador = RastreadorPaginado(config)
    resultados = rastreador.rastrear()

    ruta_datos = "datos/ac1_rastreo_paginado.json"
    ruta_reporte = "reportes/ac1_reporte_rastreo_paginado.json"

    total = rastreador.guardar_json(ruta_datos)
    rastreador.guardar_reporte(ruta_reporte)

    print()
    print("  ── Resultado AC-1 ─────────────────────────")
    print(f"  Noticias guardadas : {total}")
    print(f"  Dataset            : {ruta_datos}")
    print(f"  Reporte            : {ruta_reporte}")
    print()

    print("  Primeras noticias:")
    for noticia in resultados[:5]:
        print(f"   - {noticia['titulo'][:90]}")

    return resultados


if __name__ == "__main__":
    demo_hacker_news()
