from __future__ import annotations
import logging, csv, io
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

# Reuse logic yang sudah ada
from mnet_signup_bot.bot import run_single

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET"])
def home():
    return render_template("signup.html")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()
    gender = (data.get("gender") or "m").strip()
    birth_year = (data.get("birth_year") or "1998").strip()
    locale = (data.get("locale") or "en").strip()
    device_name = data.get("device_name") or None
    terms_ver = data.get("marketing_terms_version") or None

    if not email or not password:
        return jsonify({"detail": "email & password required"}), 400

    try:
        run_single(
            email=email,
            password=password,
            gender=gender,
            birth_year=birth_year,
            locale=locale,
            device_name=device_name,
            marketing_terms_version=terms_ver,
        )
        return jsonify({"ok": True})
    except Exception as e:
        logging.exception("signup failed")
        return jsonify({"detail": str(e)}), 500

@app.route("/batch-signup", methods=["POST"])
def batch_signup():
    if "file" not in request.files:
        return jsonify({"detail": "CSV file required as 'file'"}), 400
    f = request.files["file"]
    filename = secure_filename(f.filename or "")
    if not filename.lower().endswith(".csv"):
        return jsonify({"detail": "Please upload a CSV file"}), 400

    content = f.stream.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    processed, ok = 0, 0
    for row in reader:
        processed += 1
        email = (row.get("email") or "").strip()
        password = (row.get("password") or "").strip()
        if not email or not password:
            continue
        gender = (row.get("gender") or "m").strip()
        birth_year = (row.get("birth_year") or "1998").strip()
        device_name = row.get("device_name") or None
        locale = (row.get("locale") or "en").strip()
        terms_ver = row.get("marketing_terms_version") or None
        try:
            run_single(
                email=email,
                password=password,
                gender=gender,
                birth_year=birth_year,
                locale=locale,
                device_name=device_name,
                marketing_terms_version=terms_ver,
            )
            ok += 1
        except Exception as e:
            logging.error("[batch] %s: %s", email, e)
    return jsonify({"ok": True, "processed": processed, "success": ok})
