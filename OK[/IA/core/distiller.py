import re

class Distiller:
    """
    O Filtro de Elite. 
    Transforma parágrafos chatos em 'Conhecimento Causal' curto.
    """
    def __init__(self):
        # Palavras que indicam que a frase é uma explicação importante
        self.marcadores = ["é um", "consiste", "função", "porque", "devido", "responsável", "atua", "essencial"]

    def destilar(self, texto: str, tema: str) -> str:
        # Remove lixos comuns de scraping
        texto_limpo = re.sub(r'\(.+?\)|\[.+?\]', '', texto) 
        frases = texto_limpo.split(".")
        
        nectar = []
        for f in frases:
            f = f.strip()
            # Pega a definição (geralmente a primeira frase)
            if len(nectar) == 0 and tema.lower() in f.lower():
                nectar.append(f)
                continue
            
            # Pega frases explicativas/causais
            if any(m in f.lower() for m in self.marcadores):
                if len(f) > 20 and len(f) < 200: # Evita frases curtas ou longas demais
                    nectar.append(f)
            
            if len(nectar) >= 2: # Queremos apenas o NOBRE, não o volume
                break
        
        if nectar:
            return ". ".join(nectar) + "."
        return texto[:150] + "..." # Fallback: se não achar padrão, corta o início.
