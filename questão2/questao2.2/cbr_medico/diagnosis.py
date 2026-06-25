"""
Módulo diagnosis.py - Motor de diagnóstico baseado em CBR.

Este módulo implementa o motor de diagnóstico que utiliza o ciclo CBR
(Retrieve, Reuse, Revise, Retain) para sugerir diagnósticos médicos.
"""

from typing import List, Optional, Tuple
from collections import Counter

from models import Case, MatchResult, PatientInput
from case_base import CaseBase
from similarity import SimilarityEngine


class DiagnosisEngine:
    """
    Motor de diagnóstico baseado em Case-Based Reasoning (CBR).
    
    Implementa as quatro etapas do ciclo CBR:
    1. Retrieve (Recuperação) - Encontra casos semelhantes
    2. Reuse (Reutilização) - Sugere diagnóstico baseado nos casos
    3. Revise (Revisão) - Permite correção do diagnóstico
    4. Retain (Retenção) - Armazena novo caso na base
    """
    
    def __init__(self, case_base: CaseBase, similarity_engine: SimilarityEngine = None):
        """
        Inicializa o motor de diagnóstico.
        
        Args:
            case_base: Base de casos para consulta.
            similarity_engine: Motor de similaridade. Se None, cria um novo.
        """
        self.case_base = case_base
        self.similarity_engine = similarity_engine or SimilarityEngine()
    
    def retrieve(self, patient_input: PatientInput, 
                 top_k: int = 3) -> List[MatchResult]:
        """
        Fase de Retrieve (Recuperação) do ciclo CBR.
        
        Encontra os casos mais semelhantes na base de casos.
        
        Args:
            patient_input: Sintomas informados pelo paciente.
            top_k: Número de casos a retornar.
            
        Returns:
            Lista de MatchResult com os casos mais semelhantes.
        """
        cases = self.case_base.get_all_cases()
        return self.similarity_engine.find_most_similar(patient_input, cases, top_k)
    
    def reuse(self, matches: List[MatchResult]) -> Tuple[str, str, float]:
        """
        Fase de Reuse (Reutilização) do ciclo CBR.
        
        Utiliza os casos recuperados para sugerir um diagnóstico.
        O diagnóstico é determinado por votação majoritária ponderada
        pela similaridade dos casos.
        
        Args:
            matches: Lista de casos correspondentes com suas similaridades.
            
        Returns:
            Tupla (diagnóstico_sugerido, tratamento, confiança).
        """
        if not matches:
            return ("Desconhecido", 
                    "Procure avaliação médica para diagnóstico adequado.",
                    0.0)
        
        # Votação ponderada pela similaridade
        diagnosis_votes = {}
        diagnosis_treatments = {}
        
        for match in matches:
            diag = match.case.diagnostico
            sim = match.similaridade
            
            if diag not in diagnosis_votes:
                diagnosis_votes[diag] = 0
                diagnosis_treatments[diag] = match.case.tratamento
            
            diagnosis_votes[diag] += sim
        
        # Encontra diagnóstico com maior pontuação
        suggested_diagnosis = max(diagnosis_votes, key=diagnosis_votes.get)
        confidence = diagnosis_votes[suggested_diagnosis]
        
        # Calcula confiança normalizada (0-100)
        total_votes = sum(diagnosis_votes.values())
        if total_votes > 0:
            confidence = (confidence / total_votes) * 100
        
        treatment = diagnosis_treatments[suggested_diagnosis]
        
        return suggested_diagnosis, treatment, round(confidence, 2)
    
    def revise(self, suggested_diagnosis: str, 
               available_diagnoses: List[str] = None) -> Tuple[str, bool]:
        """
        Fase de Revise (Revisão) do ciclo CBR.
        
        Permite que o usuário confirme ou corrija o diagnóstico sugerido.
        Este método retorna o diagnóstico final e se foi modificado.
        
        Args:
            suggested_diagnosis: Diagnóstico sugerido pelo sistema.
            available_diagnoses: Lista de diagnósticos disponíveis.
            
        Returns:
            Tupla (diagnóstico_final, foi_modificado).
        """
        if available_diagnoses is None:
            # Obtém diagnósticos únicos da base
            stats = self.case_base.get_statistics()
            available_diagnoses = list(stats["diagnoses"].keys())
        
        return suggested_diagnosis, False  # Por padrão, não modifica
    
    def retain(self, patient_input: PatientInput, diagnosis: str, 
               treatment: str) -> Optional[Case]:
        """
        Fase de Retain (Retenção) do ciclo CBR.
        
        Armazena o novo caso na base de dados para uso futuro.
        
        Args:
            patient_input: Sintomas do paciente.
            diagnosis: Diagnóstico confirmado.
            treatment: Tratamento prescrito.
            
        Returns:
            Novo caso criado, ou None se falhar.
        """
        patient_case = patient_input.to_case()
        return self.case_base.add_case_from_input(patient_case, diagnosis, treatment)
    
    def diagnose(self, patient_input: PatientInput, 
                 top_k: int = 3,
                 confirm_diagnosis: bool = True) -> dict:
        """
        Executa o ciclo CBR completo para diagnóstico.
        
        Args:
            patient_input: Sintomas informados pelo paciente.
            top_k: Número de casos para considerar.
            confirm_diagnosis: Se True, permite confirmação/correção.
            
        Returns:
            Dicionário com resultados do diagnóstico.
        """
        # 1. RETRIEVE
        matches = self.retrieve(patient_input, top_k)
        
        if not matches:
            return {
                "matches": [],
                "diagnosis": "Desconhecido",
                "treatment": "Procure avaliação médica.",
                "confidence": 0.0,
                "was_modified": False
            }
        
        # 2. REUSE
        diagnosis, treatment, confidence = self.reuse(matches)
        was_modified = False
        
        # 3. REVISE (opcional)
        if confirm_diagnosis:
            diagnosis, was_modified = self.revise(diagnosis)
        
        return {
            "matches": matches,
            "diagnosis": diagnosis,
            "treatment": treatment,
            "confidence": confidence,
            "was_modified": was_modified
        }
    
    def diagnose_and_retain(self, patient_input: PatientInput,
                            diagnosis: str, treatment: str,
                            top_k: int = 3) -> Tuple[dict, Optional[Case]]:
        """
        Executa o ciclo CBR completo e retém o novo caso.
        
        Args:
            patient_input: Sintomas informados pelo paciente.
            diagnosis: Diagnóstico confirmado.
            treatment: Tratamento prescrito.
            top_k: Número de casos para considerar.
            
        Returns:
            Tupla (resultados_diagnóstico, novo_caso).
        """
        results = self.diagnose(patient_input, top_k, confirm_diagnosis=False)
        new_case = self.retain(patient_input, diagnosis, treatment)
        
        return results, new_case
    
    def get_differential_diagnosis(self, patient_input: PatientInput,
                                    top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Retorna diagnóstico diferencial baseado em todos os casos.
        
        Args:
            patient_input: Sintomas do paciente.
            top_k: Número máximo de diagnósticos para retornar.
            
        Returns:
            Lista de tuplas (diagnóstico, probabilidade).
        """
        cases = self.case_base.get_all_cases()
        
        # Calcula similaridade com todos os casos
        diagnosis_scores = {}
        
        for case in cases:
            sim = self.similarity_engine.calculate_similarity_from_input(
                patient_input, case
            )
            diag = case.diagnostico
            
            if diag not in diagnosis_scores:
                diagnosis_scores[diag] = []
            diagnosis_scores[diag].append(sim)
        
        # Calcula score médio por diagnóstico
        diagnosis_avg = {}
        for diag, scores in diagnosis_scores.items():
            diagnosis_avg[diag] = sum(scores) / len(scores)
        
        # Ordena por score decrescente
        sorted_diagnoses = sorted(
            diagnosis_avg.items(), key=lambda x: x[1], reverse=True
        )
        
        return sorted_diagnoses[:top_k]
    
    def explain_diagnosis(self, patient_input: PatientInput, 
                          matched_case: Case) -> str:
        """
        Gera uma explicação para o diagnóstico baseado na similaridade.
        
        Args:
            patient_input: Sintomas do paciente.
            matched_case: Caso correspondente.
            
        Returns:
            String com explicação do diagnóstico.
        """
        contributions = self.similarity_engine.get_symptom_contribution(
            patient_input, matched_case
        )
        
        explanation_lines = [
            f"Diagnóstico: {matched_case.diagnostico}",
            f"Similaridade: {matched_case.diagnostico}",
            "",
            "Análise dos sintomas:"
        ]
        
        matching_symptoms = []
        differing_symptoms = []
        
        for symptom, patient_val, case_val, matched in contributions:
            symptom_name = symptom.replace("_", " ").title()
            if matched:
                if patient_val:
                    matching_symptoms.append(f"  ✓ {symptom_name}: Presente em ambos")
            else:
                differing_symptoms.append(
                    f"  ✗ {symptom_name}: Paciente={'Sim' if patient_val else 'Não'}, "
                    f"Caso={'Sim' if case_val else 'Não'}"
                )
        
        explanation_lines.extend(matching_symptoms)
        if differing_symptoms:
            explanation_lines.append("")
            explanation_lines.extend(differing_symptoms)
        
        return "\n".join(explanation_lines)