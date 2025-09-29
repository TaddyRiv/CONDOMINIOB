import cv2
import base64
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/rekognition/verificar-acceso/"

# Inicia la cámara
cap = cv2.VideoCapture(0)  # 0 = webcam por defecto

print("📸 Presiona ESPACIO para capturar, ESC para salir")

while True:
    ret, frame = cap.read()
    cv2.imshow("Captura", frame)

    key = cv2.waitKey(1)
    if key % 256 == 27:  # ESC 
        print("Cerrando cámara...")
        break
    elif key % 256 == 32:  # SPACE
        # Convertir la imagen a base64
        _, buffer = cv2.imencode(".jpg", frame)
        base64_img = base64.b64encode(buffer).decode("utf-8")

        # Enviar al backend
        payload = {"foto": base64_img}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(BASE_URL, data=json.dumps(payload), headers=headers)

        print("➡️ Status:", resp.status_code)
try:
    print("➡️ JSON:", resp.json())
except Exception:
    print("➡️ Texto bruto:", resp.text)
cap.release()
cv2.destroyAllWindows()
