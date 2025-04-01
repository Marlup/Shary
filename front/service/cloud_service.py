import json
import requests

from front.core.constant import (
    FIREBASE_HOST,
    FIREBASE_PORT,
    FIREBASE_APP_ID,
    NAME_GC_LOCATION_HOST,
    TIME_ALIVE_DEFAULT,
)

from front.security.crypto import (
    make_verification_hash,
    hash_message,
)

from front.core.func_utils import (
    get_selected_fields_as_req_json,
    get_selected_fields_as_json
)

class CloudService():
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.endpoint = f"http://{FIREBASE_HOST}:{FIREBASE_PORT}/{FIREBASE_APP_ID}/{NAME_GC_LOCATION_HOST}"

    def upload_pubkey(self, cryptographer, owner):
        try:
            url = f"{self.endpoint}/upload_pubkey"
            
            timestamp = cryptographer.get_current_utc_iso()
            owner_hash = hash_message(owner)
            public_key = cryptographer.get_pub_key_string()
            data_signature = "|".join([timestamp, self.secret_key, owner_hash]) \
                                .encode("utf-8")
            
            verification_hash = hash_message(data_signature)
            #print(f"verification_hash - {verification_hash}")
            # Bytes signature to base64
            signature_b64 = cryptographer.make_bin_blob_to_base64(
                cryptographer.sign(data_signature)
            ).decode("utf-8")  # ✅ safe string

            #print(f"signature base64 - {signature_b64}")

            payload = {
                "timestamp": timestamp,
                "owner": owner_hash,
                "consumer": "",
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

    def get_other_pubkey(self, owner, timestamp):
        owner_hash = hash_message(owner)
        verification_hash = hash_message("|".join([timestamp, self.secret_key, owner_hash]))
        
        url = f"{self.endpoint}/get_pubkey?verification_hash={verification_hash}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["pub_key"]
        else:
            raise ValueError("Could not fetch other pubkey")

    def send_data(self, cryptographer, rows, owner, consumers, time_alive=TIME_ALIVE_DEFAULT, on_request=False):
        if on_request:
            data = get_selected_fields_as_req_json(rows, owner, as_dict=True)
            mode = "request"
        else:
            data = get_selected_fields_as_json(rows, as_dict=True)
            mode = "send"

        data_str = json.dumps(data) if not isinstance(data, str) else data
        encrypted_data = cryptographer.encrypt(data_str.encode("utf-8"))
        owner_hash = hash_message(owner)
        data_hash = hash_message(data_str)
        verification_hash, timestamp, nonce = make_verification_hash(data_str, self.secret_key)

        consumers_hash = [hash_message(consumer) for consumer in consumers]
        consumers_hash_string = ",".join(consumers_hash)
        data_sig = "|".join([timestamp, nonce, self.secret_key, owner_hash, consumers_hash_string, data_hash])
        signature = cryptographer.sign(data_sig)

        payload = {
            "owner": owner_hash,
            "consumers": consumers_hash,
            "timestamp": timestamp,
            "time_alive": time_alive,
            "nonce": nonce,
            "data": encrypted_data,
            "verification_hash": verification_hash,
            "signature": signature,
            "mode": mode
        }

        try:
            response = requests.post(self.endpoint, json=payload)
            response.raise_for_status()
            print(f"✅ Data sent to Firebase for {consumers_hash}: {response.json()}")
        except Exception as e:
            print(f"❌ Failed to send to Firebase: {e}")

    def add_consumer_to_document(self, doc_id: str, new_consumer_email: str):
        try:
            url = f"{self.endpoint}/update_consumers"
            new_consumer_hash = hash_message(new_consumer_email)

            payload = {
                "doc_id": doc_id,
                "action": "add",
                "consumer_hash": new_consumer_hash
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"✅ Consumer added: {new_consumer_hash}")
            return True
        except Exception as e:
            print(f"❌ Failed to add consumer: {e}")
            return False

    def remove_consumers_from_document(self, doc_id: str, consumers_to_remove: list[str]):
        try:
            url = f"{self.endpoint}/update_consumers"
            consumer_hashes = [hash_message(email) for email in consumers_to_remove]

            payload = {
                "doc_id": doc_id,
                "action": "remove",
                "consumer_hashes": consumer_hashes
            }

            response = requests.post(url, json=payload)
            response.raise_for_status()
            print(f"✅ Consumers removed: {consumer_hashes}")
            return True
        except Exception as e:
            print(f"❌ Failed to remove consumers: {e}")
            return False