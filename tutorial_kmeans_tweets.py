from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

stopwords_es = stopwords.words('spanish')
# --- 1. Tweets de ejemplo ---
tweets = [
    # Deportes
    "Fútbol deporte: gran partido de fútbol ayer, el gol fue increíble",
    "Fútbol deporte: el equipo ganó la liga, qué temporada tan buena",
    "Fútbol deporte: Messi anotó un golazo en el último minuto del partido",
    "Fútbol deporte: la selección entrena para el mundial de fútbol",
    "Fútbol deporte: increíble jugada del portero, atajó todo en el partido",
    "Fútbol deporte: el clásico del domingo fue muy emocionante",

    # Tecnología
    "Tecnología software: compré el nuevo iPhone, la cámara es genial",
    "Tecnología software: Python es un gran lenguaje para aprender programación",
    "Tecnología software: la inteligencia artificial va a cambiar todo",
    "Tecnología hardware: actualicé mi laptop y ahora va mucho más rápido",
    "Tecnología hardware: el nuevo procesador tiene un rendimiento increíble",
    "Tecnología software: aprendiendo machine learning con scikit-learn",

    # Comida
    "Comida cocina: los tacos de pastor de aquí son los mejores",
    "Comida cocina: hoy cociné una pasta con salsa de tomate casera",
    "Comida cocina: el café de esta mañana estaba delicioso",
    "Comida restaurante: probé un restaurante nuevo y la pizza estaba buenísima",
    "Comida desayuno: nada como unos chilaquiles para desayunar",
    "Comida receta: receta fácil de arroz con pollo y verduras",

    # Entretenimiento
    "Entretenimiento cine: la nueva película de Marvel es espectacular",
    "Entretenimiento serie: estoy viendo Stranger Things, me encanta la serie",
    "Entretenimiento música: el concierto de anoche fue increíble, la banda tocó sus éxitos",
    "Entretenimiento serie: recomiendo The Crown, es una serie muy bien hecha",
    "Entretenimiento música: el último álbum de Pink Floyd es una obra maestra",
    "Entretenimiento libro: terminé de leer Dune, vaya obra maestra"
]

# --- 2. Vectorizar los tweets con TF-IDF ---
vectorizador = TfidfVectorizer(
    stop_words=stopwords_es,       # podríamos filtrar stopwords del español
    max_features=100,      # usar las 100 palabras más relevantes
    lowercase=True,        # todo a minúsculas
)
X = vectorizador.fit_transform(tweets)

print(f"Matriz TF-IDF: {X.shape[0]} tweets × {X.shape[1]} palabras")

# --- 3. Aplicar K-Means ---
k = 4  # queremos 4 grupos
kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
kmeans.fit(X)

etiquetas = kmeans.labels_  # a qué cluster pertenece cada tweet

# --- 4. Mostrar resultados ---
for cluster_id in range(k):
    print(f"\n{'='*50}")
    print(f"  CLUSTER {cluster_id}")
    print(f"{'='*50}")
    for i, tweet in enumerate(tweets):
        if etiquetas[i] == cluster_id:
            print(f"  • {tweet}")

# --- 5. Palabras clave de cada cluster ---
print(f"\n{'='*50}")
print("  PALABRAS CLAVE POR CLUSTER")
print(f"{'='*50}")
nombres_palabras = vectorizador.get_feature_names_out()
centroides = kmeans.cluster_centers_

for cluster_id in range(k):
    # Obtener las 5 palabras con mayor peso en el centroide
    indices_top = centroides[cluster_id].argsort()[-5:][::-1]
    palabras_top = [nombres_palabras[i] for i in indices_top]
    print(f"  Cluster {cluster_id}: {', '.join(palabras_top)}")

# --- 6. Graficar (reducción a 2D con SVD) ---
from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=2, random_state=42)
X_2d = svd.fit_transform(X)

colores = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6']  # colores para hasta 6 clusters
nombres_cluster = [f'Cluster {i}' for i in range(k)]

plt.figure(figsize=(10, 6))
for cluster_id in range(k):
    mask = etiquetas == cluster_id
    plt.scatter(
        X_2d[mask, 0], X_2d[mask, 1],
        c=colores[cluster_id],
        label=nombres_cluster[cluster_id],
        s=100, alpha=0.7, edgecolors='black'
    )
    for i in range(len(tweets)):
        if etiquetas[i] == cluster_id:
            plt.annotate(
                tweets[i][:25] + "...",
                (X_2d[i, 0], X_2d[i, 1]),
                fontsize=7, alpha=0.8
            )

plt.title("Agrupación de Tweets con K-Means")
plt.xlabel("Componente 1")
plt.ylabel("Componente 2")
plt.legend()
plt.tight_layout()
plt.savefig("kmeans_tweets.png", dpi=150)
plt.show()
print("\nGráfica guardada en kmeans_tweets.png")