import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
dir = os.path.dirname(__file__)
service_credentials = os.path.join(dir,'service.json')
user_credential_fp = os.path.join(dir,'credentials.json')

# Use a service account
cred = credentials.Certificate(service_credentials)
default_app = firebase_admin.initialize_app(cred)
db_client = firestore.client()
# with open(user_credential_fp, 'r') as user_credential_file:
#   user_credentials = json.load(user_credential_file)

