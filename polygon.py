

import cv2


cap = cv2.VideoCapture(0)
_, frame = cap.read()

while True:
    _, frame = cap.read()
    cv2.imshow("Nothing", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break