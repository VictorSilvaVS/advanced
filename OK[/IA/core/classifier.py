import re

class Classifier:
    """
    O Cerebelo da IA. 
    Classifica a intenção antes de decidir se deve ir para o terminal, 
    para a Web ou apenas responder como uma saudação.
    """
    def __init__(self):
        self.categorias = {
            "SAUDACAO": [r"ol[aá]", r"oi", r"bom dia", r"boa tarde", r"boa noite", r"e ai"],
            "WEB": [r"(pesquise|busque|procure|quem [eé]|o que [eé]) (no google|na internet|web|sobre) (.+)"],
            "OPERACAO": [r"(liste|mostre|crie|delete|remova|abra|execute|rode|cd|dir|ipconfig|ping)"],
            "IDENTIDADE": [r"(quem [eé] voc[eê]|seu nome|o que voc[eê] faz)"]
        }

    def classificar(self, entrada: str) -> str:
        entrada_limpa = entrada.lower().strip()
        
        for categoria, padroes in self.categorias.items():
            for padrao in padroes:
                if re.search(padrao, entrada_limpa):
                    return categoria
        
        # Se não cair em nada óbvio, pode ser uma CONVERSA ou um COMANDO desconhecido
        return "CONVERSA"
