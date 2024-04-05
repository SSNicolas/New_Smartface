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


def encoder():
    ids = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[]], {'fields': ['name', 'image_1920', 'ref', 'category_id', 'id', 'comment']})
    for id in ids:
        if id['image_1920'] and id['id'] != 1:
            if id['ref'] != 'a':
                # b64 para data
                image_data = base64.b64decode(id['image_1920'])
                # data para binario
                image = Image.open(io.BytesIO(image_data))
                # binario para array np
                known_array = np.array(image)

                # comeca o encode
                face_locat = face_recognition.face_locations(known_array)
                face_encod = face_recognition.face_encodings(known_array, face_locat)
                face_encod_pickle = pickle.dumps(face_encod)
                face_encod_base64 = base64.b64encode(face_encod_pickle).decode('utf-8')
                print(face_encod_base64)
                # salva no dados para o Odoo
                models.execute_kw(db, uid, password, 'res.partner', 'write', [[id['id']], {'comment': face_encod_base64, 'ref': 'a'}])
                print(f'{id['name']} b64 saved')
            else:
                print(f'{id['name']} pass')
                pass
    encoder()


encoder()