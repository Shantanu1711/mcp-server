import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_huggingface():
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    try:
        output = query({
            "inputs": "Hello! This is a test message.",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7
            }
        })
        print("Hugging Face API is working!")
        print("Response:", output)
    except Exception as e:
        print("Error:", str(e))
        print("\nMake sure you have:")
        print("1. Created a Hugging Face account at https://huggingface.co/")
        print("2. Generated an API key at https://huggingface.co/settings/tokens")
        print("3. Added your API key to .env file as HF_API_KEY=your_key_here")

if __name__ == "__main__":
    test_huggingface() 