import os
import base64
import hashlib
import json
import time
import logging

import rsa
import rsa.prime
from rsa.key import PublicKey, PrivateKey
from rsa.common import inverse
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

from core.constant import (
    PATH_PRIVATE_KEY,
    PATH_PUBLIC_KEY,
    PATH_SECRET_KEY,
    PATH_AUTH_SIGNATURE,
    DEFAULT_SECRET_LENGTH
)
from core.security_utils import (
    generate_nonce,
    get_current_utc,
    hash_by_pbkdf2,
)

# Generador determinista de enteros y primos
class DeterministicRNG:
    def __init__(self, seed: bytes):
        self.seed = seed
        self.counter = 0

    def get_bytes(self, n: int) -> bytes:
        output = b""
        while len(output) < n:
            block = hashlib.sha256(self.seed + self.counter.to_bytes(4, 'big')).digest()
            output += block
            self.counter += 1
        return output[:n]

    def get_int(self, bits: int) -> int:
        nbytes = (bits + 7) // 8
        return int.from_bytes(self.get_bytes(nbytes), "big")

    def get_prime(self, bits: int) -> int:
        while True:
            candidate = self.get_int(bits) | 1  # forzar impar
            if rsa.prime.is_prime(candidate):
                return candidate

class SecurityService:
    _instance = None
    default_secret_length = DEFAULT_SECRET_LENGTH

    def __init__(self, private_key=None, public_key=None, other_public_key=None, secret_key: str = None):
        self.private_key = private_key
        self.public_key = public_key
        self.other_public_key = other_public_key
        self.secret_key = secret_key

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SecurityService()
        return cls._instance

    # --- Public Key Handling ---

    def get_pubkey_to_string(self) -> str:
        pub_key_bytes = self.public_key.save_pkcs1('PEM')
        return self.convert_bytes_to_b64(pub_key_bytes)

    @staticmethod
    def make_pubkey_to_string(pubkey) -> str:
        pub_key_bytes = pubkey.save_pkcs1('PEM')
        return SecurityService.convert_bytes_to_b64(pub_key_bytes)

    @staticmethod
    def get_pubkey_from_string(pubkey_str: str):
        pubkey_pem = SecurityService.convert_b64_to_bytes(pubkey_str)
        return rsa.PublicKey.load_pkcs1(pubkey_pem, format='PEM')

    # --- Key Management ---
    # TODO potential deprecation of this method
    def generate_keys(self, key_size=2048):
        self.public_key, self.private_key = rsa.newkeys(key_size)
    
    # Paso 2: Generador determinista de bytes
    class DeterministicRNG:
        def __init__(self, seed: bytes):
            self.seed = seed
            self.counter = 0

        def read(self, n: int) -> bytes:
            output = b""
            while len(output) < n:
                data = self.seed + self.counter.to_bytes(4, "big")
                output += hashlib.sha256(data).digest()
                self.counter += 1
            return output[:n]
        
    def generate_keys_from_secrets(self, password: str, username: str, key_size=1024):
        """
        Genera claves RSA públicas y privadas de forma determinista a partir de username y password.
        Las claves generadas serán idénticas para los mismos parámetros.
        """

        # Derivar semilla desde password + username como salt
        salt = username.encode("utf-8")
        seed = PBKDF2(
            password.encode("utf-8"),
            salt,
            dkLen=32,
            count=100_000,
            hmac_hash_module=SHA256
        )

        rng = DeterministicRNG(seed)

        e = 65537
        half_bits = key_size // 2

        # Obtener primos p y q distintos
        p = rng.get_prime(half_bits)
        q = rng.get_prime(half_bits)
        while q == p:
            q = rng.get_prime(half_bits)

        n = p * q
        phi_n = (p - 1) * (q - 1)
        d = inverse(e, phi_n)
        #dP = d % (p - 1)
        #dQ = d % (q - 1)
        #qInv = inverse(q, p)

        # Asignar claves
        self.public_key = PublicKey(n, e)
        self.private_key = PrivateKey(n, e, d, p, q)
        logging.debug(f"public_key: {self.public_key}")
        logging.debug(f"private_key: {self.private_key}")

        logging.debug(f"Cryptographic keys generated.")
    
    def save_signature(self, username: str, email: str, password: str):
        """Genera una firma digital del usuario y la guarda en disco"""
        self.generate_keys_from_secrets(password, username)
        message = f"{username}.{email}".encode("utf-8")
        signature = rsa.sign(message, self.private_key, "SHA-256")

        with open(PATH_AUTH_SIGNATURE, "w") as f:
            json.dump({
                "message": base64.b64encode(message).decode(),
                "signature": base64.b64encode(signature).decode()
            }, f)

        logging.debug(f"User signature stored.")

    def verify_signature(self, username: str, email: str, password) -> bool:
        """Verifica si la firma digital es válida con los datos ingresados"""
        self.generate_keys_from_secrets(password, username)
        try:
            with open(PATH_AUTH_SIGNATURE, "r") as f:
                data = json.load(f)
            message = base64.b64decode(data["message"])
            signature = base64.b64decode(data["signature"])

            rsa.verify(message, signature, self.public_key)
            logging.debug(f"User signature verified.")
            return message == f"{username}.{email}".encode("utf-8")
        
        except (rsa.VerificationError, FileNotFoundError, json.JSONDecodeError):
            logging.debug(f"Failed user signature verification.")
            return False

    def store_keys(self, priv_path=PATH_PRIVATE_KEY, pub_path=PATH_PUBLIC_KEY, secrets_path=PATH_SECRET_KEY):
        if self.private_key:
            with open(priv_path, "wb") as f:
                f.write(self.private_key.save_pkcs1('PEM'))
        if self.public_key:
            with open(pub_path, "wb") as f:
                f.write(self.public_key.save_pkcs1('PEM'))
        if self.secret_key:
            with open(secrets_path, "wb") as f:
                f.write(self.secret_key.encode("utf-8"))

    def try_load_keys_from_files(self, priv_path=PATH_PRIVATE_KEY, pub_path=PATH_PUBLIC_KEY):
        if not os.path.exists(priv_path) or not os.path.exists(pub_path):
            self.generate_keys()
            self.store_keys()
        else:
            self.load_keys_from_files(priv_path, pub_path)

    def load_keys_from_files(self, priv_path=PATH_PRIVATE_KEY, pub_path=PATH_PUBLIC_KEY):
        with open(priv_path, "rb") as f:
            self.private_key = rsa.PrivateKey.load_pkcs1(f.read(), format='PEM')
        with open(pub_path, "rb") as f:
            self.public_key = rsa.PublicKey.load_pkcs1(f.read(), format='PEM')

    def load_secret_key(self, secret_path=PATH_SECRET_KEY) -> str | None:
        if os.path.exists(secret_path):
            with open(secret_path, "rb") as f:
                return f.read().decode("utf-8")
        return ""

    # --- Crypto Core ---
    def encrypt(self, plaintext: bytes, public_key=None) -> bytes:
        key = public_key or self.public_key
        if not key:
            raise ValueError("Public key not loaded.")
        return rsa.encrypt(plaintext, key)

    def decrypt(self, ciphertext: bytes) -> bytes:
        if not self.private_key:
            raise ValueError("Private key not loaded.")
        return rsa.decrypt(ciphertext, self.private_key)

    def sign(self, message: bytes) -> bytes:
        if not self.private_key:
            raise ValueError("Private key not loaded.")
        return rsa.sign(message, self.private_key, 'SHA-256')

    def verify(self, message: bytes, signature: bytes, public_key=None) -> bool:
        key = public_key or self.public_key
        if not key:
            raise ValueError("Public key not loaded.")
        try:
            rsa.verify(message, signature, key)
            return True
        except rsa.VerificationError:
            return False

    # --- Utilities ---
    @staticmethod
    def hash_password(password: bytes, user_salt: bytes, iterations: int = 100_000) -> bytes:
        return hash_by_pbkdf2(password, user_salt, iterations)
    
    @staticmethod
    def get_current_utc_iso() -> str:
        return get_current_utc("iso")
    
    @staticmethod
    def get_current_utc_dt() -> str:
        return get_current_utc("datetime")
    
    @staticmethod
    def get_current_utc_ts() -> str:
        return get_current_utc("timestamp")
    
    @staticmethod
    def _payload_without_hash(payload: dict) -> dict:
        return {k: v for k, v in payload.items() if k != "hash"}

    @staticmethod
    def generate_secret_key() -> str:
        return generate_nonce(SecurityService.default_secret_length)

    @staticmethod
    def convert_b64_to_bytes(b64_str: str) -> bytes:
        return base64.b64decode(b64_str.encode("utf-8"))

    @staticmethod
    def convert_bytes_to_b64(data: bytes) -> str:
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def generate_nonce() -> str:
        return generate_nonce(SecurityService.default_secret_length)

    @staticmethod
    def get_timestamp_after_expiry(timestamp=None, extra_time=0) -> float:
        if not timestamp:
            timestamp = SecurityService.get_current_utc_ts()
        return timestamp + extra_time

    @staticmethod
    def compute_json_hash(data_dict) -> str:
        raw = json.dumps(data_dict, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def prepare_safe_payload(payload, nonce_store, expiry_seconds=600) -> dict:
        payload["timestamp"] = SecurityService.get_current_utc_iso()
        payload["nonce"] = generate_nonce()
        payload["hash"] = SecurityService.compute_json_hash(SecurityService._payload_without_hash(payload))
        if not nonce_store.add_nonce(payload["nonce"]):
            raise ValueError("Replay detected: nonce already used")
        return payload

    @staticmethod
    def validate_payload(payload, nonce_store, max_age_seconds=600) -> tuple[bool, str]:
        try:
            nonce = payload["nonce"]
            timestamp = payload["timestamp"]
            claimed_hash = payload["hash"]
        except KeyError:
            return False, "Missing required fields"

        try:
            timestamp_seconds = time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))
        except Exception:
            return False, "Invalid timestamp format"

        if abs(time.time() - timestamp_seconds) > max_age_seconds:
            return False, "Timestamp expired"

        expected_hash = SecurityService.compute_json_hash({k: v for k, v in payload.items() if k != "hash"})
        if claimed_hash != expected_hash:
            return False, "Hash mismatch"

        if not nonce_store.add_nonce(nonce):
            return False, "Replay detected (duplicate nonce)"

        return True, "Payload valid"
