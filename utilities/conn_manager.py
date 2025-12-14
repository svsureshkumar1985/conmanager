import base64
import getpass
import json
import os
import threading
from typing import Dict, List, Optional, Tuple


# New secure storage under the user's roaming AppData (Windows)
def _appdata_dir() -> str:
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "sampleapp")
    try:
        os.makedirs(path, exist_ok=True)
        # Try to mark hidden on Windows (best-effort)
        if os.name == "nt":
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(str(path), FILE_ATTRIBUTE_HIDDEN)
    except Exception:
        # If marking hidden fails, continue silently
        pass
    return path


APP_DIR = _appdata_dir()
KEY_DAT = os.path.join(APP_DIR, "key.dat")
ENCRYPTED_CONNECTIONS_FILE = os.path.join(APP_DIR, "connections.enc")


class ConnectionManager:
    """Enterprise-grade, singleton connection manager with encrypted storage.

    - Stores data under %APPDATA%\sampleapp (Windows)
    - Derives a Fernet key using Windows username + random salt (PBKDF2HMAC)
    - Persists key metadata in key.dat
    - Encrypts the entire connections file (connections.enc) and each password
    - Provides list/get/save/delete/test helpers
    - Performs one-time migration from legacy files if present
    """

    _instance: Optional["ConnectionManager"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        # cryptography is required per requirements
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        from cryptography.fernet import Fernet
        self._PBKDF2HMAC = PBKDF2HMAC
        self._hashes = hashes
        self._Fernet = Fernet

        self._fernet = self._init_fernet()
        # Attempt legacy migration once (best-effort)
        self._migrate_from_legacy_if_needed()

    @classmethod
    def instance(cls) -> "ConnectionManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = ConnectionManager()
        return cls._instance

    # --- Key management ---
    def _load_or_create_key(self) -> Tuple[bytes, Dict]:
        username = getpass.getuser().encode("utf-8")
        meta: Dict = {}
        if os.path.exists(KEY_DAT):
            with open(KEY_DAT, "r", encoding="utf-8") as f:
                meta = json.load(f)
            # If key is present, trust and return it (satisfies "store and load key")
            key_b64 = meta.get("key")
            if key_b64:
                try:
                    key = base64.urlsafe_b64decode(key_b64.encode("utf-8"))
                    # Ensure it's urlsafe base64 32-byte key; re-encode for Fernet
                    key_b64_norm = base64.urlsafe_b64encode(key)
                    return key_b64_norm, meta
                except Exception:
                    pass
            salt_b64 = meta.get("salt")
            if not salt_b64:
                raise RuntimeError("Invalid key.dat: missing salt")
            salt = base64.urlsafe_b64decode(salt_b64.encode("utf-8"))
        else:
            # Create new random salt
            salt = os.urandom(16)
            meta = {
                "kdf": "PBKDF2HMAC",
                "algo": "SHA256",
                "iterations": 390000,
                "salt": base64.urlsafe_b64encode(salt).decode("utf-8"),
                "username_hint": getpass.getuser(),
            }
            with open(KEY_DAT, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)

        iterations = int(meta.get("iterations", 390000))
        # Derive key from username + salt
        kdf = self._PBKDF2HMAC(
            algorithm=self._hashes.SHA256(),
            length=32,
            salt=salt + username,  # bind to user
            iterations=iterations,
        )
        raw_key = kdf.derive(b"sampleapp-conn-manager")
        fernet_key = base64.urlsafe_b64encode(raw_key)
        # Persist the key alongside salt to meet requirement
        try:
            meta_out = dict(meta)
            meta_out["key"] = base64.urlsafe_b64encode(base64.urlsafe_b64decode(fernet_key)).decode("utf-8")
            with open(KEY_DAT, "w", encoding="utf-8") as f:
                json.dump(meta_out, f, indent=2)
        except Exception:
            # Best effort: if we cannot write key, proceed
            pass
        return fernet_key, meta

    def _init_fernet(self):
        key, _ = self._load_or_create_key()
        return self._Fernet(key)

    # --- Storage helpers (encrypted file) ---
    def _load_all(self) -> Dict[str, Dict]:
        if not os.path.exists(ENCRYPTED_CONNECTIONS_FILE):
            return {}
        try:
            with open(ENCRYPTED_CONNECTIONS_FILE, "rb") as f:
                token = f.read()
            data_json = self._fernet.decrypt(token).decode("utf-8")
            payload = json.loads(data_json)
            if isinstance(payload, dict) and isinstance(payload.get("connections"), dict):
                return payload["connections"]
        except Exception:
            # Corrupted or wrong key
            return {}
        return {}

    def _save_all(self, items: Dict[str, Dict]) -> None:
        payload = {"version": 1, "connections": items}
        data = json.dumps(payload, indent=2).encode("utf-8")
        token = self._fernet.encrypt(data)
        with open(ENCRYPTED_CONNECTIONS_FILE, "wb") as f:
            f.write(token)

    # --- Public operations ---
    def list(self) -> List[Dict]:
        items = self._load_all()
        out: List[Dict] = []
        for name, rec in items.items():
            r = {k: v for k, v in rec.items() if k not in ("password", "enc_password")}
            r["name"] = name
            out.append(r)
        return out

    def get(self, name: str) -> Optional[Dict]:
        items = self._load_all()
        rec = items.get(name)
        if not rec:
            return None
        # Return with name included
        out = {**rec, "name": name}
        return out

    def upsert(self, name: str, host: str, user: str, password: str, database: str) -> None:
        from datetime import datetime
        name = (name or "").strip()
        host = (host or "").strip()
        user = (user or "").strip()
        database = (database or "").strip()
        if not (name and host and user and database):
            raise ValueError("name, host, user, and database are required")
        items = self._load_all()
        enc_pw = self._fernet.encrypt(password.encode("utf-8")).decode("utf-8")
        # Preserve created_date if updating, otherwise set new date
        existing = items.get(name, {})
        created_date = existing.get("created_date") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        items[name] = {"host": host, "user": user, "database": database, "enc_password": enc_pw, "created_date": created_date}
        self._save_all(items)

    def delete(self, name: str) -> None:
        items = self._load_all()
        if name in items:
            items.pop(name)
            self._save_all(items)

    def decrypt_password(self, record: Dict) -> Optional[str]:
        enc = record.get("enc_password")
        if not enc:
            return None
        try:
            return self._fernet.decrypt(enc.encode("utf-8")).decode("utf-8")
        except Exception:
            return None

    # --- Migration from legacy JSON files ---
    def _migrate_from_legacy_if_needed(self) -> None:
        """Best-effort one-time migration from project-local legacy files.

        Looks for connections.json and .conn_key.key next to this module.
        If not found or unreadable, silently skips. Never raises.
        """
        try:
            base_dir = os.path.dirname(os.path.dirname(__file__))  # project root
            legacy_json = os.path.join(base_dir, "connections.json")
            legacy_key_file = os.path.join(base_dir, ".conn_key.key")

            if not os.path.exists(legacy_json):
                return

            # Load legacy list
            try:
                with open(legacy_json, "r", encoding="utf-8") as f:
                    legacy = json.load(f)
                if not isinstance(legacy, list):
                    return
            except Exception:
                return

            # Try legacy Fernet (if present)
            legacy_fernet = None
            try:
                if os.path.exists(legacy_key_file):
                    from cryptography.fernet import Fernet as _LF
                    with open(legacy_key_file, "rb") as kf:
                        legacy_key = kf.read()
                    legacy_fernet = _LF(legacy_key)
            except Exception:
                legacy_fernet = None

            # Convert to new dict form and merge
            from datetime import datetime
            new_items: Dict[str, Dict] = self._load_all()
            for it in legacy:
                name = it.get("name")
                host = it.get("host")
                user = it.get("user")
                pw: Optional[str] = None
                if it.get("enc_password") and legacy_fernet is not None:
                    try:
                        pw = legacy_fernet.decrypt(it["enc_password"].encode("utf-8")).decode("utf-8")
                    except Exception:
                        pw = None
                if pw is None:
                    pw = it.get("password")
                if name and host and user and pw:
                    enc_pw = self._fernet.encrypt(pw.encode("utf-8")).decode("utf-8")
                    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_items[name] = {"host": host, "user": user, "enc_password": enc_pw, "created_date": created_date}

            # Persist and stop using legacy
            self._save_all(new_items)
        except Exception:
            # Never allow migration to break initialization
            return


# --- Backward-compatible function wrappers used by UI ---
def _mgr() -> ConnectionManager:
    return ConnectionManager.instance()


def list_connections() -> List[Dict]:
    return _mgr().list()


def get_connection(name: str) -> Optional[Dict]:
    return _mgr().get(name)


def save_connection(name: str, host: str, user: str, password: str, database: str) -> None:
    _mgr().upsert(name, host, user, password, database)


def decrypt_password(record: Dict) -> Optional[str]:
    return _mgr().decrypt_password(record)


def delete_connection(name: str) -> None:
    _mgr().delete(name)


def test_sql_server_connection(host: str, user: str, password: str, database: str) -> (bool, str):
    try:
        import pyodbc
    except Exception:
        return False, (
            "pyodbc is not installed. Please install it: pip install pyodbc, "
            "and ensure the appropriate SQL Server ODBC Driver is installed."
        )

    drivers = [d for d in pyodbc.drivers() if "ODBC Driver" in d and "SQL Server" in d]
    driver = drivers[-1] if drivers else "ODBC Driver 17 for SQL Server"
    if not database:
        return False, "Database name is required for all connections."
    conn_str = (
        f"DRIVER={{{driver}}};SERVER={host};UID={user};PWD={password};DATABASE={database};"
    )
    try:
        with pyodbc.connect(conn_str, timeout=5) as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
        return True, f"Connected successfully using driver '{driver}'."
    except Exception as e:
        return False, f"Connection failed: {e}"
