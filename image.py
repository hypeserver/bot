from PIL import Image, ImageDraw
import numpy as np
import face_recognition
import requests

def open_url(url, token):
    headers = {"Authorization": "Bearer %s"%(token)}
    return Image.open(requests.get(url, headers=headers, stream=True).raw)

def face_features(image):
    faces = face_recognition.face_landmarks(image)

    if len(faces) > 1: 
        raise Exception # TODO: more than 1 person
    else:
        return faces[0]

def find_eye_center(eye):
    x, y = zip(*eye)
    center_x = sum(x) / len(x)
    center_y = sum(y) / len(y)
    eye_center = int(center_x), int(center_y) ###

    return eye_center

def find_face_center(face):
    left_eye_center,right_eye_center = find_eye_center(face['left_eye']), find_eye_center(face['right_eye'])
    
    x = int((left_eye_center[0] + right_eye_center[0]) / 2)
    y = int((left_eye_center[1] + right_eye_center[1]) / 2)

    return x,y 

def get_center(image):
    sample_face = face_features(image)
    center = find_face_center(sample_face)

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
    w,h = image.size
    if w >= center_x*2:
        image = image.crop(box=(0,0,center_x*2,h))
    else:
        new_image = Image.new(image.mode, size=(center_x*2, h))
        new_image.paste(image)
        image = new_image

    return image

def mirror(image = None, image_path=None, save_path=None):
    if image_path:
        image = Image.open(image_path)
    
    image_array = np.asarray(image)
    print('find center')
    center = get_center(image_array)

    half = get_half_face(image, center)
    flipped = hflip_image(half)
    
    image = crop_or_expand(image, center[0])
    print('flatten')
    flatten(image, flipped, box=(center[0],0))

    if save_path:
        image.save(save_path)
    return image

if __name__ == "__main__":
    mirror(IMAGE_PATH, SAVE_PATH)
