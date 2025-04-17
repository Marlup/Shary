import requests
import keyring
from functools import wraps
import logging

from kivy.logger import Logger

from core.constant import (
    FIREBASE_HOST,
    FIREBASE_PORT,
    FIREBASE_APP_ID,
    NAME_GC_LOCATION_HOST,
    TIME_DOCUMENT_ALIVE,
)

from security.crypto import (
    hash_message,
    hash_message_extended,
    RSACrypto
)

from core.functions import (
    get_selected_fields_as_req_json,
    get_selected_fields_as_json
)

from core.enums import StatusDataSentDb

class CloudService():
    base_endpoint = f"http://{FIREBASE_HOST}:{FIREBASE_PORT}/{FIREBASE_APP_ID}/{NAME_GC_LOCATION_HOST}"
    endpoint_get_pubkey = f"{base_endpoint}/get_pubkey"
    endpoint_store_user = f"{base_endpoint}/store_user"
    endpoint_delete_user = f"{base_endpoint}/delete_user"
    endpoint_send_data = f"{base_endpoint}/store_payload"
    endpoint_ping = f"{base_endpoint}/ping"

    crypto = RSACrypto.get_instance()

    def __init__(self):
        self.document_expiration_time = TIME_DOCUMENT_ALIVE
        self.token = self.load_verification_token()
        
        # Attributes for service states
        self.is_online: bool = None

        self.crypto = RSACrypto.get_instance()

    def check_service_online():
        def decorator(method):
            @wraps(method)
            def wrapper(self, *args, **kwargs):
                #logging.info(f"check_service_online - token: {self.token}")
                if self.is_online in [False, None]:
                    self.is_online = self.send_ping()
                if self.is_online:
                    return method(self, *args, **kwargs)
                
                Logger.info("Cloud-Service is not online")
                return False
            return wrapper
        return decorator
        
    def is_owner_registered(self, owner: str):
        # Owner
        owner_hash: str = hash_message(owner)

        pubkey_data: dict = self.get_other_pubkey(owner_hash)
        pubkey: str = pubkey_data.get("pubkey") if pubkey_data else ""
        
        self.is_online = True if pubkey else False
        return self.is_online
    
    def send_ping(self):
        logging.info(f"Ping sent to endpoint {self.base_endpoint}")
        try:
            _ = requests.get(self.endpoint_ping)
            self.is_online = True
            self.load_verification_token()
            return True
        except:
            self.is_online = False
            return False

    @check_service_online()
    def store_user(self, owner: str):
        try:
            #print(f"1 Owner before hash: {owner}")

            # Owner
            owner_hash: str = hash_message(owner)

            # Data
            pubkey = self.crypto.get_pubkey_to_string()
            #logging.debug(f"store_user - pubkey - {pubkey}")
            
            # Setup payload details
            payload_details = self._setup_user_payload_details(owner_hash, pubkey)

            # Base payload
            payload = {"owner": owner_hash}

            # Complete payload
            payload.update(payload_details)

            # Make request
            response = requests.post(self.endpoint_store_user, json=payload)
            print(repr(response.text),  response.status_code)

            payload = response.json()
            
            if response.status_code == 200:
                self.is_online = True
                self._set_verification_token(payload["token"])
                logging.debug(f"store_user - payload['token'] - {payload['token']}")
                return True
            
            elif response.status_code != 409:
                self.is_online = False
            return False
        
        except Exception as e:
            self.is_online = False
            Logger.error(f"cloud-service - store_user: {e}")
            return False
    
    @check_service_online()
    def delete_user(self, owner: str):
        try:
            # Owner
            owner_hash = hash_message(owner)

            # Signature
            signature, _ = self._make_credentials([owner_hash])

            # Base payload
            payload = {
                "owner": owner_hash,
                "signature": signature,
            }

            # Header request
            header = self._make_header()

            # Make request
            response = requests.post(self.endpoint_delete_user, 
                                     json=payload, 
                                     headers=header)

            return True if response.status_code in 200 else False
        
        except Exception as e:
            Logger.error(f"delete_user: {e}")
            return False

    def get_other_pubkey(self, user: str, as_hash: bool=True):
        if not as_hash:
            user = hash_message(user)
        # Header request
        header = self._make_header()

        # Make request
        response = requests.get(f"{self.endpoint_get_pubkey}?owner={user}", headers=header)
        if response.status_code == 200:
            pubkey_str = response.json()["pubkey"]
            pubkey = CloudService._get_pubkey_from_string(pubkey_str)

            return {"owner": user, "pubkey": pubkey}
        else :
            raise Exception(f"Public key does not exist for consumer {user}")
    @staticmethod
    def _get_pubkey_from_string(pubkey_str: str):
        return RSACrypto.get_pubkey_from_string(pubkey_str)

    @check_service_online()
    def send_data(
            self,
            fields: list, 
            owner: str, 
            consumers: list[str], 
            on_request: bool=False
            ) -> dict[str, str]:
        
        if not consumers or len(consumers) == 0:
            Logger.warning("No consumers selected.")
            return {}

        if not fields or len(fields) == 0:
            Logger.warning("No fields selected.")
            return {}
        
        # Request
        if on_request:
            data = get_selected_fields_as_req_json(fields, owner, as_dict=False)
        else:
            data = get_selected_fields_as_json(fields, as_dict=False)

        # Owner        
        owner_hash = hash_message(owner)
        
        # Header request
        header = self._make_header()
        
        results = {}
        for consumer in consumers:
            # Consumer
            consumer_hash = hash_message(consumer)

            # Base payload
            payload = {"owner": owner_hash}

            try:
                # Setup payload details
                payload_details = self._setup_data_payload_details(owner_hash, consumer_hash, data)

                # Complete payload
                payload.update(payload_details)

                # Make request
                response = requests.post(self.endpoint_send_data, 
                                         json=payload,
                                         headers=header)
                results[consumer] = CloudService.evaluate_status_code(response.status_code)
                Logger.info(f"✅ Data sent to Firebase: {response.json()}")
            except Exception as e:
                results[consumer] = CloudService.evaluate_status_code(StatusDataSentDb.ERROR)
                Logger.error(f"❌ Failed to send data to Firebase: {e}")
        return results
    
    def _setup_user_payload_details(self, owner_hash: str, pubkey: str):
        # Creation timestamp
        creation_at = self.crypto.get_current_utc_dt()
        creation_at_str = str(int(creation_at))

        # Expiration timestamp
        expires_at = self.crypto.get_timestamp_after_expiry(
            creation_at, 
            self.document_expiration_time
            )
        expires_at_str = str(int(expires_at))

        # Verification fields and data
        verification_fields = [owner_hash, pubkey]
        
        # 1. Create signature (bytes) and verification code (string)
        signature, verification_code = self._make_credentials(verification_fields)
        
        return {
            "creation_at": creation_at_str,
            "expires_at": expires_at_str,
            "pubkey": pubkey,
            "verification": verification_code,
            "signature": signature
            }

    def _setup_data_payload_details(self, owner_hash: str, consumer_hash: str, data: str):
        
        # Creation timestamp
        creation_at = self.crypto.get_current_utc_dt()
        creation_at_str = str(int(creation_at))

        # Expiration timestamp
        expires_at = self.crypto.get_timestamp_after_expiry(
            creation_at, 
            self.document_expiration_time
            )
        expires_at_str = str(int(expires_at))

        # Get consumer's public key
        consumer_pubkey = self.get_other_pubkey(consumer_hash)["pubkey"]

        # Encrypt data with consumer's public key
        data_hash = hash_message(data)
        
        verification_fields = [owner_hash, consumer_hash, data_hash]
        
        encrypted_data = self.crypto.encrypt(data.encode("utf-8"), consumer_pubkey)
        
        payload_data_str = self.crypto.convert_bytes_to_b64(encrypted_data)
        
        # 1. Create signature (bytes) and verification code (string)
        signature, verification_code = self._make_credentials(verification_fields)

        return {
            "consumer": consumer_hash,
            "creation_at": creation_at_str,
            "expires_at": expires_at_str,
            "data": payload_data_str,
            "verification": verification_code,
            "signature": signature
            }

    def _make_header(self):
        header = {
            "Authorization": f"Bearer {self.token}"
        }
        Logger.debug(f"self.token: {self.token}")
        return header

    def _make_credentials(self, fields: list[str]):
        # 1. Create signature (bytes) and verification code (string)
        signature_code, verification_code = hash_message_extended(".".join(fields))

        # 2. Sign raw hash bytes directly
        signature = self.crypto.sign(signature_code)

        # 3. Convert signature to base64 string for safe transport
        signature = self.crypto.convert_bytes_to_b64(signature)
        return signature, verification_code
    
    def _set_verification_token(self, token: str):
        self.token = token
        self.save_verification_token(token)
    
    def save_verification_token(self, token: str) -> None:
        keyring.set_password("shary_app", "owner_verification_token", token)
    
    def load_verification_token(self) -> str:
        token = keyring.get_password("shary_app", "owner_verification_token")
        self.token = token if token else ""
        return self.token

    @staticmethod
    def evaluate_status_code(status_code):
        if status_code == 200:
            return StatusDataSentDb.STORED
        elif status_code == 400:
            return StatusDataSentDb.MISSING_FIELD
        elif status_code == 409:
            return StatusDataSentDb.EXISTS
        elif status_code == 500:
            return StatusDataSentDb.ERROR