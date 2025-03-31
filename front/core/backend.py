# --- source/backend.py ---
from flask import Flask, request, jsonify

def restrict_access():
    allowed_ips = ['127.0.0.1']
    if request.remote_addr not in allowed_ips:
        return jsonify({"error": "Access forbidden"}), 403

def open_file():
    filename = request.args.get("filename")
    if filename:
        return jsonify({"message": f"Processing {filename}..."}), 200
    else:
        return jsonify({"error": "No filename provided."}), 400

def run_flask():
    backend_app = Flask(__name__)
    backend_app.before_request(restrict_access)
    backend_app.add_url_rule("/files/open", "open_file", open_file, methods=['GET'])
    backend_app.run(host="127.0.0.1", port=5001)