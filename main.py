from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Only allow your Netlify site
CORS(app, origins=["https://roaring-travesseiro-ef49de.netlify.app"])

@app.route("/receive", methods=["POST", "OPTIONS"])
def receive():
    if request.method == "OPTIONS":
        # Preflight request
        return jsonify({"status": "OK"}), 200

    # Actual POST request
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    print("Received H1 content:", message)
    return jsonify({"status": f"Message received: {message}"}), 200

@app.get("/")
def home():
    return "Flask server is running with CORS enabled."
