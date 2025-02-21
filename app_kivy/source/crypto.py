from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

def load_encryption_key(path="secret.key"):
    # Load the encryption key
    with load_encryption_key("secret.key", "rb") as key_file:
        key = key_file.read()
    return Fernet(key)

def decrypt_data(path=".env.enc"):
    # Decrypt the .env file
    with open(path, "rb") as enc_file:
        encrypted_data = enc_file.read()
    cipher = load_encryption_key()
    return cipher.decrypt(encrypted_data)

def write_temp_decrypted_data(decrypted_data, path=".env"):
# Write the decrypted data back to a .env file (temporarily)
    with open(path, "wb") as file:
        file.write(decrypted_data)

# Load environment variables from the decrypted .env file
load_dotenv()

# Access the environment variables
my_secret_key = os.getenv('MY_SECRET_KEY')
print("Decrypted secret key:", my_secret_key)

# Optionally, delete the decrypted .env file after use
os.remove(".env")
