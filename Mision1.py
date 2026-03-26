import cv2
import numpy as np

img = cv2.imread('./expediente/evidencia_1.png', cv2.IMREAD_GRAYSCALE)

lsb_imagen = cv2.bitwise_and(img, 1)

mensaje_extraido = ''
byte_actual = ""

for bit in lsb_imagen.flatten():
    byte_actual += str(bit)
    if len(byte_actual) == 8:
        caracter = chr(int(byte_actual, 2))
        mensaje_extraido += caracter
        byte_actual = ""
        
        if mensaje_extraido.endswith("###FIN###"):
            break

print("Mensaje extraído:", mensaje_extraido)



