from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    message = data.get("message", "")
    print("Received H1 content:", message)
    return jsonify({"status": f"Message received: {message}"}), 200

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
