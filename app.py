from flask import Flask, request, jsonify
from supabase import create_client, Client
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "ACEest API v1"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
