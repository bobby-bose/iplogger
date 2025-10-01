from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS
from pathlib import Path
import re
from datetime import datetime

app = Flask(__name__)

# Allow only your Netlify site (will also allow preflight responses)
CORS(app, origins=["https://roaring-travesseiro-ef49de.netlify.app"])

# File to store IPs (same directory as this script)
BASE_DIR = Path(__file__).resolve().parent
IPS_FILE = BASE_DIR / "ips.txt"

# Regex for IPv4 and IPv6 (simple, practical patterns)
IPv4_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
IPv6_RE = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b')

def extract_ips(text):
    """Return list of IP-like strings found in text (IPv4 first, then IPv6)."""
    if not text:
        return []
    ips = IPv4_RE.findall(text) or []
    ips += IPv6_RE.findall(text)
    return ips

@app.route("/receive", methods=["POST"])
def receive():
    # Expect JSON body like {"message": "..."}
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    # Extract IPs if present
    ips = extract_ips(message)

    # If none found, store the raw message anyway (optional)
    records_to_write = []
    if ips:
        for ip in ips:
            # optional: minimal IPv4 sanity check (0-255) for IPv4 addresses
            if IPv4_RE.match(ip):
                # Accept as-is (you can add stronger validation if desired)
                records_to_write.append(ip)
            else:
                records_to_write.append(ip)
    else:
        # No IP found — store the raw message so you don't lose data
        records_to_write.append(f"RAW: {message}")

    # Append to ips.txt with timestamp
    try:
        with IPS_FILE.open("a", encoding="utf-8") as f:
            for rec in records_to_write:
                f.write(f"{datetime.utcnow().isoformat()}Z\t{rec}\n")
    except Exception as e:
        app.logger.exception("Failed to write to ips.txt")
        return jsonify({"status": "error", "error": str(e)}), 500

    app.logger.info("Stored: %s", records_to_write)
    return jsonify({"status": "Message received", "stored": records_to_write}), 200

@app.route("/download", methods=["GET"])
def download():
    # Return ips.txt as downloadable file named ips.txt
    if not IPS_FILE.exists():
        # If file does not exist, return 404 or an empty file — choose 404:
        abort(404, description="No ips.txt file yet")
    # send_file will set proper Content-Disposition for download
    return send_file(
        IPS_FILE,
        as_attachment=True,
        download_name="ips.txt",
        mimetype="text/plain"
    )

@app.get("/")
def home():
    return "Flask server is running with CORS enabled."

if __name__ == "__main__":
    # Run with flask run or python this_file.py
    app.run(host="0.0.0.0", port=5000, debug=True)
