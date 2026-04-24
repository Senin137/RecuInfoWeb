import nltk
import re
import csv
import requests  # <-- Nueva librería necesaria
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import wordpunct_tokenize

# --- CONFIGURACIÓN DE EXTRACCIÓN ---
def obtener_comentarios_api(cantidad=200):
    print(f"🚀 Extrayendo {cantidad} comentarios desde Hugging Face API...")
    url_base = "https://datasets-server.huggingface.co/rows"
    params = {
        "dataset": "gplsi/SocialTOX",
        "config": "default",
        "split": "train",
        "offset": 0,
        "length": 100
    }
    
    textos_extraidos = []
    while len(textos_extraidos) < cantidad:
        try:
            response = requests.get(url_base, params=params)
            response.raise_for_status()
            data = response.json()
            
            for item in data['rows']:
                # Extraemos solo el campo 'text'
                textos_extraidos.append(item['row']['text'])
                if len(textos_extraidos) >= cantidad:
                    break
            
            params['offset'] += 100
        except Exception as e:
            print(f"❌ Error en API: {e}")
            break
    return textos_extraidos

# --- CARGA DE DATOS ---
# Sustituimos tu lista manual por la llamada a la API
comentarios = obtener_comentarios_api(200)
print(f"✅ Total de comentarios listos para procesar: {len(comentarios)}")

# --- TU LÓGICA DE NLTK (Normalización y Featurización) ---
def ensure_nltk_resources():
    for resource in ("punkt", "stopwords"):
        try:
            nltk.data.find(f"tokenizers/{resource}" if resource == "punkt" else f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=False)

ensure_nltk_resources()

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

sw = set(stopwords.words("spanish"))
stemmer = SnowballStemmer("spanish")

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
    feats["LEN_GT_120"] = len(t) > 120
    feats["HAS_EXCLAMATION"] = "!" in text
    feats["HAS_NEGATION"] = any(w in t.split() for w in ("no", "nunca", "jamás", "ni"))
    return feats

# --- ENTRENAMIENTO DEL CLASIFICADOR (Naive Bayes) ---

train_data_sarcasmo = [
    # --- CATEGORÍA: INGENIERÍA Y SOFTWARE ---
    ("Qué gran idea subir cambios a producción un viernes a las 5 PM sin probar.", "sar"),
    ("Me fascina que el compilador me de 400 errores por un punto y coma.", "sar"),
    ("Claro, porque Docker nunca da problemas de red en Windows.", "sar"),
    ("Increíble, la base de datos se borró sola. Qué sistema tan confiable.", "sar"),
    ("Amo pasar 4 horas buscando un bug que era una variable mal escrita.", "sar"),
    ("El despliegue fue exitoso y todos los servicios están en línea.", "ns"),
    ("Estamos usando una arquitectura de microservicios para este proyecto.", "ns"),
    ("La consulta SQL tardó 2ms en ejecutar el JOIN.", "ns"),
    ("Es necesario instalar las dependencias antes de correr el script.", "ns"),
    ("El servidor tiene un uptime del 99.9% este mes.", "ns"),
    ("Genial, otra actualización que rompe la compatibilidad hacia atrás.", "sar"),
    ("Wow, el modo oscuro es tan oscuro que ya no veo ni el cursor.", "sar"),

    # --- CATEGORÍA: VIDA ESTUDIANTIL (Tono ITM / Morelia) ---
    ("Me encanta que se caiga el sistema de inscripciones justo cuando me toca.", "sar"),
    ("Qué emoción, otra tarea de 10 horas para entregar mañana a las 7 AM.", "sar"),
    ("Claro, el profesor explica súper claro, por eso nadie aprobó el parcial.", "sar"),
    ("Qué clima tan hermoso en Morelia, justo para salir sin paraguas y empaparse.", "sar"),
    ("Seguro que si no duermo hoy, mañana seré un genio en el examen de redes.", "sar"),
    ("La cafetería del tec hoy tiene mucha gente.", "ns"),
    ("Aprobé la materia de sistemas operativos con buen promedio.", "ns"),
    ("El laboratorio de cómputo tiene aire acondicionado nuevo.", "ns"),
    ("Mañana hay conferencia sobre inteligencia artificial en el auditorio.", "ns"),
    ("Necesito renovar mi credencial de estudiante esta semana.", "ns"),

    # --- CATEGORÍA: REDES SOCIALES Y SERVICIOS ---
    ("Qué buen servicio, solo tardaron 3 meses en entregar mi paquete.", "sar"),
    ("Gracias por dejarme en visto, realmente valoro tu falta de interés.", "sar"),
    ("Me encanta que el internet se vaya justo cuando estoy en una reunión.", "sar"),
    ("Qué original tu comentario, nunca lo había leído en los últimos 5 minutos.", "sar"),
    ("Wow, otro video de política en mi feed, justo lo que necesitaba para ser feliz.", "sar"),
    ("La velocidad de descarga es de 100 Mbps constantes.", "ns"),
    ("Recibí un correo de confirmación después de la compra.", "ns"),
    ("El video tiene una resolución de 1080p y buen audio.", "ns"),
    ("Ayer publicaron las fotos del evento en la página oficial.", "ns"),
    ("La aplicación se actualizó automáticamente esta mañana.", "ns"),
    ("Bravo, otra vez subieron el precio de la gasolina. Qué gran noticia.", "sar"),
    ("Claro, porque mi opinión no cuenta, como siempre.", "sar"),

    # --- CATEGORÍA: IRONÍA SUTIL ---
    ("Qué sorpresa, el político prometió cosas y no cumplió ninguna.", "sar"),
    ("Me fascina cómo la gente cree todo lo que lee en Facebook.", "sar"),
    ("Increíble precisión la del clima, dijeron sol y está granizando.", "sar"),
    ("Qué divertido es esperar el camión 40 minutos bajo el sol.", "sar"),
    ("El transporte público llega a la estación cada diez minutos.", "ns"),
    ("El pronóstico del tiempo indica lluvia para la tarde.", "ns"),
    ("La mayoría de los ciudadanos votaron en las elecciones pasadas.", "ns"),
    ("El libro tiene una introducción muy detallada sobre el tema.", "ns"),
    ("Qué maravilla que la batería del celular dure 20 minutos.", "sar"),
    ("Seguro que gritando vas a arreglar el problema más rápido.", "sar"),
    ("El dispositivo móvil tiene una garantía de un año por el fabricante.", "ns"),
    ("La conexión Wi-Fi es inestable en esta zona del edificio.", "ns"),
    ("Qué genio, metió el celular al microondas para cargarlo más rápido.", "sar"),
    ("Sí, claro, y yo soy el dueño de Microsoft.", "sar"),
    ("El usuario ingresó sus credenciales correctamente.", "ns"),
    ("La pantalla táctil responde bien a los gestos.", "ns")
]

# --- 2. MEJORA DE CARACTERÍSTICAS (FEATURIZE) ---
def featurize_sarcasmo(text: str) -> dict:
    t = normalize_text(text)
    tokens = wordpunct_tokenize(t)
    feats = {}
    
    # Palabras clave de "sarcasmo común"
    SARCASM_INDICATORS = ["qué gran", "increíble", "qué sorpresa", "me encanta", "claro", "fascinante"]
    
    for tok in tokens:
        if len(tok) < 2 or tok in sw: continue
        stem = stemmer.stem(tok)
        feats[f"w={stem}"] = True

    # Pistas visuales del sarcasmo
    feats["HAS_EXCLAMATION"] = "!" in text
    feats["HAS_ELLIPSIS"] = "..." in text # Los puntos suspensivos son clave
    feats["LONG_TEXT"] = len(t) > 100
    
    # Detectar frases exageradas al inicio
    lower_text = text.lower()
    feats["HYPERBOLE_START"] = any(lower_text.startswith(x) for x in SARCASM_INDICATORS)
    
    return feats

# --- 3. RE-ENTRENAMIENTO DEL MODELO ---
train_set = [(featurize_sarcasmo(text), label) for text, label in train_data_sarcasmo]
classifier = nltk.NaiveBayesClassifier.train(train_set)

# --- 4. CLASIFICACIÓN DE LOS 200 COMENTARIOS DE LA API ---
out_rows = []
for text in comentarios:
    feats = featurize_sarcasmo(text)
    dist = classifier.prob_classify(feats)
    label = dist.max()
    prob = float(dist.prob(label))
    
    # Traducción para el reporte final
    resultado = "Sarcástico" if label == "sar" else "Normal"
    out_rows.append((text, resultado, f"{prob:.2f}"))

# Guardar resultados
with open("clasificacion_sarcasmo_200.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["texto", "prediccion", "confianza"])
    w.writerows(out_rows)

print("🎯 Clasificación de sarcasmo completada sobre los 200 comentarios.")