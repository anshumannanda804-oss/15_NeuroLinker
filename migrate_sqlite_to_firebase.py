# migrate_sqlite_to_firestore.py
import sqlite3, os
from database import FirestoreDatabaseManager

path = "decision_system.db"
if not os.path.exists(path):
    raise SystemExit("No SQLite DB found.")

cred = os.getenv("FIREBASE_KEY_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred:
    raise SystemExit("Set FIREBASE_KEY_PATH environment variable to your service account JSON path.")

db = FirestoreDatabaseManager(cred)

conn = sqlite3.connect(path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Users
for row in cur.execute("SELECT * FROM users"):
    uid = str(row["id"])
    user_doc = {
        "email": row["email"],
        "password_hash": row["password_hash"],
        "full_name": row["full_name"],
        "created_at": row["created_at"]
    }
    db.users.document(uid).set(user_doc)
    pref = cur.execute("SELECT * FROM user_preferences WHERE user_id = ?", (row["id"],)).fetchone()
    if pref:
        db.prefs.document(uid).set({"user_id": uid, "share_data_with_ai": bool(pref["share_data_with_ai"]), "view_chat_history": bool(pref["view_chat_history"])})

# Decisions
for row in cur.execute("SELECT * FROM decisions"):
    doc = dict(row)
    db.decisions.document(doc["id"]).set(doc)

# Chat history
for row in cur.execute("SELECT * FROM chat_history"):
    doc = dict(row)
    db.chat.document().set(doc)

print("Migration complete.")