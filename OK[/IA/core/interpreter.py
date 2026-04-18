import re

class Interpreter:
    """
    O Tradutor Causal. Ele transforma a intenção humana em ações reais.
    Diferença: Ele não apenas mapeia palavras, mas entende CONCEITOS (ou tenta).
    """
    def __init__(self):
        # Base de mapeamento de intenções "Sementes"
        # Isso será expandido dinamicamente conforme a IA aprende com você.
        self.conceitos = {
            r"(listar|ver|quais arquivos|o que tem na|me mostre)": "dir",
            r"(quem sou eu|meu usuario|sou quem)": "whoami",
            r"(ip|configuracao de rede|meu endereco)": "ipconfig",
            r"(teste de conexao|internet|ping)": "ping 8.8.8.8",
            r"(limpar terminal|limpar tela|cls)": "cls",
            r"(data|que dia|calendario)": "date /t",
            r"(hora|que horas|relogio)": "time /t",
            r"(navegar|abrir site|vaja o site) (.+)": "start \g<2>" # Pega a URL dinamicamente
        }

    def traduzir(self, objetivo: str) -> str:
        """
        Analisa o objetivo e retorna o comando mais provável no Windows.
        Se não encontrar, retorna o original para que o Sandbox falhe 
        e a IA aprenda o 'porquê' com o usuário.
        """
        objetivo_limpo = objetivo.lower().strip()
        
        for padrao, comando in self.conceitos.items():
            if re.search(padrao, objetivo_limpo):
                # Se for um comando com Regex (ex: abrir site), ele faz a substituição
                if "(" in padrao and "\\" in comando:
                     return re.sub(padrao, comando, objetivo_limpo)
                return comando
                
        # Se ela não sabe, ela falha propositalmente para ser ensinada do zero.
        return objetivo
