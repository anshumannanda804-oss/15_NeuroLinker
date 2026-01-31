Firestore-backed DB with JSON fallback.
Drop-in replacement for the existing SQLite-based DatabaseManager.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional

# Try to import firebase-admin
_fire_imported = False
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    _fire_imported = True
except Exception:
    _fire_imported = False


DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _gen_id() -> str:
    import uuid
    return str(uuid.uuid4())


# ----------------------
# JSON-backed manager
# ----------------------
class JSONDatabaseManager:
    def _init_(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self._files = {
            "users": os.path.join(self.data_dir, "users.json"),
            "decisions": os.path.join(self.data_dir, "decisions.json"),
            "chat": os.path.join(self.data_dir, "chat.json"),
            "preferences": os.path.join(self.data_dir, "preferences.json"),
        }
        for p in self._files.values():
            if not os.path.exists(p):
                with open(p, "w", encoding="utf-8") as f:
                    json.dump([], f)

    def _load(self, key: str) -> List[Dict[str, Any]]:
        with open(self._files[key], "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self, key: str, data: List[Dict[str, Any]]):
        with open(self._files[key], "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, ensure_ascii=False, indent=2)

    # --- Users ---
    def create_user(self, email: str, password: str, full_name: str = "") -> bool:
        users = self._load("users")
        if any(u["email"] == email for u in users):
            return False
        uid = len(users) + 1
        users.append({
            "id": uid,
            "email": email,
            "password_hash": _hash_password(password),
            "full_name": full_name,
            "created_at": datetime.utcnow().isoformat()
        })
        self._save("users", users)
        # default preferences
        prefs = self._load("preferences")
        prefs.append({"user_id": uid, "share_data_with_ai": False, "view_chat_history": True})
        self._save("preferences", prefs)
        return True

    def authenticate_user(self, email: str, password: str) -> Optional[int]:
        users = self._load("users")
        for u in users:
            if u["email"] == email and u["password_hash"] == _hash_password(password):
                return u["id"]
        return None

    def get_user(self, user_id: int) -> Optional[Dict]:
        users = self._load("users")
        for u in users:
            if u["id"] == user_id:
                return {k: v for k, v in u.items() if k != "password_hash"}
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        users = self._load("users")
        for u in users:
            if u["email"] == email:
                return {k: v for k, v in u.items() if k != "password_hash"}
        return None

    def update_user_password(self, user_id: int, new_password: str) -> bool:
        users = self._load("users")
        for u in users:
            if u["id"] == user_id:
                u["password_hash"] = _hash_password(new_password)
                self._save("users", users)
                return True
        return False

    # --- Decisions ---
    def save_decision(self, user_id: int, decision_data: Dict) -> str:
        decisions = self._load("decisions")
        decision_id = decision_data.get("id") or _gen_id()
        found = None
        for d in decisions:
            if d["id"] == decision_id and d["user_id"] == user_id:
                found = d
                break
        payload = {
            "id": decision_id,
            "user_id": user_id,
            "title": decision_data.get("title"),
            "description": decision_data.get("description"),
            "goal": decision_data.get("goal"),
            "constraints": decision_data.get("constraints", []),
            "alternatives": decision_data.get("alternatives", []),
            "final_choice": decision_data.get("final_choice"),
            "reasoning": decision_data.get("reasoning"),
            "expected_outcome": decision_data.get("expected_outcome"),
            "memory_layer": decision_data.get("memory_layer", "private"),
            "tags": decision_data.get("tags", []),
            "reflection": decision_data.get("reflection"),
            "outcome_status": decision_data.get("outcome_status"),
            "created_at": datetime.utcnow().isoformat()
        }
        if found:
            found.update(payload)
        else:
            decisions.insert(0, payload)
        self._save("decisions", decisions)
        return decision_id

    def get_decision(self, user_id: int, decision_id: str) -> Optional[Dict]:
        decisions = self._load("decisions")
        for d in decisions:
            if d["id"] == decision_id and d["user_id"] == user_id:
                return d
        return None

    def get_user_decisions(self, user_id: int, limit: int = None) -> List[Dict]:
        decisions = [d for d in self._load("decisions") if d["user_id"] == user_id]
        decisions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return decisions[:limit] if limit else decisions

    def delete_decision(self, user_id: int, decision_id: str) -> bool:
        decisions = self._load("decisions")
        new = [d for d in decisions if not (d["id"] == decision_id and d["user_id"] == user_id)]
        changed = len(new) != len(decisions)
        if changed:
            self._save("decisions", new)
        return changed

    # --- Chat ---
    def save_chat_message(self, user_id: int, user_message: str, ai_response: str,
                          chat_type: str = "decision_recording", decision_id: str = None,
                          is_visible: bool = True) -> int:
        chat = self._load("chat")
        cid = len(chat) + 1
        chat.append({
            "id": cid,
            "user_id": user_id,
            "decision_id": decision_id,
            "chat_type": chat_type,
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": datetime.utcnow().isoformat(),
            "is_visible_to_user": bool(is_visible)
        })
        self._save("chat", chat)
        return cid

    def get_chat_history(self, user_id: int, decision_id: str = None,
                         chat_type: str = None, include_hidden: bool = False) -> List[Dict]:
        chat = [c for c in self._load("chat") if c["user_id"] == user_id]
        if decision_id:
            chat = [c for c in chat if c["decision_id"] == decision_id]
        if chat_type:
            chat = [c for c in chat if c["chat_type"] == chat_type]
        if not include_hidden:
            chat = [c for c in chat if c.get("is_visible_to_user", True)]
        chat.sort(key=lambda x: x.get("timestamp"))
        return chat

    def get_chat_history_for_decision(self, user_id: int, decision_id: str) -> List[Dict]:
        return self.get_chat_history(user_id, decision_id=decision_id, include_hidden=True)

    # --- Preferences ---
    def get_user_preferences(self, user_id: int) -> Dict:
        prefs = self._load("preferences")
        for p in prefs:
            if p["user_id"] == user_id:
                return {
                    "share_data_with_ai": bool(p.get("share_data_with_ai", False)),
                    "view_chat_history": bool(p.get("view_chat_history", True))
                }
        return {"share_data_with_ai": False, "view_chat_history": True}

    def update_user_preferences(self, user_id: int, preferences: Dict) -> bool:
        prefs = self._load("preferences")
        for p in prefs:
            if p["user_id"] == user_id:
                p["share_data_with_ai"] = bool(preferences.get("share_data_with_ai", p.get("share_data_with_ai", False)))
                p["view_chat_history"] = bool(preferences.get("view_chat_history", p.get("view_chat_history", True)))
                self._save("preferences", prefs)
                return True
        # create if missing
        prefs.append({"user_id": user_id, "share_data_with_ai": bool(preferences.get("share_data_with_ai", False)), "view_chat_history": bool(preferences.get("view_chat_history", True))})
        self._save("preferences", prefs)
        return True


# ----------------------
# Firestore-backed manager
# ----------------------
class FirestoreDatabaseManager:
    def _init_(self, cred_path: Optional[str] = None):
        if not _fire_imported:
            raise RuntimeError("firebase-admin not installed")
        if not firebase_admin._apps:
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
        self.client = firestore.client()
        self.users = self.client.collection("users")
        self.decisions = self.client.collection("decisions")
        self.chat = self.client.collection("chat_history")
        self.prefs = self.client.collection("user_preferences")

    # --- Users ---
    def create_user(self, email: str, password: str, full_name: str = "") -> bool:
        q = self.users.where("email", "==", email).limit(1).get()
        if q:
            return False
        doc = {"email": email, "password_hash": _hash_password(password), "full_name": full_name, "created_at": firestore.SERVER_TIMESTAMP}
        ref = self.users.document()
        ref.set(doc)
        uid = ref.id
        self.prefs.document(uid).set({"user_id": uid, "share_data_with_ai": False, "view_chat_history": True})
        return True

    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        q = self.users.where("email", "==", email).limit(1).get()
        for doc in q:
            data = doc.to_dict()
            if data.get("password_hash") == _hash_password(password):
                return doc.id
        return None

    def get_user(self, user_id: str) -> Optional[Dict]:
        doc = self.users.document(user_id).get()
        if doc.exists:
            d = doc.to_dict()
            d.pop("password_hash", None)
            d["id"] = doc.id
            return d
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        q = self.users.where("email", "==", email).limit(1).get()
        for doc in q:
            d = doc.to_dict()
            d.pop("password_hash", None)
            d["id"] = doc.id
            return d
        return None

    def update_user_password(self, user_id: str, new_password: str) -> bool:
        doc = self.users.document(user_id)
        if doc.get().exists:
            doc.update({"password_hash": _hash_password(new_password)})
            return True
        return False

    # --- Decisions ---
    def save_decision(self, user_id: str, decision_data: Dict) -> str:
        decision_id = decision_data.get("id") or _gen_id()
        payload = {
            "user_id": user_id,
            "title": decision_data.get("title"),
            "description": decision_data.get("description"),
            "goal": decision_data.get("goal"),
            "constraints": decision_data.get("constraints", []),
            "alternatives": decision_data.get("alternatives", []),
            "final_choice": decision_data.get("final_choice"),
            "reasoning": decision_data.get("reasoning"),
            "expected_outcome": decision_data.get("expected_outcome"),
            "memory_layer": decision_data.get("memory_layer", "private"),
            "tags": decision_data.get("tags", []),
            "reflection": decision_data.get("reflection"),
            "outcome_status": decision_data.get("outcome_status"),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        self.decisions.document(decision_id).set(payload, merge=True)
        return decision_id

    def get_decision(self, user_id: str, decision_id: str) -> Optional[Dict]:
        doc = self.decisions.document(decision_id).get()
        if doc.exists:
            d = doc.to_dict()
            if d.get("user_id") == user_id:
                d["id"] = doc.id
                return d
        return None

    def get_user_decisions(self, user_id: str, limit: int = None) -> List[Dict]:
        q = self.decisions.where("user_id", "==", user_id).order_by("created_at", direction=firestore.Query.DESCENDING)
        if limit:
            q = q.limit(limit)
        return [{**doc.to_dict(), "id": doc.id} for doc in q.stream()]

    def delete_decision(self, user_id: str, decision_id: str) -> bool:
        doc_ref = self.decisions.document(decision_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get("user_id") == user_id:
            doc_ref.delete()
            return True
        return False

    # --- Chat ---
    def save_chat_message(self, user_id: str, user_message: str, ai_response: str,
                          chat_type: str = "decision_recording", decision_id: str = None,
                          is_visible: bool = True) -> str:
        payload = {
            "user_id": user_id,
            "decision_id": decision_id,
            "chat_type": chat_type,
            "user_message": user_message,
            "ai_response": ai_response,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "is_visible_to_user": bool(is_visible),
        }
        ref = self.chat.document()
        ref.set(payload)
        return ref.id

    def get_chat_history(self, user_id: str, decision_id: str = None,
                         chat_type: str = None, include_hidden: bool = False) -> List[Dict]:
        q = self.chat.where("user_id", "==", user_id)
        if decision_id:
            q = q.where("decision_id", "==", decision_id)
        if chat_type:
            q = q.where("chat_type", "==", chat_type)
        if not include_hidden:
            q = q.where("is_visible_to_user", "==", True)
        q = q.order_by("timestamp")
        return [{**doc.to_dict(), "id": doc.id} for doc in q.stream()]

    def get_chat_history_for_decision(self, user_id: str, decision_id: str) -> List[Dict]:
        return self.get_chat_history(user_id, decision_id=decision_id, include_hidden=True)

    # --- Preferences ---
    def get_user_preferences(self, user_id: str) -> Dict:
        doc = self.prefs.document(user_id).get()
        if doc.exists:
            d = doc.to_dict()
            return {"share_data_with_ai": bool(d.get("share_data_with_ai", False)), "view_chat_history": bool(d.get("view_chat_history", True))}
        return {"share_data_with_ai": False, "view_chat_history": True}

    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        self.prefs.document(user_id).set({
            "share_data_with_ai": bool(preferences.get("share_data_with_ai", False)),
            "view_chat_history": bool(preferences.get("view_chat_history", True))
        }, merge=True)
        return True


# ----------------------
# Init global db instance (drop-in)
# ----------------------
def _select_backend():
    # FORCE_JSON_DB=1 to force JSON backend
    if os.getenv("FORCE_JSON_DB", "0") == "1":
        return JSONDatabaseManager()

    cred_path = os.getenv("FIREBASE_KEY_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and _fire_imported and os.path.exists(cred_path):
        try:
            return FirestoreDatabaseManager(cred_path)
        except Exception:
            pass

    # Fallback
    return JSONDatabaseManager()

db = _select_backend()
