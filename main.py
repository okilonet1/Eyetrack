import cv2
import dlib
import numpy as np


def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype=dtype)

    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    return coords


def eye_on_mask(mask, side):
    points = [shape[i] for i in side]
    points = np.array(points, dtype="int32")
    mask = cv2.fillConvexPoly(mask, points, 255)
    return mask


def contouring(thresh, mid, img, right=False):
    cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    try:
        cnt = max(cnts, key=cv2.contourArea)
        M = cv2.moments(cnt)
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        if right:
            cx = mid + cx
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), 2)
    except:
        pass


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_68.dat")

left = [36, 37, 38, 39, 40, 41]
right = [42, 43, 44, 45, 46, 47]

cap = cv2.VideoCapture(0)
ret, img = cap.read()
thresh = img.copy()

cv2.namedWindow("img", cv2.WINDOW_NORMAL)
kernel = np.ones((9, 9), np.uint8)


def nothing(x):
    pass


cv2.createTrackbar("threshold", "image", 0, 255, nothing)

while (True):
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        mask = np.zeros(img.shape[:2], dtype="uint8")
        mask = eye_on_mask(mask, left)
        mask = eye_on_mask(mask, right)
        mask = cv2.dilate(mask, kernel, 5)
        eyes = cv2.bitwise_and(img, img, mask=mask)
        mask = (eyes == [0, 0, 0]).all(axis=2)
        eyes[mask] = [255, 255, 255]
        mid = (shape[42][0] + shape[43][0]) // 2
        eyes_gray = cv2.cvtColor(eyes, cv2.COLOR_BGR2GRAY)
        threshold = cv2.getTrackbarPos("threshold", "image")
        _, thresh = cv2.threshold(eyes_gray, threshold, 255, cv2.THRESH_BINARY)
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=4)
        thresh = cv2.medianBlur(thresh, 3)
        thresh = cv2.bitwise_not(thresh)
        contouring(thresh[:, :mid], mid, img)
        contouring(thresh[:, mid:], mid, img, True)

    cv2.imshow("eyes", img)
    cv2.imshow("image", thresh)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
