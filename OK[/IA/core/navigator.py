import requests
import urllib.parse
from bs4 import BeautifulSoup

class Navigator:
    """
    O Olho da IA. 
    Busca na Wikipedia e, se falhar, vasculha a 'Internet Aberta'.
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def buscar_na_web(self, query: str) -> str:
        """
        Pesquisa na internet aberta (usando DuckDuckGo como fallback estável).
        """
        try:
            termo = urllib.parse.quote(query)
            # Versão leve do DuckDuckGo para evitar bloqueios de scraping
            url = f"https://html.duckduckgo.com/html/?q={termo}"
            res = requests.get(url, headers=self.headers, timeout=10)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Pega os primeiros 3 snippets de resultados
                snippets = soup.find_all('a', class_='result__snippet')
                textos = [s.get_text() for s in snippets[:3]]
                
                if textos:
                    return " ".join(textos)
            return "Não encontrei informações relevantes na web aberta."
        except Exception as e:
            return f"Erro na pesquisa aberta: {str(e)}"

    def buscar(self, query: str) -> str:
        try:
            termo_seguro = urllib.parse.quote(query.strip())
            
            # TENTATIVA 1: Wikipedia PT
            url = f"https://pt.wikipedia.org/api/rest_v1/page/summary/{termo_seguro}"
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code == 200:
                return response.json().get("extract", "")
            
            # TENTATIVA 2: Wikipedia EN
            url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{termo_seguro}"
            response_en = requests.get(url_en, headers=self.headers, timeout=5)
            if response_en.status_code == 200:
                return response_en.json().get("extract", "")

            # TENTATIVA 3: INTERNET ABERTA
            return self.buscar_na_web(query)

        except Exception as e:
            # Se tudo falhar, tenta a WEB aberta diretamente antes de desistir
            return self.buscar_na_web(query)
