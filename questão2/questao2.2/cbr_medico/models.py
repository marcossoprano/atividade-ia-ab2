"""
Módulo models.py - Definição das classes do sistema CBR médico.

Este módulo contém as classes fundamentais para representação dos casos
e estruturas de dados utilizadas no sistema de diagnóstico.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json


@dataclass
class Case:
    """
    Representa um caso médico no sistema CBR.
    
    Attributes:
        id: Identificador único do caso.
        sintomas: Dicionário contendo os sintomas e seus valores (True/False).
        diagnostico: Diagnóstico médico associado ao caso.
        tratamento: Tratamento recomendado para o diagnóstico.
    """
    id: int
    sintomas: Dict[str, bool]
    diagnostico: str
    tratamento: str
    
    def to_dict(self) -> dict:
        """
        Converte o caso para um dicionário JSON serializável.
        
        Returns:
            Dicionário com todos os atributos do caso.
        """
        case_dict = {
            "id": self.id,
            "diagnostico": self.diagnostico,
            "tratamento": self.tratamento
        }
        # Adiciona os sintomas ao dicionário
        case_dict.update(self.sintomas)
        return case_dict
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Case':
        """
        Cria uma instância de Case a partir de um dicionário.
        
        Args:
            data: Dicionário contendo os dados do caso.
            
        Returns:
            Instância de Case.
        """
        # Lista de sintomas conhecidos
        sintoma_keys = [
            'febre', 'tosse', 'dor_garganta', 'dor_muscular', 'coriza',
            'dor_cabeca', 'fadiga', 'congestao_nasal', 'falta_ar', 'nausea'
        ]
        
        sintomas = {}
        for key in sintoma_keys:
            sintomas[key] = data.get(key, False)
        
        return cls(
            id=data["id"],
            sintomas=sintomas,
            diagnostico=data["diagnostico"],
            tratamento=data["tratamento"]
        )
    
    def get_sintoma(self, nome: str) -> bool:
        """
        Obtém o valor de um sintoma específico.
        
        Args:
            nome: Nome do sintoma.
            
        Returns:
            Valor booleano do sintoma, ou False se não existir.
        """
        return self.sintomas.get(nome, False)
    
    def set_sintoma(self, nome: str, valor: bool) -> None:
        """
        Define o valor de um sintoma.
        
        Args:
            nome: Nome do sintoma.
            valor: Valor booleano do sintoma.
        """
        self.sintomas[nome] = valor
    
    def __str__(self) -> str:
        """Retorna uma representação em string do caso."""
        sintomas_str = ", ".join(
            [f"{k}: {'Sim' if v else 'Não'}" for k, v in self.sintomas.items()]
        )
        return f"Case {self.id}: {self.diagnostico} [{sintomas_str}]"


@dataclass
class MatchResult:
    """
    Representa o resultado de uma correspondência entre casos.
    
    Attributes:
        case: Caso correspondente.
        similaridade: Percentual de similaridade (0-100).
    """
    case: Case
    similaridade: float
    
    def __str__(self) -> str:
        """Retorna uma representação em string do resultado."""
        return f"{self.case.diagnostico} - Similaridade: {self.similaridade:.1f}%"


@dataclass
class PatientInput:
    """
    Representa os sintomas informados por um paciente.
    
    Attributes:
        sintomas: Dicionário contendo os sintomas informados.
    """
    sintomas: Dict[str, bool] = field(default_factory=dict)
    
    def set_sintoma(self, nome: str, valor: bool) -> None:
        """
        Define o valor de um sintoma informado pelo paciente.
        
        Args:
            nome: Nome do sintoma.
            valor: Valor booleano do sintoma.
        """
        self.sintomas[nome] = valor
    
    def get_sintoma(self, nome: str) -> bool:
        """
        Obtém o valor de um sintoma informado.
        
        Args:
            nome: Nome do sintoma.
            
        Returns:
            Valor booleano do sintoma, ou False se não existir.
        """
        return self.sintomas.get(nome, False)
    
    def to_case(self, case_id: int = -1) -> Case:
        """
        Converte a entrada do paciente em um objeto Case.
        
        Args:
            case_id: ID para o novo caso (padrão: -1 para casos temporários).
            
        Returns:
            Objeto Case com os sintomas do paciente.
        """
        return Case(
            id=case_id,
            sintomas=self.sintomas.copy(),
            diagnostico="",
            tratamento=""
        )