import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin impo


cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
  'projectId': os.environ.get("PROJECT_ID"),
})

db = firestore.client()
