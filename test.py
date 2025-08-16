import os
import base64
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("PLANT_API_KEY")  # set in .env as PLANT_API_KEY

# Path to local plant image
IMAGE_PATH = "download (1).jpg"  # change to your local image filename

# Convert image to Base64
with open(IMAGE_PATH, "rb") as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    img_data = f"data:image/jpeg;base64,{img_base64}"

# API endpoint for health assessment
url = "https://plant.id/api/v3/health_assessment?details=local_name,description,url,treatment,classification,common_names,cause"

headers = {
    "Api-Key": API_KEY,
    "Content-Type": "application/json"
}

payload = {
    "images": [img_data]
}

# Send request
response = requests.post(url, json=payload, headers=headers)
data = response.json()

print("Status Code:", response.status_code)

# Extract structured info
if "result" in data and "disease" in data["result"]:
    print("\n=== Plant Health Assessment ===")
    is_healthy = data["result"].get("is_healthy", {}).get("binary")
    prob_healthy = data["result"].get("is_healthy", {}).get("probability")
    print(f"Healthy? {is_healthy} (confidence: {prob_healthy:.2f})")

    print("\nDetected Diseases:")
    for disease in data["result"]["disease"]["suggestions"]:
        name = disease.get("name")
        prob = disease.get("probability", 0)
        details = disease.get("details", {})

        print(f"- {name} (confidence: {prob:.2f})")
        if "description" in details:
            print(f"   Description: {details['description']}")
        if "cause" in details:
            print(f"   Cause: {details['cause']}")
        if "treatment" in details:
            treatment = details["treatment"]
            print("   Remedy:")
            if "prevention" in treatment:
                print(f"     • Prevention: {treatment['prevention']}")
            if "biological" in treatment:
                print(f"     • Biological: {treatment['biological']}")
            if "chemical" in treatment:
                print(f"     • Chemical: {treatment['chemical']}")
else:
    print("Raw Response:", data)
