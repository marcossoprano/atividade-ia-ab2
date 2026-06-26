"""
Módulo de utilitários para o sistema de perguntas e respostas.

Este módulo contém funções auxiliares para operações comuns como
carregamento de dados, formatação de saída e cálculos estatísticos.
"""

import json
from typing import Dict, List, Any, Optional


def carregar_base_conhecimento(caminho: str = "knowledge_base.json") -> Dict[str, Any]:
    """
    Carrega a base de conhecimento a partir de um arquivo JSON.
    
    Args:
        caminho: Caminho para o arquivo JSON da base de conhecimento.
        
    Returns:
        Dicionário contendo os dados da base de conhecimento.
        
    Raises:
        FileNotFoundError: Se o arquivo não for encontrado.
        json.JSONDecodeError: Se o arquivo não for um JSON válido.
    """
    try:
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho}' não encontrado.")
        raise
    except json.JSONDecodeError as e:
        print(f"Erro ao parsear JSON: {e}")
        raise


def obter_lista_artistas(base_conhecimento: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrai a lista de artistas da base de conhecimento.
    
    Args:
        base_conhecimento: Dicionário contendo a base de conhecimento.
        
    Returns:
        Lista de dicionários, onde cada dicionário representa uma artista.
    """
    return base_conhecimento.get("artistas", [])


def obter_lista_atributos(base_conhecimento: Dict[str, Any]) -> List[str]:
    """
    Extrai a lista de atributos da base de conhecimento.
    
    Args:
        base_conhecimento: Dicionário contendo a base de conhecimento.
        
    Returns:
        Lista de strings com os nomes dos atributos.
    """
    return base_conhecimento.get("atributos", [])


def formatar_saida(mensagem: str, estilo: str = "normal") -> str:
    """
    Formata uma mensagem para exibição no terminal.
    
    Args:
        mensagem: A mensagem a ser formatada.
        estilo: O estilo de formatação ("normal", "destaque", "sucesso", "erro").
        
    Returns:
        String formatada com códigos ANSI apropriados.
    """
    cores = {
        "normal": "\033[0m",
        "destaque": "\033[1;36m",  # Ciano em negrito
        "sucesso": "\033[1;32m",   # Verde em negrito
        "erro": "\033[1;31m",      # Vermelho em negrito
        "info": "\033[1;34m",      # Azul em negrito
        "amarelo": "\033[1;33m",   # Amarelo em negrito
    }
    
    cor = cores.get(estilo, cores["normal"])
    reset = "\033[0m"
    
    return f"{cor}{mensagem}{reset}"


def limpar_terminal() -> None:
    """Limpa a tela do terminal (funciona em Windows e Unix)."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def calcular_estatisticas(
    total_inicial: int,
    total_final: int,
    perguntas_realizadas: int
) -> Dict[str, Any]:
    """
    Calcula estatísticas sobre o processo de inferência.
    
    Args:
        total_inicial: Número inicial de hipóteses (artistas).
        total_final: Número final de hipóteses restantes.
        perguntas_realizadas: Quantidade de perguntas feitas.
        
    Returns:
        Dicionário com as estatísticas calculadas.
    """
    hipoteses_eliminas = total_inicial - total_final
    taxa_reducao = (hipoteses_eliminas / total_inicial * 100) if total_inicial > 0 else 0
    
    return {
        "total_inicial": total_inicial,
        "total_final": total_final,
        "hipoteses_eliminas": hipoteses_eliminas,
        "taxa_reducao": round(taxa_reducao, 2),
        "perguntas_realizadas": perguntas_realizadas
    }


def validar_resposta(resposta: str) -> Optional[str]:
    """
    Valida e normaliza a resposta do usuário.
    
    Args:
        resposta: A resposta fornecida pelo usuário.
        
    Returns:
        Resposta normalizada ("sim", "nao", "nao_sei") ou None se inválida.
    """
    resposta = resposta.strip().lower()
    
    # Mapeamento de respostas válidas
    mapeamento = {
        "sim": "sim",
        "s": "sim",
        "nao": "nao",
        "não": "nao",
        "n": "nao",
        "nao_sei": "nao_sei",
        "não_sei": "nao_sei",
        "?": "nao_sei",
        "nao sei": "nao_sei",
        "não sei": "nao_sei",
    }
    
    return mapeamento.get(resposta)


def obter_nome_atributo_pergunta(atributo: str) -> str:
    """
    Converte o nome interno do atributo para uma pergunta legível.
    
    Args:
        atributo: Nome interno do atributo (ex: "americana").
        
    Returns:
        Pergunta formatada (ex: "Ela é norte-americana?").
    """
    perguntas = {
        "americana": "Ela é norte-americana?",
        "ativa_atualmente": "Ela está em atividade atualmente?",
        "grammy": "Ela possui Grammy?",
        "atuou_filmes": "Ela já atuou em filmes?",
        "atriz": "Ela também é atriz?",
        "carreira_antes_2010": "Ela começou a carreira antes de 2010?",
        "country": "Ela é conhecida por música country?",
        "latina": "Ela é conhecida por música latina?",
        "ascendencia_latina": "Ela possui ascendência latina?",
        "super_bowl": "Ela já participou do Super Bowl?",
        "geracao_z": "Ela é considerada uma artista da geração Z?",
        "carreira_mais_10_anos": "Ela possui mais de 10 anos de carreira?",
        "compositora": "Ela é compositora das próprias músicas?",
        "turne_mundial_recente": "Ela possui turnê mundial recente?",
        "instagram_100mi": "Ela tem mais de 100 milhões de seguidores no Instagram?",
        "performances_extravagantes": "Ela é conhecida por performances extravagantes?",
        "baladas_romanticas": "Ela é conhecida por baladas românticas?",
        "grupo_musical_antes": "Ela já integrou grupo musical antes da carreira solo?",
        "oscar": "Ela possui Oscar?",
        "album_2024_ou_posterior": "Ela possui álbum lançado em 2024 ou posteriormente?",
    }
    
    return perguntas.get(atributo, f"atributo {atributo}?")


def exibir_cabecalho() -> None:
    """Exibe o cabeçalho inicial do programa."""
    print(formatar_saida("=" * 60, "destaque"))
    print(formatar_saida("    SISTEMA INTELIGENTE DE PERGUNTAS E RESPOSTAS", "destaque"))
    print(formatar_saida("         Inspirado no Akinator - Divas Pop", "destaque"))
    print(formatar_saida("=" * 60, "destaque"))
    print()


def exibir_rodape() -> None:
    """Exibe o rodapé do programa."""
    print()
    print(formatar_saida("=" * 60, "destaque"))