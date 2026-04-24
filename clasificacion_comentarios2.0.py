# 5 algoritmos de aprendizaje supervisado y 5 semi-supervisado para clasificación de texto

import nltk
import re
import csv
import requests
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import wordpunct_tokenize

# --- 1. CONFIGURACIÓN DE EXTRACCIÓN ---
def obtener_comentarios_api(cantidad=100):
    print(f"🚀 Extrayendo {cantidad} comentarios desde Hugging Face API...")
    url_base = "https://datasets-server.huggingface.co/rows"
    params = {"dataset": "gplsi/SocialTOX", "config": "default", "split": "train", "offset": 0, "length": 100}
    
    textos_extraidos = []
    try:
        response = requests.get(url_base, params=params)
        response.raise_for_status()
        data = response.json()
        for item in data['rows']:
            textos_extraidos.append(item['row']['text'])
    except Exception as e:
        print(f"❌ Error en API: {e}")
    return textos_extraidos[:cantidad]

# --- 2. RECURSOS Y NORMALIZACIÓN ---
def ensure_nltk_resources():
    for resource in ("punkt", "stopwords"):
        try:
            nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=False)

ensure_nltk_resources()
sw = set(stopwords.words("spanish"))
stemmer = SnowballStemmer("spanish")

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_MENTION_RE = re.compile(r"@\w+")
_HASHTAG_RE = re.compile(r"#\w+")
_NON_LETTER_RE = re.compile(r"[^a-záéíóúñü0-9\s]+", re.IGNORECASE)
_MULTISPACE_RE = re.compile(r"\s+")

def normalize_text(text: str) -> str:
    if not text: return ""
    t = text.strip().lower()
    t = _URL_RE.sub(" ", t)
    t = _MENTION_RE.sub(" ", t)
    t = _HASHTAG_RE.sub(" ", t)
    t = _NON_LETTER_RE.sub(" ", t)
    t = _MULTISPACE_RE.sub(" ", t).strip()
    return t

def featurize(text: str) -> dict:
    t = normalize_text(text)
    tokens = wordpunct_tokenize(t)
    feats = {}
    for tok in tokens:
        if tok.isdigit():
            feats["HAS_NUMBER"] = True
            continue
        if len(tok) < 2 or tok in sw:
            continue
        stem = stemmer.stem(tok)
        feats[f"w={stem}"] = True
    feats["HAS_EXCLAMATION"] = "!" in text
    feats["HAS_NEGATION"] = any(w in t.split() for w in ("no", "nunca", "jamás", "ni"))
    return feats

# --- 3. SET DE ENTRENAMIENTO EXTENDIDO (Mapeado a Pos/Neg/Neu) ---
# He convertido los ejemplos de sarcasmo a 'neg' para este clasificador
train_data = [
    # Positivos
    ("Me encanta que ahora se integre nativamente con Git", "pos"),
    ("Excelente contraste para trabajar de noche", "pos"),
    ("La refactorización se hace casi de manera mágica", "pos"),
    ("Es increíble lo fácil que es configurar el entorno", "pos"),
    ("El profesor explicó maravillosamente el concepto", "pos"),
    ("Me gustó mucho la interfaz del dashboard", "pos"),
    # Negativos (Incluye sarcasmo mapeado como 'neg')
    ("El autocompletado es bastante lento", "neg"),
    ("La actualización arruinó la indentación", "neg"),
    ("No ayuda en nada a resolver el problema", "neg"),
    ("Qué gran idea subir a producción sin probar", "neg"), # Sarcasmo
    ("Claro, el servidor siempre se cae cuando más lo necesito", "neg"), # Sarcasmo
    ("Increíble, la base de datos se borró sola", "neg"), # Sarcasmo
    ("El consumo de RAM es excesivo", "neg"),
    # Neutros
    ("Para esta práctica utilizaremos React", "neu"),
    ("El dataset contiene 5,000 imágenes", "neu"),
    ("El backup se ejecuta a las 3:00 AM", "neu"),
    ("La cafetería del tec hoy tiene mucha gente", "neu"),
    ("Se requiere una versión de Node superior a 18", "neu"),
    ("Mañana hay clase en el laboratorio a las 9", "neu")
]

# --- 4. ENTRENAMIENTO ---
train_set = [(featurize(text), label) for text, label in train_data]
classifier = nltk.NaiveBayesClassifier.train(train_set)
print(f"✅ Entrenamiento OK. Modelo cargado con {len(train_set)} ejemplos.")

# --- 5. CLASIFICACIÓN Y EXPORTACIÓN ---
comentarios = obtener_comentarios_api(100)
out_rows = []

for text in comentarios:
    feats = featurize(text)
    dist = classifier.prob_classify(feats)
    label = dist.max()
    prob = float(dist.prob(label))
    out_rows.append((text, label, prob))

out_path = "sentimientos_resultados_100.csv"
with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["texto", "sentimiento", "probabilidad"])
    w.writerows(out_rows)

print(f"🎯 Clasificación terminada. Archivo generado: {out_path}")

# Muestra rápida
print("\nPrimeros 5 resultados:")
for i, (t, lab, p) in enumerate(out_rows[:5]):
    print(f"{i}: [{lab}] (p={p:.2f}) - {t[:80]}...")