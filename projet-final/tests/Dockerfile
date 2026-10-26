# Image de base : Python 3.11 slim, même base que le back et le lint
FROM python:3.11-slim

LABEL description="Tests de bout en bout de l'application - pytest"

# Installation des dépendances de test
# pytest : lance les tests et produit un rapport
# requests : envoie les requêtes HTTP vers l'application
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Opération sur l'OS : utilisateur sans droits admin
RUN useradd --system --no-create-home tester
USER tester

# Copie des tests dans l'image
WORKDIR /tests
COPY test_app.py .

# Adresse de l'application testée, remplaçable au run
ENV BASE_URL=http://nginx

# ENTRYPOINT : l'exécutable fixe, toujours pytest
# CMD : options par défaut (-v : affiche le détail de chaque test)
ENTRYPOINT ["pytest"]
# -p no:cacheprovider : pas de cache pytest (conteneur jetable, sans droit d'écriture)
CMD ["-v", "-p", "no:cacheprovider"]