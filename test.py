import asyncio
import sys
import logging
from pathlib import Path
from datetime import datetime

from ghost_projects.config.settings import settings
from ghost_projects.schemas.project import ProjectInfo
from ghost_projects.schemas.assessment import ProjectAssessment
from ghost_projects.services.scanner import ProjectScanner
from ghost_projects.services.reader import FileReader
from ghost_projects.services.search import FileSearchService
from ghost_projects.services.git_inspector import GitInspector
from ghost_projects.services.evidence import EvidenceCollector
from ghost_projects.ai.runner import run_investigation
from ghost_projects.services.file_filter import FileFilter

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# Altere este caminho para o diretório do projeto que deseja investigar
PROJECT_PATH = r"C:\xampp\htdocs\forgotten-downloads"
# ==============================================================================

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def print_section(title):
    print(f"\n{'='*80}")
    print(f" {title}")
    print(f"{'='*80}")

async def main():
    start_time = datetime.now()
    root_path = Path(PROJECT_PATH)

    # 1. Validação do Caminho
    if not root_path.exists():
        print(f"Erro: O caminho especificado não existe: {PROJECT_PATH}")
        sys.exit(1)
    if not root_path.is_dir():
        print(f"Erro: O caminho especificado não é um diretório: {PROJECT_PATH}")
        sys.exit(1)

    # 2. Verificação de Configuração
    # O settings.ollama_api_key é um SecretStr, usamos .get_secret_value()
    api_key = settings.ollama_api_key.get_secret_value()
    if not api_key or api_key == "ollama":
        # Se o valor for o default "ollama" e não houver .env, pode ser um erro de config
        # dependendo de como o Ollama Cloud exige a chave.
        logger.warning("Aviso: A chave de API do Ollama parece estar usando o valor padrão ou está ausente.")

    print_section("A. Configuração da Investigação")
    print(f"Caminho do Projeto: {root_path}")
    print(f"Modelo Configurado: {settings.model_name}")
    print(f"Endpoint: {settings.ollama_base_url}")
    print(f"Provedor: Real (Ollama Cloud)")

    try:
        # 3. Inicialização de Serviços
        scanner = ProjectScanner()
        filter = FileFilter(root_path)
        reader = FileReader(file_filter=filter)
        search_service = FileSearchService()
        git_inspector = GitInspector()
        evidence_collector = EvidenceCollector()

        # 4. Preparação de Informações do Projeto
        has_git = git_inspector.is_git_repository(root_path)
        project_info = ProjectInfo(
            name=root_path.name,
            root_path=root_path,
            detected_languages=[], # O runner/agent descobrirá isso
            detected_technologies=[],
            has_git=has_git
        )

        print("\nIniciando investigação... Isso pode levar alguns minutos.")
        
        # 5. Execução da Investigação
        assessment: ProjectAssessment = await run_investigation(
            project_info=project_info,
            scanner=scanner,
            reader=reader,
            search_service=search_service,
            git_inspector=git_inspector,
            evidence_collector=evidence_collector,
            max_turns=19
        )

        # 6. Relatório de Resultados (em Português)
        
        print_section("B. Visão Geral do Projeto")
        print(f"Intenção Original: {assessment.original_intent}")
        print(f"Resumo da Investigação: {assessment.investigation_summary}")
        print(f"Arquitetura Recuperada: {assessment.recovered_architecture}")
        print(f"Git Detectado: {'Sim' if has_git else 'Não'}")

        print_section("C. Pistas da Investigação (Clues)")
        if not assessment.clues:
            print("Nenhuma pista significativa encontrada.")
        else:
            for i, clue in enumerate(assessment.clues, 1):
                print(f"\n{i}. {clue.title}")
                print(f"   Categoria: {clue.category.value}")
                print(f"   Confiança: {clue.confidence:.2%}")
                print(f"   Descrição: {clue.description}")
                print(f"   Evidências: {', '.join(clue.evidence_ids) if clue.evidence_ids else 'Nenhuma'}")

        print_section("D. Plano de Ressurreição")
        if not assessment.resurrection_plan:
            print("Nenhuma etapa de ressurreição recomendada.")
        else:
            for i, step in enumerate(assessment.resurrection_plan, 1):
                print(f"\n{i}. {step.title}")
                print(f"   Prioridade: {step.priority.value.upper()}")
                print(f"   Ação Concreta: {step.concrete_action}")
                print(f"   Detalhes: {step.description}")
                print(f"   Evidências: {', '.join(step.evidence_ids) if step.evidence_ids else 'Nenhuma'}")

        print_section("E. Evidências")
        if not assessment.evidence:
            print("Nenhuma evidência coletada.")
        else:
            for ev in assessment.evidence:
                line_info = f"Linhas {ev.line_start}-{ev.line_end}" if ev.line_start else "N/A"
                print(f"\nID: {ev.id}")
                print(f"Arquivo: {ev.source_path}")
                print(f"Linhas: {line_info}")
                print(f"Descrição: {ev.description}")
                if ev.excerpt:
                    print(f"Trecho:\n--- \n{ev.excerpt}\n---")

        print_section("F. Fantasmas e Limitações")
        if not assessment.unknowns:
            print("Nenhuma limitação ou fantasma reportada.")
        else:
            for unknown in assessment.unknowns:
                print(f"- {unknown}")

        end_time = datetime.now()
        duration = end_time - start_time

        print_section("G. Resumo da Execução")
        print(f"Status: Sucesso")
        print(f"Total de Pistas: {len(assessment.clues)}")
        print(f"Total de Evidências: {len(assessment.evidence)}")
        print(f"Duração: {duration}")

    except ValueError as e:
        print(f"\nErro de Validação: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"\nErro de Execução: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Ocorreu um erro inesperado durante a investigação")
        print(f"\nErro Inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())