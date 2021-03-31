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

    return faces[0]["box"]


def find_eyes(image, face):
    [x, y, x_final, y_final] = face
    x = 0 if x < 0 else x
    y = 0 if y < 0 else y
    eye_detector = EyeCascade()
    eyes = eye_detector.detect_eyes(image[y:y_final, x:x_final])
    if len(eyes) < 2:
        raise Not2EyesException("not 2 eyes")

    return eyes[:2]


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

    center_x = int((face[0] + face[2]) / 2)
    center_y = int((face[1] + face[3]) / 2)
    center = [center_x, center_y]

    return center


def get_half_face(image, center, side="right"):
    w, h = image.size
    if side == "left":
        area = (0, 0, center[0], h)
    elif side == "right":
        area = (center[0], 0, w, h)
    half = image.crop(area)
    return half


def hflip_image(image):
    return image.transpose(method=Image.FLIP_LEFT_RIGHT)


def flatten(layer_1, layer_2, box):
    layer_1.paste(layer_2, box)


def crop_or_expand(image, center_x, side='right'):
    w, h = image.size

    if side == 'right':
        face_width = center_x * 2
    if side == 'left':
        face_width = (w - center_x) *2

    if w >= face_width:
        image = image.crop(box=(w - face_width , 0, w, h))
    else:
        new_image = Image.new(image.mode, size=(face_width, h))
        new_image.paste(image)
        image = new_image

    return image


def mirror(image=None, image_path=None, save_path=None, side='right'):
    if image_path:
        image = Image.open(image_path)

    image_array = np.asarray(image)
    center = get_center(image_array)

    half = get_half_face(image, center, side)
    flipped = hflip_image(half)

    image = Image.new(image.mode, size=(half.size[0]*2, half.size[1]))
    if side == 'right':
        image.paste(flipped)
        image.paste(half, box=(half.size[0], 0))
    elif side == 'left':
        image.paste(half)
        image.paste(flipped, box=(half.size[0], 0))

    if save_path:
        image.save(side + "_" + save_path)
    return image


if __name__ == "__main__":
    IMAGE_PATH = sys.argv[1]
    SAVE_PATH = "out.jpg"
    mirror(image_path=IMAGE_PATH, save_path=SAVE_PATH, side='right')
    mirror(image_path=IMAGE_PATH, save_path=SAVE_PATH, side='left')
