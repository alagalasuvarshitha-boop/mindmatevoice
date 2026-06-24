import cv2
import numpy as np
import base64

from face_service import get_face_embedding
from face_match import find_user

def authenticate(base64_image):

    image_data = base64_image.split(",")[1]

    image_bytes = base64.b64decode(image_data)

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    embedding = get_face_embedding(image)

    if embedding is None:
        return None

    return find_user(embedding)