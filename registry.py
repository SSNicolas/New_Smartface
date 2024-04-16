import base64
import xmlrpc.client
import time
from dotenv import load_dotenv
import os
from datetime import datetime
import requests
import zmq
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

# Inicialização do ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


def create_partner(self, name, ref, image_1920):
    partner_id = self.models.execute_kw(
        db, self.uid, password, 'res.partner', 'create', [{
            'name': name,
            'ref': ref,
            'image_1920': image_1920,
        }])
    return partner_id

while True:
    # Aguardar uma mensagem
    message = socket.recv_string()
    socket.send_string("Mensagem recebida com sucesso!")
    user_name, img_all, face_img, top, right, bottom, left = message.split(",")
    models.execute_kw(db, uid, password, 'res.partner', 'create', [{'name': user_name, 'image_1920': face_img, 'ref': 0}])
    print('Cadastrado!')  # todo testar se ta funcionando normalmente

    # encodeFaceloc = face_recognition.face_landmarks(user_face)
    # Aqui você pode adicionar a lógica para lidar com os dados recebidos
    # face_location = user_face
    # top, right, bottom, left = face_location
    # face_image = img_all[top:bottom, left:right]
    # print(face_image)

    # Enviar uma resposta de confirmação
