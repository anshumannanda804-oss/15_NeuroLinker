# test_firestore.py
import os
from firebase_admin import credentials, initialize_app, firestore
cred_path = os.getenv("FIREBASE_KEY_PATH")
assert cred_path and os.path.exists(cred_path), "Set FIREBASE_KEY_PATH to your JSON key path"
cred = credentials.Certificate(cred_path)
initialize_app(cred)
db = firestore.client()
ref = db.collection("test_connection").document()
ref.set({"ok": True})
print("Wrote:", ref.id)
print("Docs:", [d.to_dict() for d in db.collection("test_connection").stream()])