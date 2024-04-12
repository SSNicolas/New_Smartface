import base64
import xmlrpc.client
import time
from dotenv import load_dotenv
import os
from datetime import datetime
import requests
import zmq



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

