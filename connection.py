import xmlrpc.client
import base64
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import os
import io
import face_recognition
import cv2 as cv

load_dotenv()

# Informações de configuração
url_odoo = os.getenv("ODOO_URL")
db = os.getenv("DB_ODOO")
username = os.getenv("USER_ODOO")
password = os.getenv("PASS_ODOO")

# Autenticação
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo))

ids = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[]], {'fields': ['name', 'image_1920', 'ref', 'category_id']})

# Carrega vídeo
cap = cv.VideoCapture(0)
cap.set(3,1280)
cap.set(4, 720)

while True:
    success, img = cap.read()

    imgS = cv.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    if faceCurFrame:
        for id in ids:
            try:
                image_data = base64.b64decode(id['image_1920'])
                image = Image.open(io.BytesIO(image_data))
                known_array = np.array(image)
                # image_array = cv.cvtColor(known_array, cv.COLOR_BGR2GRAY)
                face_locat = face_recognition.face_locations(known_array)
                encodeCurFrame = face_recognition.face_encodings(known_array, face_locat)


                # print(compare)
                # if compare == True:
                #     print(f"Bateu o usuario {id['name']}")
                #     break
                # else:
                #     print(f"Não bateu o usuario {id['name']}")


            except BaseException:
                print(f"Usuario {id['name']} não tem imagem")
                continue
            compare = face_recognition.compare_faces(known_array, encodeCurFrame)
            # image_array = cv.cvtColor(known_array, cv.COLOR_BGR2GRAY)
            # face_locat = face_recognition.face_locations(image_array)
            # encodeCurFrame = face_recognition.face_encodings(image_array, face_locat)
            # compare = face_recognition.compare_faces(image_array, encodeCurFrame)

            # print(compare)
            # if compare == True:
            #     print(f"Bateu o usuario {id['name']}")
            #     break
            # else:
            #     print(f"Não bateu o usuario {id['name']}")


