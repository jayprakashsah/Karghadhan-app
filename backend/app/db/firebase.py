"""
app/db/firebase.py
Initialises Firebase Admin SDK and exports the Firestore client instance `db`.
"""
import os
import glob
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

# Search for serviceAccountKey.json or any firebase-adminsdk key file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

possible_paths = [
    os.path.join(BASE_DIR, "serviceAccountKey.json"),
    os.path.join(BASE_DIR, "backend", "serviceAccountKey.json"),
    os.path.join(os.getcwd(), "serviceAccountKey.json"),
    os.path.join(os.getcwd(), "backend", "serviceAccountKey.json"),
]

matching_root = glob.glob(os.path.join(BASE_DIR, "*firebase-adminsdk*.json"))
matching_backend = glob.glob(os.path.join(BASE_DIR, "backend", "*firebase-adminsdk*.json"))
matching_cwd = glob.glob(os.path.join(os.getcwd(), "*firebase-adminsdk*.json"))

all_candidate_paths = possible_paths + matching_backend + matching_root + matching_cwd

cred_path: Optional[str] = None
for path in all_candidate_paths:
    if os.path.exists(path):
        cred_path = path
        break

try:
    if not firebase_admin._apps:
        firebase_json_env = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if firebase_json_env:
            import json
            logger.info("Initializing Firebase Admin SDK from environment variable FIREBASE_CREDENTIALS_JSON")
            cred_dict = json.loads(firebase_json_env)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        elif cred_path:
            logger.info("Initializing Firebase Admin SDK with key file: %s", cred_path)
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        else:
            logger.warning("No service account key JSON file found. Attempting Application Default Credentials.")
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)

    db = firestore.client()
except Exception as e:
    logger.warning("Firebase Firestore initialization skipped or failed (%s). Using safe fallback DB.", e)
    class DummyQuery:
        def where(self, *args, **kwargs): return self
        def stream(self, *args, **kwargs): return []
        def get(self, *args, **kwargs): return []
        def document(self, *args, **kwargs): return self
        def set(self, *args, **kwargs): return None
        def limit(self, *args, **kwargs): return self
        def order_by(self, *args, **kwargs): return self

    class DummyFirestore:
        def collection(self, *args, **kwargs):
            return DummyQuery()
        def document(self, *args, **kwargs):
            return DummyQuery()

    db = DummyFirestore()


def get_db():
    """FastAPI dependency that returns the Firestore client."""
    return db
