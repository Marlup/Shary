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

    def __init__(self):
        #if secret_key:
        #    self.secret_key = secret_key
        #else:
        #    self.secret_key = RSACrypto.generate_secret_key()
        self.document_expiration_time = TIME_DOCUMENT_ALIVE
        self.token = self.load_verification_token()

        # Attributes for service states
        self.is_online = None

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
    def store_user(self, cryptographer, owner: str):
        try:
            #print(f"1 Owner before hash: {owner}")

            # Owner
            owner_hash: str = hash_message(owner)

            # Data
            pubkey = cryptographer.get_pubkey_to_string()
            logging.debug(f"store_user - pubkey - {pubkey}")

            # Base payload
            payload = {
                "owner": owner_hash,
            }
            
            # Setup payload details
            payload_details = self._setup_store_user_payload_details(
                cryptographer, 
                owner_hash, 
                pubkey, 
            )

            # Complete payload
            payload.update(payload_details)

            # Make request
            response = requests.post(self.endpoint_store_user, json=payload)
            payload = response.json()
            
            if response.status_code == 200:
                self.is_online = True
                self._set_verification_token(payload["token"])
                logging.debug(f"store_user - payload['token'] - {payload["token"]}")
                return True
            
            elif response.status_code != 409:
                self.is_online = False
            return False
        
        except Exception as e:
            self.is_online = False
            Logger.error(f"store_user: {e}")
            return False
    
    @check_service_online()
    def delete_user(self, cryptographer, owner: str):
        try:
            # Owner
            owner_hash = hash_message(owner)

            # Signature
            signature, _ = self._make_credentials([owner_hash], cryptographer)

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

    def get_other_pubkey(self, other: str, as_hash: bool=True):
        if not as_hash:
            other = hash_message(other)
        # Header request
        header = self._make_header()

        # Make request
        response = requests.get(f"{self.endpoint_get_pubkey}?owner={other}", headers=header)
        if response.status_code == 200:
            pubkey_str = response.json()["pubkey"]
            pubkey = CloudService._get_pubkey_from_string(pubkey_str)

            return {"owner": other, "pubkey": pubkey}
        elif response.status_code == 409:
            return {"owner": other, "pubkey": ""}
        else:
            Logger.error(f"method get_other_pubkey: {response.json()["error"]}")
            return {"owner": other, "pubkey": ""}

    @staticmethod
    def _get_pubkey_from_string(pubkey_str: str):
        return RSACrypto.get_pubkey_from_string(pubkey_str)

    @check_service_online()
    def send_data(
            self,
            cryptographer,
            rows: list, 
            owner: str, 
            consumers: list[str], 
            on_request: bool=False
            ):
        
        if consumers is None or len(consumers) == 0:
            Logger.warning("No consumers selected.")
            return
        
        # Request
        if on_request:
            data = get_selected_fields_as_req_json(rows, owner, as_dict=False)
        else:
            data = get_selected_fields_as_json(rows, as_dict=False)

        # Owner        
        owner_hash = hash_message(owner)
        
        # Header request
        header = self._make_header()
        
        results = {}
        for consumer in consumers:
            # Consumer
            consumer_hash = hash_message(consumer)

            # Base payload
            payload = {
                "owner": owner_hash,
            }

            # Setup payload details
            payload_details = self._setup_store_data_payload_details(
                cryptographer, 
                owner_hash, 
                consumer_hash,
                data, 
                )

            # Complete payload
            payload.update(payload_details)

            # Make request
            try:
                response = requests.post(self.endpoint_send_data, 
                                         json=payload,
                                         headers=header)
                results[consumer] = CloudService.evaluate_status_code(response.status_code)
                Logger.info(f"Data sent to Firebase: {response.json()}")
            except Exception as e:
                results[consumer] = CloudService.evaluate_status_code(StatusDataSentDb.ERROR)
                Logger.error(f"❌ Failed to send data to Firebase: {e}")

    @check_service_online()
    def add_consumer_to_document(self, doc_id: str, new_consumers: list[str]):
        try:
            new_consumer_hashes = [hash_message(new_consumer) for new_consumer in new_consumers]

            # Header request
            header = self._make_header()

            payload = {
                "doc_id": doc_id,
                "consumers": new_consumer_hashes,
            }
            
            # Make request
            response = requests.post(f"{self.base_endpoint}/update_consumers",
                                      json=payload,
                                      headers=header)
            response.raise_for_status()
            Logger.info(f"✅ Consumers added: {new_consumer_hashes}")
            return True
        except Exception as e:
            Logger.error(f"add_consumer_to_document sent: {e}")
            return False
    
    @check_service_online()
    def remove_consumers_from_document(self, doc_id: str, consumers: list[str]):
        try:
            consumer_hashes = [hash_message(consumer) for consumer in consumers]

            # Header request
            header = self._make_header()

            payload = {
                "doc_id": doc_id,
                "consumers": consumer_hashes
            }

            # Make request
            response = requests.post(f"{self.base_endpoint}/delete_consumers", 
                                     json=payload,
                                     headers=header)
            response.raise_for_status()
            Logger.info(f"remove_consumers_from_document sent: {consumer_hashes}")
            return True
        except Exception as e:
            Logger.error(f"❌ Failed to remove consumers: {e}")
            return False
    
    def _setup_store_user_payload_details(
            self, 
            cryptographer,
            owner_hash: str, 
            pubkey: str
            ):
        # Creation timestamp
        creation_at = cryptographer.get_current_utc_dt()
        creation_at_str = str(int(creation_at))

        # Expiration timestamp
        expires_at = cryptographer.get_timestamp_after_expiry(
            creation_at, 
            self.document_expiration_time
            )
        expires_at_str = str(int(expires_at))

        # Verification fields and data
        verification_fields = [owner_hash, pubkey]
        # 1. Create signature (bytes) and verification code (string)
        signature, verification_code = self._make_credentials(verification_fields, cryptographer)
        
        return {
            "creation_at": creation_at_str,
            "expires_at": expires_at_str,
            "pubkey": pubkey,
            "verification": verification_code,
            "signature": signature
            }

    def _setup_store_data_payload_details(
            self, 
            cryptographer: RSACrypto,
            owner_hash: str, 
            consumer_hash: str, 
            data: str
            ):
        
        # Creation timestamp
        creation_at = cryptographer.get_current_utc_dt()
        creation_at_str = str(int(creation_at))

        # Expiration timestamp
        expires_at = cryptographer.get_timestamp_after_expiry(
            creation_at, 
            self.document_expiration_time
            )
        expires_at_str = str(int(expires_at))

        # Get consumer's public key
        consumer_pubkey = self.get_other_pubkey(consumer_hash)["pubkey"]
        
        logging.debug(f"_setup_store_data_payload_details - consumer_pubkey: {RSACrypto.make_pubkey_to_string(consumer_pubkey)}")
        if not consumer_pubkey:
            raise ValueError(f"Public key does not exist for consumer {consumer_pubkey}")

        # Encrypt data with consumer's public key
        logging.debug(f"_setup_store_data_payload_details - data: {data}")
        data_hash = hash_message(data)
        logging.debug(f"_setup_store_data_payload_details - data_hash: {data_hash}")
        logging.debug(f"_setup_store_data_payload_details - encrypted_data: {encrypted_data}")
        verification_fields = [owner_hash, consumer_hash, data_hash]
        encrypted_data = cryptographer.encrypt(data.encode("utf-8"), consumer_pubkey)
        payload_data_str = cryptographer.convert_bytes_to_b64(encrypted_data)
        
        logging.debug(f"_setup_store_data_payload_details - verification_fields: {verification_fields}")

        # 1. Create signature (bytes) and verification code (string)
        signature, verification_code = self._make_credentials(verification_fields, cryptographer)

        logging.debug(f"_setup_store_data_payload_details - verification_code: {verification_code}")
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

    def _make_credentials(self, fields: list[str], cryptographer):
        # 1. Create signature (bytes) and verification code (string)
        signature_code, verification_code = hash_message_extended(".".join(fields))

        # 2. Sign raw hash bytes directly
        signature = cryptographer.sign(signature_code)

        # 3. Convert signature to base64 string for safe transport
        signature = cryptographer.convert_bytes_to_b64(signature)
        return signature, verification_code
    
    def _set_verification_token(self, token: str):
        self.token = token
        self.save_verification_token(token)

        loaded_token = self.load_verification_token()
        Logger.debug(f"Token saved to keyring: {repr(token)}")
        Logger.debug(f"Token loaded to keyring: {repr(loaded_token)}")

        print(f"tokens token: {token}")
        print(f"tokens loaded token: {loaded_token}")
        print(f"tokens lenghts (token and loaded): {len(token)}, {len(loaded_token)}")
        print(f"tokens equal?: {token.strip() == loaded_token.strip()}")
        #for x, y in zip(token, loaded_token):
        #    print(f"{x} - {y}: {x == y}\n")
    
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