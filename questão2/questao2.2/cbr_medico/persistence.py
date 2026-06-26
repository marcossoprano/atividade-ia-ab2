"""
Módulo persistence.py - Gerenciamento de persistência de dados.

Este módulo é responsável por carregar e salvar casos médicos
em arquivo JSON, garantindo a persistência da base de casos.
"""

import json
import os
from typing import List, Dict, Any

from models import Case


class PersistenceManager:
    """
    Gerencia operações de persistência para a base de casos.
    
    Esta classe fornece métodos para carregar, salvar e gerenciar
    casos médicos em arquivos JSON.
    """
    
    DEFAULT_FILE_PATH: str = "casos.json"
    
    def __init__(self, file_path: str = None):
        """
        Inicializa o gerenciador de persistência.
        
        Args:
            file_path: Caminho para o arquivo JSON. Se None, usa o padrão.
        """
        self.file_path = file_path or self.DEFAULT_FILE_PATH
    
    def load_cases(self) -> List[Case]:
        """
        Carrega casos do arquivo JSON.
        
        Returns:
            Lista de objetos Case carregados do arquivo.
            
        Raises:
            FileNotFoundError: Se o arquivo não existir.
            json.JSONDecodeError: Se o arquivo estiver corrompido.
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.file_path}")
        
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        cases = []
        if isinstance(data, list):
            for case_data in data:
                try:
                    case = Case.from_dict(case_data)
                    cases.append(case)
                except (KeyError, TypeError) as e:
                    print(f"Aviso: Caso inválido ignorado: {e}")
        
        return cases
    
    def save_cases(self, cases: List[Case]) -> bool:
        """
        Salva uma lista de casos no arquivo JSON.
        
        Args:
            cases: Lista de objetos Case para salvar.
            
        Returns:
            True se salvamento bem-sucedido, False caso contrário.
        """
        try:
            data = [case.to_dict() for case in cases]
            
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
            
            return True
        except IOError as e:
            print(f"Erro ao salvar casos: {e}")
            return False
    
    def append_case(self, case: Case) -> bool:
        """
        Adiciona um novo caso ao arquivo existente.
        
        Args:
            case: Objeto Case para adicionar.
            
        Returns:
            True se adição bem-sucedida, False caso contrário.
        """
        try:
            # Carrega casos existentes
            cases = self.load_cases()
            
            # Adiciona novo caso
            cases.append(case)
            
            # Salva todos os casos
            return self.save_cases(cases)
        except FileNotFoundError:
            # Se arquivo não existe, cria com o novo caso
            return self.save_cases([case])
        except Exception as e:
            print(f"Erro ao adicionar caso: {e}")
            return False
    
    def update_case(self, case_id: int, updated_case: Case) -> bool:
        """
        Atualiza um caso existente.
        
        Args:
            case_id: ID do caso a ser atualizado.
            updated_case: Caso com os novos dados.
            
        Returns:
            True se atualização bem-sucedida, False caso contrário.
        """
        try:
            cases = self.load_cases()
            
            for i, case in enumerate(cases):
                if case.id == case_id:
                    cases[i] = updated_case
                    return self.save_cases(cases)
            
            print(f"Caso com ID {case_id} não encontrado.")
            return False
        except Exception as e:
            print(f"Erro ao atualizar caso: {e}")
            return False
    
    def get_next_id(self) -> int:
        """
        Obtém o próximo ID disponível para um novo caso.
        
        Returns:
            Próximo ID disponível.
        """
        try:
            cases = self.load_cases()
            if not cases:
                return 1
            return max(case.id for case in cases) + 1
        except FileNotFoundError:
            return 1
        except Exception:
            return 1
    
    def file_exists(self) -> bool:
        """
        Verifica se o arquivo de casos existe.
        
        Returns:
            True se o arquivo existe, False caso contrário.
        """
        return os.path.exists(self.file_path)
    
    def get_case_count(self) -> int:
        """
        Retorna o número de casos no arquivo.
        
        Returns:
            Número de casos.
        """
        try:
            cases = self.load_cases()
            return len(cases)
        except Exception:
            return 0