# Roteiro de Vídeo/Apresentação - Questão 3

## 1. Abertura

Apresentar o AgenteMed como uma aplicação de agente inteligente baseado em LLM para triagem médica educacional.

Mensagem sugerida:

> Este sistema não realiza diagnóstico real. Ele demonstra como um agente de IA generativa pode coordenar métodos de raciocínio simbólico, probabilístico e baseado em casos para produzir respostas explicáveis.

## 2. Mostrar a Estrutura dos Arquivos

Exibir:

- `agente_med/main.py`
- `agente_med/agent.py`
- `agente_med/inference.py`
- `agente_med/data/knowledge_base.json`
- `relatorio_tecnico.md`

## 3. Rodar a Demonstração

Comando:

```bash
python3 questão3/agente_med/main.py --demo
```

Pontos a destacar:

- sintomas são extraídos de texto livre;
- regras SE-ENTAO disparam conclusões;
- Bayes gera probabilidades;
- CBR recupera casos semelhantes;
- a resposta final explica "por quê" e "como".

## 4. Demonstrar Comandos Técnicos

Executar:

```text
/regras
/bayes febre tosse falta_ar
/cbr febre manchas dor_muscular
/forward dor_peito falta_ar
```

## 5. Mostrar Testes

Comando:

```bash
python3 -m unittest discover -s questão3/tests -v
```

## 6. Fechamento

Explicar limitações:

- base fictícia;
- probabilidades simplificadas;
- uso educacional;
- LLM aberto local via Ollama, com fallback explicável se o modelo não estiver disponível.

Finalizar mostrando que os entregáveis da Questão 3 estão completos: código, base de dados, relatório e roteiro para demonstração.
