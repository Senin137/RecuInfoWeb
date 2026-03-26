import cv2
import numpy as np
import glob
import os

rutas_img = glob.glob('./images/*.jpg')

colores = {
    'Verde': [np.array([35, 50, 50]), np.array([85, 255, 255])],
    'Rojo_1': [np.array([0, 50, 50]), np.array([10, 255, 255])],
    'Rojo_2': [np.array([170, 50, 50]), np.array([179, 255, 255])],
    'Azul': [np.array([100, 50, 50]), np.array([130, 255, 255])],
    'Amarillo': [np.array([20, 100, 100]), np.array([30, 255, 255])]
}

lower_white = np.array([0, 0, 200])
upper_white = np.array([180, 50, 255])

for i, ruta in enumerate(rutas_img, start=1):
    img = cv2.imread(ruta)

    if img is None:
        print(f"No se pudo leer la imagen: {ruta}")
        continue

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    mask_not_white = cv2.bitwise_not(mask_white)

    total_pixels_interes = cv2.countNonZero(mask_not_white)

    if total_pixels_interes == 0:
        print(f"Imagen {i}: No hay píxeles de interés (todos son blancos).")
        continue

    resultados = {}
    mascaras_colores = {}

    for color_nombre, rangos in colores.items():
        mask = cv2.inRange(hsv, rangos[0], rangos[1])
        mask_final = cv2.bitwise_and(mask, mask_not_white)

        conteo = cv2.countNonZero(mask_final)
        resultados[color_nombre] = conteo
        mascaras_colores[color_nombre] = mask_final

    resultados['Rojo'] = resultados.get('Rojo_1', 0) + resultados.get('Rojo_2', 0)
    mascaras_colores['Rojo'] = cv2.bitwise_or(
        mascaras_colores.get('Rojo_1', np.zeros_like(mask_not_white)),
        mascaras_colores.get('Rojo_2', np.zeros_like(mask_not_white))
    )

    resultados.pop('Rojo_1', None)
    resultados.pop('Rojo_2', None)
    mascaras_colores.pop('Rojo_1', None)
    mascaras_colores.pop('Rojo_2', None)

    color_predominante = max(resultados, key=resultados.get)
    pixeles_ganadores = resultados[color_predominante]
    porcentaje = (pixeles_ganadores * 100) / total_pixels_interes

    nombre_archivo = os.path.basename(ruta)

    print(f"\n--- Análisis de Color: {nombre_archivo} ---")
    print(f"Píxeles totales (sin blanco): {total_pixels_interes}")
    print(f"Color predominante: {color_predominante}")
    print(f"Porcentaje: {porcentaje:.2f}%")

    print("Porcentaje por color:")
    for nombre, conteo in resultados.items():
        porcentaje_color = (conteo * 100) / total_pixels_interes
        print(f"  {nombre}: {porcentaje_color:.2f}%")

    mask_ganadora = mascaras_colores[color_predominante]
    imagen_resultado = cv2.bitwise_and(img, img, mask=mask_ganadora)

    cv2.imshow(f"Original {i} - {nombre_archivo}", img)
    cv2.imshow(f"Predominante {i} - {color_predominante}", imagen_resultado)
    cv2.waitKey(0)
    cv2.destroyAllWindows()