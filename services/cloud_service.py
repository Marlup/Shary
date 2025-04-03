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
            url = f"{self.base_endpoint}/upload_pubkey"
            url = self.endpoint_upload_pubkey
            
            timestamp = cryptographer.get_current_utc_iso()
            expires_at = datetime.datetime.fromisoformat(timestamp) + datetime.datetime(second=self.document_expiration_time),
            owner_hash = hash_message(owner)
            public_key = cryptographer.get_pub_key_string()
            data_signature = ".".join([#timestamp, 
                                       owner_hash,
                                       self.secret_key, 
                                       ]) \
                                .encode("utf-8")
            
            verification_hash = hash_message(data_signature)
            #print(f"verification_hash - {verification_hash}")
            # Bytes signature to base64
            signature_b64 = cryptographer.make_bin_blob_to_base64(
                cryptographer.sign(data_signature)
            ).decode("utf-8")  # ✅ safe string

            #print(f"signature base64 - {signature_b64}")

            payload = {
                "owner": owner_hash,
                "consumer": "",
                "timestamp": timestamp,
                "expires_at": expires_at,
                "pub_key": public_key,
                "verification_hash": verification_hash,
                "signature": signature_b64
            }

            response = requests.post(url, json=payload)
            print("PubKey upload:", response.json())

            return True
        
        except Exception as e:
            print(f"Error at upload_pubkey: {e}")
            return False

    def get_other_pubkey(self, owner: str, timestamp: str):
        owner_hash = hash_message(owner)
        verification_hash = hash_message(
            ".".join(
                [
                    #timestamp, 
                    owner_hash,
                    self.secret_key
                ]
                    )
                    )
        
        url = f"{self.endpoint_get_pubkey}?verification_hash={verification_hash}"
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

        # Owner and consumers
        owner_hash = hash_message(owner)
        consumers_hash = [hash_message(consumer) for consumer in consumers]
        consumers_hash_string = ",".join(consumers_hash)
        
        # Timestamp and expiration timestamp
        timestamp = cryptographer.get_current_utc_dt()
        timestamp_str = timestamp.isoformat()
        expires_at_str = cryptographer.get_dt_after_expiry_seconds(
            timestamp,
            self.document_expiration_time
            ).isoformat()
        
        # Data
        data_str = json.dumps(data) if not isinstance(data, str) else data
        encrypted_data = cryptographer.encrypt(data_str.encode("utf-8"))
        encoded_data = cryptographer.make_bin_blob_to_base64(encrypted_data)
        encoded_data_str = encoded_data.decode("utf-8")
        
        # Verification and Authentication 
        verification_string = ".".join([#timestamp_str,
                                        owner_hash,
                                        consumers_hash_string,
                                        self.secret_key,
                                        ]) \
                                 .encode("utf-8")
    
        verification_hash = hash_message(verification_string)
        signature_data = ".".join([timestamp_str,
                                   self.secret_key,
                                   owner_hash, 
                                   consumers_hash_string,
                                   encoded_data_str]) \
                            .encode("utf-8")
        signature = cryptographer.sign(
            cryptographer.make_bin_blob_to_base64(signature_data)
            )
        signature_str = str(cryptographer.make_bin_blob_to_base64(signature).decode("utf-8"))

        payload = {
            "mode": mode,
            "owner": owner_hash,
            "consumers": consumers_hash,
            "creation_at": timestamp_str,
            "expires_at": expires_at_str,
            "data": signature_str,
            "verification_hash": verification_hash,
            "signature": signature_str,
        }

        try:
            response = requests.post(url, json=payload)
            #response.raise_for_status()
            print(f"✅ Data sent to Firebase for {consumers_hash}: {response.json()}")
        except Exception as e:
            print(f"❌ Failed to send to Firebase: {e}")

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