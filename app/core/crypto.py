from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
import hashlib
import time
import secrets  # Secure nonce generation

def load_encryption_key(secret_path="secret.key"):
    if not os.path.exists(secret_path):
        # Generate a new encryption key and save it to a file
        key = Fernet.generate_key()
        with open(secret_path, "wb") as key_file:
            key_file.write(key)
    
    # Load the encryption key
    with open("secret.key", "rb") as key_file:
        key = key_file.read()
    return Fernet(key)

def encrypt_data(data, path=".env.enc"):
    """
    Encrypts the given data and saves it to a file.
    """
    cipher = load_encryption_key()
    encrypted_data = cipher.encrypt(data.encode())

    with open(path, "wb") as enc_file:
        enc_file.write(encrypted_data)

    return encrypted_data

def decrypt_data(path=".env.enc"):
    # Decrypt the .env file
    with open(path, "rb") as enc_file:
        encrypted_data = enc_file.read()
    cipher = load_encryption_key()
    return cipher.decrypt(encrypted_data)

def encrypt_verification_code(data, secret_key, timestamp=None, nonce=None):
    """Create a secure hash (HMAC) to verify sender identity."""
    if timestamp is None:
        timestamp = int(time.time()) # Get current UNIX timestamp
    elif timestamp <= int(time.time()):  # Reject if older than 10 minutes
        raise ValueError("Timestamp is too old")

    if nonce is None:
        nonce = secrets.token_hex(16) # Generate a random nonce
    else:
        #TODO: Check if nonce is unique
        pass

    message = f"{data}|{timestamp}|{nonce}|{secret_key}".encode()

    return hashlib.sha256(message).hexdigest(), timestamp, nonce

def write_temp_decrypted_data(decrypted_data, path=".env"):
# Write the decrypted data back to a .env file (temporarily)
    with open(path, "wb") as file:
        file.write(decrypted_data)

"""# Load environment variables from the decrypted .env file
load_dotenv()

# Access the environment variables
my_secret_key = os.getenv('MY_SECRET_KEY')
print("Decrypted secret key:", my_secret_key)

# Optionally, delete the decrypted .env file after use
os.remove(".env")"""
