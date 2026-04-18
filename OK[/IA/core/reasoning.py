import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class Reasoning:
    """
    O Lóbulo Frontal da IA. 
    Usando 1.5-flash por ser mais estável em limites de cota.
    """
    def __init__(self, api_key=None):
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API Key do Gemini não encontrada. Configure GOOGLE_API_KEY no arquivo .env")
        
        genai.configure(api_key=api_key)
        # 1.5-flash é o 'pau para toda obra' do Google, com melhor cota gratuita
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def decidir_contexto(self, entrada: str) -> str:
        try:
            prompt = f"Categorize (SAUDACAO, OPERACAO, WEB, CONVERSA): {entrada}"
            response = self.model.generate_content(prompt)
            return response.text.strip().upper()
        except Exception as e:
            if "429" in str(e):
                return "[ERRO DE COTA: AGUARDE]"
            return "CONVERSA"

    def traduzir_comando(self, objetivo: str) -> str:
        try:
            prompt = f"Comando Windows puro para: {objetivo}"
            response = self.model.generate_content(prompt)
            return response.text.strip().replace("`", "")
        except:
            return objetivo

    def extrair_insight(self, texto_bruto: str, tema: str) -> str:
        prompt = f"Explique o que é {tema} baseado nisso: {texto_bruto[:2000]}"
        response = self.model.generate_content(prompt)
        return response.text.strip()

