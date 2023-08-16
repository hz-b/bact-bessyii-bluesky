import requests

def test_measurement_config_post():
    # Your FastAPI server URL (replace with your actual server URL)
    server_url = "http://127.0.0.1:8001/measurements/measurements"

    # Example data for the measurement_config
    data = {
        "prefix": "Pierre:DT:",
        "currents": [0, -2, 0, 2, 0],
        "catalog_name": "heavy_local",
        "machine_name": "BessyII",
        "measurement_name": "beam_based_alignment"
    }

    # Send a POST request to the server with the data
    response = requests.post(server_url, json=data)

    # Check the response status code (should be 200 for a successful request)
    assert response.status_code == 200

    # Convert the response content (in JSON format) to a Python dictionary
    response_data = response.json()

    # Check if the 'uids' key exists in the response
    assert "uids" in response_data

    # Print the generated uids (for demonstration purposes)
    print("Measurement uids:", response_data["uids"])

if __name__ == "__main__":
    test_measurement_config_post()
