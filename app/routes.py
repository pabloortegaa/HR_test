from flask import Flask, request
from app import app
import csv
from flask import jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import hashlib
import requests
load_dotenv()


# Connect to MongoDB
mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
mongo_db_name = os.getenv("MONGO_DB_NAME")
mongo_collection_name = "happy-robot-api-keys"
client = MongoClient(mongo_connection_string)
db = client[mongo_db_name]
collection = db[mongo_collection_name]
# Retrieve all the images from the database
#cursor = collection.find({})
#FMCSA API key
web_key = os.getenv("FMCSA_WEB_KEY")


CSV_FILE = "data/loads.csv"  # Path to your CSV file

@app.route('/')
def hello_world():
    return 'Hello happy robotsss'

def find_load(reference_number):
    """Efficiently searches for a load in the CSV file"""
    try:
        with open(CSV_FILE, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                #print(row["reference_number"][3:], type(reference_number))
                if int(row["reference_number"][3:]) == int(reference_number):
                    return row
    except FileNotFoundError:
        return None
    return None


def authenticate():
    """Check if the request has a valid API key."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    provided_key = auth_header.split(" ")[1]
    hash_provided_key = hashlib.sha256(provided_key.encode()).hexdigest() #hashed key
    # Check if the provided key is in the database
    if not collection.find_one({"key": hash_provided_key}):
        return False
    return True

@app.route("/loads", methods=["GET"])
def get_load():
    """Get a load by reference number."""
    # Check if the request is authenticated
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    # Get the JSON data from the request
    data = request.get_json()
    reference_number = data.get("reference_number")
    if not reference_number:
        return jsonify({"error": "Reference number is required"}), 400
    load_details = find_load(reference_number)
    if not load_details:
        return jsonify({"error": "Load not found."}), 404
    
    return jsonify(load_details), 200


@app.route("/verify_carrier", methods=["POST"])
def obtener_datos_carrier():
    """Verify a carrier by MC number."""
    # Check if the request is authenticated
    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401
    # Get the JSON data from the request
    data = request.get_json()
    mc_number = data.get("mc_number")
    if not mc_number:
        return jsonify({"error": "MC number is required"}), 400
    # Make a request to the FMCSA API
    url = f"https://mobile.fmcsa.dot.gov/qc/services/carriers/{mc_number}?webKey={web_key}"
    response_fmcsa = requests.get(url)
    # Check if the carrier is allowed to operate
    if response_fmcsa.status_code == 200:
        response_fmcsa = response_fmcsa.json()
        # if response_fmcsa['content']['carrier'] exists
        if response_fmcsa['content'] is None or response_fmcsa['content'] == "null": # if the carrier is not found
            return jsonify(
            {
                "error": "Carrier not found.",
                "next_steps": {
                    "1": "Inform the user that no carrier was found under the given MC  number.",
                    "2": {
                        "a": "Ask the user to repeat the MC / DOT number to ensure it was entered correctly.",
                        "b": "If the user provides a new number, attempt to search for the carrier again.",
                        "c": "If no carrier is still found, suggest the user verify their carrier information with FMCSA."
                    }
                }
            }
        ), 404

        elif response_fmcsa['content']["carrier"]['allowedToOperate'] == "Y": # if the carrier is allowed to operate
            legal_name = response_fmcsa['content']["carrier"]['legalName']
            return jsonify(
                {
                "carrier":{
                "legal_name": legal_name,
                "allowed_to_operate": True
            },
            "next_steps": {
                "1" : f"Confirm you found the right carrier name. Ask user exactly this: '{legal_name}?'. Then wait for user to respond." ,
                "2" : {
                "a" : f"If user confirms: move on to finding available loads, MAKE SURE you do not give them load information until you have verified they work for the carrier '{legal_name}'.",
                "b": "If user denies: first, you must ask the user to repeat the name of the carrier they work for ('I'm sorry, I didn't quite catch that. What's the name of the carrier you work for?'). Wait for the user to provide the name again and check if it matches the carrier name you have.",
                "c": "If you still cannot verify the carrier name, ask the user for their MC number ('I'm sorry, what's that MC number again?'). Wait for user to provide number again. Then search for the carrier again with new number the caller provides."
            }}
            }) , 200
        else: # if the carrier is not allowed to operate
            return jsonify(
            {
                "carrier": {
                    "allowed_to_operate": False
                },
                "message": "Carrier is not allowed to operate.",
                "next_steps": {
                    "1": "Inform the user that this carrier is not allowed to operate.",
                    "2": {
                        "a": "Politely let the user know that they will need to verify with FMCSA why their carrier is restricted.",
                        "b": "If the user insists, offer to check another carrier by asking for a different MC number.",
                        "c": "If the user cannot provide another MC number, suggest they contact FMCSA directly for more details."
                    }
                }
            }
        ), 200
    '''
    else:
        return jsonify(
        {
            "error": "Carrier not found.",
            "next_steps": {
                "1": "Inform the user that no carrier was found under the given MC  number.",
                "2": {
                    "a": "Ask the user to repeat the MC / DOT number to ensure it was entered correctly.",
                    "b": "If the user provides a new number, attempt to search for the carrier again.",
                    "c": "If no carrier is still found, suggest the user verify their carrier information with FMCSA."
                }
            }
        }
    ), 404

    '''



if __name__ == "__main__":
    app.run() 

