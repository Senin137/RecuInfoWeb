import feedparser
import json
import re


def fetch_rss(lista_urls, max_entries=20):
    """Extrae ítems de un feed RSS/Atom. Devuelve lista de diccionarios."""
    items = []
    for url in lista_urls:
        print(f"Procesando: {url}")
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", url)
            for e in feed.entries[:max_entries]:
                items.append({
                    "source": source_name,
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "published": e.get("published", e.get("updated", "")),
                    "summary": e.get("summary", e.get("description", "")),
                })
        except Exception as err:
            items.append({"error": str(err), "url": url})
    return items

def clean_text(text):
    """Limpieza básica: quitar tags HTML, solo letras y espacios, minúsculas."""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text

def normalize_items(items):
    """Añade campo 'text_clean' a cada ítem (título + resumen limpios)."""
    for it in items:
        if "error" in it:
            continue
        title = it.get("title", "")
        summary = it.get("summary", "")
        it["text_clean"] = clean_text(title) + " " + clean_text(summary)
    return items

urls = ["https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/mexico/portada", "https://heraldodemexico.com.mx/rss/feed.html?r=4", "https://www.reforma.com/rss/nacional.xml",
        "https://www.proceso.com.mx/rss/feed.html?r=1", "https://editorial.aristeguinoticias.com/category/mexico/feed/"]
items = fetch_rss(urls, max_entries=15)
items_norm = normalize_items(items)
print(json.dumps(items_norm, indent=2, ensure_ascii=False))
with open("Lista_RSS", "w", encoding="utf-8") as f:
    json.dump(items, f, indent=2, ensure_ascii=False)
print("Archivo 'Lista_RSS' creado con éxito.")