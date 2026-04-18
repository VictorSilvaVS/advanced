import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("--- LISTANDO MODELOS DISPONÍVEIS ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Erro ao listar: {e}")

print("\n--- TESTANDO CHAMADA DIRETA ---")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Diga 'Olá Mundo'")
    print(f"Resposta: {response.text}")
except Exception as e:
    print(f"Erro no teste: {e}")
