"""
Mecanismo de Inferência para o Sistema de Perguntas e Respostas.

Este módulo implementa o mecanismo de inferência baseado em eliminação
de hipóteses, filtrando progressivamente as artistas incompatíveis
com as respostas fornecidas pelo usuário.
"""

from typing import Dict, List, Any, Optional, Tuple
from questions import GerenciadorPerguntas


class MecanismoInferencia:
    """
    Classe responsável pelo mecanismo de inferência do sistema.
    
    Implementa um algoritmo de eliminação de hipóteses baseado em
    filtragem progressiva, onde cada resposta do usuário elimina
    as artistas incompatíveis com aquela característica.
    """
    
    def __init__(
        self, 
        artistas: List[Dict[str, Any]], 
        atributos: List[str]
    ) -> None:
        """
        Inicializa o mecanismo de inferência.
        
        Args:
            artistas: Lista de todas as artistas possíveis.
            atributos: Lista de todos os atributos disponíveis.
        """
        self.todas_artistas = artistas
        self.atributos = atributos
        
        # Conjunto atual de hipóteses (artistas candidatas)
        self.hipoteses_atuais = artistas.copy()
        
        # Gerenciador de perguntas
        self.gerenciador_perguntas = GerenciadorPerguntas(atributos)
        
        # Histórico de perguntas e respostas
        self.historico: List[Dict[str, Any]] = []
        
        # Contador de perguntas
        self.numero_perguntas = 0
        
        # Limite máximo de perguntas
        self.limite_perguntas = len(atributos)
    
    def resetar(self) -> None:
        """Reseta o mecanismo de inferência para o estado initial."""
        self.hipoteses_atuais = self.todas_artistas.copy()
        self.gerenciador_perguntas.resetar()
        self.historico.clear()
        self.numero_perguntas = 0
    
    def obter_proxima_pergunta(self) -> Tuple[Optional[str], Optional[float]]:
        """
        Seleciona a próxima pergunta a ser feita.
        
        Returns:
            Tupla contendo (atributo, ganho_informacao) ou (None, None)
            se não houver mais perguntas ou se já foi encontrada a resposta.
        """
        # Verifica se já temos uma resposta definitiva
        if len(self.hipoteses_atuais) == 1:
            return (None, None)
        
        # Verifica se não há mais hipóteses
        if len(self.hipoteses_atuais) == 0:
            return (None, None)
        
        # Verifica se atingiu o limite de perguntas
        if self.numero_perguntas >= self.limite_perguntas:
            return (None, None)
        
        # Seleciona a melhor pergunta
        atributo, ganho = self.gerenciador_perguntas.selecionar_melhor_pergunta(
            self.hipoteses_atuais
        )
        
        return (atributo, ganho)
    
    def processar_resposta(
        self, 
        atributo: str, 
        resposta: str
    ) -> List[str]:
        """
        Processa a resposta do usuário e filtra as hipóteses.
        
        Args:
            atributo: Nome do atributo perguntado.
            resposta: Resposta do usuário ("sim", "nao", "nao_sei").
            
        Returns:
            Lista de nomes das artistas eliminadas nesta rodada.
        """
        self.numero_perguntas += 1
        self.gerenciador_perguntas.marcar_pergunta_feita(atributo)
        
        eliminadas = []
        novas_hipoteses = []
        
        if resposta == "sim":
            # Mantém apenas artistas onde o atributo é True
            for artista in self.hipoteses_atuais:
                if artista.get(atributo) is True:
                    novas_hipoteses.append(artista)
                else:
                    eliminadas.append(artista["nome"])
                    
        elif resposta == "nao":
            # Mantém apenas artistas onde o atributo é False
            for artista in self.hipoteses_atuais:
                if artista.get(atributo) is False:
                    novas_hipoteses.append(artista)
                else:
                    eliminadas.append(artista["nome"])
                    
        elif resposta == "nao_sei":
            # Não elimina nenhuma artista, mas registra a informação
            novas_hipoteses = self.hipoteses_atuais.copy()
        
        # Registra no histórico
        self.historico.append({
            "pergunta": atributo,
            "resposta": resposta,
            "hipoteses_antes": len(self.hipoteses_atuais),
            "hipoteses_depois": len(novas_hipoteses),
            "eliminadas": eliminadas
        })
        
        # Atualiza as hipóteses
        self.hipoteses_atuais = novas_hipoteses
        
        return eliminadas
    
    def obter_hipoteses_atuais(self) -> List[str]:
        """
        Retorna a lista de hipóteses atuais (nomes das artistas).
        
        Returns:
            Lista de nomes das artistas ainda consideradas possíveis.
        """
        return [a["nome"] for a in self.hipoteses_atuais]
    
    def obter_hipoteses_completas(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista completa de hipóteses atuais.
        
        Returns:
            Lista de dicionários das artistas ainda consideradas possíveis.
        """
        return self.hipoteses_atuais.copy()
    
    def obter_resultado(self) -> Optional[Dict[str, Any]]:
        """
        Retorna o resultado final da inferência.
        
        Returns:
            Dicionário da artista identificada, ou None se não foi possível
            identificar com certeza.
        """
        if len(self.hipoteses_atuais) == 1:
            return self.hipoteses_atuais[0]
        elif len(self.hipoteses_atuais) > 1:
            # Retorna a primeira como "mais provável" (empate técnico)
            return self.hipoteses_atuais[0]
        return None
    
    def obter_explicacao(self) -> str:
        """
        Gera uma explicação detalhada do processo de inferência.
        
        Returns:
            String contendo a explicação do raciocínio utilizado.
        """
        if not self.historico:
            return "Nenhuma pergunta foi realizada."
        
        explicacao = "Processo de Inferência:\n"
        explicacao += "-" * 40 + "\n"
        
        for i, registro in enumerate(self.historico, 1):
            from utils import obter_nome_atributo_pergunta
            pergunta = obter_nome_atributo_pergunta(registro["pergunta"])
            resposta = registro["resposta"]
            
            if resposta == "sim":
                resp_formatada = "SIM"
            elif resposta == "nao":
                resp_formatada = "NÃO"
            else:
                resp_formatada = "NÃO SEI"
            
            explicacao += f"{i}. {pergunta}\n"
            explicacao += f"   Resposta: {resp_formatada}\n"
            explicacao += f"   Hipóteses antes: {registro['hipoteses_antes']}\n"
            explicacao += f"   Hipóteses depois: {registro['hipoteses_depois']}\n"
            
            if registro["eliminadas"]:
                eliminadas_str = ", ".join(registro["eliminadas"])
                explicacao += f"   Eliminadas: {eliminadas_str}\n"
            
            explicacao += "\n"
        
        return explicacao
    
    def obter_estatisticas(self) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre o processo de inferência.
        
        Returns:
            Dicionário contendo estatísticas do processo.
        """
        total_inicial = len(self.todas_artistas)
        total_final = len(self.hipoteses_atuais)
        hipoteses_eliminas = total_inicial - total_final
        taxa_reducao = (hipoteses_eliminas / total_inicial * 100) if total_inicial > 0 else 0
        
        return {
            "total_inicial": total_inicial,
            "total_final": total_final,
            "hipoteses_eliminas": hipoteses_eliminas,
            "taxa_reducao": round(taxa_reducao, 2),
            "perguntas_realizadas": self.numero_perguntas,
            "sucesso": total_final == 1
        }
    
    def total_hipoteses(self) -> int:
        """
        Retorna o número atual de hipóteses.
        
        Returns:
            Número de artistas ainda consideradas possíveis.
        """
        return len(self.hipoteses_atuais)
    
    def ha_certeza(self) -> bool:
        """
        Verifica se há certeza sobre a artista identificada.
        
        Returns:
            True se restar apenas uma hipótese, False caso contrário.
        """
        return len(self.hipoteses_atuais) == 1
    
    def obter_candidatas_restantes(self) -> List[str]:
        """
        Retorna a lista de candidatas restantes.
        
        Returns:
            Lista de nomes das artistas ainda possíveis.
        """
        return [a["nome"] for a in self.hipoteses_atuais]