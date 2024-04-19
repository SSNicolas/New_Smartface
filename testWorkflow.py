import xmlrpc.client
import os
from dotenv import load_dotenv

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

print(ids)