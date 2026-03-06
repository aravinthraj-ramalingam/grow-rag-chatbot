import os
import google.generativeai as genai
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
env_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=env_path)

api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    try:
        print("Testing gemini-1.5-flash...")
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Generation Error: {e}")
else:
    print("No API Key.")
