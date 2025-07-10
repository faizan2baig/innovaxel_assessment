from flask import Flask, request, jsonify, redirect
from flask import Flask, request, jsonify, redirect, render_template, url_for
from datetime import datetime
import string, random

app = Flask(__name__)

# In-memory storage
data_store = {}

def generate_shortcode(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/shorten", methods=["POST"])
def create_url():
    body = request.json
    if not body or "url" not in body:
        return jsonify({"error": "URL is required"}), 400

    short_code = generate_shortcode()
    now = datetime.utcnow().isoformat()

    new_entry = {
        "id": str(len(data_store) + 1),
        "url": body["url"],
        "shortCode": short_code,
        "createdAt": now,
        "updatedAt": now,
        "accessCount": 0
    }

    data_store[short_code] = new_entry
    return jsonify(new_entry), 201

@app.route("/shorten/<short_code>", methods=["GET"])
def get_url(short_code):
    entry = data_store.get(short_code)
    if not entry:
        return jsonify({"error": "Short URL not found"}), 404

    entry["accessCount"] += 1
    return jsonify(entry), 200

@app.route("/shorten/<short_code>", methods=["PUT"])
def update_url(short_code):
    entry = data_store.get(short_code)
    if not entry:
        return jsonify({"error": "Short URL not found"}), 404

    body = request.json
    if not body or "url" not in body:
        return jsonify({"error": "New URL is required"}), 400

    entry["url"] = body["url"]
    entry["updatedAt"] = datetime.utcnow().isoformat()
    return jsonify(entry), 200

@app.route("/shorten/<short_code>", methods=["DELETE"])
def delete_url(short_code):
    if short_code not in data_store:
        return jsonify({"error": "Short URL not found"}), 404

    del data_store[short_code]
    return '', 204

@app.route("/shorten/<short_code>/stats", methods=["GET"])
def get_stats(short_code):
    entry = data_store.get(short_code)
    if not entry:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "id": entry["id"],
        "url": entry["url"],
        "shortCode": entry["shortCode"],
        "createdAt": entry["createdAt"],
        "updatedAt": entry["updatedAt"],
        "accessCount": entry["accessCount"]
    }), 200

# 🆕 Redirect handler
@app.route("/<short_code>", methods=["GET"])
def redirect_to_original(short_code):
    entry = data_store.get(short_code)
    if not entry:
        return jsonify({"error": "Short URL not found"}), 404
    entry["accessCount"] += 1
    return redirect(entry["url"])
