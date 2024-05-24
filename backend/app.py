# backend/app.py

from flask import Flask, request, jsonify
from ai_service import get_gemini_info

app = Flask(__name__)

@app.route("/ai-service")
def gemini_info():
    place_name = request.args.get("place")
    if place_name:
        # Call the get_gemini_info function and process the results
        results, estimated_cost = get_gemini_info(place_name)
        print(f"Results: {results}")
        return jsonify({"results": results, "estimated_cost": estimated_cost})
    else:
        return jsonify({"error": "Place name not provided"}), 400

if __name__ == "__main__":
    app.run(debug=True)
