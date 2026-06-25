"""
Módulo similarity.py - Mecanismo de similaridade entre casos.

Este módulo implementa o cálculo de similaridade entre casos médicos,
utilizando o método de correspondência de sintomas (matching coefficient).
"""

from typing import List, Tuple
from models import Case, MatchResult, PatientInput


class SimilarityEngine:
    """
    Motor de cálculo de similaridade entre casos.
    
    Implementa diferentes métricas de similaridade para comparação
    entre casos médicos baseados em seus sintomas.
    """
    
    def __init__(self, symptom_weights: dict = None):
        """
        Inicializa o motor de similaridade.
        
        Args:
            symptom_weights: Dicionário opcional com pesos para cada sintoma.
                           Se None, todos os sintomas têm peso igual.
        """
        self.symptom_weights = symptom_weights or {}
    
    def calculate_similarity(self, case1: Case, case2: Case) -> float:
        """
        Calcula a similaridade entre dois casos.
        
        Utiliza o coeficiente de correspondência simples (Simple Matching Coefficient):
        similaridade = (número de sintomas coincidentes) / (total de sintomas)
        
        Args:
            case1: Primeiro caso para comparação.
            case2: Segundo caso para comparação.
            
        Returns:
            Percentual de similaridade (0.0 a 100.0).
        """
        sintomas1 = case1.sintomas
        sintomas2 = case2.sintomas
        
        # Obtém todos os sintomas únicos de ambos os casos
        all_symptoms = set(sintomas1.keys()) | set(sintomas2.keys())
        
        if not all_symptoms:
            return 0.0
        
        matches = 0
        total_weight = 0.0
        
        for symptom in all_symptoms:
            val1 = sintomas1.get(symptom, False)
            val2 = sintomas2.get(symptom, False)
            
            # Peso do sintoma (1 se não especificado)
            weight = self.symptom_weights.get(symptom, 1.0)
            total_weight += weight
            
            if val1 == val2:
                matches += weight
        
        similarity = (matches / total_weight) * 100.0
        return round(similarity, 2)
    
    def calculate_similarity_from_input(self, patient_input: PatientInput, 
                                         case: Case) -> float:
        """
        Calcula similaridade entre entrada de paciente e um caso.
        
        Args:
            patient_input: Sintomas informados pelo paciente.
            case: Caso da base para comparação.
            
        Returns:
            Percentual de similaridade (0.0 a 100.0).
        """
        input_symptoms = patient_input.sintomas
        case_symptoms = case.sintomas
        
        # Obtém todos os sintomas únicos
        all_symptoms = set(input_symptoms.keys()) | set(case_symptoms.keys())
        
        if not all_symptoms:
            return 0.0
        
        matches = 0
        total_weight = 0.0
        
        for symptom in all_symptoms:
            val1 = input_symptoms.get(symptom, False)
            val2 = case_symptoms.get(symptom, False)
            
            weight = self.symptom_weights.get(symptom, 1.0)
            total_weight += weight
            
            if val1 == val2:
                matches += weight
        
        similarity = (matches / total_weight) * 100.0
        return round(similarity, 2)
    
    def find_most_similar(self, patient_input: PatientInput, 
                          cases: List[Case], 
                          top_k: int = 3) -> List[MatchResult]:
        """
        Encontra os k casos mais semelhantes ao input do paciente.
        
        Args:
            patient_input: Sintomas informados pelo paciente.
            cases: Lista de casos para busca.
            top_k: Número de casos mais semelhantes para retornar.
            
        Returns:
            Lista de MatchResult ordenada por similaridade (decrescente).
        """
        results = []
        
        for case in cases:
            similarity = self.calculate_similarity_from_input(patient_input, case)
            results.append(MatchResult(case=case, similaridade=similarity))
        
        # Ordena por similaridade decrescente
        results.sort(key=lambda x: x.similaridade, reverse=True)
        
        # Retorna os top_k primeiros
        return results[:top_k]
    
    def find_cases_above_threshold(self, patient_input: PatientInput,
                                    cases: List[Case],
                                    threshold: float = 50.0) -> List[MatchResult]:
        """
        Encontra todos os casos acima de um limiar de similaridade.
        
        Args:
            patient_input: Sintomas informados pelo paciente.
            cases: Lista de casos para busca.
            threshold: Limiar mínimo de similaridade (0-100).
            
        Returns:
            Lista de MatchResult com similaridade acima do limiar.
        """
        results = []
        
        for case in cases:
            similarity = self.calculate_similarity_from_input(patient_input, case)
            if similarity >= threshold:
                results.append(MatchResult(case=case, similaridade=similarity))
        
        # Ordena por similaridade decrescente
        results.sort(key=lambda x: x.similaridade, reverse=True)
        
        return results
    
    def get_symptom_contribution(self, patient_input: PatientInput, 
                                  case: Case) -> List[Tuple[str, bool, bool, bool]]:
        """
        Analisa a contribuição de cada sintoma para a similaridade.
        
        Args:
            patient_input: Sintomas informados pelo paciente.
            case: Caso para comparação.
            
        Returns:
            Lista de tuplas (sintoma, valor_paciente, valor_caso, coincidiu).
        """
        input_symptoms = patient_input.sintomas
        case_symptoms = case.sintomas
        
        all_symptoms = set(input_symptoms.keys()) | set(case_symptoms.keys())
        
        contributions = []
        for symptom in sorted(all_symptoms):
            val1 = input_symptoms.get(symptom, False)
            val2 = case_symptoms.get(symptom, False)
            matched = val1 == val2
            contributions.append((symptom, val1, val2, matched))
        
        return contributions
    
    def set_symptom_weight(self, symptom: str, weight: float) -> None:
        """
        Define o peso de um sintoma específico.
        
        Args:
            symptom: Nome do sintoma.
            weight: Peso (valor maior = mais importante).
        """
        self.symptom_weights[symptom] = weight
    
    def reset_weights(self) -> None:
        """Reseta todos os pesos para valores iguais."""
        self.symptom_weights = {}