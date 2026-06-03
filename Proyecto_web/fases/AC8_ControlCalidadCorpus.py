
"""
SIMANW - AC-8: Control de calidad del corpus rastreado
======================================================

Complemento de Fases 1-2.

Objetivo:
    Validar el corpus obtenido por rastreo antes de enviarlo al pipeline NLP.

Cumple:
- Informe automático JSON.
- Total de registros.
- Registros inválidos o incompletos.
- Duplicados exactos.
- Duplicados casi idénticos por mismo título o misma URL.
- Reglas mínimas de validez documentadas.
- Lista de registros rechazados con motivo.
- Corpus depurado utilizable en fases siguientes.
- Párrafo breve de máximo 200 palabras.

Uso:
    python fases/AC8_ControlCalidadCorpus.py

Entrada por defecto:
    datos/dataset_maestro.json

Salida:
    datos/dataset_depurado_ac8.json
    reportes/ac8_control_calidad_corpus.json
"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


def resolver_raiz_proyecto():
    actual = Path.cwd().resolve()

    if (actual / "datos").exists():
        return actual

    if actual.name.lower() == "fases" and (actual.parent / "datos").exists():
        return actual.parent

    archivo = Path(__file__).resolve()
    if (archivo.parent.parent / "datos").exists():
        return archivo.parent.parent

    return actual


ROOT = resolver_raiz_proyecto()


class ValidadorCorpus:
    def __init__(self, longitud_minima_cuerpo=40):
        self.longitud_minima_cuerpo = longitud_minima_cuerpo
        self.reglas = {
            "campos_obligatorios": ["titulo", "cuerpo", "url", "fecha", "fuente"],
            "longitud_minima_cuerpo": longitud_minima_cuerpo,
            "formato_fecha_aceptado": [
                "YYYY-MM-DD",
                "YYYY-MM-DDTHH:MM:SS",
                "cadenas no vacías provenientes de RSS si no se pueden normalizar",
            ],
            "url_valida": "Debe iniciar con http:// o https:// y contener dominio.",
            "duplicado_exacto": "Misma combinación normalizada de título + URL.",
            "duplicado_casi_identico": "Mismo título normalizado o misma URL normalizada.",
        }

    def validar(self, registros):
        aceptados = []
        rechazados = []
        vistos_exactos = set()
        titulos_vistos = {}
        urls_vistas = {}

        estadisticas = {
            "total_registros": len(registros),
            "validos": 0,
            "rechazados": 0,
            "invalidos_incompletos": 0,
            "duplicados_exactos": 0,
            "duplicados_casi_identicos": 0,
        }

        for indice, registro in enumerate(registros):
            motivos = self._validar_registro(registro)

            titulo_norm = self._normalizar_texto(registro.get("titulo", ""))
            url_norm = self._normalizar_url(registro.get("url", ""))
            huella_exacta = f"{titulo_norm}|{url_norm}"

            if not motivos:
                if huella_exacta in vistos_exactos:
                    motivos.append("duplicado_exacto_titulo_url")
                    estadisticas["duplicados_exactos"] += 1
                elif titulo_norm and titulo_norm in titulos_vistos:
                    motivos.append(f"duplicado_casi_identico_mismo_titulo:id_original={titulos_vistos[titulo_norm]}")
                    estadisticas["duplicados_casi_identicos"] += 1
                elif url_norm and url_norm in urls_vistas:
                    motivos.append(f"duplicado_casi_identico_misma_url:id_original={urls_vistas[url_norm]}")
                    estadisticas["duplicados_casi_identicos"] += 1

            if motivos:
                estadisticas["rechazados"] += 1
                if any(m.startswith("campo_") or m.startswith("cuerpo_") or m.startswith("url_") or m.startswith("fecha_") for m in motivos):
                    estadisticas["invalidos_incompletos"] += 1

                rechazados.append({
                    "indice": indice,
                    "titulo": registro.get("titulo", ""),
                    "url": registro.get("url", ""),
                    "motivos": motivos,
                    "registro": registro,
                })
                continue

            registro_limpio = self._normalizar_registro(registro)
            aceptados.append(registro_limpio)
            vistos_exactos.add(huella_exacta)
            titulos_vistos[titulo_norm] = indice
            urls_vistas[url_norm] = indice

        estadisticas["validos"] = len(aceptados)

        return {
            "reglas": self.reglas,
            "estadisticas": estadisticas,
            "rechazados": rechazados,
            "corpus_depurado": aceptados,
            "resumen_200_palabras": self._generar_resumen(estadisticas, rechazados),
            "distribucion_fuentes": dict(Counter(r.get("fuente", "desconocida") for r in aceptados)),
            "distribucion_categorias": dict(Counter(r.get("categoria", "general") for r in aceptados)),
        }

    def _validar_registro(self, registro):
        motivos = []

        for campo in self.reglas["campos_obligatorios"]:
            valor = registro.get(campo)
            if valor is None or str(valor).strip() == "":
                motivos.append(f"campo_obligatorio_faltante:{campo}")

        titulo = str(registro.get("titulo", "")).strip()
        cuerpo = str(registro.get("cuerpo", "")).strip()
        url = str(registro.get("url", "")).strip()
        fecha = str(registro.get("fecha", "")).strip()

        if titulo and len(titulo) < 8:
            motivos.append("campo_titulo_demasiado_corto")

        if cuerpo and len(cuerpo) < self.longitud_minima_cuerpo:
            motivos.append(f"cuerpo_demasiado_corto:minimo={self.longitud_minima_cuerpo}")

        if url and not self._url_valida(url):
            motivos.append("url_invalida_o_sin_dominio")

        if fecha and not self._fecha_aceptable(fecha):
            motivos.append("fecha_formato_no_reconocido")

        return motivos

    def _normalizar_registro(self, registro):
        limpio = dict(registro)

        for campo in ["titulo", "cuerpo", "resumen", "fuente", "autor", "categoria"]:
            if campo in limpio and isinstance(limpio[campo], str):
                limpio[campo] = re.sub(r"\s+", " ", limpio[campo]).strip()

        if "categoria" not in limpio or not limpio.get("categoria"):
            limpio["categoria"] = "general"

        if "autor" not in limpio or not limpio.get("autor"):
            limpio["autor"] = "No identificado"

        limpio["validado_ac8"] = True
        limpio["fecha_validacion_ac8"] = datetime.now().isoformat(timespec="seconds")

        return limpio

    def _generar_resumen(self, estadisticas, rechazados):
        total = estadisticas["total_registros"]
        validos = estadisticas["validos"]
        rechazados_total = estadisticas["rechazados"]
        incompletos = estadisticas["invalidos_incompletos"]
        exactos = estadisticas["duplicados_exactos"]
        casi = estadisticas["duplicados_casi_identicos"]

        causas = Counter()
        for item in rechazados:
            for motivo in item["motivos"]:
                causas[motivo.split(":")[0]] += 1

        causa_principal = causas.most_common(1)[0][0] if causas else "sin rechazos"

        resumen = (
            f"El control de calidad revisó {total} registros del corpus rastreado. "
            f"Se conservaron {validos} noticias válidas y se descartaron {rechazados_total}. "
            f"Los descartes se debieron principalmente a {causa_principal}. "
            f"Se detectaron {incompletos} registros inválidos o incompletos, "
            f"{exactos} duplicados exactos y {casi} duplicados casi idénticos por coincidencia de título o URL. "
            f"El corpus depurado conserva únicamente noticias con campos obligatorios, URL coherente, fecha aceptable "
            f"y cuerpo con longitud mínima suficiente para las fases de NLP."
        )

        palabras = resumen.split()
        return " ".join(palabras[:200])

    @staticmethod
    def _normalizar_texto(texto):
        texto = (texto or "").lower()
        texto = re.sub(r"[^\w\sáéíóúñü]", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    @staticmethod
    def _normalizar_url(url):
        url = (url or "").strip()
        url = url.split("#")[0]
        url = url.rstrip("/")
        return url

    @staticmethod
    def _url_valida(url):
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    @staticmethod
    def _fecha_aceptable(fecha):
        fecha = fecha.strip()
        if not fecha:
            return False

        patrones = [
            r"^\d{4}-\d{2}-\d{2}$",
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}",
            r"^[A-Za-z]{3},",
            r"\d{4}",
        ]

        return any(re.search(p, fecha) for p in patrones)


class AC8ControlCalidadCorpus:
    def __init__(
        self,
        ruta_entrada=None,
        ruta_salida=None,
        ruta_reporte=None,
    ):
        self.ruta_entrada = Path(ruta_entrada) if ruta_entrada else ROOT / "datos" / "dataset_maestro.json"
        self.ruta_salida = Path(ruta_salida) if ruta_salida else ROOT / "datos" / "dataset_depurado_ac8.json"
        self.ruta_reporte = Path(ruta_reporte) if ruta_reporte else ROOT / "reportes" / "ac8_control_calidad_corpus.json"

    def ejecutar(self):
        registros = self._cargar_registros()
        validador = ValidadorCorpus()
        resultado = validador.validar(registros)

        self._guardar_json(self.ruta_salida, resultado["corpus_depurado"])

        reporte = {
            "actividad": "AC-8 Control de calidad del corpus rastreado",
            "fecha": datetime.now().isoformat(timespec="seconds"),
            "entrada": str(self.ruta_entrada),
            "salida_corpus_depurado": str(self.ruta_salida),
            "reglas": resultado["reglas"],
            "estadisticas": resultado["estadisticas"],
            "distribucion_fuentes": resultado["distribucion_fuentes"],
            "distribucion_categorias": resultado["distribucion_categorias"],
            "rechazados": resultado["rechazados"],
            "resumen_200_palabras": resultado["resumen_200_palabras"],
        }

        self._guardar_json(self.ruta_reporte, reporte)

        print("╔══════════════════════════════════════════════╗")
        print("║   AC-8 — Control de calidad del corpus       ║")
        print("╚══════════════════════════════════════════════╝")
        print(f"  Entrada        : {self.ruta_entrada}")
        print(f"  Total registros: {resultado['estadisticas']['total_registros']}")
        print(f"  Válidos        : {resultado['estadisticas']['validos']}")
        print(f"  Rechazados     : {resultado['estadisticas']['rechazados']}")
        print(f"  Inválidos      : {resultado['estadisticas']['invalidos_incompletos']}")
        print(f"  Dup. exactos   : {resultado['estadisticas']['duplicados_exactos']}")
        print(f"  Dup. similares : {resultado['estadisticas']['duplicados_casi_identicos']}")
        print()
        print("  Resumen:")
        print("  " + resultado["resumen_200_palabras"])
        print()
        print("  [Corpus depurado] Guardado →", self.ruta_salida)
        print("  [Reporte]         Guardado →", self.ruta_reporte)

        return reporte

    def _cargar_registros(self):
        if not self.ruta_entrada.exists():
            raise FileNotFoundError(f"No se encontró el corpus: {self.ruta_entrada}")

        with open(self.ruta_entrada, "r", encoding="utf-8") as f:
            datos = json.load(f)

        if not isinstance(datos, list):
            raise ValueError("El corpus debe ser una lista de registros/noticias.")

        return datos

    def _guardar_json(self, ruta, contenido):
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    AC8ControlCalidadCorpus().ejecutar()
