import time
import xmlrpc.client
import base64
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import datetime
import os
import io
import face_recognition
import cv2 as cv
import pickle
import re

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

def is_date(string):
    # Validação se é datetime
    try:
        date_format = datetime.datetime.strptime(string, '%d-%m-%Y %H:%M:%S')
        return date_format
    except ValueError as e:
        print(f'ERROR: {e}')
        return datetime.datetime.strftime(datetime.datetime(9999, 1, 1, 0, 0), '%d-%m-%Y %H:%M:%S')


# Carrega vídeo
cap = cv.VideoCapture(0)
cap.set(3,1280)
cap.set(4, 720)

# start_time_detection = {}

while True:
    ids = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[]], {'fields': ['name', 'image_1920', 'ref', 'category_id', 'id', 'comment']})
    # Frame do Vídeo
    success, img = cap.read()
    imgS = cv.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv.cvtColor(img, cv.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    # for (top, right, bottom, left) in faceCurFrame:
    #     # Extrair a região da face
    #     face_image = imgS[top:bottom, left:right]
    #     # Aplicar modelo de estimativa de idade
    #     idade = estimate_age(face_image)
    #     print(f"Idade estimada: {idade} anos")
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    if faceCurFrame:
        current_time = datetime.datetime.now()
        for encodeFace in encodeCurFrame:
            for id in ids:
                user_found = False
                if id['image_1920'] and id['id'] != 1:
                    try:
                        clean_decode = base64.b64decode(re.sub(r'<p>|</p>', '', id['comment']))
                        # print(face_encod_return)
                        face_encod = pickle.loads(clean_decode)

                        compare = face_recognition.compare_faces(face_encod, encodeFace)  # Comparar com cada face detectada
                        # Usuario encontrado

                        # @todo Arrumar o compare
                        if True in compare:
                            # if id['id'] not in start_time_detection:
                            #     start_time_detection[id['id']] = current_time
                            #     print(start_time_detection)
                            #     print(f'{id['name']} foi adicionado a lista')
                            #     print(start_time_detection)

                            # elif current_time - start_time_detection[id['id']] >= datetime.timedelta(seconds=5):
                            if is_date(id['ref']) <= datetime.datetime.now():
                                print(f'Usuario {id['name']} bateu? {compare}')
                                models.execute_kw(db, uid, password, 'res.partner', 'write', [[id['id']], {'ref': datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(minutes=5), '%d-%m-%Y %H:%M:%S')}, ])
                                pass

                            elif is_date(id['ref']) > datetime.datetime.now():
                                print(f'Usuario {id['name']} está em cooldown até as {id['ref']}')
                                pass

                            # del start_time_detection[id['id']]
                            user_found = True
                            break

                        # Usuario não encontrado

                    except BaseException as e:
                        print(f'ERROR: {id['name'], e}')
                        continue

            if not user_found:
                # Funcionalidade de cadastro
                print('Não bateu')


        # if id['id'] in start_time_detection or is_date(id['ref']) > datetime.datetime.now():
        #     print(f'Cooldown {id['ref']}')

















