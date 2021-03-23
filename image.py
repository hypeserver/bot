import sys

import cv2
import numpy as np
import requests
from cv2utils import EyeCascade, FaceDnn
from PIL import Image


class Not2EyesException(Exception):
    pass


def open_url(url, token):
    headers = {"Authorization": "Bearer %s" % (token)}
    return Image.open(requests.get(url, headers=headers, stream=True).raw)


def find_face(image):
    image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    face_detector = FaceDnn()
    faces = face_detector.detect_faces(image)

    if len(faces) != 1:
        raise Exception("not 1 face")

    return faces[0]


def find_eyes(image, face):
    [x, y, x_final, y_final] = face["box"]
    eye_detector = EyeCascade()
    eyes = eye_detector.detect_eyes(image[y:y_final, x:x_final])
    if len(eyes) != 2:
        raise Not2EyesException("not 2 eyes")

    return eyes


def find_eye_center(eye):
    center_x = (eye[0] + eye[2]) / 2
    center_y = (eye[1] + eye[3]) / 2
    eye_center = int(center_x), int(center_y)

    return eye_center


def find_face_center(eyes):
    eye0_center = find_eye_center(eyes[0]["box"])
    eye1_center = find_eye_center(eyes[1]["box"])

    x = int((eye0_center[0] + eye1_center[0]) / 2)
    y = int((eye0_center[1] + eye1_center[1]) / 2)
    center = [x, y]
    center[0] = int(eye0_center[0])
    return center


def get_center(image):
    face = find_face(image)

    center_x = int((face["box"][0] + face["box"][2]) / 2)
    center_y = int((face["box"][1] + face["box"][3]) / 2)
    center = [center_x, center_y]

    return center


def get_half_face(image, center):
    w, h = image.size
    area = (0, 0, center[0], h)
    right_half = image.crop(area)
    return right_half


def hflip_image(image):
    return image.transpose(method=Image.FLIP_LEFT_RIGHT)


def flatten(layer_1, layer_2, box):
    layer_1.paste(layer_2, box)


def crop_or_expand(image, center_x):
    w, h = image.size
    if w >= center_x * 2:
        image = image.crop(box=(0, 0, center_x * 2, h))
    else:
        new_image = Image.new(image.mode, size=(center_x * 2, h))
        new_image.paste(image)
        image = new_image

    return image


def mirror(image=None, image_path=None, save_path=None):
    if image_path:
        image = Image.open(image_path)

    image_array = np.asarray(image)
    print("find center")
    center = get_center(image_array)

    half = get_half_face(image, center)
    flipped = hflip_image(half)

    image = crop_or_expand(image, center[0])
    print("flatten")
    flatten(image, flipped, box=(center[0], 0))

    if save_path:
        image.save(save_path)
    return image


if __name__ == "__main__":
    IMAGE_PATH = sys.argv[1]
    SAVE_PATH = "out.jpg"
    mirror(image_path=IMAGE_PATH, save_path=SAVE_PATH)
