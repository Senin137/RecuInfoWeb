#OpenCV
import cv2 as cv
import numpy as np
import glob
import os

videos = glob.glob('./video/*.mp4')

if not os.path.exists('capturas'):
    os.makedirs('capturas')

for video_path in videos:
    print(f"Procedando video: {videos}")
    cap = cv.VideoCapture(video_path)
    i = 0
    
    while (cap.isOpened()):
        ret, img = cap.read()
        
        if not ret:
            print(f"Final del video: {video_path}")
            break
        
        cv.imshow('Video', img)
        
        nombre_video = os.path.basename(video_path).split('.')[0]
        cv.imwrite(f'capturas/{nombre_video}_frame_{i}.jpg', img)
        
        i += 1
        
        k = cv.waitKey(1) & 0xFF
        
        if k == 27:
            print(f"Video detenido por el usuario: {video_path}")
            break
    
    cap.release()
        
cv.destroyAllWindows()
print("Programa tieso")