import json
import requests
import datetime

from core.constant import (
    FIREBASE_HOST,
    FIREBASE_PORT,
    FIREBASE_APP_ID,
    NAME_GC_LOCATION_HOST,
    TIME_DOCUMENT_ALIVE,
)

from security.crypto import (
    make_verification_hash,
    hash_message,
)

from core.functions import (
    get_selected_fields_as_req_json,
    get_selected_fields_as_json
)

class CloudService():
    base_endpoint = f"http://{FIREBASE_HOST}:{FIREBASE_PORT}/{FIREBASE_APP_ID}/{NAME_GC_LOCATION_HOST}"
    endpoint_get_pubkey = f"{base_endpoint}/get_pubkey"
    endpoint_upload_pubkey = f"{base_endpoint}/upload_pubkey"
    endpoint_send_data = f"{base_endpoint}/store_payload"

    def __init__(self, secret_key: str):
        self.document_expiration_time = TIME_DOCUMENT_ALIVE
        self.secret_key = secret_key
    
    def set_secret_key(self, key: str):
        self.secret_key = key

    def upload_pubkey(self, cryptographer, owner: str):
        try:
            url = self.endpoint_upload_pubkey
            
            owner_hash = hash_message(owner)
            timestamp = cryptographer.get_current_utc_iso()
            timestamp_str = str(int(timestamp))
            expires_at = datetime.datetime.fromisoformat(timestamp) + \
                  datetime.datetime(second=self.document_expiration_time),
            expires_at_str = str(int(expires_at))
            public_key = cryptographer.get_pub_key_string()
            data_encoded = ".".join([timestamp_str, owner_hash, public_key]) \
                              .encode("utf-8")
            
            # Bytes signature to base64
            signature = cryptographer.make_blob_to_base64(
                cryptographer.sign(data_encoded)
            ).decode("utf-8")  # ✅ safe string

            payload = {
                "owner": owner_hash,
                "creation_at": timestamp_str,
                "expires_at": expires_at_str,
                "pub_key": public_key,
                "verification_hash": hash_message(data_encoded),
                "signature": signature
            }

            response = requests.post(url, json=payload)
            print("PubKey upload:", response.json())

            return True
        
        except Exception as e:
            print(f"Error at upload_pubkey: {e}")
            return False

    def get_other_pubkey(self, owner: str):
        owner_hash = hash_message(owner)
        
        url = f"{self.endpoint_get_pubkey}?owner={owner_hash}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["pub_key"]
        else:
            raise ValueError("Could not fetch other pubkey")

    def send_data(
            self,
            cryptographer,
            rows: list, 
            owner: str, 
            consumers: list[str], 
            on_request: bool=False
            ):
        url = self.endpoint_send_data
        
        # Request mode
        if on_request:
            data = get_selected_fields_as_req_json(rows, owner, as_dict=True)
            mode = "request"
        else:
            data = get_selected_fields_as_json(rows, as_dict=True)
            mode = "send"

        # Owner        
        owner_hash = hash_message(owner)

        # Timestamp and expiration timestamp
        timestamp = cryptographer.get_current_utc_dt()
        timestamp_str = str(int(timestamp))
        expires_at = cryptographer.get_dt_after_expiry_seconds(
            timestamp,
            self.document_expiration_time
            )
        expires_at_str = str(int(expires_at))
        
        # Data
        data_str = json.dumps(data) if not isinstance(data, str) else data
        encrypted_data = cryptographer.encrypt(data_str.encode("utf-8"))
        encrypted_data_str = cryptographer.make_blob_to_base64(encrypted_data).decode("utf-8"),
        
        for consumer in consumers:
            # Consumers
            consumer_hash = hash_message(consumer)
        
            # Verification and Authentication 
            data_encoded = ".".join([
                timestamp_str,
                owner_hash,
                consumer_hash,
                encrypted_data_str
                ]).encode("utf-8")
            
            signature = cryptographer.sign(
                cryptographer.make_blob_to_base64(data_encoded)
                )

            payload = {
                "mode": mode,
                "owner": owner_hash,
                "consumer": consumer_hash,
                "creation_at": timestamp_str,
                "expires_at": expires_at_str,
                "data": encrypted_data_str,
                "verification_hash": hash_message(data_encoded),
                "signature": cryptographer.make_blob_to_base64(signature).decode("utf-8"),
            }

            try:
                response = requests.post(url, json=payload)
                #response.raise_for_status()
                print(f"✅ Data sent to Firebase for consumer {consumer_hash}: {response.json()}")
            except Exception as e:
                print(f"❌ Failed to send data to Firebase for consumer {consumer_hash}: {e}")

    def add_consumer_to_document(self, doc_id: str, new_consumers: list[str]):
        try:
            url = f"{self.base_endpoint}/update_consumers"
            new_consumer_hashes = [hash_message(new_consumer) for new_consumer in new_consumers]

            payload = {
                "doc_id": doc_id,
                "action": "add_consumer",
                "consumers": new_consumer_hashes,
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"✅ Consumers added: {new_consumer_hashes}")
            return True
        except Exception as e:
            print(f"❌ Failed to add consumers: {e}")
            return False

    def remove_consumers_from_document(self, doc_id: str, consumers: list[str]):
        try:
            url = f"{self.base_endpoint}/update_consumers"
            consumer_hashes = [hash_message(consumer) for consumer in consumers]

            payload = {
                "doc_id": doc_id,
                "action": "remove_consumer",
                "consumers": consumer_hashes
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"✅ Consumers removed: {consumer_hashes}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove consumers: {e}")
            return False