import os
import json
import random
import signal
import sys
from flask import Flask, jsonify

# Arrêt propre : quitte avec le code 0 quand Docker envoie SIGTERM
signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

app = Flask(__name__)


# Lit les citations dans le fichier citations.json
# Relu à chaque demande : une modification est prise en compte immédiatement
def charger_citations():
    with open("citations.json", encoding="utf-8") as f:
        return json.load(f)


# Renvoie une citation au hasard au format JSON
@app.route("/quote")
def quote():
    return jsonify(random.choice(charger_citations()))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)