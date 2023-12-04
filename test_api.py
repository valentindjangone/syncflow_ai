from fastapi.testclient import TestClient
from main import api  # Assurez-vous que ceci importe correctement votre instance FastAPI
client = TestClient(api)

def test_extract_mission_details():
    # Données de test
    test_mission = {
        "mission": "I want to sell shoes online. The newly created website must have a trend prediction feature."
    }

    # Envoi de la requête POST à l'endpoint
    response = client.post("/extract_all_details", json=test_mission)
    print(response.text)

    # Vérification du statut de la réponse
    assert response.status_code == 200

    # Vérification de la structure des données de la réponse
    response_data = response.json()
    assert "detail" in response_data  # ou toute autre clé attendue dans la réponse




