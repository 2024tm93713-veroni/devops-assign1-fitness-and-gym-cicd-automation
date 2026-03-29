from flask import Flask, request, jsonify
from supabase import create_client
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

PROGRAMS_JSON = {
    "Fat Loss (FL)": {
        "factor": 22,
        "desc": "3-day full-body fat loss",
        "name": "Fat Loss"
    },
    "Muscle Gain (MG)": {
        "factor": 35,
        "desc": "Push/Pull/Legs hypertrophy",
        "name": "Muscle Gain"
    },
    "Beginner (BG)": {
        "factor": 26,
        "desc": "Beginner full-body",
        "name": "Beginner"
    }
}


def get_supabase():
    """Lazy init Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY required")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def calculate_bmi(weight, height):
    """Calculate BMI. Weight in kg, height in meters."""
    if height <= 0:
        return None
    return round(weight / (height ** 2), 2)


def get_bmi_category(bmi):
    """Get BMI category."""
    if bmi is None:
        return "Unknown"
    elif bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


@app.route("/")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "ACEest API v1"})


@app.route("/programs", methods=["GET"])
def list_programs():
    """List available programs."""
    return jsonify(PROGRAMS_JSON)


@app.route("/clients", methods=["POST"])
def create_gym_client():
    """Create new client."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400
    name = data.get("name")
    age = data.get("age")
    weight = data.get("weight")
    height = data.get("height")
    program = data.get("program")

    if not name or not program or weight is None:
        return jsonify({"error": "name, weight, program required"}), 400

    if program not in PROGRAMS_JSON:
        return jsonify({"error": "invalid program"}), 400

    if not isinstance(weight, (int, float)):
        return jsonify({"error": "weight must be number"}), 400

    if age is not None and not isinstance(age, int):
        return jsonify({"error": "age must be integer"}), 400

    if height is not None and not isinstance(height, (int, float)):
        return jsonify({"error": "height must be number"}), 400

    calories = int(weight * PROGRAMS_JSON[program]["factor"])
    bmi = calculate_bmi(weight, height) if height else None

    payload = {
        "name": name,
        "age": age,
        "weight": weight,
        "height": height,
        "program": PROGRAMS_JSON[program]["name"],
        "calories": calories,
        "bmi": bmi
    }

    supabase = get_supabase()
    res = supabase.table("clients").insert(payload).execute()
    return jsonify({
        "client": payload,
        "supabase_result": res.model_dump()
    }), 201


@app.route("/clients/<name>", methods=["GET"])
def get_client(name):
    """Get client by name."""
    supabase = get_supabase()
    res = supabase.table("clients").select("*").eq("name", name).execute()
    if not res.data:
        return jsonify({"error": "not found"}), 404
    return jsonify(res.data[0])


@app.route("/clients/<name>/progress", methods=["POST"])
def add_progress(name):
    """Add weekly progress."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400
    adherence = data.get("adherence")
    if adherence is None:
        return jsonify({"error": "adherence required"}), 400

    week = datetime.utcnow().strftime("Week %U - %Y")
    payload = {
        "client_name": name,
        "week": week,
        "adherence": adherence
    }
    supabase = get_supabase()
    res = supabase.table("progress").insert(payload).execute()
    return jsonify({
        "progress": payload,
        "supabase_result": res.model_dump()
    }), 201


@app.route("/clients/<name>/progress", methods=["GET"])
def list_progress(name):
    """List client progress."""
    supabase = get_supabase()
    res = supabase.table("progress") \
        .select("*") \
        .eq("client_name", name) \
        .order("id") \
        .execute()
    return jsonify(res.data)


@app.route("/clients/bmi-groups", methods=["GET"])
def get_bmi_groups():
    """Group all clients by BMI category."""
    supabase = get_supabase()
    res = supabase.table("clients").select("*").execute()
    
    if not res.data:
        return jsonify({
            "Underweight": [],
            "Normal": [],
            "Overweight": [],
            "Obese": [],
            "Unknown": []
        }), 200
    
    # Group clients by BMI category
    grouped = {
        "Underweight": [],
        "Normal": [],
        "Overweight": [],
        "Obese": [],
        "Unknown": []
    }
    
    for client in res.data:
        bmi = client.get("bmi")
        category = get_bmi_category(bmi)
        client_info = {
            "name": client.get("name"),
            "age": client.get("age"),
            "weight": client.get("weight"),
            "height": client.get("height"),
            "bmi": bmi,
            "program": client.get("program"),
            "calories": client.get("calories")
        }
        grouped[category].append(client_info)
    
    return jsonify(grouped), 200


@app.route("/calculate_calories", methods=["POST"])
def calculate_calories():
    """Calculate calories for program."""
    data = request.get_json(force=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400
    weight = data.get("weight")
    code = data.get("program_code")

    if weight is None or code not in PROGRAMS_JSON:
        return jsonify({
            "error": "weight and valid program_code required"
        }), 400

    factor = PROGRAMS_JSON[code]["factor"]
    calories = int(weight * factor)
    return jsonify({
        "program": PROGRAMS_JSON[code]["name"],
        "weight": weight,
        "calories": calories
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
