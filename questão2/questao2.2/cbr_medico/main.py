"""
main.py - Sistema Inteligente de Diagnóstico Médico Baseado em Casos (CBR).

Este é o arquivo principal que fornece a interface de terminal para o sistema
de diagnóstico médico baseado em Case-Based Reasoning (CBR).

Disciplina: Inteligência Artificial
Autor: Desenvolvido para fins educacionais
"""

import sys
from typing import Optional

from models import PatientInput
from case_base import CaseBase
from similarity import SimilarityEngine
from diagnosis import DiagnosisEngine
import utils


def show_menu() -> str:
    """
    Exibe o menu principal e retorna a opção escolhida.
    
    Returns:
        String com a opção selecionada.
    """
    print("\n")
    utils.print_header("SISTEMA CBR MÉDICO - DIAGNÓSTICO INTELIGENTE")
    print("""
  1. Novo Diagnóstico
  2. Ver Estatísticas da Base
  3. Listar Casos Existentes
  4. Adicionar Caso Manualmente
  5. Sair
    """)
    
    return input("  Escolha uma opção: ").strip()


def perform_diagnosis(engine: DiagnosisEngine) -> None:
    """
    Realiza o processo completo de diagnóstico usando CBR.
    
    Args:
        engine: Motor de diagnóstico.
    """
    utils.clear_screen()
    
    # Coleta sintomas do paciente
    sintomas = utils.get_symptom_input()
    patient_input = PatientInput(sintomas=sintomas)
    
    # Executa o ciclo CBR
    print("\nAnalisando casos semelhantes...")
    
    # 1. RETRIEVE - Encontrar casos semelhantes
    matches = engine.retrieve(patient_input, top_k=3)
    
    if not matches:
        print("\nNenhum caso semelhante encontrado na base.")
        print("Não foi possível sugerir um diagnóstico.")
        return
    
    # Exibe casos semelhantes
    print(utils.format_similarity_results(matches))
    
    # 2. REUSE - Reutilizar casos para sugerir diagnóstico
    diagnosis, treatment, confidence = engine.reuse(matches)
    
    # Exibe diagnóstico sugerido
    print(f"\n{'=' * 50}")
    print("  DIAGNÓSTICO SUGERIDO")
    print(f"{'=' * 50}")
    print(f"  Diagnóstico: {diagnosis}")
    print(f"  Confiança: {confidence:.1f}%")
    print(f"{'=' * 50}")
    
    # 3. REVISE - Permitir correção do diagnóstico
    print("\nDeseja confirmar este diagnóstico?")
    if utils.get_yes_no_input("  Confirmar"):
        final_diagnosis = diagnosis
        final_treatment = treatment
        was_modified = False
    else:
        # Usuário deseja corrigir
        stats = engine.case_base.get_statistics()
        available_diagnoses = list(stats["diagnoses"].keys())
        
        print(f"\nDiagnóstico sugerido: {diagnosis}")
        final_diagnosis = utils.get_diagnosis_choice(available_diagnoses, diagnosis)
        final_treatment = utils.get_treatment_input()
        was_modified = True
    
    # Exibe resultado final
    print(f"\n{'=' * 50}")
    print("  RESULTADO FINAL")
    print(f"{'=' * 50}")
    print(f"  Diagnóstico: {final_diagnosis}")
    print(f"  Tratamento: {final_treatment}")
    if was_modified:
        print("  [Diagnóstico modificado pelo usuário]")
    print(f"{'=' * 50}")
    
    # 4. RETAIN - Perguntar se deseja salvar o caso
    print("\nDeseja salvar este caso na base para uso futuro?")
    if utils.get_yes_no_input("  Salvar caso"):
        new_case = engine.retain(patient_input, final_diagnosis, final_treatment)
        if new_case:
            print(f"\n✓ Caso salvo com sucesso! (ID: {new_case.id})")
    
    # Registra no log
    utils.log_diagnosis(sintomas, final_diagnosis, confidence, was_modified)
    
    input("\nPressione Enter para continuar...")


def show_statistics(case_base: CaseBase) -> None:
    """
    Exibe estatísticas da base de casos.
    
    Args:
        case_base: Base de casos.
    """
    utils.clear_screen()
    stats = case_base.get_statistics()
    utils.print_statistics(stats)
    input("Pressione Enter para continuar...")


def list_cases(case_base: CaseBase) -> None:
    """
    Lista todos os casos na base.
    
    Args:
        case_base: Base de casos.
    """
    utils.clear_screen()
    utils.print_header("CASOS CADASTRADOS")
    
    cases = case_base.get_all_cases()
    
    if not cases:
        print("\nNenhum caso cadastrado.")
    else:
        print(f"\nTotal: {len(cases)} casos\n")
        for case in cases:
            sintomas_presentes = [
                name for sid, name in utils.SYMPTOMS_LIST 
                if case.sintomas.get(sid, False)
            ]
            print(f"  ID {case.id}: {case.diagnostico}")
            print(f"    Sintomas: {', '.join(sintomas_presentes[:5])}{'...' if len(sintomas_presentes) > 5 else ''}")
            print()
    
    input("Pressione Enter para continuar...")


def add_manual_case(case_base: CaseBase) -> None:
    """
    Adiciona um caso manualmente à base.
    
    Args:
        case_base: Base de casos.
    """
    utils.clear_screen()
    utils.print_header("ADICIONAR NOVO CASO")
    
    print("\nInforme os sintomas do paciente:")
    sintomas = utils.get_symptom_input()
    
    # Seleciona diagnóstico
    stats = case_base.get_statistics()
    available_diagnoses = list(stats["diagnoses"].keys())
    print("\nDiagnósticos disponíveis:")
    for i, diag in enumerate(available_diagnoses, 1):
        print(f"  {i}. {diag}")
    
    while True:
        try:
            choice = input("\nEscolha o diagnóstico (número): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(available_diagnoses):
                diagnosis = available_diagnoses[idx]
                break
            else:
                print("Opção inválida.")
        except ValueError:
            diagnosis = input("Ou digite o diagnóstico: ").strip().title()
            break
    
    # Informa tratamento
    print("\nInforme o tratamento prescrito:")
    treatment = input("  Tratamento: ").strip()
    
    # Cria e salva o case
    from models import Case
    new_case = Case(
        id=0,  # Será substituído pelo próximo ID disponível
        sintomas=sintomas,
        diagnostico=diagnosis,
        tratamento=treatment
    )
    
    if case_base.add_case(new_case):
        print(f"\n✓ Caso adicionado com sucesso! (ID: {new_case.id})")
    else:
        print("\n✗ Erro ao adicionar caso.")
    
    input("\nPressione Enter para continuar...")


def main() -> None:
    """Função principal do sistema."""
    utils.clear_screen()
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   SISTEMA INTELIGENTE DE DIAGNÓSTICO MÉDICO BASEADO EM    ║
    ║              CASE-BASED REASONING (CBR)                   ║
    ║                                                           ║
    ║   Disciplina: Inteligência Artificial                     ║
    ║   Finalidade: Educacional                                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Inicializa a base de casos
    try:
        case_base = CaseBase("casos.json")
        print(f"\n✓ Base de casos carregada: {case_base.get_case_count()} casos.")
    except Exception as e:
        print(f"\n✗ Erro ao carregar base de casos: {e}")
        print("O sistema será iniciado com base vazia.")
        case_base = CaseBase()
    
    # Inicializa os motores
    similarity_engine = SimilarityEngine()
    diagnosis_engine = DiagnosisEngine(case_base, similarity_engine)
    
    input("\nPressione Enter para continuar...")
    
    # Loop principal
    while True:
        utils.clear_screen()
        option = show_menu()
        
        if option == '1':
            perform_diagnosis(diagnosis_engine)
        elif option == '2':
            show_statistics(case_base)
        elif option == '3':
            list_cases(case_base)
        elif option == '4':
            add_manual_case(case_base)
        elif option == '5':
            print("\nObrigado por usar o Sistema CBR Médico!")
            print("Desenvolvido para fins educacionais.\n")
            break
        else:
            print("\nOpção inválida! Tente novamente.")
            input("Pressione Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSistema encerrado pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        print("Por favor, verifique os arquivos do sistema.")