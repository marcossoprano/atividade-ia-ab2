"""
Módulo case_base.py - Gerenciamento da base de casos.

Este módulo contém a classe CaseBase que gerencia a coleção
de casos médicos, fornecendo operações de CRUD e consultas.
"""

from typing import List, Optional
from models import Case
from persistence import PersistenceManager


class CaseBase:
    """
    Gerencia a base de casos médicos.
    
    Esta classe fornece uma interface para operações na base de casos,
    incluindo carregamento, salvamento, adição e recuperação de casos.
    """
    
    def __init__(self, file_path: str = None):
        """
        Inicializa a base de casos.
        
        Args:
            file_path: Caminho para o arquivo JSON. Se None, usa o padrão.
        """
        self.persistence = PersistenceManager(file_path)
        self.cases: List[Case] = []
        self._load_cases()
    
    def _load_cases(self) -> None:
        """Carrega os casos do arquivo de persistência."""
        try:
            self.cases = self.persistence.load_cases()
            print(f"Base de casos carregada: {len(self.cases)} casos.")
        except FileNotFoundError:
            print(f"Arquivo de casos não encontrado: {self.persistence.file_path}")
            print("Iniciando com base vazia.")
            self.cases = []
        except Exception as e:
            print(f"Erro ao carregar casos: {e}")
            self.cases = []
    
    def save(self) -> bool:
        """
        Salva a base de casos atual.
        
        Returns:
            True se salvamento bem-sucedido, False caso contrário.
        """
        return self.persistence.save_cases(self.cases)
    
    def add_case(self, case: Case) -> bool:
        """
        Adiciona um novo caso à base.
        
        Args:
            case: Caso a ser adicionado.
            
        Returns:
            True se adição bem-sucedida, False caso contrário.
        """
        # Verifica se o ID já existe
        if any(c.id == case.id for c in self.cases):
            print(f"ID {case.id} já existe. Gerando novo ID.")
            case.id = self.persistence.get_next_id()
        
        self.cases.append(case)
        return self.persistence.append_case(case)
    
    def add_case_from_input(self, patient_case: Case, diagnostico: str, 
                            tratamento: str) -> Case:
        """
        Adiciona um novo caso baseado na entrada de um paciente.
        
        Args:
            patient_case: Caso com os sintomas do paciente.
            diagnostico: Diagnóstico confirmado.
            tratamento: Tratamento prescrito.
            
        Returns:
            Novo caso criado.
        """
        new_case = Case(
            id=self.persistence.get_next_id(),
            sintomas=patient_case.sintomas.copy(),
            diagnostico=diagnostico,
            tratamento=tratamento
        )
        
        if self.add_case(new_case):
            print(f"Novo caso adicionado com ID: {new_case.id}")
            return new_case
        else:
            print("Erro ao adicionar novo caso.")
            return None
    
    def update_case(self, case_id: int, updated_case: Case) -> bool:
        """
        Atualiza um caso existente.
        
        Args:
            case_id: ID do caso a ser atualizado.
            updated_case: Caso com os novos dados.
            
        Returns:
            True se atualização bem-sucedida, False caso contrário.
        """
        if self.persistence.update_case(case_id, updated_case):
            # Atualiza na lista local
            for i, case in enumerate(self.cases):
                if case.id == case_id:
                    self.cases[i] = updated_case
                    break
            return True
        return False
    
    def get_all_cases(self) -> List[Case]:
        """
        Retorna todos os casos da base.
        
        Returns:
            Lista de todos os casos.
        """
        return self.cases.copy()
    
    def get_case_by_id(self, case_id: int) -> Optional[Case]:
        """
        Retorna um caso específico pelo ID.
        
        Args:
            case_id: ID do caso.
            
        Returns:
            Caso encontrado ou None.
        """
        for case in self.cases:
            if case.id == case_id:
                return case
        return None
    
    def get_cases_by_diagnosis(self, diagnosis: str) -> List[Case]:
        """
        Retorna todos os casos com um diagnóstico específico.
        
        Args:
            diagnosis: Diagnóstico a ser buscado.
            
        Returns:
            Lista de casos com o diagnóstico especificado.
        """
        return [case for case in self.cases 
                if case.diagnostico.lower() == diagnosis.lower()]
    
    def get_case_count(self) -> int:
        """
        Retorna o número total de casos.
        
        Returns:
            Número de casos.
        """
        return len(self.cases)
    
    def get_statistics(self) -> dict:
        """
        Retorna estatísticas sobre a base de casos.
        
        Returns:
            Dicionário com estatísticas da base.
        """
        stats = {
            "total_cases": len(self.cases),
            "diagnoses": {}
        }
        
        for case in self.cases:
            diag = case.diagnostico
            if diag not in stats["diagnoses"]:
                stats["diagnoses"][diag] = 0
            stats["diagnoses"][diag] += 1
        
        return stats
    
    def __iter__(self):
        """Permite iterar sobre os casos."""
        return iter(self.cases)
    
    def __len__(self):
        """Retorna o número de casos."""
        return len(self.cases)