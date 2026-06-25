#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do sistema.
"""

from utils import carregar_base_conhecimento, obter_nome_atributo_pergunta
from inference_engine import MecanismoInferencia


def testar_carregamento():
    """Testa o carregamento da base de conhecimento."""
    print("=" * 50)
    print("TESTE 1: Carregamento da Base de Conhecimento")
    print("=" * 50)
    
    base = carregar_base_conhecimento()
    artistas = base.get("artistas", [])
    atributos = base.get("atributos", [])
    
    print(f"✓ Artistas carregadas: {len(artistas)}")
    print(f"✓ Atributos carregados: {len(atributos)}")
    
    assert len(artistas) >= 20, f"Esperado pelo menos 20 artistas, encontrado {len(artistas)}"
    assert len(atributos) >= 15, f"Esperado pelo menos 15 atributos, encontrado {len(atributos)}"
    
    print("\nPrimeiras 5 artistas:")
    for a in artistas[:5]:
        print(f"  - {a['nome']}")
    
    print("\n✓ TESTE 1 APROVADO!\n")
    return base


def testar_mecanismo_inferencia():
    """Testa o mecanismo de inferência com respostas simuladas."""
    print("=" * 50)
    print("TESTE 2: Mecanismo de Inferência")
    print("=" * 50)
    
    base = carregar_base_conhecimento()
    artistas = base.get("artistas", [])
    atributos = base.get("atributos", [])
    
    mecanismo = MecanismoInferencia(artistas, atributos)
    
    print(f"Total inicial de hipóteses: {mecanismo.total_hipoteses()}")
    assert mecanismo.total_hipoteses() == len(artistas)
    
    # Simula perguntas para identificar Taylor Swift
    # Taylor Swift: americana=True, country=True, compositora=True
    perguntas_simuladas = [
        ("americana", "sim"),
        ("country", "sim"),
    ]
    
    for atributo, resposta in perguntas_simuladas:
        pergunta_texto = obter_nome_atributo_pergunta(atributo)
        print(f"\nPergunta: {pergunta_texto}")
        print(f"Resposta: {resposta}")
        
        eliminadas = mecanismo.processar_resposta(atributo, resposta)
        print(f"Eliminadas: {len(eliminadas)}")
        print(f"Hipóteses restantes: {mecanismo.total_hipoteses()}")
        
        if mecanismo.total_hipoteses() <= 5:
            print(f"Candidatas: {mecanismo.obter_candidatas_restantes()}")
    
    resultado = mecanismo.obter_resultado()
    print(f"\nResultado: {resultado['nome'] if resultado else 'Nenhum'}")
    
    estatisticas = mecanismo.obter_estatisticas()
    print(f"Estatísticas: {estatisticas}")
    
    print("\n✓ TESTE 2 APROVADO!\n")


def testar_selecao_perguntas():
    """Testa a seleção inteligente de perguntas."""
    print("=" * 50)
    print("TESTE 3: Seleção Inteligente de Perguntas")
    print("=" * 50)
    
    base = carregar_base_conhecimento()
    artistas = base.get("artistas", [])
    atributos = base.get("atributos", [])
    
    mecanismo = MecanismoInferencia(artistas, atributos)
    
    # Testa as 3 primeiras perguntas selecionadas
    for i in range(3):
        atributo, ganho = mecanismo.obter_proxima_pergunta()
        if atributo:
            pergunta = obter_nome_atributo_pergunta(atributo)
            print(f"Pergunta {i+1}: {pergunta} (ganho: {ganho:.4f})")
            
            # Simula resposta "sim" para continuar
            mecanismo.processar_resposta(atributo, "sim")
    
    print("\n✓ TESTE 3 APROVADO!\n")


def testar_todas_artistas():
    """Testa se todas as artistas podem ser identificadas."""
    print("=" * 50)
    print("TESTE 4: Identificação de Todas as Artistas")
    print("=" * 50)
    
    base = carregar_base_conhecimento()
    artistas = base.get("artistas", [])
    atributos = base.get("atributos", [])
    
    acertos = 0
    total = len(artistas)
    
    for artista_alvo in artistas:
        mecanismo = MecanismoInferencia(artistas, atributos)
        
        # Simula respostas baseadas nos atributos reais da artista
        while True:
            atributo, _ = mecanismo.obter_proxima_pergunta()
            if atributo is None:
                break
            
            # Obtém a resposta correta da artista
            resposta_valor = artista_alvo.get(atributo)
            if resposta_valor is True:
                resposta = "sim"
            elif resposta_valor is False:
                resposta = "nao"
            else:
                resposta = "nao_sei"
            
            mecanismo.processar_resposta(atributo, resposta)
            
            if mecanismo.ha_certeza():
                break
        
        resultado = mecanismo.obter_resultado()
        if resultado and resultado["nome"] == artista_alvo["nome"]:
            acertos += 1
    
    taxa_sucesso = (acertos / total) * 100
    print(f"Artistas identificadas corretamente: {acertos}/{total}")
    print(f"Taxa de sucesso: {taxa_sucesso:.1f}%")
    
    assert taxa_sucesso >= 90, f"Taxa de sucesso muito baixa: {taxa_sucesso}%"
    
    print("\n✓ TESTE 4 APROVADO!\n")


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 50)
    print("  SISTEMA INTELIGENTE - TESTES")
    print("=" * 50 + "\n")
    
    try:
        testar_carregamento()
        testar_mecanismo_inferencia()
        testar_selecao_perguntas()
        testar_todas_artistas()
        
        print("=" * 50)
        print("  TODOS OS TESTES APROVADOS! ✓")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n✗ TESTE FALHOU: {e}\n")
    except Exception as e:
        print(f"\n✗ ERRO: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()