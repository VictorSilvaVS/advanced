from typing import List, Optional
from datetime import datetime
from core.memory_storage import MemoryStorage
import re

class CerebroCausal:
    def __init__(self):
        self.storage = MemoryStorage()
        self.memorias: List = []
        self.conhecimento = self.storage.load_data().get("conceitos", {})

    def absorver_experiencia(self, intencao: str, acao: str, resultado: str, insight: str = None):
        # Se o insight (Gemini) falhou, mas temos o resultado bruto (Wikipedia), usamos o bruto!
        conteudo_final = insight if insight and "Dificuldade" not in insight else resultado
        
        nome_conceito = intencao.lower().replace("aprenda o que é", "").replace("o que é", "").strip()
        
        if len(nome_conceito) > 2:
            self.storage.guardar_conceito(nome_conceito, conteudo_final)
            self.conhecimento[nome_conceito] = conteudo_final
            self.gerar_curiosidades(conteudo_final)

        if "Erro" in resultado:
            self.storage.guardar_trauma(acao, resultado, insight or "Erro sistêmico")

    def gerar_curiosidades(self, texto: str):
        # Extração orgânica via Regex (sem depender de API)
        palavras = re.findall(r'\b[A-ZÀ-Ú][a-zà-ú]{6,}\b', str(texto))
        for p in palavras:
            self.storage.adicionar_curiosidade(p)

    def validar_acao(self, acao: str) -> bool:
        traumas = self.storage.load_data().get("traumas", [])
        for t in traumas:
            if t["acao"] == acao: return False
        return True

    def refletir(self, objetivo: str) -> Optional[dict]:
        obj_limpo = objetivo.lower().replace("o que é", "").strip()
        if obj_limpo in self.conhecimento:
            # SÓ ACEITA SE NÃO FOR MENSAGEM DE ERRO
            valor = self.conhecimento[obj_limpo]
            palavras_erro = ["erro", "não consegui", "dificuldade", "falha"]
            if not any(erro in valor.lower() for erro in palavras_erro):
                return {"resultado": "Conhecimento Interno", "por_que": valor}
        return None

