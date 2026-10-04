"""
Backend for a genuinely LIVE demo — deploy this (don't just run it locally)
so judges opening your real URL get a live call to Moth's API, not a replay.

Key comes from an environment variable, never hardcoded, so it's safe to
commit/push this file to a public repo for deployment.

Local test:
    pip install flask requests gunicorn
    export MOTH_API_KEY="moth_..."
    python server.py
    -> open http://localhost:5000

Deploy (e.g. Render.com free tier):
    1. Push this folder (server.py, quantum-interference-live.html,
       requirements.txt) to a GitHub repo.
    2. On Render: New -> Web Service -> connect the repo.
    3. Build command: pip install -r requirements.txt
       Start command: gunicorn server:app
    4. In the service's Environment tab, add MOTH_API_KEY as a secret
       (NOT in the code, NOT in the repo).
    5. Deploy -> you get a public URL like https://yourapp.onrender.com
       -> THAT is your real, live, submittable link.
"""
import os, time, random
from flask import Flask, jsonify, send_from_directory
import requests

MOTH_API_KEY = os.environ.get("MOTH_API_KEY")
API = "https://api.mothquantum.com/api/v1"
H = {"Authorization": f"Bearer {MOTH_API_KEY}"}

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(".", "quantum-interference-live.html")

@app.route("/api/measure")
def measure():
    shots = 300  # enough for one render; keep small so it stays fast for a live demo
    job = requests.post(f"{API}/engines/coin-toss-v1/process", headers=H,
        json={"params": {"mode": "emu", "shots": shots}}).json()
    job_id = job["job_id"]

    while True:
        st = requests.get(f"{API}/jobs/{job_id}/status", headers=H).json()
        if st["status"] in ("completed", "failed", "cancelled"):
            break
        time.sleep(1)
    if st["status"] != "completed":
        return jsonify({"error": st.get("error", "job failed")}), 502

    result = requests.get(f"{API}/jobs/{job_id}/result", headers=H).json()["result"]
    bits = [1]*result["heads"] + [0]*result["tails"]
    random.shuffle(bits)
    return jsonify({"bits": bits, "job_id": job_id, "backend": result.get("backend")})

if __name__ == "__main__":
    if not MOTH_API_KEY:
        raise SystemExit("Set MOTH_API_KEY as an environment variable first.")
    port = int(os.environ.get("PORT", 5000))  # Render/most hosts set PORT for you
    app.run(host="0.0.0.0", port=port, debug=False)
