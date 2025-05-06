import requests
import keyring
from functools import wraps
import logging
from typing import Optional

from core.constant import (
    BACKEND_HOST,
    BACKEND_PORT,
    BACKEND_APP_ID,
    NAME_GC_LOCATION_HOST,
    TIME_DOCUMENT_ALIVE,
)

from services.security_service import (
    SecurityService
)

from core.session import Session

from core.functions import (
    get_selected_fields_as_req_json,
    get_selected_fields_as_json
)

from core.cloud_services_utils import (
    shorten_key_string
)

from core.security_utils import (
    hash_message,
    hash_message_extended
)

from core.enums import StatusDataSentDb

class CloudService():
    base_endpoint = f"http://{BACKEND_HOST}:{BACKEND_PORT}/{BACKEND_APP_ID}/{NAME_GC_LOCATION_HOST}"
    endpoint_get_pubkey = f"{base_endpoint}/get_pubkey"
    endpoint_store_user = f"{base_endpoint}/store_user"
    endpoint_delete_user = f"{base_endpoint}/delete_user"
    endpoint_send_data = f"{base_endpoint}/store_payload"
    endpoint_ping = f"{base_endpoint}/ping"

    def __init__(self, session: Session, security_service: SecurityService):
        self.session = session
        self.security_service = security_service

        self.document_expiration_time = TIME_DOCUMENT_ALIVE
        
        # Attributes for service states
        self.is_online: bool = None

    def check_service_online():
        def decorator(method):
            @wraps(method)
            def wrapper(self, *args, **kwargs):
                if self.is_online in [False, None]:
                    self.is_online = self._send_ping()
                if self.is_online:
                    return method(self, *args, **kwargs)
                
                logging.info("Cloud-Service is not online")
                return False
            return wrapper
        return decorator
    
    def is_owner_registered(self, owner: str):
        # Owner
        print(f"email: ", owner)
        owner_hash: str = hash_message(owner)

        pubkey_data: dict = self.get_user_pubkey(owner_hash)
        pubkey: str = pubkey_data.get("pubkey") if pubkey_data else ""
        
        self.is_online = True if pubkey else False
        return self.is_online
    
    def send_ping(self):
        logging.info(f"Ping sent to endpoint {self.base_endpoint}")
        try:
            _ = requests.get(self.endpoint_ping)
            self.is_online = True
            return True
        except:
            self.is_online = False
            return False

    @check_service_online()
    def upload_user(self, owner: str):
        try:
            #print(f"1 Owner before hash: {owner}")

            # Owner
            owner_hash: str = hash_message(owner)

            # Data
            pubkey = self.security_service.get_pubkey_to_string()
            #logging.debug(f"upload_user - pubkey - {pubkey}")
            
            # Setup payload details
            payload_details = self._setup_user_payload_details(owner_hash, pubkey)

            # Base payload
            payload = {"owner": owner_hash}

            # Complete payload
            payload.update(payload_details)

            # Make request
            response = requests.post(self.endpoint_store_user, json=payload)
            payload = response.json()
            
            if response.status_code == 200:
                self.is_online = True
                shorten_token = shorten_key_string(payload["token"])
                logging.debug(f"User stored in cloud. Token: {shorten_token}")
                return True, payload["token"]
            
            elif response.status_code != 409:
                self.is_online = False
                logging.debug(f"User already stored in cloud")
                return True, ""
            return False, ""
        
        except Exception as e:
            self.is_online = False
            logging.error(f"Error at storing user in cloud. Message: {e}")
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
            logging.error(f"delete_user: {e}")
            return False

    def get_user_pubkey(self, user_hash: str) -> dict[str, str]:
        """
        Public method to obtain parsed public key for a given user.
        Handles errors and returns a safe default on failure.
        """
        header = self._make_header()

        try:
            response = self._get_pubkey(user_hash, header)
            response.raise_for_status()  # Raise HTTPError if status is 4xx/5xx

            pubkey_str = response.json().get("pubkey", "")
            pubkey = self._get_pubkey_from_string(pubkey_str)

            return {"owner": user_hash, "pubkey": pubkey}

        except requests.RequestException as e:
            logging.error(f"[CloudService] HTTP request failed: {e}")
        except (ValueError, KeyError) as e:
            logging.error(f"[CloudService] Invalid response structure: {e}")

        return {"owner": user_hash, "pubkey": ""}
    
    def _get_pubkey(self, user_hash: str, header: Optional[dict[str, str]] = None) -> requests.Response:
        """
        Internal method that makes the HTTP request to fetch the pubkey.
        It doesn't handle errors — caller is responsible for exception handling.
        """
        header = header or {"Content-Type": "application/json"}
        url = f"{self.endpoint_get_pubkey}?owner={user_hash}"
        return requests.get(url, headers=header)

    @staticmethod
    def _get_pubkey_from_string(pubkey_str: str):
        return SecurityService.get_pubkey_from_string(pubkey_str)

    @check_service_online()
    def upload_data(
            self,
            fields: list, 
            owner: str, 
            consumers: list[str], 
            on_request: bool=False
            ) -> dict[str, str]:
        
        if not consumers or len(consumers) == 0:
            logging.warning("No consumers selected.")
            return {}

        if not fields or len(fields) == 0:
            logging.warning("No fields selected.")
            return {}
        
        # Request
        if on_request:
            data = get_selected_fields_as_req_json(fields, owner, as_dict=False)
        else:
            data = get_selected_fields_as_json(fields, as_dict=False)

        # Owner
        print(f"email: ", owner)
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
                logging.info(f"✅ Data sent to BACKEND: {response.json()}")
            except Exception as e:
                results[consumer] = CloudService.evaluate_status_code(StatusDataSentDb.ERROR)
                logging.error(f"❌ Failed to send data to BACKEND: {e}")
        return results
    
    def _setup_user_payload_details(self, owner_hash: str, pubkey: str):
        # Creation timestamp
        creation_at = self.security_service.get_current_utc_ts()
        creation_at_str = str(int(creation_at))

        # Expiration timestamp
        expires_at = self.security_service.get_timestamp_after_expiry(
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
        creation_at = self.security_service.get_current_utc_dt()
        creation_at_str = str(int(creation_at))

        # Expiration timestamp
        expires_at = self.security_service.get_timestamp_after_expiry(
            creation_at, 
            self.document_expiration_time
            )
        expires_at_str = str(int(expires_at))

        # Get consumer's public key
        consumer_pubkey = self.get_user_pubkey(consumer_hash)["pubkey"]

        # Encrypt data with consumer's public key
        data_hash = hash_message(data)
        
        verification_fields = [owner_hash, consumer_hash, data_hash]
        
        encrypted_data = self.security_service.encrypt(data.encode("utf-8"), consumer_pubkey)
        
        payload_data_str = self.security_service.convert_bytes_to_b64(encrypted_data)
        
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
        token = self.session.get_verification_token()
        header = {
            "Authorization": f"Bearer {token}"
        }
        return header

    def _make_credentials(self, fields: list[str]):
        # 1. Create signature (bytes) and verification code (string)
        signature_code, verification_code = hash_message_extended(".".join(fields))

        # 2. Sign raw hash bytes directly
        signature = self.security_service.sign(signature_code)

        # 3. Convert signature to base64 string for safe transport
        signature = self.security_service.convert_bytes_to_b64(signature)
        return signature, verification_code

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