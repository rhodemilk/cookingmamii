from flask import Flask, request, jsonify
from flask_cors import CORS
from time import time
import os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://your-frontend.app"}})

# In-memory seeds for MVP
DISHES = {"pad_thai": {"id":"pad_thai","steps":[{"id":"soak_noodles","type":"timer","targetMs":70000}]}}
CHARACTERS = {"raj":{"id":"raj","name":"Raj","fallback":{"1":["Quiet nights need warm cups."]}}}
ORDERS = {}

@app.get("/api/menu")
def menu():
    return jsonify({"dishes":[{"id":k,"name":v.get("name",k)} for k,v in DISHES.items()]})

@app.get("/api/recipes/<dish_id>")
def recipe(dish_id):
    dish = DISHES.get(dish_id)
    if not dish: return jsonify({"error":"not_found"}), 404
    return jsonify({"id":dish_id,"steps":dish["steps"]})

@app.post("/api/orders")
def create_order():
    data = request.get_json()
    oid = f"ord_{int(time()*1000)}"
    ORDERS[oid] = {"customerId":data["customerId"],"dishId":data["dishId"],"score":0}
    return jsonify({"orderId":oid,"customer":CHARACTERS[data["customerId"]],"dish":{"id":data["dishId"]}})

@app.post("/api/orders/<oid>/finish")
def finish(oid):
    body = request.get_json()
    score = sum(s.get("score",0) for s in body.get("totalStepScores",[]))
    ORDERS[oid]["score"] = score
    return jsonify({"finalScore":score,"tags":["demo_tag"]})

@app.post("/api/dialogue/generate")
def dialogue():
    body = request.get_json()
    # call Gemini here; if fails, fallback:
    lines = CHARACTERS.get(body["customerId"],{}).get("fallback",{}).get(str(body["context"].get("stage",1)),["Enjoy your meal."])
    return jsonify({"lines":lines, "nextStage":body["context"].get("stage",1)+1})
