import os
import hashlib
import base64
import time
#import datetime
from datetime import datetime, timezone
import secrets  # Secure nonce generation
import time
import uuid
import threading
import json

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from front.core.constant import (
    PATH_PRIVATE_KEY,
    PATH_PUBLIC_KEY
)

def hash_message(message: str|bytes):
    if isinstance(message, str):
        return hashlib.sha256(message.encode("utf-8")).hexdigest()
    
    return hashlib.sha256(message).hexdigest()

def make_verification_hash(data, secret_key, timestamp=None, nonce=None):
    """Create a secure hash (HMAC) to verify sender identity."""
    if timestamp is None:
        timestamp = RSACrypto.get_current_utc_iso() # Get current UNIX timestamp
    elif timestamp <= RSACrypto.get_current_utc_iso():  # Reject if older than 10 minutes
        raise ValueError("Timestamp is too old")

    if nonce is None:
        nonce = RSACrypto.generate_nonce() # Generate a random nonce
    else:
        #TODO: Check if nonce is unique
        pass

    message = f"{data}|{timestamp}|{nonce}|{secret_key}".encode()

    return hashlib.sha256(message).hexdigest(), timestamp, nonce

def write_temp_decrypted_data(decrypted_data, path=".env"):
# Write the decrypted data back to a .env file (temporarily)
    with open(path, "wb") as file:
        file.write(decrypted_data)

class RSACrypto:
    def __init__(self, private_key=None, public_key=None):
        self.private_key = private_key
        self.public_key = public_key

    def get_pub_key_bytes(self):
        pub_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pub_key_bytes
    
    def get_pub_key_string(self):
        pub_key_str = self.get_pub_key_bytes().decode("utf-8")
        return pub_key_str

    @staticmethod
    def generate(key_size=2048):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        return RSACrypto(private_key, private_key.public_key())

    def save_keys(self, priv_path=PATH_PRIVATE_KEY, pub_path=PATH_PUBLIC_KEY):
        if self.private_key:
            with open(priv_path, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

        if self.public_key:
            with open(pub_path, "wb") as f:
                f.write(self.get_pub_key_bytes())

    @staticmethod
    def try_load_from_files(
        priv_path=PATH_PRIVATE_KEY, 
        pub_path=PATH_PUBLIC_KEY
        ):

        if not os.path.exists(priv_path) or not os.path.exists(pub_path):
            rsa_crypto = RSACrypto.generate()
            rsa_crypto.save_keys()
            return rsa_crypto

        rsa_crypto = RSACrypto.load_from_files()
        return rsa_crypto
    
    @staticmethod
    def load_from_files(priv_path=PATH_PRIVATE_KEY, pub_path=PATH_PUBLIC_KEY):

        private_key = None
        public_key = None

        if priv_path:
            with open(priv_path, "rb") as f:
                private_key = serialization.load_pem_private_key(f.read(), password=None)

        if pub_path:
            with open(pub_path, "rb") as f:
                public_key = serialization.load_pem_public_key(f.read())
                print(f"-----------\n\n public_key - {public_key}")

        return RSACrypto(private_key, public_key)

    def encrypt(self, plaintext: bytes) -> bytes:
        if not self.public_key:
            raise ValueError("Public key not loaded.")
        return self.public_key.encrypt(
            plaintext,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

    def decrypt(self, ciphertext: bytes) -> bytes:
        if not self.private_key:
            raise ValueError("Private key not loaded.")
        return self.private_key.decrypt(
            ciphertext,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

    def sign(self, message: bytes) -> bytes:
        if not self.private_key:
            raise ValueError("Private key not loaded.")
        return self.private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )

    def verify(self, message: bytes, signature: bytes) -> bool:
        if not self.public_key:
            raise ValueError("Public key not loaded.")
        try:
            self.public_key.verify(
                signature,
                message,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    @staticmethod
    def make_bin_blob_to_base64(message):
        return base64.b64encode(message)  # ✅ safe string
    
    @staticmethod
    def generate_nonce(length=16):
        #return str(uuid.uuid4())
        return secrets.token_hex(length)
    
    @staticmethod
    def get_current_utc_iso():
        #return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def compute_json_hash(data_dict):
        """Hash a dict in canonical form."""
        raw = json.dumps(data_dict, sort_keys=True).encode('utf-8')
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def prepare_secure_payload(payload, nonce_store, expiry_seconds=600):
        """Prepare a payload with nonce, timestamp, and hash. Adds nonce to store."""
        payload["timestamp"] = RSACrypto.get_current_utc_iso()
        payload["nonce"] = RSACrypto.generate_nonce()
        payload["hash"] = RSACrypto.compute_json_hash({k: v for k, v in payload.items() if k != "hash"})
        
        if not nonce_store.add_nonce(payload["nonce"]):
            raise ValueError("Replay detected: nonce already used")
        
        return payload

    @staticmethod
    def validate_payload(payload, nonce_store, max_age_seconds=600):
        """Check for hash match, valid timestamp, and replay-safe nonce."""
        try:
            nonce = payload["nonce"]
            timestamp = payload["timestamp"]
            claimed_hash = payload["hash"]
        except KeyError:
            return False, "Missing required fields"

        # Check timestamp freshness
        try:
            timestamp_seconds = time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))
        except Exception:
            return False, "Invalid timestamp format"

        now = time.time()
        if abs(now - timestamp_seconds) > max_age_seconds:
            return False, "Timestamp expired"

        # Check hash
        expected_hash = RSACrypto.compute_hash({k: v for k, v in payload.items() if k != "hash"})
        if claimed_hash != expected_hash:
            return False, "Hash mismatch"

        # Check replay
        if not nonce_store.add_nonce(nonce):
            return False, "Replay detected (duplicate nonce)"

        return True, "Payload valid"

"""
# --- Demo usage ---
if __name__ == "__main__":
    rsa_crypto = RSACrypto.generate()
    rsa_crypto.save_keys()

    # Reload (simulate separate system)
    rsa2 = RSACrypto.load_from_files()

    message = b"Top secret from Shary"
    encrypted = rsa2.encrypt(message)
    decrypted = rsa2.decrypt(encrypted)

    print("[Encrypted/Decrypted]")
    print("Decrypted:", decrypted)

    sig = rsa2.sign(message)
    is_valid = rsa2.verify(message, sig)

    print("\n[Signature]")
    print("Signature (base64):", base64.b64encode(sig).decode())
    print("Valid Signature?:", is_valid)
"""

class NonceStore():
    def __init__(self, expiry_seconds=600):
        self.expiry = expiry_seconds
        self.store = {}  # nonce -> expire_time
        self.lock = threading.Lock()
        self.cleanup_thread = threading.Thread(target=self._cleaner, daemon=True)
        self.cleanup_thread.start()

    def add_nonce(self, nonce):
        expire_at = time.time() + self.expiry * 1.1
        with self.lock:
            if nonce in self.store:
                return False  # replay detected
            self.store[nonce] = expire_at
            return True

    def _cleaner(self):
        while True:
            now = time.time()
            with self.lock:
                expired = [nonce for nonce, exp in self.store.items() if exp < now]
                for nonce in expired:
                    del self.store[nonce]
            time.sleep(self.expiry / 2)  # periodic cleanup

    @staticmethod
    def generate_nonce(length=16):
        #return str(uuid.uuid4())
        return secrets.token_hex(length)
    
    @staticmethod
    def get_current_utc_iso():
        #return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def compute_json_hash(data_dict):
        """Hash a dict in canonical form."""
        raw = json.dumps(data_dict, sort_keys=True).encode('utf-8')
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def prepare_secure_payload(payload, nonce_store, expiry_seconds=600):
        """Prepare a payload with nonce, timestamp, and hash. Adds nonce to store."""
        payload["timestamp"] = RSACrypto.get_current_utc_iso()
        payload["nonce"] = RSACrypto.generate_nonce()
        payload["hash"] = RSACrypto.compute_json_hash({k: v for k, v in payload.items() if k != "hash"})
        
        if not nonce_store.add_nonce(payload["nonce"]):
            raise ValueError("Replay detected: nonce already used")
        
        return payload

    @staticmethod
    def validate_payload(payload, nonce_store, max_age_seconds=600):
        """Check for hash match, valid timestamp, and replay-safe nonce."""
        try:
            nonce = payload["nonce"]
            timestamp = payload["timestamp"]
            claimed_hash = payload["hash"]
        except KeyError:
            return False, "Missing required fields"

        # Check timestamp freshness
        try:
            timestamp_seconds = time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))
        except Exception:
            return False, "Invalid timestamp format"

        now = time.time()
        if abs(now - timestamp_seconds) > max_age_seconds:
            return False, "Timestamp expired"

        # Check hash
        expected_hash = RSACrypto.compute_hash({k: v for k, v in payload.items() if k != "hash"})
        if claimed_hash != expected_hash:
            return False, "Hash mismatch"

        # Check replay
        if not nonce_store.add_nonce(nonce):
            return False, "Replay detected (duplicate nonce)"

        return True, "Payload valid"
"""
# Usage Example
if __name__ == "__main__":
    store = NonceStore(expiry_seconds=300)

    original_data = {
        "from_user": "alice",
        "to_user": "bob",
        "message": "Hello from Shary!"
    }

    secure_payload = prepare_secure_payload(original_data, store)
    print("Generated Payload:", json.dumps(secure_payload, indent=2))

    result, reason = validate_payload(secure_payload, store)
    print("Validation:", result, "-", reason)

    # Attempt replay
    result2, reason2 = validate_payload(secure_payload, store)
    print("Replay Test:", result2, "-", reason2)
"""