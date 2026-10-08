import os
import random
import signal
import sys
from flask import Flask, jsonify

signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))
app = Flask(__name__)

CITATIONS = [
    {"texte": "Connais-toi toi-même.", "auteur": "Socrate"},
    {"texte": "Je pense, donc je suis.", "auteur": "Descartes"},
    {"texte": "Le cœur a ses raisons que la raison ne connaît point.", "auteur": "Pascal"},
]

@app.route("/quote")
def quote():
    return jsonify(random.choice(CITATIONS))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)