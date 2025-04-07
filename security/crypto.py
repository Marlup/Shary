import os
import hashlib
import base64
import time
#import datetime
from datetime import datetime, timezone, timedelta
import secrets  # Secure nonce generation
import time
import uuid
import threading
import json

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from core.constant import (
    PATH_PRIVATE_KEY,
    PATH_PUBLIC_KEY,
    PATH_SECRET_KEY
)

def get_sha256_hash(message: bytes | str):
    """Returns a SHA-256 hash object (internal use only)."""
    if isinstance(message, str):
        message = message.encode("utf-8")
    return hashlib.sha256(message)

def hash_message(message: bytes|str, return_str: bool=True) -> bytes | str:
    """Hash a message using SHA-256. If message is a string, encode it first."""
    hash = get_sha256_hash(message)  # Get the hash object
    
    if return_str:
        return hash.hexdigest()
    return hash.digest()
    
def hash_message_extended(message: bytes | str) -> tuple[bytes, str]:
    """Hash a message using SHA-256. If message is a string, encode it first."""
    hash = get_sha256_hash(message)  # Get the hash object
    return hash.digest(), hash.hexdigest()
    
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
    """RSA Cryptography class for encryption, decryption, signing, and verifying."""
    def __init__(self, private_key=None, public_key=None, other_public_key=None, secret_key: str=None):
        self.private_key = private_key
        self.public_key = public_key
        self.other_public_key = other_public_key
        self.secret_key = secret_key

    def get_pubkey_to_string(self) -> str:
        """Get the public key as a string."""
        pub_key_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return RSACrypto.convert_bytes_to_b64(pub_key_bytes)
    staticmethod
    def make_pubkey_to_string(pubkey) -> str:
        """Get the public key as a string."""
        pub_key_bytes = pubkey.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return RSACrypto.convert_bytes_to_b64(pub_key_bytes)

    @staticmethod
    def get_pubkey_from_string(pubkey_str: str):
        """Deserialize Base64(DER) string to a usable public key object."""
        pubkey_der = RSACrypto.convert_b64_to_bytes(pubkey_str)
        return serialization.load_der_public_key(pubkey_der)

    @staticmethod
    def generate(key_size=2048) -> 'RSACrypto':
        """Generate a new RSA key pair."""
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        return RSACrypto(private_key, private_key.public_key())

    def save_keys(self, 
                  priv_path=PATH_PRIVATE_KEY, 
                  pub_path=PATH_PUBLIC_KEY,
                  secrets_path=PATH_SECRET_KEY
                  ) -> None:
        """Save the private and public keys to files."""
        
        if self.private_key:
            with open(priv_path, "wb") as f:
                f.write(self.private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))

        if self.public_key:
            with open(pub_path, "wb") as f:
                f.write(self.public_key.public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))

        if self.secret_key:
            with open(secrets_path, "wb") as f:
                f.write(self.secret_key.encode("utf-8"))

    @staticmethod
    def try_load_from_files(
        priv_path=PATH_PRIVATE_KEY, 
        pub_path=PATH_PUBLIC_KEY
        ) -> 'RSACrypto':
        """Try to load keys from files. Generate new keys if not found."""

        if not os.path.exists(priv_path) or not os.path.exists(pub_path):
            rsa_crypto = RSACrypto.generate()
            rsa_crypto.save_keys()
            return rsa_crypto

        rsa_crypto = RSACrypto.load_from_files()
        return rsa_crypto
    
    @staticmethod
    def load_from_files(priv_path=PATH_PRIVATE_KEY, pub_path=PATH_PUBLIC_KEY) -> 'RSACrypto':
        """Load keys from files."""

        private_key = None
        public_key = None

        if priv_path:
            with open(priv_path, "rb") as f:
                private_key = serialization.load_der_private_key(f.read(), password=None)

        if pub_path:
            with open(pub_path, "rb") as f:
                public_key = serialization.load_der_public_key(f.read())
                print(f"-----------\n\n public_key - {public_key}")

        return RSACrypto(private_key, public_key)

    def load_secret_key(self, secret_path=PATH_SECRET_KEY) -> str | None:
        """Load secret key from file."""
        if secret_path:
            with open(secret_path, "rb") as f:
                secret_key = f.read().decode("utf-8")
                print(f"-----------\n\n secret_key - {secret_key}")
            return secret_key
        return ""

    def encrypt(self, plaintext: bytes, public_key=None) -> bytes:
        """Encrypt a message using the public key."""
        if not public_key:
            public_key = self.public_key
        if not public_key:
            raise ValueError("Public key not loaded.")
        return public_key.encrypt(
            plaintext,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt a message using the private key."""
        if not self.private_key:
            raise ValueError("Private key not loaded.")
        return self.private_key.decrypt(
            ciphertext,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )

    def sign(self, message: bytes) -> bytes:
        """Sign a message using the private key."""
        if not self.private_key:
            raise ValueError("Private key not loaded.")
        return self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()), 
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

    def verify(self, message: bytes, signature: bytes, public_key=None) -> bool:
        """Verify a signature using the public key."""
        if not public_key:
            public_key = self.public_key
        if not public_key:
            raise ValueError("Public key not loaded.")
        try:
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()), 
                    salt_length=padding.PSS.MAX_LENGTH
                    ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
        
    @staticmethod
    def generate_secret_key(length=16) -> str:
        """Generate a random secret key."""
        return RSACrypto.generate_nonce(length=length)

    @staticmethod
    def convert_b64_to_bytes(b64_str: str) -> bytes:
        return base64.b64decode(b64_str.encode("utf-8"))
    
    @staticmethod
    def convert_bytes_to_b64(data: bytes) -> str:
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def generate_nonce(length=16) -> str:
        """Generate a random nonce."""
        #return str(uuid.uuid4())
        return secrets.token_hex(length)
    
    @staticmethod
    def get_current_utc_dt(return_timestamp=True) -> datetime | float:
        """Get current UTC datetime or timestamp."""
        current_utc_dt = datetime.now(timezone.utc)
        if return_timestamp:
            return current_utc_dt.timestamp()
        #return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return current_utc_dt.isoformat()

    @staticmethod
    def get_timestamp_after_expiry(timestamp: float=None, extra_time: int=0) -> float:
        """Timestamp (POSIX TS) after expiry time in seconds"""
        if not timestamp:
            timestamp = RSACrypto.get_current_utc_dt(return_timestamp=True)
        if extra_time <= 0:
            return timestamp
        return timestamp + extra_time #timedelta(seconds=extra_time)

    @staticmethod
    def compute_json_hash(data_dict) -> str:
        """Hash a dict in canonical form."""
        raw = json.dumps(data_dict, sort_keys=True).encode('utf-8')
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def prepare_safe_payload(payload, nonce_store, expiry_seconds=600) -> dict:
        """Prepare a payload with nonce, timestamp, and hash. Adds nonce to store."""
        payload["timestamp"] = RSACrypto.get_current_utc_iso()
        payload["nonce"] = RSACrypto.generate_nonce()
        payload["hash"] = RSACrypto.compute_json_hash({k: v for k, v in payload.items() if k != "hash"})
        
        if not nonce_store.add_nonce(payload["nonce"]):
            raise ValueError("Replay detected: nonce already used")
        
        return payload

    @staticmethod
    def validate_payload(payload, nonce_store, max_age_seconds=600) -> tuple[bool, str]:
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
    def get_current_utc_dt(return_timestamp=True):
        current_utc_dt = datetime.now(timezone.utc)
        if return_timestamp:
            return current_utc_dt
        #return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return current_utc_dt.isoformat()

    @staticmethod
    def get_dt_after_expiry_seconds(dt: datetime=None, extra_time: int=0):
        if not dt:
            dt = RSACrypto.get_current_utc_dt(return_timestamp=True)
        if extra_time == 0:
            return dt
        return dt + datetime.timedelta(seconds=extra_time)

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