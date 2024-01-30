import cv2

img = cv2.imread("fish.jpg")

img[100:110, 100:110] = (0, 0, 255)

cv2.imshow("title", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
