import requests
import pandas as pd

def extraer_primeros_200():
    url_base = "https://datasets-server.huggingface.co/rows"
    dataset_name = "gplsi/SocialTOX"
    
    todos_los_comentarios = []
    
    print(f"📦 Extrayendo los primeros 200 comentarios de {dataset_name}...")

    # Hacemos 2 peticiones (cada una de 100 para completar 200)
    for offset in [0, 100]:
        params = {
            "dataset": dataset_name,
            "config": "default",
            "split": "train",
            "offset": offset,
            "length": 100
        }
        
        try:
            response = requests.get(url_base, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extraemos la información de cada fila
            for item in data['rows']:
                fila = item['row']
                todos_los_comentarios.append({
                    "id": fila.get('id'),
                    "comentario": fila.get('text'),
                    "toxicidad": fila.get('TOXICIDAD'),
                    "constructividad": fila.get('CONST')
                })
                
            print(f"✅ Bloque desde offset {offset} recuperado.")
            
        except Exception as e:
            print(f"❌ Error al obtener el bloque {offset}: {e}")
            break

    # 1. Crear el DataFrame
    df = pd.DataFrame(todos_los_comentarios)

    # 2. Guardar en CSV (usando utf-8-sig para que Excel en Windows no rompa los acentos)
    nombre_archivo = "dataset_redes_sociales_200.csv"
    df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')

    print(f"\n✨ ¡Proceso terminado! Se han guardado {len(df)} comentarios en '{nombre_archivo}'.")

if __name__ == "__main__":
    extraer_primeros_200()