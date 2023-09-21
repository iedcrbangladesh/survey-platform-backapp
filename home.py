import os
from flask import Flask,request,jsonify, json,send_from_directory
from flask_cors import CORS, cross_origin
from app import app
from db import my_col
from bson.objectid import ObjectId
from datetime import datetime
import asyncio

#CORS(app)

@app.route('/api', methods=['GET'])
def home_page():
    return "<h1>Hello, we have started api, Testing Automated Deployment </h1>"

