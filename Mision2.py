import cv2
import numpy as np

img = cv2.imread('./expediente/evidencia_2.png')
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

enemy_mask = cv2.inRange(hsv, (60, 50, 50), (66, 255, 255))

result = cv2.bitwise_and(img, img, mask=enemy_mask)

cv2.imshow('Imagen Original', img)
cv2.imshow('Resultado', result)
cv2.imshow('Mascara del enemigo', enemy_mask)

cv2.waitKey(0)
cv2.destroyAllWindows()