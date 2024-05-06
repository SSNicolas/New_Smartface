import signal
import time
import zmq
import xmlrpc.client
import base64
from PIL import Image
import numpy as np
from dotenv import load_dotenv
import datetime
import requests
import os
import io
import face_recognition
import cv2 as cv
import pickle
import re
from concurrent.futures import ThreadPoolExecutor

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


# Funções para mensagens
def send_message(func, *args, **kwargs):
    with ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result()


def create_attachment(base64_image):
    attachment_id = models.execute_kw(
        db, uid, password, 'ir.attachment', 'create', [{
            'name': "image",
            'type': 'binary',
            'datas': base64_image,
            'res_model': 'mail.channel',
            'res_id': 0,
            'mimetype': 'image/png',
        }])
    return attachment_id


def create_vip_message(attachment_id, bot_id, nome_membro, channel_id):
    message = f"O usuário VIP {nome_membro} chegou!"
    models.execute_kw(db, uid, password, 'discuss.channel', 'message_post', [channel_id], {
        'body': message,
        'message_type': 'comment',
        'subtype_xmlid': 'mail.mt_comment',
        'author_id': bot_id,
        'attachment_ids': [attachment_id],
    })


def create_user_message(user_name, bot_id, channel_id):
    message = f"O usuário {user_name} chegou!"
    models.execute_kw(db, uid, password, 'discuss.channel', 'message_post', [channel_id], {
        'body': message,
        'message_type': 'comment',
        'subtype_xmlid': 'mail.mt_comment',
        'author_id': bot_id,
    })


def create_unknown_user_message(bot_id, channel_id):
    message = "Um usuario chegou"
    models.execute_kw(db, uid, password, 'discuss.channel', 'message_post', [channel_id], {
        'body': message,
        'message_type': 'comment',
        'subtype_xmlid': 'mail.mt_comment',
        'author_id': bot_id,
    })


def create_log(message, attachment_id, contact_id):
    models.execute_kw(db, uid, password, 'res.partner', 'message_post', [contact_id], {
        'body': message,
        'attachment_ids': [attachment_id],  # Referencia o anexo criado
        'subtype_xmlid': 'mail.mt_note',
    })

def update_cdtime(id_user):
    models.execute_kw(db, uid, password, 'res.partner', 'write', [[id_user], {
        'ref': datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(minutes=5), '%d-%m-%Y %H:%M:%S')}, ])


# Inicialização do ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Carrega vídeo
# cap = cv.VideoCapture(os.getenv("URL_RTSP"), cv.CAP_FFMPEG)
cap = cv.VideoCapture(os.getenv("URL_RTSP"), cv.CAP_FFMPEG)
# cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
# cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)


scale_factor = 1.9

frame_count = 0
# @ todo
frame_skip = 30

while True:
    # try:
    # Frame Vídeo
    ret, img = cap.read()
    if not ret:
        print("Erro na captura do frame")
        break
    ids = models.execute_kw(db, uid, password, 'res.partner', 'search_read', [[]], {'fields': ['name', 'image_1920', 'ref', 'category_id', 'id', 'comment']})
    frame_count += 1
    if frame_count % 2 == 0:  # Process for each 2 frames
        try:
            imgS = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        except cv.error as e:
            print(f"Erro ao converter cor do frame: {e}")
        # todo
        # face location
        faceCurFrame = face_recognition.face_locations(imgS, model="hog")
        # face encoding
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)


        # verificação de frame atual
        if faceCurFrame:
            for index_lista, encodeFace in enumerate(encodeCurFrame):
                # posicoes da face na imagem original
                top, right, bottom, left = faceCurFrame[index_lista]
                # configuracao pra diminuir a imagem dentro da parada
                face_width = right - left
                face_height = bottom - top
                left = max(int(left - face_width * ((scale_factor - 1) / 2)), 0)
                top = max(int(top - face_height * ((scale_factor - 1) / 2)), 0)
                right = min(int(right + face_width * ((scale_factor - 1) / 2)), img.shape[1])
                bottom = min(int(bottom + face_height * ((scale_factor - 1) / 2)), img.shape[0])
                face_image = img[top:bottom, left:right] # todo trocar o img por imgS e Testes
                _, encoded_face = cv.imencode('.jpg', face_image)
                encoded_face_str = base64.b64encode(encoded_face).decode('utf-8')

                bot_id = 1
                channel_id = models.execute_kw(db, uid, password, 'discuss.channel', 'search', [[['name', '=', 'Administrator']]])
                user_found = False
                for index, id in enumerate(ids):
                    if id['image_1920'] and id['id'] != 1:
                        try:
                            clean_decode = base64.b64decode(re.sub(r'<p>|</p>', '', id['comment']))
                            # print(face_encod_return)
                            face_encod = pickle.loads(clean_decode)

                            compare = face_recognition.compare_faces(face_encod, encodeFace)  # Comparar com cada face detectada
                            # Usuario encontrado

                            if True in compare and index < len(ids):
                                print(id['category_id'])
                                # @todo envio de mensagem no Odoo e funcionalidade de VIP
                                if is_date(id['ref']) <= datetime.datetime.now():
                                    print(f'Usuario {id['name']} bateu? {compare}')
                                    # Set cooldown each user to 5 minutes
                                    send_message(update_cdtime, id_user=id['id'])  # Coodown time

                                    # VIP User
                                    if id['category_id'] == [1]:
                                        send_message(create_vip_message, create_attachment(encoded_face_str), bot_id=bot_id, nome_membro=id['name'], channel_id=channel_id) # VIP Message

                                    # Normal User
                                    elif not id['category_id']: # todo
                                        send_message(create_user_message, user_name=id['name'], bot_id=bot_id, channel_id=channel_id) # user message

                                    # Log creation of each user
                                    message = f"Data e hora de chegada {datetime.datetime.strftime(datetime.datetime.now(), '%d-%m-%Y %H:%M:%S')}"
                                    send_message(create_log, message=message, attachment_id=create_attachment(encoded_face_str), contact_id=id['id']) # log creation

                                # User cooldown alert (the configuration is above)
                                elif is_date(id['ref']) > datetime.datetime.now():
                                    print(f'Usuario {id['name']} está em cooldown até as {id['ref']}')
                                    pass

                                user_found = True
                                break

                        except BaseException as e:
                            print(f'ERROR: {id['name'], e}')
                            continue

                if not user_found:
                    # Funcionalidade de cadastro
                    print('Não bateu')
                    message = f"{'----------------'},{imgS},{encoded_face_str},{top},{right},{bottom},{left}" # todo testar se ta funcionando normalmente
                    socket.send_string(message)
                    response = socket.recv_string()  # send / receive a string message between archives
                    create_unknown_user_message(bot_id=bot_id, channel_id=channel_id)
                    print(response)

            print('time')
            time.sleep(3)
        else:
            print('Nenhum rosto identificado')
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
            # if id['id'] in start_time_detection or is_date(id['ref']) > datetime.datetime.now():
            #     print(f'Cooldown {id['ref']}')
    # finally:
    #     executor.shutdown(wait=True)












