import os
import re
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# Rate limiting rule: 10 requests per minute
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

DB_PATH = "provenance_guard.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                content_id TEXT PRIMARY KEY,
                creator_id TEXT,
                timestamp TEXT,
                llm_score REAL,
                sty_score REAL,
                confidence REAL,
                attribution TEXT,
                label_text TEXT,
                status TEXT,
                appeal_reasoning TEXT
            )
        """)
init_db()

def calculate_stylometrics(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    tokens = [t.lower().strip(",.()\"';:") for t in text.split() if t.strip()]
    if not tokens or not sentences:
        return 0.5
    ttr = len(set(tokens)) / len(tokens)
    lengths = [len(s.split()) for s in sentences]
    avg_len = sum(lengths) / len(lengths)
    variance = sum((x - avg_len) ** 2 for x in lengths) / len(lengths) if len(lengths) > 1 else 0.0
    ttr_score = 1.0 - min(ttr / 0.6, 1.0)
    var_score = 1.0 if variance < 5.0 else max(0.0, 1.0 - (variance / 50.0))
    return (ttr_score * 0.5) + (var_score * 0.5)

def get_llm_score(text: str) -> float:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return 0.20
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Output only a single float between 0.0 and 1.0 representing AI probability. No commentary."},
                {"role": "user", "content": text}
            ],
            temperature=0.1, max_tokens=5
        )
        return max(0.0, min(1.0, float(re.search(r"[-+]?\d*\.\d+|\d+", response.choices[0].message.content).group())))
    except:
        return 0.40

def generate_label(confidence: float) -> tuple:
    if confidence >= 0.75:
        return ("likely_ai", "Automated Generation: Highly uniform structural patterns suggest this content matches styles common to generative AI systems.")
    elif confidence <= 0.35:
        return ("likely_human", "Verified Human Characteristics: This work displays organic variation in style, structure, and vocabulary consistent with individual human expression.")
    else:
        return ("uncertain", "Mixed Attributes: Structural metrics indicate a highly standardized style. Determination is inconclusive; currently open for community context.")

@app.route("/submit", methods=["POST"])
@limiter.limit("10 per minute")
def submit():
    data = request.get_json() or {}
    text, creator_id = data.get("text", "").strip(), data.get("creator_id", "").strip()
    if not text or not creator_id:
        return jsonify({"error": "Missing fields"}), 400
    
    llm_s, sty_s = get_llm_score(text), calculate_stylometrics(text)
    conf = (0.70 * llm_s) + (0.30 * sty_s)
    attr, label = generate_label(conf)
    c_id = str(uuid.uuid4())
    ts = datetime.utcnow().isoformat() + "Z"
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO audit_log VALUES (?,?,?,?,?,?,?,?,?,?)", 
                     (c_id, creator_id, ts, llm_s, sty_s, conf, attr, label, "classified", None))
    return jsonify({"content_id": c_id, "attribution": attr, "confidence": round(conf, 4), "transparency_label": label}), 200

@app.route("/appeal", methods=["POST"])
def appeal():
    data = request.get_json() or {}
    c_id, reasoning = data.get("content_id", "").strip(), data.get("creator_reasoning", "").strip()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT content_id FROM audit_log WHERE content_id = ?", (c_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Not found"}), 404
        conn.execute("UPDATE audit_log SET status = 'under_review', appeal_reasoning = ? WHERE content_id = ?", (reasoning, c_id))
    return jsonify({"status": "success", "message": "Appealed successfully"}), 200

@app.route("/log", methods=["GET"])
def get_log():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        entries = [dict(r) for r in conn.execute("SELECT * FROM audit_log ORDER BY timestamp DESC").fetchall()]
    return jsonify({"entries": entries}), 200

if __name__ == "__main__":
    app.run(port=5000)

