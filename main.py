import sys
import os
import argparse
from run_artifacts import create_run_dir

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'src'))

from interfaces import I_Interface_Usuario, I_Orquestrador
from orquestrador import MainCompiler

# O terminal e a web falam com o compilador so pela interface I_Orquestrador.
COMPILADOR: I_Orquestrador = MainCompiler()


def compile_file(source_path: str, output_name: str, output_dir: str = None) -> bool:
    """Processa as fases do compilador em um arquivo alvo (via componente orquestrador)."""
    return COMPILADOR.compile_file(source_path, output_name, output_dir)


def start_interactive():
    """Inicia a tela de seleção inicial do sistema."""
    from test_orchestrator import (
        check_active_session_for_new_terminal,
        join_session,
        get_terminal_id,
        run_joiner_progress_monitor,
        _load_session,
    )

    action, session = check_active_session_for_new_terminal()
    if action == "join" and session:
        join_session(session)
        session = _load_session() or session
        print("\n" + "=" * 45)
        print("  MINIPAR — PARTICIPANTE DE TESTE")
        print("=" * 45)
        print(f"\n  Terminal identificado: {get_terminal_id()}")
        print(f"  Teste em andamento: {session.get('titulo', session.get('test_file', ''))}")
        print("\n  Monitor de progresso iniciado...\n")
        run_joiner_progress_monitor(session)
    elif action == "independent":
        print("\n  [INFO] Sessão em andamento ignorada — modo independente.\n")

    print("\n" + "=" * 45)
    print("      MINIPAR COMPILER & IDE")
    print("=" * 45)
    print("\nComo você deseja rodar o sistema?\n")
    print("[1] - Modo Terminal (Menu Interativo)")
    print("[2] - Modo Web Interface (IDE no Navegador)\n")
    
    escolha = input("Digite a sua escolha (1 ou 2): ").strip()
    
    if escolha == '1':
        print("\nIniciando modo Terminal...\n")
        try:
            from menu import MenuCLI
            interface: I_Interface_Usuario = MenuCLI()
            interface.iniciar_interacao()
        except ImportError as e:
            print(f"[ERRO] Falha ao carregar o menu: {e}")
            
    elif escolha == '2':
        print("\nIniciando Web Interface IDE...")
        print("Servidor inicializado! Acesse no navegador: http://127.0.0.1:5000\n")
        try:
            from app import IDEWebApp
            # Executa o Flask. Deixamos debug=False para o terminal ficar mais limpo
            interface: I_Interface_Usuario = IDEWebApp(host="127.0.0.1", port=5000)
            interface.iniciar_interacao()
        except ImportError as e:
            print(f"[ERRO] Falha ao carregar a interface web: {e}")
        except Exception as e:
            print(f"[ERRO] Erro ao iniciar o servidor Flask: {e}")
    else:
        print("\n[ERRO] Escolha inválida. Finalizando o sistema.")


def main() -> int:
    if len(sys.argv) < 2:
        start_interactive()
        return 0

    arguments = argparse.ArgumentParser(description="MiniPar compiler")
    arguments.add_argument("source_path")
    arguments.add_argument("output_name", nargs="?")
    arguments.add_argument("--output-dir", help="Explicit artifact directory (default: a private run directory)")
    args = arguments.parse_args()
    source_path = args.source_path
    
    if args.output_name:
        output_name = args.output_name
    else:
        base_file = os.path.basename(source_path)
        output_name = base_file.replace('.minipar', '')

    print("=== Compilador MiniPar ===")
    success = compile_file(source_path, output_name, args.output_dir)
    
    if success:
        print("=== Processo Finalizado ===")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
