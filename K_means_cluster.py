from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

docs = [
    "Un grupo de vigilantes se dispuso a acabar con los superhéroes corruptos que abusan de sus superpoderes.",
    "Una batalla entre las personas corrientes y los superhéroes tiene lugar cuando estos últimos deciden desvelar la verdad sobre “Los Siete” y una corporación multinacional todopoderosa que maneja a los superhéroes y oculta todos sus sucios secretos, llamada Vought.",
    "Hughie Campbell es un simple vendedor de una tienda de tecnología que vive su día a día junto a su pareja, hasta que un superhéroe de Los Siete, llamado A-Tren, la mata traspasarle literalmente mediante su supervelocidad.",
    "¡Estás invitado al 70º Herogasmo anual. Las mismas reglas de siempre: ¡nada de cámaras, nada de invitados que no sean de Supe a menos que firmen un acuerdo de confidencialidad y sean DTF, y nada de informar a los medios de comunicación.",
    "Butcher pierde la oportunidad de matar a Homelander utilizando a Soldier Boy, intenta volver a poner a Ryan de su lado y corregir sus errores. Mientras tanto, Homelander busca un nuevo aliado en su lucha por aceptar su mortalidad.",
    "C# es un lenguaje de programaciónmoderno, innovador, de código abierto, multiplataforma orientado a objetos y uno de los 5 principales lenguajes de programación de GitHub.",
    "Es uno de los lenguajes de programación más populares del mundo.",
    "C# es un lenguaje orientado a objetos que proporciona una estructura clara a los programas y permite reutilizar el código, reduciendo los costos de desarrollo.",
    "Las aplicaciones escritas en C# utilizan .NET Framework, por lo que tiene sentido usar Visual Studio, ya que tanto el programa como el framework y el lenguaje son creados por Microsoft.",
    "Las variables son identificadores asociados a valores. Se declaran indicando el tipo de dato que almacenará y su identificador. Un identificador puede:"
]
print("Docs:", len(docs))

X = TfidfVectorizer(ngram_range=(2,2), min_df=1).fit_transform(docs)
kmeans = KMeans(n_clusters=2, n_init="auto", random_state=42)
labels = kmeans.fit_predict(X)

for d, c in zip(docs, labels):
    print(c, "-", d)
