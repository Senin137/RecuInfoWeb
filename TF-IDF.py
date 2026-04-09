import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from sklearn.decomposition import TruncatedSVD

documentos = [
"El aprendizaje automático es una rama de la inteligencia artificial que permite a las computadoras aprender a partir de datos sin ser programadas explícitamente. Se utiliza en aplicaciones como reconocimiento de voz, visión por computadora y sistemas de recomendación.",
"La salud pública se enfoca en la prevención de enfermedades y la promoción del bienestar en la población. Incluye campañas de vacunación, educación sanitaria y el control de epidemias.",
"El fútbol es uno de los deportes más populares en el mundo. Requiere habilidades físicas, trabajo en equipo y estrategias para anotar goles y ganar partidos.",
"Los sistemas de inteligencia artificial pueden analizar grandes volúmenes de datos para identificar patrones y tomar decisiones automatizadas en diversos contextos.",
"La educación moderna incorpora tecnologías digitales para mejorar el aprendizaje. Plataformas en línea, simuladores y recursos interactivos facilitan la enseñanza.",
"El cambio climático afecta a los ecosistemas  y provoca fenómenos extremos como sequías, inundaciones y aumento de temperatura global.",
"La inflación es el aumento generalizado de los precios de bienes y servicios en una economía durante un periodo de tiempo.",
"Las redes neuronales profundas permiten el desarrollo de sistemas avanzados de reconocimiento de imágenes y procesamiento de lenguaje natural.",
"Una alimentación balanceada y el ejercicio regular son fundamentales para prevenir enfermedades y mantener una buena calidad de vida.",
"El aprendizaje en línea ha crecido significativamente gracias al acceso a internet y a plataformas digitales educativas."
]

nltk.download('stopwords')

stop_words = stopwords.words('spanish')

vectorizer = TfidfVectorizer(stop_words=stop_words)
X = vectorizer.fit_transform(documentos)

print(X.shape)

svd = TruncatedSVD(n_components=2)
X_reducido = svd.fit_transform(X)

print(X_reducido)