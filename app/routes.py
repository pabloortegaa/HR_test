from flask import Flask, request
from app import app
import csv
from flask import jsonify

@app.route('/')
def hello_world():
    return 'Hello, World!'



CSV_FILE = "data/loads.csv"  # Path to your CSV file

def find_load(reference_number):
    """Efficiently searches for a load in the CSV file without loading everything into memory."""
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


@app.route("/loads", methods=["GET"])
def get_load():
    # Get the JSON data from the request
    data = request.get_json()
    reference_number = data.get("reference_number")
    if not reference_number:
        return jsonify({"error": "Reference number is required"}), 400
    load_details = find_load(reference_number)
    if not load_details:
        return jsonify({"error": "Load not found"}), 404
    
    return jsonify(load_details), 200



if __name__ == "__main__":
    app.run() 
