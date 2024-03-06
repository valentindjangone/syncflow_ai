from fastapi.testclient import TestClient
from main import api
client = TestClient(api)

def test_extract_mission_details():
    test_mission = {
        "mission": "I want to sell shoes online. The newly created website must have a trend prediction feature."
    }

    response = client.post("/extract_all_details", json=test_mission)
    print(response.text)

    assert response.status_code == 200

    response_data = response.json()
    assert "detail" in response_data




