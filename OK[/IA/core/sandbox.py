import subprocess
import os

class Sandbox:
    """
    O Executor. Ele roda comandos no mundo real (Windows/OS)
    e captura o que aconteceu (Causa -> Resultado).
    """
    def __init__(self):
        # Podemos definir um diretório seguro no futuro
        self.cwd = os.getcwd()

    def executar(self, comando: str) -> dict:
        """
        Tenta rodar um comando e retorna o resultado estruturado.
        """
        try:
            # shell=True permite comandos como 'dir', 'echo', etc no Windows
            processo = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10 # Segurança: não deixa o comando rodar pra sempre
            )
            
            if processo.returncode == 0:
                return {
                    "status": "sucesso",
                    "saida": processo.stdout.strip(),
                    "erro": None
                }
            else:
                return {
                    "status": "erro",
                    "saida": processo.stdout.strip(),
                    "erro": processo.stderr.strip()
                }
                
        except Exception as e:
            return {
                "status": "explosao",
                "saida": None,
                "erro": str(e)
            }
