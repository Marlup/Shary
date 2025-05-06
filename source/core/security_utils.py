from datetime import datetime
import hashlib
import secrets  # Secure nonce generation
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

def get_current_utc(return_format="iso"):
    now = datetime.now()
    if return_format == "timestamp":
        return now.timestamp()
    elif return_format == "datetime":
        return now
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")

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
    current_timestamp = get_current_utc("datetime") # Get current UNIX timestamp
    if timestamp is None:
        timestamp = current_timestamp # Get current UNIX timestamp
    elif timestamp <= current_timestamp:  # Reject if older than 10 minutes
        raise ValueError("Timestamp is too old")

    if nonce is None:
        nonce = generate_nonce() # Generate a random nonce
    else:
        #TODO: Check if nonce is unique
        pass

    message = f"{data}|{timestamp}|{nonce}|{secret_key}".encode()

    return hashlib.sha256(message).hexdigest(), timestamp, nonce

def generate_nonce(length=16) -> str:
    """Generate a random nonce."""
    #return str(uuid.uuid4())
    return secrets.token_hex(length)

def hash_by_pbkdf2(password: bytes, salt: bytes, iterations: int = 100_000) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", 
        password, 
        salt, 
        iterations, 
        dklen=32
        )

def aes_encrypt(key: bytes, plaintext: str) -> bytes:
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return iv + ciphertext

def aes_decrypt(key: bytes, encrypted_data: bytes) -> str:
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()

def make_user_salt(user: str) -> bytes:
    """Create a salt for the user as raw bytes."""
    return f"shary_creds.{user}".encode("utf-8")

