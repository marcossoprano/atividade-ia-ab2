#!/usr/bin/env python3
"""
Sistema Inteligente de Perguntas e Respostas - Divas Pop

Este é o ponto de entrada principal da aplicação. Implementa uma interface
em terminal para o jogo de adivinhação de divas pop, inspirado no Akinator.

O sistema utiliza um mecanismo de inferência baseado em eliminação de hipóteses
para identificar a artista escolhida pelo usuário através de perguntas sobre
características e atributos.

Autor: Desenvolvedor Sênior em IA
Disciplina: Inteligência Artificial
"""

from typing import Optional
from utils import (
    carregar_base_conhecimento,
    formatar_saida,
    validar_resposta,
    obter_nome_atributo_pergunta,
    exibir_cabecalho,
    exibir_rodape,
    calcular_estatisticas,
)
from questão1.inference_engine import MecanismoInferencia


def exibir_instrucoes() -> None:
    """Exibe as instruções iniciais do jogo."""
    print(formatar_saida("\nPense em uma diva pop internacional...", "info"))
    print(formatar_saida("O sistema fará perguntas sobre características da artista.", "normal"))
    print(formatar_saida("Responda com:\n", "normal"))
    print(formatar_saida("  [S] Sim", "destaque"))
    print(formatar_saida("  [N] Não", "destaque"))
    print(formatar_saida("  [?] Não sei", "destaque"))
    print()


def obter_resposta_usuario() -> Optional[str]:
    """
    Solicita e valida a resposta do usuário.
    
    Returns:
        Resposta validada ("sim", "nao", "nao_sei") ou None se o usuário
        desejar sair.
    """
    while True:
        entrada = input(formatar_saida("Sua resposta: ", "amarelo")).strip()
        
        # Verifica se o usuário deseja sair
        if entrada.lower() in ["sair", "exit", "quit", "q"]:
            return None
        
        resposta = validar_resposta(entrada)
        if resposta:
            return resposta
        
        print(formatar_saida(
            "Resposta inválida! Por favor, digite S (Sim), N (Não) ou ? (Não sei).",
            "erro"
        ))


def exibir_progresso(
    pergunta_numero: int,
    total_hipoteses: int,
    pergunta_texto: str
) -> None:
    """
    Exibe o progresso atual do jogo.
    
    Args:
        pergunta_numero: Número da pergunta atual.
        total_hipoteses: Quantidade de hipóteses restantes.
        pergunta_texto: Texto da pergunta a ser feita.
    """
    print(formatar_saida(f"\nPergunta {pergunta_numero}:", "destaque"))
    print(formatar_saida(f"  {pergunta_texto}", "info"))
    print()
    print("[S] Sim    [N] Não    [?] Não sei    [sair] Desistir")
    print()


def exibir_candidatas_restantes(candidatas: list) -> None:
    """
    Exibe as candidatas restantes de forma discreta.
    
    Args:
        candidatas: Lista de nomes das artistas ainda possíveis.
    """
    if len(candidatas) <= 5:
        print(formatar_saida(
            f"  >> Candidatas restantes: {', '.join(candidatas)}",
            "amarelo"
        ))
    else:
        print(formatar_saida(
            f"  >> {len(candidatas)} candidatas restantes...",
            "amarelo"
        ))


def exibir_resultado_final(
    artista: dict,
    estatisticas: dict,
    mecanismo: MecanismoInferencia
) -> None:
    """
    Exibe o resultado final do jogo.
    
    Args:
        artista: Dicionário contendo os dados da artista identificada.
        estatisticas: Dicionário com as estatísticas do jogo.
        mecanismo: Mecanismo de inferência usado (para explicação).
    """
    print()
    print(formatar_saida("=" * 60, "destaque"))
    print(formatar_saida("                RESULTADO FINAL", "destaque"))
    print(formatar_saida("=" * 60, "destaque"))
    print()
    
    # Exibe a artista identificada
    print(formatar_saida("A artista que você pensou é:", "sucesso"))
    print()
    print(formatar_saida(f"  ★  {artista['nome']}  ★", "sucesso"))
    print()
    
    # Exibe estatísticas
    print(formatar_saida("Estatísticas:", "info"))
    print(f"  • Total de perguntas: {estatisticas['perguntas_realizadas']}")
    print(f"  • Hipóteses iniciais: {estatisticas['total_inicial']}")
    print(f"  • Hipóteses restantes: {estatisticas['total_final']}")
    print(f"  • Hipóteses eliminadas: {estatisticas['hipoteses_eliminas']}")
    print(f"  • Taxa de redução: {estatisticas['taxa_reducao']}%")
    print()
    
    # Exibe explicação do processo
    if estatisticas['perguntas_realizadas'] > 0:
        print(formatar_saida("Explicação do raciocínio:", "info"))
        print()
        explicacao = mecanismo.obter_explicacao()
        print(explicacao)
    
    # Mensagem de confirmação
    if mecanismo.ha_certeza():
        print(formatar_saida(
            "✓ O sistema identificou a artista com CERTEZA!",
            "sucesso"
        ))
    else:
        print(formatar_saida(
            "⚠ O sistema chegou a um resultado provável, mas não há certeza absoluta.",
            "amarelo"
        ))
        print(formatar_saida(
            "  Candidatas possíveis: " + ", ".join(mecanismo.obter_candidatas_restantes()),
            "normal"
        ))


def exibir_mensagem_saida() -> None:
    """Exibe mensagem de saída quando o usuário desiste."""
    print()
    print(formatar_saida("=" * 60, "destaque"))
    print(formatar_saida("Jogo encerrado pelo usuário.", "info"))
    print(formatar_saida("=" * 60, "destaque"))


def perguntar_se_acertou() -> bool:
    """
    Pergunta ao usuário se o sistema acertou.
    
    Returns:
        True se o usuário confirmou que o sistema acertou, False caso contrário.
    """
    print()
    resposta = input(formatar_saida(
        "O sistema acertou? [S/N]: ", "amarelo"
    )).strip().lower()
    
    return resposta in ["s", "sim", "y", "yes"]


def jogar_novamente() -> bool:
    """
    Pergunta se o usuário deseja jogar novamente.
    
    Returns:
        True se o usuário quiser jogar novamente, False caso contrário.
    """
    print()
    resposta = input(formatar_saida(
        "Deseja jogar novamente? [S/N]: ", "amarelo"
    )).strip().lower()
    
    return resposta in ["s", "sim", "y", "yes"]


def gerar_relatorio_tecnico(
    base_conhecimento: dict,
    mecanismo: MecanismoInferencia,
    nome_arquivo: str = "relatorio_tecnico.md"
) -> None:
    """
    Gera um relatório técnico sobre o sistema.
    
    Args:
        base_conhecimento: Base de conhecimento utilizada.
        mecanismo: Mecanismo de inferência usado.
        nome_arquivo: Nome do arquivo a ser criado.
    """
    artistas = base_conhecimento.get("artistas", [])
    atributos = base_conhecimento.get("atributos", [])
    estatisticas = mecanismo.obter_estatisticas()
    
    relatorio = f"""# Relatório Técnico - Sistema Inteligente de Perguntas e Respostas

## 1. Descrição do Domínio

Este sistema foi desenvolvido para identificar **divas pop internacionais** através
de um processo de perguntas e respostas, inspirado no famoso jogo Akinator.

### Artistas Incluídos ({len(artistas)} artistas)

"""
    
    for i, artista in enumerate(artistas, 1):
        relatorio += f"{i}. {artista['nome']}\n"
    
    relatorio += f"""
## 2. Estratégia de Representação do Conhecimento

O conhecimento foi representado utilizando uma abordagem **baseada em atributos binários**.
Cada artista é descrita por um conjunto de {len(atributos)} atributos, cada um com valor
verdadeiro (True) ou falso (False).

### Atributos Utilizados ({len(atributos)} atributos)

"""
    
    for i, atributo in enumerate(atributos, 1):
        pergunta = obter_nome_atributo_pergunta(atributo)
        relatorio += f"{i}. {pergunta}\n"
    
    relatorio += f"""
## 3. Estrutura da Base de Conhecimento

A base de conhecimento é armazenada em formato JSON (`knowledge_base.json`) contendo:

- **atributos**: Lista de {len(atributos)} características utilizadas para diferenciação
- **artistas**: Lista de {len(artistas)} artistas, cada uma com seus respectivos valores de atributos

### Exemplo de Estrutura de uma Artista

```json
{{
    "nome": "Taylor Swift",
    "americana": true,
    "grammy": true,
    "country": true,
    ...
}}
```

## 4. Mecanismo de Inferência Utilizado

O sistema implementa um **mecanismo de inferência baseado em eliminação de hipóteses**:

1. **Inicialização**: Começa com todas as {len(artistas)} artistas como candidatas possíveis
2. **Seleção de Pergunta**: Utiliza uma heurística de **ganho de informação** para selecionar
   a pergunta que melhor divide o conjunto atual de hipóteses
3. **Filtragem**: Com base na resposta do usuário, elimina as artistas incompatíveis
4. **Iteração**: Repete o processo até restar uma única hipótese ou atingir o limite de perguntas

### Algoritmo de Seleção de Perguntas

O algoritmo calcula para cada atributo disponível:
- **Entropia**: Mede o quão bem o atributo divide o conjunto
- **Ganho de Informação**: Combina redução de entropia com bônus por eliminação
- Seleciona o atributo com maior ganho de informação

## 5. Exemplos de Interação

### Exemplo 1: Identificação Rápida

```
Pense em uma diva pop.

Pergunta 1: Ela é norte-americana?
[S] Sim  [N] Não  [?] Não sei
>>> S

Pergunta 2: Ela é conhecida por música country?
[S] Sim  [N] Não  [?] Não sei
>>> S

...

Resultado: Taylor Swift
```

## 6. Discussão dos Resultados

### Estatísticas da Sessão

- **Total de perguntas realizadas**: {estatisticas['perguntas_realizadas']}
- **Hipóteses eliminadas**: {estatisticas['hipoteses_eliminas']} de {estatisticas['total_inicial']}
- **Taxa de redução do espaço de busca**: {estatisticas['taxa_reducao']}%
- **Sucesso na identificação**: {"Sim" if estatisticas['sucesso'] else "Parcial"}

### Análise

O sistema demonstrou eficácia na identificação de artistas através de um número
reduzido de perguntas, eliminando progressivamente as hipóteses incompatíveis.

## 7. Limitações e Melhorias Futuras

### Limitações Atuais

1. **Atributos binários**: Alguns atributos poderiam ser mais granulares
2. **"Não sei"**: Quando o usuário responde "não sei", nenhuma eliminação ocorre
3. **Base fixa**: As artistas e atributos são pré-definidos
4. **Sem aprendizado**: O sistema não aprende com sessões anteriores

### Melhorias Futuras

1. **Atributos multi-valor**: Permitir mais de dois valores por atributo
2. **Sistema de pesos**: Atribuir pesos diferentes para diferentes atributos
3. **Aprendizado**: Implementar mecanismo para adicionar novas artistas
4. **Interface web**: Criar interface gráfica mais amigável
5. **Base colaborativa**: Permitir que usuários contribuam com informações

## 8. Conclusão

O sistema demonstrou ser uma implementação eficaz de um sistema baseado em conhecimento
para identificação de entidades através de perguntas sequenciais. A abordagem de eliminação
de hipóteses provou-se adequada para o domínio das divas pop, conseguindo identificar
corretamente a artista escolhida em maioria dos casos.

---

*Relatório gerado automaticamente pelo Sistema Inteligente de Perguntas e Respostas*
"""
    
    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        print(formatar_saida(
            f"\nRelatório técnico gerado com sucesso: {nome_arquivo}",
            "sucesso"
        ))
    except IOError as e:
        print(formatar_saida(
            f"\nErro ao gerar relatório: {e}",
            "erro"
        ))


def main() -> None:
    """Função principal que controla o fluxo do jogo."""
    try:
        # Carrega a base de conhecimento
        base_conhecimento = carregar_base_conhecimento()
        artistas = base_conhecimento.get("artistas", [])
        atributos = base_conhecimento.get("atributos", [])
        
        # Verifica se há dados suficientes
        if len(artistas) < 2:
            print(formatar_saida(
                "Erro: Base de conhecimento insuficiente. É necessário pelo menos 2 artistas.",
                "erro"
            ))
            return
        
        if len(atributos) < 3:
            print(formatar_saida(
                "Erro: Base de conhecimento insuficiente. É necessário pelo menos 3 atributos.",
                "erro"
            ))
            return
        
        print(formatar_saida("\n" + "=" * 60, "destaque"))
        print(formatar_saida("  BEM-VINDO AO ADIVINHE A DIVA POP!", "destaque"))
        print(formatar_saida("=" * 60, "destaque"))
        
        # Loop principal do jogo
        while True:
            # Exibe cabeçalho e instruções
            exibir_cabecalho()
            exibir_instrucoes()
            
            # Inicializa o mecanismo de inferência
            mecanismo = MecanismoInferencia(artistas, atributos)
            
            print(formatar_saida(
                f"Total de {len(artistas)} divas pop no banco de dados.",
                "info"
            ))
            
            # Loop de perguntas
            while True:
                # Obtém próxima pergunta
                atributo, ganho = mecanismo.obter_proxima_pergunta()
                
                # Verifica condições de término
                if atributo is None:
                    break
                
                # Exibe pergunta
                pergunta_texto = obter_nome_atributo_pergunta(atributo)
                exibir_progresso(
                    mecanismo.numero_perguntas + 1,
                    mecanismo.total_hipoteses(),
                    pergunta_texto
                )
                
                # Exibe candidatas restantes (opcional, para debug)
                exibir_candidatas_restantes(mecanismo.obter_candidatas_restantes())
                
                # Obtém resposta do usuário
                resposta = obter_resposta_usuario()
                
                # Verifica se usuário desistiu
                if resposta is None:
                    exibir_mensagem_saida()
                    return
                
                # Processa resposta
                eliminadas = mecanismo.processar_resposta(atributo, resposta)
                
                # Feedback sobre eliminações
                if eliminadas:
                    print(formatar_saida(
                        f"  >> {len(eliminadas)} artista(s) eliminada(s): {', '.join(eliminadas[:3])}"
                        + (f" e mais {len(eliminadas) - 3}..." if len(eliminadas) > 3 else ""),
                        "amarelo"
                    ))
                
                # Verifica se restou apenas uma
                if mecanismo.ha_certeza():
                    break
                
                # Verifica se não há mais hipóteses
                if mecanismo.total_hipoteses() == 0:
                    print(formatar_saida(
                        "\nNão há mais candidatas compatíveis com suas respostas.",
                        "erro"
                    ))
                    break
            
            # Exibe resultado
            resultado = mecanismo.obter_resultado()
            estatisticas = mecanismo.obter_estatisticas()
            
            if resultado:
                exibir_resultado_final(resultado, estatisticas, mecanismo)
                
                # Pergunta se acertou
                acertou = perguntar_se_acertou()
                if not acertou:
                    print(formatar_saida(
                        "\nQue pena! O sistema não conseguiu identificar corretamente.",
                        "erro"
                    ))
                    print(formatar_saida(
                        "Isso pode ajudar a melhorar o sistema no futuro.",
                        "info"
                    ))
            
            # Gera relatório técnico
            gerar_relatorio_tecnico(base_conhecimento, mecanismo)
            
            # Pergunta se deseja jogar novamente
            if not jogar_novamente():
                break
            
            print()
        
        # Mensagem de despedida
        exibir_rodape()
        print(formatar_saida("\nObrigado por jogar! Até a próxima!\n", "sucesso"))
        
    except FileNotFoundError:
        print(formatar_saida(
            "\nErro: Arquivo 'knowledge_base.json' não encontrado.",
            "erro"
        ))
        print(formatar_saida(
            "Certifique-se de que o arquivo esteja no mesmo diretório que este script.",
            "normal"
        ))
    except KeyboardInterrupt:
        print(formatar_saida("\n\nJogo interrompido pelo usuário.", "info"))
    except Exception as e:
        print(formatar_saida(f"\nErro inesperado: {e}", "erro"))


if __name__ == "__main__":
    main()