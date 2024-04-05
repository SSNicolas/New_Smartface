import xmlrpc.client
import base64
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import os
import io
import face_recognition
import cv2 as cv
import pickle

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

ids = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[]], {'fields': ['name', 'image_1920', 'ref', 'category_id', 'id', 'comment']})

# Carrega vídeo
cap = cv.VideoCapture(0)
cap.set(3,1280)
cap.set(4, 720)

while True:
    # Frame do Vídeo
    success, img = cap.read()
    imgS = cv.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    if faceCurFrame:
        for encodeFace in encodeCurFrame:
            for id in ids:
                if id['ref'] == 'a':

                    # _______________________________________________________

                    # TESTAR FAZER O SAVE DO BASE64 NO CAMPO REF
                    # OU
                    # DESCOBRIR UM MEIO DE TRAZER OS DADOS DO CAMPO 'COMMENT'

                    # _______________________________________________________
                    decode = id['comment']
                    print(decode)
                    face_encod_return = base64.b64decode(id['comment'])
                    print(face_encod_return)
                    face_encod = pickle.loads(face_encod_return)

                    compare = face_recognition.compare_faces(face_encod, encodeFace)  # Comparar com cada face detectada
                    # if True in compare:  # Se encontrar uma correspondência
                    #     print(f"Bateu o usuário {id['name']}")
                    #     break

                # except BaseException as e:
                #     print(f"Usuario {id['name']} não tem imagem {e}")
                #     continue










