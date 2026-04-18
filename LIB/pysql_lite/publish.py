#!/usr/bin/env python3
"""
publish.py - Script para publicar pysql_lite no PyPI

Uso:
    python publish.py              # Build local
    python publish.py test         # Upload para Test PyPI
    python publish.py prod         # Upload para PyPI oficial
    python publish.py clean        # Limpar artifacts
    python publish.py check        # Validar distribuição
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(msg):
    print(f"{Colors.OKGREEN}✅ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}❌ {msg}{Colors.ENDC}")

def print_info(msg):
    print(f"{Colors.OKCYAN}ℹ️  {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠️  {msg}{Colors.ENDC}")

def print_header(msg):
    print(f"\n{Colors.BOLD}{Colors.OKBLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{msg:^60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKBLUE}{'='*60}{Colors.ENDC}\n")

def run_command(cmd, check=True):
    """Executar comando no shell"""
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Comando falhou: {cmd}")
        print(e.stderr)
        return None

def check_prerequisites():
    """Verificar que ferramentas necessárias estão instaladas"""
    print_header("1️⃣  Verificando Pré-requisitos")
    
    tools = {
        'python -m build': 'build',
        'python -m twine --version': 'twine',
    }
    
    for cmd, name in tools.items():
        result = run_command(cmd, check=False)
        if result.returncode == 0:
            print_success(f"{name} instalado")
        else:
            print_error(f"{name} não encontrado")
            print_info(f"Instale com: pip install {name}")
            return False
    
    return True

def clean_artifacts():
    """Limpar arquivos de build anteriores"""
    print_header("🧹 Limpando Artifacts Antigos")
    
    dirs_to_remove = [
        'build',
        'dist',
        '*.egg-info',
        '__pycache__',
        '.pytest_cache',
    ]
    
    for pattern in dirs_to_remove:
        if '*' in pattern:
            for item in Path('.').glob(pattern):
                shutil.rmtree(item)
                print_success(f"Removido: {item}")
        else:
            path = Path(pattern)
            if path.exists():
                shutil.rmtree(path)
                print_success(f"Removido: {path}")

def get_version():
    """Ler versão do setup.py"""
    with open('setup.py', 'r') as f:
        for line in f:
            if 'version=' in line:
                return line.split('"')[1]
    return "desconhecida"

def validate_distribution():
    """Validar distribuição com Twine"""
    print_header("✅ Validando Distribuição")
    
    result = run_command('python -m twine check dist/*', check=False)
    
    if result.returncode == 0:
        print_success("Validação passou!")
        return True
    else:
        print_error("Validação falhou!")
        return False

def build_distribution():
    """Criar distribuição"""
    print_header("🔨 Buildando Distribuição")
    
    # Limpar primeiro
    clean_artifacts()
    
    # Build
    result = run_command('python -m build', check=False)
    
    if result.returncode == 0:
        print_success("Build concluído!")
        
        # Listar arquivos
        dist_files = list(Path('dist').glob('*'))
        print_info(f"\nArquivos gerados ({len(dist_files)}):")
        for f in dist_files:
            print(f"  📦 {f.name}")
        
        return True
    else:
        print_error("Build falhou!")
        return False

def upload_to_testpypi():
    """Upload para Test PyPI"""
    print_header("🧪 Upload para Test PyPI")
    
    print_warning("Isto fará upload para https://test.pypi.org/")
    response = input("Continuar? (s/n): ").strip().lower()
    
    if response != 's':
        print_info("Cancelado")
        return False
    
    cmd = 'python -m twine upload --repository testpypi dist/*'
    result = run_command(cmd, check=False)
    
    if result.returncode == 0:
        print_success("Upload para Test PyPI concluído!")
        version = get_version()
        print_info(f"\nView em: https://test.pypi.org/project/pysql_lite/")
        print_info(f"Testar com: pip install --index-url https://test.pypi.org/simple/ pysql_lite=={version}")
        return True
    else:
        print_error("Upload falhou!")
        return False

def upload_to_pypi():
    """Upload para PyPI oficial"""
    print_header("🚀 Upload para PyPI Oficial")
    
    print_warning("Isto fará upload para https://pypi.org/")
    response = input("Tem certeza? (s/n): ").strip().lower()
    
    if response != 's':
        print_info("Cancelado")
        return False
    
    version = get_version()
    print_info(f"Publicando versão {version}...")
    
    cmd = 'python -m twine upload dist/*'
    result = run_command(cmd, check=False)
    
    if result.returncode == 0:
        print_success("Upload para PyPI concluído!")
        print_info(f"\nView em: https://pypi.org/project/pysql_lite/")
        print_info(f"Instalar com: pip install pysql_lite=={version}")
        return True
    else:
        print_error("Upload falhou!")
        return False

def run_tests():
    """Executar testes"""
    print_header("🧪 Rodando Testes")
    
    cmd = 'python tests/test_database.py'
    result = run_command(cmd, check=False)
    
    if result.returncode == 0:
        print_success("Testes passaram!")
        return True
    else:
        print_error("Testes falharam!")
        return False

def show_menu():
    """Mostrar menu interativo"""
    print_header("📦 PYSQL_LITE PUBLISH TOOL")
    print("""
Opções:
  1. Clean        - Limpar artifacts
  2. Check        - Validar distribuição
  3. Build        - Criar distribuição
  4. Test         - Upload para Test PyPI
  5. Prod         - Upload para PyPI
  6. Run Tests    - Executar testes
  7. Full Flow    - Build → Validate → Upload
  0. Exit         - Sair

Escolha uma opção (0-7):
    """)

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = None
    
    # Verificar pré-requisitos
    if not check_prerequisites():
        sys.exit(1)
    
    if command == 'clean':
        clean_artifacts()
    
    elif command == 'check':
        if not build_distribution():
            sys.exit(1)
        if not validate_distribution():
            sys.exit(1)
    
    elif command == 'build':
        if not build_distribution():
            sys.exit(1)
        if not validate_distribution():
            sys.exit(1)
    
    elif command == 'test':
        if not build_distribution():
            sys.exit(1)
        if not validate_distribution():
            sys.exit(1)
        if not upload_to_testpypi():
            sys.exit(1)
    
    elif command == 'prod':
        if not run_tests():
            sys.exit(1)
        if not build_distribution():
            sys.exit(1)
        if not validate_distribution():
            sys.exit(1)
        if not upload_to_pypi():
            sys.exit(1)
    
    elif command == 'full':
        if not run_tests():
            sys.exit(1)
        if not build_distribution():
            sys.exit(1)
        if not validate_distribution():
            sys.exit(1)
        print_info("Pronto para upload!")
        response = input("Upload para PyPI? (s/n): ").strip().lower()
        if response == 's':
            if not upload_to_pypi():
                sys.exit(1)
    
    elif command == 'tests':
        if not run_tests():
            sys.exit(1)
    
    else:
        # Menu interativo
        show_menu()
        try:
            choice = input("Opção: ").strip()
            
            if choice == '1':
                clean_artifacts()
            elif choice == '2':
                if not build_distribution():
                    sys.exit(1)
                if not validate_distribution():
                    sys.exit(1)
            elif choice == '3':
                if not build_distribution():
                    sys.exit(1)
            elif choice == '4':
                if not build_distribution():
                    sys.exit(1)
                if not validate_distribution():
                    sys.exit(1)
                if not upload_to_testpypi():
                    sys.exit(1)
            elif choice == '5':
                if not run_tests():
                    sys.exit(1)
                if not build_distribution():
                    sys.exit(1)
                if not validate_distribution():
                    sys.exit(1)
                if not upload_to_pypi():
                    sys.exit(1)
            elif choice == '6':
                if not run_tests():
                    sys.exit(1)
            elif choice == '7':
                if not run_tests():
                    sys.exit(1)
                if not build_distribution():
                    sys.exit(1)
                if not validate_distribution():
                    sys.exit(1)
                response = input("Upload para PyPI? (s/n): ").strip().lower()
                if response == 's':
                    if not upload_to_pypi():
                        sys.exit(1)
            elif choice == '0':
                print("Bye! 👋")
            else:
                print_error("Opção inválida")
                sys.exit(1)
        
        except KeyboardInterrupt:
            print("\n\nCancelado")
            sys.exit(1)
    
    print("\n" + Colors.OKGREEN + "✅ Done!" + Colors.ENDC)

if __name__ == '__main__':
    main()
