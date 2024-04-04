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
import cvzone


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

for id in ids:
    img_b64 = id['image_1920']
    try:
        image_data = base64.b64decode(img_b64)
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        print(id['name'])

    except BaseException:
        print(f"Usuario {id['name']} não tem imagem")
        continue

    image_array = cv.cvtColor(image_array, cv.COLOR_BGR2GRAY)
    face_locations = face_recognition.face_locations(image_array)
    print(face_locations)