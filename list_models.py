"""
Liệt kê các model Gemini có sẵn
"""
import google.generativeai as genai
from scripts.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

print("Các model Gemini có sẵn:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display name: {model.display_name}")
        print(f"   Description: {model.description}")
        print()
