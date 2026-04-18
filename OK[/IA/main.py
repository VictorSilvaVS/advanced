import sys
import time
import threading
import re
from rich.console import Console
from rich.panel import Panel
from core.brain import CerebroCausal
from core.sandbox import Sandbox
from core.reasoning import Reasoning
from core.navigator import Navigator
from core.distiller import Distiller

console = Console()
cerebro = CerebroCausal()
executor = Sandbox()
raciocinio = Reasoning()
navegador = Navigator()
destilador = Distiller()

ultima_interacao = time.time()
ativo = True

def motor_consciencia():
    global ultima_interacao
    while ativo:
        try:
            if time.time() - ultima_interacao > 45:
                topico = cerebro.storage.consumir_curiosidade()
                if topico:
                    console.print(f"\n[bold magenta][AUTO-EXPLORAÇÃO]:[/bold magenta] Pesquisando '{topico}'...")
                    conteudo = navegador.buscar(topico)
                    try:
                        insight = raciocinio.extrair_insight(conteudo, topico)
                    except:
                        insight = destilador.destilar(conteudo, topico)
                    cerebro.absorver_experiencia(topico, "Navegação Autónoma", conteudo, insight)
                    ultima_interacao = time.time()
        except: pass
        time.sleep(10)

def main():
    global ultima_interacao, ativo
    console.print(Panel.fit("[bold green]IA CAUSAL v4.0 - ESTÁVEL & ORGÂNICA[/bold green]"))
    threading.Thread(target=motor_consciencia, daemon=True).start()
    
    try:
        while True:
            entrada = console.input("\n[bold cyan]Você >>[/bold cyan] ")
            ultima_interacao = time.time()
            if not entrada.strip(): continue
            if entrada.lower() in ["exit", "sair", "quit"]:
                ativo = False
                break
            
            # 1. FILTRO SOCIAL EXPANDIDO (Zero API)
            saudacoes = ["oi", "ola", "olá", "e ai", "opa", "como vai", "bom dia", "boa tarde", "boa noite"]
            if any(s == entrada.lower().strip() for s in saudacoes):
                console.print("[bold green]IA:[/bold green] Salve! Estou aqui pronto para aprender ou agir.")
                continue

            # 2. MEMÓRIA LOCAL
            memoria = cerebro.refletir(entrada)
            if memoria:
                console.print(f"[bold green]IA (Conhecimento):[/bold green]\n{memoria['por_que']}")
                continue

            # 3. TRATAMENTO DE APRENDIZADO (WEB)
            if "o que é" in entrada.lower() or "aprenda" in entrada.lower():
                tema = re.sub(r'aprenda|sobre|o que é|quem é|pesquise|busque|sobre', '', entrada, flags=re.IGNORECASE).strip()
                if not tema:
                    console.print("[yellow]Aprender o quê? Me diga o assunto.[/yellow]")
                    continue
                
                console.print(f"[dim]Investigando '{tema}'...[/dim]")
                conteudo = navegador.buscar(tema)
                
                if "ERRO:" in conteudo or "FALHA:" in conteudo:
                    console.print(f"[red]{conteudo}[/red]")
                    continue

                try:
                    insight = raciocinio.extrair_insight(conteudo, tema)
                    console.print(f"\n[bold blue]Essência (Gemini):[/bold blue]\n{insight}")
                except:
                    insight = destilador.destilar(conteudo, tema)
                    console.print(f"\n[bold yellow]Essência Orgânica:[/bold yellow]\n{insight}")
                
                cerebro.absorver_experiencia(entrada, "Pesquisa", conteudo, insight)
                continue

            # 4. TRATAMENTO DE COMANDOS / DIÁLOGO
            try:
                contexto = raciocinio.decidir_contexto(entrada)
                if contexto == "OPERACAO":
                    comando = raciocinio.traduzir_comando(entrada)
                    if cerebro.validar_acao(comando):
                        console.print(f"[dim]Executando: '{comando}'...[/dim]")
                        res = executor.executar(comando)
                        if res['status'] == "sucesso":
                            console.print(f"[green]Sucesso:[/green]\n{res['saida']}")
                            cerebro.absorver_experiencia(entrada, comando, "Sucesso", "Funcional")
                        else:
                            console.print(f"[red]Erro:[/red] {res['erro']}")
                            explica = console.input("[yellow]Por que falhou? [/yellow]")
                            cerebro.absorver_experiencia(entrada, comando, f"Erro: {res['erro']}", explica)
                else:
                    console.print("[bold green]IA:[/bold green] Entendi seu ponto. Refletirei sobre isso.")
            except:
                console.print("[bold green]IA:[/bold green] Meus neurônios se perderam nessa frase. Pode repetir?")

    except KeyboardInterrupt:
        ativo = False
        sys.exit(0)

if __name__ == "__main__":
    main()
