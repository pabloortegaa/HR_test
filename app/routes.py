from flask import Flask, request
from app import app

@app.route('/')
def hello_world():
    return 'Hello, World!'

