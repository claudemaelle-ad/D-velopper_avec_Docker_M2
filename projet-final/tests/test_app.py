import os
import time

import pytest
import requests

# Adresse de nginx dans le réseau Docker, passée au run
BASE_URL = os.environ.get("BASE_URL", "http://nginx")


@pytest.fixture(scope="session", autouse=True)
def attendre_application():
    # depends_on garantit que les conteneurs ont démarré, pas qu'ils sont prêts :
    # on attend que l'API réponde (30 s maximum) avant de lancer les tests
    for _ in range(30):
        try:
            if requests.get(BASE_URL + "/api/quote", timeout=2).status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    pytest.fail("L'application n'a pas répondu dans les 30 secondes")


def test_page_accueil():
    # La page d'accueil (servie par le front via nginx) répond
    r = requests.get(BASE_URL + "/", timeout=5)
    assert r.status_code == 200
    assert "Citation du jour" in r.text


def test_api_renvoie_une_citation():
    # L'API (servie par le back via nginx) renvoie une citation valide
    r = requests.get(BASE_URL + "/api/quote", timeout=5)
    assert r.status_code == 200
    citation = r.json()
    assert citation["texte"]
    assert citation["auteur"]


def test_healthcheck_front():
    # La route de santé du front répond OK
    r = requests.get(BASE_URL + "/health", timeout=5)
    assert r.status_code == 200
    assert r.text == "OK"