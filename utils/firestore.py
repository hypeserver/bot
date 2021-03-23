import os

import firebase_admin as fs

cred = fs.credentials.ApplicationDefault()
fs.initialize_app(
    cred,
    {
        "projectId": os.environ.get("PROJECT_ID"),
    },
)

db = fs.client()
