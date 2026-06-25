"""
Módulo de gerenciamento de perguntas para o sistema de inferência.

Este módulo é responsável por selecionar a melhor pergunta a ser feita
com base no conjunto atual de hipóteses, maximizando a eliminação de
candidatas incompatíveis.
"""

from typing import Dict, List, Any, Tuple, Set
from collections import Counter


class GerenciadorPerguntas:
    """
    Classe responsável por gerenciar as perguntas do sistema.
    
    Esta classe implementa uma estratégia de seleção de perguntas baseada
    no ganho de informação, selecionando o atributo que melhor divide o
    conjunto atual de hipóteses.
    """
    
    def __init__(self, atributos: List[str]) -> None:
        """
        Inicializa o gerenciador de perguntas.
        
        Args:
            atributos: Lista de todos os atributos disponíveis.
        """
        self.atributos = atributos
        self.perguntas_feitas: Set[str] = set()
    
    def resetar(self) -> None:
        """Reseta o estado do gerenciador, limpando as perguntas já feitas."""
        self.perguntas_feitas.clear()
    
    def calcular_entropia(
        self, 
        artistas: List[Dict[str, Any]], 
        atributo: str
    ) -> float:
        """
        Calcula a entropia de um atributo para um conjunto de artistas.
        
        A entropia mede o quão bem um atributo divide o conjunto de artistas.
        Quanto mais próximo de 0.5 a proporção entre verdadeiro/falso, menor
        a entropia e melhor o atributo para dividir o conjunto.
        
        Args:
            artistas: Lista de dicionários representando as artistas.
            atributo: Nome do atributo a ser avaliado.
            
        Returns:
            Valor da entropia (quanto menor, melhor para divisão).
        """
        if not artistas:
            return float('inf')
        
        # Conta quantas artistas têm o atributo como True ou False
        contador = Counter()
        total = len(artistas)
        
        for artista in artistas:
            valor = artista.get(atributo)
            if valor is True:
                contador['verdadeiro'] += 1
            elif valor is False:
                contador['falso'] += 1
            # None ou valores desconhecidos não são contados
        
        total_validos = contador['verdadeiro'] + contador['falso']
        
        if total_validos == 0:
            return float('inf')
        
        # Calcula a proporção
        prop_verdadeiro = contador['verdadeiro'] / total_validos
        prop_falso = contador['falso'] / total_validos
        
        # Entropia de Shannon (simplificada para binary split)
        # Quanto mais próximo de 0.5 cada proporção, menor a entropia
        # Usamos uma fórmula que favorece divisões equilibradas
        if prop_verdadeiro == 0 or prop_falso == 0:
            return float('inf')  # Não divide nada
        
        # Calcula o índice de Gini como medida de qualidade
        gini = 1 - (prop_verdadeiro ** 2 + prop_falso ** 2)
        
        return gini
    
    def calcular_ganho_informacao(
        self,
        artistas: List[Dict[str, Any]],
        atributo: str
    ) -> float:
        """
        Calcula o ganho de informação de um atributo.
        
        O ganho de informação mede o quanto um atributo ajuda a reduzir
        a incerteza sobre qual é a artista correta.
        
        Args:
            artistas: Lista de dicionários representando as artistas.
            atributo: Nome do atributo a ser avaliado.
            
        Returns:
            Valor do ganho de informação (quanto maior, melhor).
        """
        if not artistas:
            return 0.0
        
        # Separa as artistas por valor do atributo
        verdadeiros = [a for a in artistas if a.get(atributo) is True]
        falsos = [a for a in artistas if a.get(atributo) is False]
        
        total = len(artistas)
        total_validos = len(verdadeiros) + len(falsos)
        
        if total_validos == 0:
            return 0.0
        
        # Calcula a entropia antes da divisão (entropia do conjunto total)
        # Para simplificação, consideramos a entropia máxima possível
        entropia_total = 1.0  # Entropia máxima para divisão binária
        
        # Calcula a entropia após a divisão (média ponderada)
        entropia_verdadeiros = self._entropia_conjunto(verdadeiros)
        entropia_falsos = self._entropia_conjunto(falsos)
        
        entropia_ponderada = (
            (len(verdadeiros) / total_validos) * entropia_verdadeiros +
            (len(falsos) / total_validos) * entropia_falsos
        )
        
        # Ganho de informação
        ganho = entropia_total - entropia_ponderada
        
        # Bônus para atributos que eliminam mais candidatas
        # (considerando o pior caso de eliminação)
        min_eliminados = min(len(verdadeiros), len(falsos))
        bonus_eliminacao = min_eliminados / total_validos * 0.5
        
        return ganho + bonus_eliminacao
    
    def _entropia_conjunto(self, artistas: List[Dict[str, Any]]) -> float:
        """
        Calcula a entropia de um conjunto de artistas baseada na diversidade.
        
        Args:
            artistas: Lista de dicionários representando as artistas.
            
        Returns:
            Valor da entropia do conjunto.
        """
        if len(artistas) <= 1:
            return 0.0
        
        # Entropia baseada no tamanho do conjunto (quanto maior, maior a entropia)
        import math
        n = len(artistas)
        # Normaliza pela entropia máxima possível
        entropia_max = math.log2(n) if n > 1 else 1
        return entropia_max
    
    def selecionar_melhor_pergunta(
        self,
        artistas: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """
        Seleciona a melhor pergunta para fazer com base no conjunto atual.
        
        A melhor pergunta é aquela que maximiza o ganho de informação,
        ou seja, que melhor divide o conjunto de artistas em grupos
        distintos.
        
        Args:
            artistas: Lista de dicionários representando as artistas candidatas.
            
        Returns:
            Tupla contendo (nome_do_atributo, ganho_informacao).
            Retorna (None, 0) se não houver perguntas disponíveis.
        """
        if not artistas or len(artistas) <= 1:
            return (None, 0.0)
        
        # Atributos disponíveis (não feitos ainda)
        atributos_disponiveis = [
            a for a in self.atributos 
            if a not in self.perguntas_feitas
        ]
        
        if not atributos_disponiveis:
            return (None, 0.0)
        
        melhor_atributo = None
        melhor_ganho = -1.0
        
        for atributo in atributos_disponiveis:
            # Verifica se o atributo tem valores válidos para as artistas
            valores = [a.get(atributo) for a in artistas]
            verdadeiros = sum(1 for v in valores if v is True)
            falsos = sum(1 for v in valores if v is False)
            
            # Pula atributos que não dividem o conjunto
            if verdadeiros == 0 or falsos == 0:
                continue
            
            ganho = self.calcular_ganho_informacao(artistas, atributo)
            
            if ganho > melhor_ganho:
                melhor_ganho = ganho
                melhor_atributo = atributo
        
        # Se nenhum atributo divide bem, seleciona o primeiro disponível
        if melhor_atributo is None and atributos_disponiveis:
            melhor_atributo = atributos_disponiveis[0]
            melhor_ganho = 0.0
        
        return (melhor_atributo, melhor_ganho)
    
    def marcar_pergunta_feita(self, atributo: str) -> None:
        """
        Marca uma pergunta como já feita.
        
        Args:
            atributo: Nome do atributo da pergunta feita.
        """
        self.perguntas_feitas.add(atributo)
    
    def obter_perguntas_restantes(self) -> List[str]:
        """
        Retorna a lista de perguntas ainda não feitas.
        
        Returns:
            Lista de nomes de atributos ainda não perguntados.
        """
        return [a for a in self.atributos if a not in self.perguntas_feitas]
    
    def total_perguntas_feitas(self) -> int:
        """
        Retorna o total de perguntas já feitas.
        
        Returns:
            Número de perguntas feitas.
        """
        return len(self.perguntas_feitas)