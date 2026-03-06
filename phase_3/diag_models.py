import os
import google.generativeai as genai
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
env_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=env_path)

api_key = os.environ.get("GOOGLE_API_KEY")
print(f"Loading .env from: {env_path}")
print(f"API Key present: {bool(api_key)}")

if api_key:
    genai.configure(api_key=api_key)
    print("Available Embedding Models:")
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("No API Key found.")
