"""
Módulo utils.py - Utilitários para o sistema CBR médico.

Este módulo contém funções utilitárias para formatação, validação
e outras operações auxiliares do sistema.
"""

from typing import List, Dict, Tuple
from datetime import datetime


# Lista completa de sintomas suportados pelo sistema
SYMPTOMS_LIST = [
    ("febre", "Febre"),
    ("tosse", "Tosse"),
    ("dor_garganta", "Dor de garganta"),
    ("dor_muscular", "Dor muscular"),
    ("coriza", "Coriza"),
    ("dor_cabeca", "Dor de cabeça"),
    ("fadiga", "Fadiga"),
    ("congestao_nasal", "Congestão nasal"),
    ("falta_ar", "Falta de ar"),
    ("nausea", "Náusea"),
]

# Lista de diagnósticos possíveis
DIAGNOSES_LIST = [
    "Gripe",
    "COVID-19",
    "Sinusite",
    "Amigdalite",
    "Dengue",
    "Resfriado Comum",
    "Rinite Alérgica",
    "Faringite",
]


def clear_screen() -> None:
    """Limpa a tela do terminal."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str, char: str = "=") -> None:
    """
    Imprime um cabeçalho formatado.
    
    Args:
        title: Texto do cabeçalho.
        char: Caractere para borda.
    """
    width = max(len(title) + 4, 50)
    print(char * width)
    print(f"  {title}")
    print(char * width)


def print_section(title: str) -> None:
    """
    Imprime uma seção formatada.
    
    Args:
        title: Título da seção.
    """
    print(f"\n{'─' * 40}")
    print(f"  {title}")
    print(f"{'─' * 40}")


def get_yes_no_input(prompt: str) -> bool:
    """
    Solicita uma entrada Sim/Não do usuário.
    
    Args:
        prompt: Texto da pergunta.
        
    Returns:
        True para 'S' ou 'sim', False caso contrário.
    """
    while True:
        response = input(f"{prompt} [S/N]: ").strip().upper()
        if response in ['S', 'SIM']:
            return True
        elif response in ['N', 'NAO', 'NÃO']:
            return False
        else:
            print("Por favor, digite 'S' para sim ou 'N' para não.")


def get_symptom_input() -> dict:
    """
    Solicita ao usuário que informe seus sintomas.
    
    Returns:
        Dicionário com sintomas e seus valores booleanos.
    """
    print_header("INFORME SEUS SINTOMAS")
    print("Responda S (Sim) ou N (Não) para cada sintoma:\n")
    
    sintomas = {}
    for symptom_id, symptom_name in SYMPTOMS_LIST:
        while True:
            try:
                response = input(f"  {symptom_name}? ").strip().upper()
                if response in ['S', 'SIM']:
                    sintomas[symptom_id] = True
                    break
                elif response in ['N', 'NAO', 'NÃO']:
                    sintomas[symptom_id] = False
                    break
                else:
                    print("    Por favor, digite 'S' ou 'N'.")
            except EOFError:
                sintomas[symptom_id] = False
                break
    
    return sintomas


def format_similarity_results(matches: list, max_results: int = 3) -> str:
    """
    Formata os resultados de similaridade para exibição.
    
    Args:
        matches: Lista de MatchResult.
        max_results: Número máximo de resultados para exibir.
        
    Returns:
        String formatada com os resultados.
    """
    if not matches:
        return "Nenhum caso semelhante encontrado."
    
    lines = []
    lines.append("\nCasos mais semelhantes encontrados:\n")
    
    for i, match in enumerate(matches[:max_results], 1):
        ordinal = f"{i}º"
        lines.append(f"  {ordinal} Caso (ID: {match.case.id}):")
        lines.append(f"    Diagnóstico: {match.case.diagnostico}")
        lines.append(f"    Similaridade: {match.similaridade:.1f}%")
        lines.append(f"    Tratamento: {match.case.tratamento}")
        lines.append("")
    
    return "\n".join(lines)


def format_diagnosis_result(results: dict) -> str:
    """
    Formata o resultado do diagnóstico para exibição.
    
    Args:
        results: Dicionário com resultados do diagnóstico.
        
    Returns:
        String formatada com o diagnóstico.
    """
    lines = []
    lines.append("\n" + "=" * 50)
    lines.append("  DIAGNÓSTICO SUGERIDO")
    lines.append("=" * 50)
    lines.append(f"  Diagnóstico: {results['diagnosis']}")
    lines.append(f"  Confiança: {results['confidence']:.1f}%")
    lines.append("")
    lines.append("  Tratamento Recomendado:")
    lines.append(f"  {results['treatment']}")
    lines.append("=" * 50)
    
    return "\n".join(lines)


def format_case_for_display(case, similarity: float = None) -> str:
    """
    Formata um caso para exibição detalhada.
    
    Args:
        case: Objeto Case.
        similarity: Similaridade (opcional).
        
    Returns:
        String formatada com detalhes do caso.
    """
    lines = []
    lines.append(f"  Caso ID: {case.id}")
    lines.append(f"  Diagnóstico: {case.diagnostico}")
    if similarity is not None:
        lines.append(f"  Similaridade: {similarity:.1f}%")
    lines.append("")
    lines.append("  Sintomas:")
    
    for symptom_id, symptom_name in SYMPTOMS_LIST:
        value = case.sintomas.get(symptom_id, False)
        status = "✓ Sim" if value else "✗ Não"
        lines.append(f"    {symptom_name}: {status}")
    
    lines.append("")
    lines.append(f"  Tratamento: {case.tratamento}")
    
    return "\n".join(lines)


def print_statistics(stats: dict) -> None:
    """
    Imprime estatísticas da base de casos.
    
    Args:
        stats: Dicionário com estatísticas.
    """
    print_header("ESTATÍSTICAS DA BASE DE CASOS")
    print(f"\nTotal de casos: {stats['total_cases']}\n")
    print("Distribuição por diagnóstico:")
    
    for diagnosis, count in sorted(stats["diagnoses"].items()):
        percentage = (count / stats["total_cases"]) * 100
        bar = "█" * int(percentage / 5)
        print(f"  {diagnosis:20s}: {count:3d} ({percentage:5.1f}%) {bar}")
    
    print()


def get_diagnosis_choice(diagnoses: List[str], suggested: str = None) -> str:
    """
    Permite ao usuário escolher um diagnóstico da lista.
    
    Args:
        diagnoses: Lista de diagnósticos disponíveis.
        suggested: Diagnóstico sugerido (opcional).
        
    Returns:
        Diagnóstico escolhido.
    """
    print("\nDiagnósticos disponíveis:")
    for i, diag in enumerate(diagnoses, 1):
        marker = " (sugerido)" if diag == suggested else ""
        print(f"  {i}. {diag}{marker}")
    
    while True:
        try:
            choice = input("\nEscolha o diagnóstico (número): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(diagnoses):
                return diagnoses[idx]
            else:
                print("Opção inválida. Tente novamente.")
        except ValueError:
            # Permite digitar o nome diretamente
            choice = choice.title()
            if choice in [d.title() for d in diagnoses]:
                return choice
            print("Diagnóstico não encontrado. Tente novamente.")


def get_treatment_input() -> str:
    """
    Solicita ao usuário que informe o tratamento.
    
    Returns:
        String com o tratamento.
    """
    print("\nInforme o tratamento prescrito:")
    treatment = input("  Tratamento: ").strip()
    return treatment


def log_diagnosis(patient_symptoms: dict, diagnosis: str, 
                  confidence: float, was_modified: bool) -> None:
    """
    Registra um diagnóstico em arquivo de log.
    
    Args:
        patient_symptoms: Sintomas do paciente.
        diagnosis: Diagnóstico final.
        confidence: Nível de confiança.
        was_modified: Se o diagnóstico foi modificado.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    symptoms_str = ", ".join([k for k, v in patient_symptoms.items() if v])
    
    log_entry = (
        f"[{timestamp}] Diagnóstico: {diagnosis} | "
        f"Confiança: {confidence:.1f}% | "
        f"Modificado: {'Sim' if was_modified else 'Não'} | "
        f"Sintomas: {symptoms_str}\n"
    )
    
    try:
        with open("diagnostico.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except IOError:
        pass  # Falha silenciosa no log


def validate_symptoms(sintomas: dict) -> bool:
    """
    Valida se o dicionário de sintomas está correto.
    
    Args:
        sintomas: Dicionário de sintomas.
        
    Returns:
        True se válido, False caso contrário.
    """
    required_symptoms = [s[0] for s in SYMPTOMS_LIST]
    
    for symptom in required_symptoms:
        if symptom not in sintomas:
            return False
        if not isinstance(sintomas[symptom], bool):
            return False
    
    return True