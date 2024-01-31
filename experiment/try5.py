import numpy as np
import cv2

PROTOTXT = "/home/itarato/Desktop/MobileNetSSD_deploy.prototxt"
MODEL = "/home/itarato/Desktop/MobileNetSSD_deploy.caffemodel"

img = cv2.imread("/home/itarato/Desktop/frame2.jpg", cv2.IMREAD_COLOR)

net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
blob = cv2.dnn.blobFromImage(img, 0.007843, (300, 300), 127.5)
h, w = img.shape[:2]
net.setInput(blob)
detections = net.forward()

for i in np.arange(0, detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    if confidence <= 0.5:
        continue

    idx = int(detections[0, 0, i, 1])
    if idx != 7:
        continue

    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
    (startX, startY, endX, endY) = box.astype("int")

    print(startX, startY)
