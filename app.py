"""Local server for the Adamic Model Lab."""

from __future__ import annotations

from flask import Flask, jsonify, request

from simulation import SimulationInputError, run_simulation

app = Flask(__name__, static_folder="design", static_url_path="")


@app.get("/")
def index():
    return app.send_static_file("adamic-model-lab.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "engine": "msprime"}


@app.post("/api/simulate")
def simulate():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a JSON object with simulation inputs."}), 400
    try:
        return jsonify(run_simulation(payload))
    except SimulationInputError as error:
        return jsonify({"error": str(error)}), 400
    except Exception:
        app.logger.exception("Simulation failed")
        return jsonify({"error": "The simulation could not be completed."}), 500


if __name__ == "__main__":
    app.run(debug=True)
