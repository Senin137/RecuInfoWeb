import cv2
import numpy as np

img = cv2.imread('./expediente/evidencia_3_prueba.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

amarillo_pardo_mask = cv2.inRange(hsv, (15, 100, 100), (20, 255, 255)) 

result_mask = cv2.bitwise_and(img, img, mask=amarillo_pardo_mask)
canal_v = hsv[:, :, 2]
pixeles_interes = canal_v[amarillo_pardo_mask > 0]

lsb_img = cv2.bitwise_and(pixeles_interes, 1)
mensaje_extraido = ''
byte_actual = ""

for bit in lsb_img.flatten():
    byte_actual += str(bit)
    if len(byte_actual) == 8:
        caracter = chr(int(byte_actual, 2))
        mensaje_extraido += caracter
        byte_actual = ""
        
        if mensaje_extraido.endswith("###FIN###"):
            break
        
print("Mensaje extraído:", mensaje_extraido)