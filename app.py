from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import os

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

PROGRAMS_JSON = {
    "Fat Loss (FL)": {"factor": 22, "desc": "3-day full-body fat loss", "name": "Fat Loss"},
    "Muscle Gain (MG)": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy", "name": "Muscle Gain"},
    "Beginner (BG)": {"factor": 26, "desc": "Beginner full-body", "name":"Beginner"},
}

@app.route("/")
def health():
    return jsonify({"status": "ok", "service": "ACEest API v1"})

@app.route("/programs", methods=["GET"])
def list_programs():
    return jsonify(PROGRAMS_JSON)

@app.route("/clients", methods=["POST"])
def create_client():
    data = request.get_json()
    name = data.get("name")
    age = data.get("age")
    weight = data.get("weight")
    program = data.get("program")

    if not name or not program or weight is None:
        return jsonify({"error": "name, weight, program required"}), 400

    if program not in PROGRAMS_JSON:
        return jsonify({"error": "invalid program"}), 400

    calories = int(weight * PROGRAMS_JSON[program]["factor"])

    payload = {
        "name": name,
        "age": age,
        "weight": weight,
        "program": PROGRAMS_JSON[program]["name"],
        "calories": calories,
    }

    res = supabase.table("clients").insert(payload).execute()
    return jsonify({"client": payload, "supabase_result": res.model_dump()}), 201

@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    res = supabase.table("clients").select("*").eq("name", name).execute()
    if not res.data:
        return jsonify({"error": "not found"}), 404
    return jsonify(res.data[0])

@app.route("/clients/<name>/progress", methods=["POST"])
def add_progress(name):
    data = request.get_json()
    adherence = data.get("adherence")
    if adherence is None:
        return jsonify({"error": "adherence required"}), 400

    week = datetime.utcnow().strftime("Week %U - %Y")
    payload = {"client_name": name, "week": week, "adherence": adherence}
    res = supabase.table("progress").insert(payload).execute()
    return jsonify({"progress": payload, "supabase_result": res.model_dump()}), 201

@app.route("/clients/<name>/progress", methods=["GET"])
def list_progress(name):
    res = supabase.table("progress").select("*").eq("client_name", name).order("id").execute()
    return jsonify(res.data)

@app.route("/calculate_calories", methods=["POST"])
def calculate_calories():
    data = request.get_json(force=True)
    weight = data.get("weight")
    code = data.get("program_code")

    if weight is None or code not in PROGRAMS_JSON:
        return jsonify({"error": "weight and valid program_code required"}), 400

    factor = PROGRAMS_JSON[code]["factor"]
    calories = int(weight * factor)
    return jsonify({
        "program": PROGRAMS_JSON[code]["name"],
        "weight": weight,
        "calories": calories
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
