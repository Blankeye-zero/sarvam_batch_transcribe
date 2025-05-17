from pprint import pprint
from dotenv import load_dotenv
import requests
import json
from sarvam_client import API_SUBSCRIPTION_KEY,LANGUAGE_CODE


async def initialize_job():
    print("\n🚀 Initializing job...")
    url = "https://api.sarvam.ai/speech-to-text/job/init"
    headers = {"API-Subscription-Key": API_SUBSCRIPTION_KEY}
    response = requests.post(url, headers=headers)
    print("\nInitialize Job Response:")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    pprint(response.json() if response.status_code == 202 else response.text)

    if response.status_code == 202:
        return response.json()
    return None


async def check_job_status(job_id):
    print(f"\n🔍 Checking status for job: {job_id}")
    url = f"https://api.sarvam.ai/speech-to-text/job/{job_id}/status"
    headers = {"API-Subscription-Key": API_SUBSCRIPTION_KEY}
    response = requests.get(url, headers=headers)
    print("\nJob Status Response:")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    pprint(response.json() if response.status_code == 200 else response.text)

    if response.status_code == 200:
        return response.json()
    return None


async def start_job(job_id, language_code=LANGUAGE_CODE):
    print(f"\n▶️ Starting job: {job_id}")
    url = "https://api.sarvam.ai/speech-to-text/job"
    headers = {
        "API-Subscription-Key": API_SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }
    data = {"job_id": job_id, "job_parameters": {"language_code": language_code}}
    print("\nRequest Body:")
    pprint(data)

    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("\nStart Job Response:")
    print(f"Status Code: {response.status_code}")
    print("Response Body:")
    pprint(response.json() if response.status_code == 200 else response.text)

    if response.status_code == 200:
        return response.json()
    return None