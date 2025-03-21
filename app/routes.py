from flask import Flask, request
from app import app
import csv
from flask import jsonify

@app.route('/')
def hello_world():
    return 'Hello, World!'



# Security: API Key Authentication
VALID_API_KEYS = {
    "user1": "key_ABC123",
    "user2": "key_XYZ789",
    "admin": "key_SUPERSECURE"
}
CSV_FILE = "data/loads.csv"  # Path to your CSV file

def find_load(reference_number):
    """Efficiently searches for a load in the CSV file without loading everything into memory."""
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                #print(row.reference_number, reference_number)
                if row["reference_number"][3:] == reference_number:
                    return row
    except FileNotFoundError:
        return None
    return None

'''
@app.before_request
def check_api_key():
    # Get the Authorization header (e.g., "Bearer key_ABC123")
    auth_header = request.headers.get("Authorization")
    print(auth_header)
    
    # If no Authorization header is provided, return an error
    if not auth_header:
        return jsonify({"error": "Missing API key"}), 400
    
    # Extract the API key from the "Bearer" prefix
    token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None

    if not token:
        return jsonify({"error": "Invalid API key format"}), 400
    
    # Validate the API key
    if token not in VALID_API_KEYS:
        return jsonify({"error": "Unauthorized access"}), 401

'''
@app.route("/loads", methods=["GET"])
def get_load():
    reference_number = request.args.get("reference_number")
    if not reference_number:
        return jsonify({"error": "Reference number is required"}), 400
    load_details = find_load(reference_number)
    if not load_details:
        return jsonify({"error": "Load not found"}), 404
    
    return jsonify(load_details), 200



if __name__ == "__main__":
    app.run() #ssl_context=('cert.pem', 'key.pem'))  # Enforce HTTPS
