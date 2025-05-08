import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api():
    API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
    headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    try:
        # Test with a simple prompt
        output = query({
            "inputs": "What is the capital of France?",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "return_full_text": False
            }
        })
        print("API is working!")
        print("Response:", output)
    except Exception as e:
        print("Error:", str(e))
        print("\nSetup Instructions:")
        print("1. Go to https://huggingface.co/")
        print("2. Sign up for a free account")
        print("3. Go to https://huggingface.co/settings/tokens")
        print("4. Create a new token (read access is enough)")
        print("5. Create a .env file in your project root")
        print("6. Add this line to .env: HF_API_KEY=your_token_here")

if __name__ == "__main__":
    test_api() 