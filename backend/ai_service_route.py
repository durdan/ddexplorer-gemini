# backend/app.py

from flask import Flask, request, jsonify
from ai_service import get_gemini_info
from flask import Blueprint

routes_blueprint = Blueprint('routes', __name__)


@routes_blueprint.route('/ai-service', methods=['GET'])
def gemini_info():
    place_name = request.args.get("place")
    user_phone = request.args.get("phone_number")
    if place_name:
        # Call the get_gemini_info function and process the results
        results, estimated_cost = get_gemini_info(place_name,user_phone)
         
        return jsonify({"results": results, "estimated_cost": estimated_cost})
    else:
        return jsonify({"error": "Place name not provided"}), 400
