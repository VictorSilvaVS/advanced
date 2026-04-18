import json
import os

class MemoryStorage:
    """
    O Córtex de Longo Prazo. 
    Lida com o salvamento de fatos, segredos e aprendizados no disco.
    """
    def __init__(self, filename=r"c:\Users\victo\OneDrive\Documentos\projetos\advanced\OK[\IA\brain_data.json"):

        self.filename = filename
        if not os.path.exists(self.filename):
            self.save_data({"conceitos": {}, "traumas": [], "curiosidades": []})

    def load_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"conceitos": {}, "traumas": [], "curiosidades": []}

    def save_data(self, data):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def guardar_conceito(self, nome, definicao):
        data = self.load_data()
        data["conceitos"][nome.lower()] = definicao
        self.save_data(data)

    def guardar_trauma(self, acao, erro, por_que):
        data = self.load_data()
        data["traumas"].append({
            "acao": acao,
            "erro": erro,
            "por_que": por_que
        })
        self.save_data(data)
        
    def adicionar_curiosidade(self, topico):
        data = self.load_data()
        if topico.lower() not in data["curiosidades"]:
            data["curiosidades"].append(topico.lower())
            self.save_data(data)
            
    def consumir_curiosidade(self):
        data = self.load_data()
        if data["curiosidades"]:
            topico = data["curiosidades"].pop(0)
            self.save_data(data)
            return topico
        return None
