import numpy as np
import cv2

PROTOTXT = "/home/itarato/Desktop/MobileNetSSD_deploy.prototxt"
MODEL = "/home/itarato/Desktop/MobileNetSSD_deploy.caffemodel"
# INP_VIDEO_PATH = "cars.mp4"
# OUT_VIDEO_PATH = "cars_detection.mp4"
# GPU_SUPPORT = 0
CLASSES = [
    "background",
    "aeroplane",
    "bicycle",
    "bird",
    "boat",
    "bottle",
    "bus",
    "car",
    "cat",
    "chair",
    "cow",
    "diningtable",
    "dog",
    "horse",
    "motorbike",
    "person",
    "pottedplant",
    "sheep",
    "sofa",
    "train",
    "tvmonitor",
]
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

img = cv2.imread("/home/itarato/Desktop/frame2.jpg", cv2.IMREAD_COLOR)

net = cv2.dnn.readNetFromCaffe(PROTOTXT, MODEL)
# if GPU_SUPPORT:
#     net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
#     net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

blob = cv2.dnn.blobFromImage(img, 0.007843, (300, 300), 127.5)
h, w = img.shape[:2]

net.setInput(blob)
detections = net.forward()

print(len(detections))

for i in np.arange(0, detections.shape[2]):
    confidence = detections[0, 0, i, 2]
    if confidence > 0.5:
        idx = int(detections[0, 0, i, 1])
        if idx == 7 or idx == 1:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            cv2.rectangle(img, (startX, startY), (endX, endY), COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(
                img, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2
            )


cv2.imshow("title", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
