import time
from graphql_client import GraphQLClient
from dotenv import load_dotenv
import os
from datetime import datetime
import requests
import base64
import xmlrpc.client
from twilio.rest import Client

load_dotenv()
listando_ids = {}
lista_ids = []


# Criação do conector com os dados do Odoo
class OdooConnector:
    def __init__(self, url, db, username, password):
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(db, username, password, {})
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Pega a imagem enviada no chat do contato e prepara ela pra mensagem de log
    def create_attachment(self, base64_image):
        attachment_id = self.models.execute_kw(
            db, self.uid, password, 'ir.attachment', 'create', [{
                'name': "image",
                'type': 'binary',
                'datas': base64_image,
                'res_model': 'mail.channel',
                'res_id': 0,
                'mimetype': 'image/png',
            }])
        return attachment_id

    # Faz o cadastro de um usuario VIP no Odoo com a tag
    def create_VIP_partner(self, name, ref, image_1920):
        partner_id = self.models.execute_kw(
            db, self.uid, password, 'res.partner', 'create', [{
                'name': name,
                'category_id': [(4, 1)],
                'ref': ref,
                'image_1920': image_1920,
            }])
        return partner_id

    # Faz o cadastro de um usuario comum no Odoo
    def create_partner(self, name, ref, image_1920):
        partner_id = self.models.execute_kw(
            db, self.uid, password, 'res.partner', 'create', [{
                'name': name,
                'ref': ref,
                'image_1920': image_1920,
            }])
        return partner_id

    # Pega a imagem e envia a mensagem no chat pra notificação -- Esse é pro VIP
    def create_message(self, attachment_id, bot_id, nome_membro, channel_id):
        message = f"O usuário VIP {nome_membro} chegou"
        self.models.execute_kw(db, self.uid, password, 'discuss.channel', 'message_post', [channel_id], {
            'body': message,
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_comment',
            'author_id': bot_id,
            'attachment_ids': [attachment_id],
        })

    # Envia a mensagem no chat pra notificação -- Esse é pro Usuario comum
    def create_message_each_user(self, bot_id, channel_id):
        message = "Um usuario chegou"
        self.models.execute_kw(db, self.uid, password, 'discuss.channel', 'message_post', [channel_id], {
            'body': message,
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_comment',
            'author_id': bot_id,
        })

# Criação da classe relacionada realmente ao reconhecimento facial
class FaceRecognition:
    contador = 0
    marca_id = ""

    # Inicia e recebe a variavel do conector odoo
    def __init__(self, odoo_connector):
        self.odoo_connector = odoo_connector

    # Transforma a imagem pega no código, em um base64
    def url_base64(self, image_url):
        response = requests.get(image_url)
        base64_data = base64.b64encode(response.content)
        return base64_data.decode('utf-8')

    # Faz o envio da mensagem em SMS, mas provavelmente não vai ser usado
    # def enviar_sms_twilio(self, mensagem):
    #     account_sid = os.getenv('TWILIO_ACCOUNT_SID') # envs
    #     auth_token = os.getenv('TWILIO_AUTH_TOKEN') # envs
    #     numero_twilio = os.getenv('TWILIO_PHONE_NUMBER') # envs
    #     numero_destino = '+5511976267951'
    #
    #     cliente = Client(account_sid, auth_token)
    #     mensagem_enviada = cliente.messages.create(
    #         body=mensagem,
    #         from_=numero_twilio,
    #         to=numero_destino
    #     )
    #     print(f"Mensagem enviada com sucesso! SID: {mensagem_enviada.sid}")

    # Código pra caso reconheça alguém cadastrado no Innovatrics
    def process_match_result(self, data):
        nome_membro = data['payload']['data']['matchResult']['watchlistMemberDisplayName']
        nome_watchlist = data['payload']['data']['matchResult']['watchlistDisplayName']
        validacao_face = data['payload']['data']['matchResult']['score']
        id_reconhecimento = data['payload']['data']['matchResult']['trackletId']
        id_membro = data['payload']['data']['matchResult']['watchlistMemberId']
        face_id = data['payload']['data']['matchResult']['faceId']
        face_url = f'http://localhost:8098/api/v1/Faces/{face_id}'

        response = requests.get(face_url)
        faceimg_info = response.json()
        faceimage_data_id = faceimg_info.get('imageDataId')

        facematch_img_url = f'http://localhost:8098/api/v1/Images/{faceimage_data_id}'

        base64_image = self.url_base64(facematch_img_url)
        
        if nome_watchlist == 'VIPs' and validacao_face >= 50 and id_reconhecimento not in listando_ids:
            print("VIP")

            # Se tirar o comentario, faz o envio de SMS no celular To, mas é muito travado
            # face_recognition.enviar_sms_twilio(f"VIP {nome_membro} chegou!")

            ref_ids = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'search', [[['ref', '=', id_membro]]])

            if ref_ids:
                print("VIP já cadastrado o Odoo.")
                contact_id = ref_ids[0]

                attachment_id = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'ir.attachment',
                                                                 'create', [{
                        'name': "image",
                        'datas': base64_image,
                        'res_model': 'res.partner',
                        'res_id': contact_id,  # O ID do contato a que a imagem será associada
                        'mimetype': 'image/png',  # Indica que é um arquivo, não uma URL
                    }])

                message = f"{nome_membro} chegou as {datetime.now()}"

                odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'message_post',
                                                 [contact_id], {
                                                     'body': message,
                                                     'attachment_ids': [attachment_id],  # Referencia o anexo criado
                                                     'subtype_xmlid': 'mail.mt_note',
                                                 })

                print(f'Log do vip {nome_membro} atualizado!')

            listando_ids[id_reconhecimento] = []
            lista_ids.append(id_reconhecimento)

        elif nome_watchlist == 'Users' and validacao_face >= 50 and id_reconhecimento not in listando_ids:
            print("User")
            ref_ids = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'search', [[['ref', '=', id_membro]]])
            if ref_ids:
                print("User já cadastrado no Odoo")
                contact_id = ref_ids[0]

                attachment_id = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'ir.attachment',
                                                                 'create', [{
                        'name': "image",
                        'datas': base64_image,
                        'res_model': 'res.partner',
                        'res_id': contact_id,  # O ID do contato a que a imagem será associada
                        'mimetype': 'image/png',  # Indica que é um arquivo, não uma URL
                    }])

                message = f"Usuario apareceu as {datetime.now()}"

                odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'message_post',
                                                 [contact_id], {
                                                     'body': message,
                                                     'attachment_ids': [attachment_id],  # Referencia o anexo criado
                                                     'subtype_xmlid': 'mail.mt_note',
                                                 })

                print(f'Log do usuário atualizado!')

            listando_ids[id_reconhecimento] = []
            lista_ids.append(id_reconhecimento)

        elif id_reconhecimento in listando_ids and len(listando_ids[id_reconhecimento]) < 1:
            listando_ids[id_reconhecimento].append(id_reconhecimento)

            ref_id = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'search', [[['ref', '=', id_membro]]])
            if ref_id:
                contact_id = ref_id[0]

                attachment_id = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'ir.attachment', 'create', [{
                    'name': "image",
                    'datas': base64_image,
                    'res_model': 'res.partner',
                    'res_id': contact_id,  # O ID do contato a que a imagem será associada
                    'mimetype': 'image/png',  # Indica que é um arquivo, não uma URL
                }])

                message = f"Usuario apareceu as {datetime.now()}"

                odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'message_post', [contact_id], {
                    'body': message,
                    'attachment_ids': [attachment_id],  # Referencia o anexo criado
                    'subtype_xmlid': 'mail.mt_note',
                })

                print(f'Mensagem enviada para {nome_membro} em {datetime.now()}')

        elif validacao_face < 50:
            print("Score abaixo de 50")

    # Código pra caso a pessoa não esteja cadastrado no Innovatrics
    def process_no_match_result(self, data):
        reg_url = 'http://localhost:8098/api/v1/WatchlistMembers/Register'
        face_id = data['payload']['data']['noMatchResult']['faceId']
        frame_id = data['payload']['data']['noMatchResult']['frameId']
        nomatch_id = data['payload']['data']['noMatchResult']['id']
        id_reconhecimento = data['payload']['data']['noMatchResult']['trackletId']

        face_url = f'http://localhost:8098/api/v1/Faces/{face_id}'
        frame_url = f'http://localhost:8098/api/v1/Frames/{frame_id}'

        response = requests.get(face_url)
        faceimg_info = response.json()
        print(faceimg_info)
        faceimage_data_id = faceimg_info.get('imageDataId')

        response = requests.get(frame_url)
        frameimg_info = response.json()
        frameimage_data_id = frameimg_info.get('imageDataId')

        face_img_url = f'http://localhost:8098/api/v1/Images/{faceimage_data_id}'
        frame_img_url = f'http://localhost:8098/api/v1/Images/{frameimage_data_id}'

        facebase64_image = self.url_base64(face_img_url)
        framebase64_image = self.url_base64(frame_img_url)
        del_member = f'http://localhost:8098/api/v1/WatchlistMembers/{nomatch_id}'

        if id_reconhecimento not in lista_ids:

            face_url = f'http://localhost:8098/api/v1/Faces/{face_id}'
            frame_url = f'http://localhost:8098/api/v1/Frames/{frame_id}'

            response_face = requests.get(face_url)
            faceimg_info = response_face.json()
            faceimage_data_id = faceimg_info.get('imageDataId')

            response_frame = requests.get(frame_url)
            frameimg_info = response_frame.json()
            frameimage_data_id = frameimg_info.get('imageDataId')

            face_img_url = f'http://localhost:8098/api/v1/Images/{faceimage_data_id}'
            frame_img_url = f'http://localhost:8098/api/v1/Images/{frameimage_data_id}'

            facebase64_image = self.url_base64(face_img_url)
            framebase64_image = self.url_base64(frame_img_url)





            print("newUSER")
            reg_data = {
                "id": nomatch_id,
                "images": [
                    {
                        "data": framebase64_image
                    }
                ],
                "watchlistIds": [
                    os.getenv('LISTA_USERS')
                ],
                "faceDetectorConfig": {
                    "minFaceSize": 25,
                    "maxFaceSize": 600,
                    "maxFaces": 20
                },
                "faceDetectorResourceId": "any",
                "templateGeneratorResourceId": "any",
                "fullName": nomatch_id,
            }
            try:
                response = requests.post(reg_url, json=reg_data)
                print(f"{response} 2")

                if response.status_code == 201:
                    try:
                        partner_ids = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'search', [[['name', '=', nomatch_id]]])
                        if partner_ids:

                            partners = odoo_connector.models.execute_kw(db, odoo_connector.uid, password, 'res.partner', 'read', [partner_ids, ['ref']])
                            for partner in partners:
                                if partner['ref'] == nomatch_id:
                                    print("Contato com o ref especificado já existe:", partner['id'])
                                    return partner['id']
                        else:
                            new_partner_id = odoo_connector.create_partner(
                                name=nomatch_id,
                                ref=nomatch_id,
                                image_1920=facebase64_image
                                )
                            print("Novo user criado com ID:", new_partner_id)

                    except:
                        response = requests.delete(del_member)
                        print(f"Não foi possivel decodificar a imagem, usuario deletado Innova - {response}")
                        pass



                else:
                    print("Usuario não cadastrado.")
                listando_ids[id_reconhecimento] = []
                lista_ids.append(id_reconhecimento)

            except:
                print("Falha no cadastro no Smartface, variavel da imagem nula")

    # Contador e envio de mensagens pelo chat avisando que alguém chegou
    def sms_chegada(self, data):
        id_tracklet = data['payload']['data']['faceProcessed']['faceInformation']['trackletId']

        if id_tracklet not in self.marca_id:
            self.marca_id = id_tracklet
            self.contador += 1
            print(f"Contador {self.contador}")




# Cria a classe relacionada as queries do GraphQL do Innovatrics
class GraphQLSubscriber:
    def __init__(self, url, odoo_connector, face_recognition):
        self.client = GraphQLClient(url)
        self.subscription_ids = []
        self.odoo_connector = odoo_connector
        self.face_recognition = face_recognition

    # Recebe a resposta de retorno das queries e identifica o tipo de resposta
    def callback(self, _id, data):
        if 'faceProcessed' in data['payload']['data']:
            self.face_recognition.sms_chegada(data)

        if 'matchResult' in data['payload']['data']:
            self.face_recognition.process_match_result(data)

        elif 'noMatchResult' in data['payload']['data']:
            self.face_recognition.process_no_match_result(data)

    # Recebe as respostas das queries e direciona para o callback, colocando as queries na lista de execução
    def subscribe(self, query):
        sub_id = self.client.subscribe(query=query, callback=self.callback)
        self.subscription_ids.append(sub_id)

    # Inicia o código, lendo a lista de execuções em looping
    def start_subscriptions(self):
        for sub_id in self.subscription_ids:
            try:
                time.sleep(1)
                while True:
                    pass
            except KeyboardInterrupt:
                self.client.stop_subscribe(sub_id)

# Recebe as variaveis, passa os parametros para as classes e executa tudo
if __name__ == "__main__":
    url_odoo = os.getenv("ODOO_URL") # envs
    db = os.getenv("DB_ODOO") # envs
    username = os.getenv("USER_ODOO") # envs
    password = os.getenv("PASS_ODOO") # envs

    odoo_connector = OdooConnector(
        url=url_odoo,
        db=db,
        username=username,
        password=password
        )
    face_recognition = FaceRecognition(odoo_connector=odoo_connector)

    url_graphql = os.getenv("GRAPHQL_URL") # envs

    # Query caso a pessoa esteja cadastrada no Innovatrics
    query_match_result = """
        subscription {
            matchResult {
                watchlistMemberDisplayName
                watchlistMemberId
                createdAt
                score
                trackletId
                watchlistDisplayName
                faceId
            }
        }
    """

    # Query caso a pessoa não esteja cadastrada no Innovatrics
    query_no_match_result = """
        subscription {
            noMatchResult {
                trackletId
                faceId
                frameId
                id
            }
        }
    """
    # Query descontinuada pro contador
    # query_contador_pessoas = """
    #     subscription {
    #         trackletCompleted {
    #             id
    #         }
    #     }
    # """

    # Query que está sendo usada pra fazer o envio da mensagem de chegada por pessoa e o contador
    query_process_face = """
        subscription {
            faceProcessed {
                faceInformation {
                    trackletId
                }
            }
        }
    """

    graphql_subscriber = GraphQLSubscriber(
        url_graphql,
        odoo_connector,
        face_recognition
        )

    # Inscrevendo as queries na lista de execução
    graphql_subscriber.subscribe(query_process_face)
    graphql_subscriber.subscribe(query_match_result)
    graphql_subscriber.subscribe(query_no_match_result)

    graphql_subscriber.start_subscriptions() # Executa a lista de execuções
