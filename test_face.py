import cv2
from face_service import get_face_embedding

image = cv2.imread("test.jpg")

embedding = get_face_embedding(image)

if embedding is not None:
    print("Face Found")
    print(len(embedding))
else:
    print("No Face Found")