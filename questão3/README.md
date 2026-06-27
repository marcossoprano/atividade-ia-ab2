# Questão 3 - Agente Inteligente Baseado em LLM

## Sistema: AgenteMed

O AgenteMed é uma aplicação educacional de agente conversacional para apoio a triagem médica simulada. O sistema combina um agente baseado em LLM com motores locais de inferência, para que as conclusões apresentadas ao usuário tenham rastreabilidade computável.

> Uso estritamente acadêmico. O sistema não substitui avaliação médica real.

## Estrutura

```text
questão3/
├── agente_med/
│   ├── data/knowledge_base.json   # Base de sintomas, regras, hipóteses, Bayes e CBR
│   ├── agent.py                   # Orquestração do agente
│   ├── inference.py               # Forward chaining, backward, Bayes e CBR
│   ├── knowledge_base.py          # Carregamento da base JSON
│   ├── llm_client.py              # Cliente LLM opcional e fallback local
│   └── main.py                    # Interface CLI
├── tests/test_inference.py        # Testes automatizados
├── relatorio_tecnico.md           # Relatório técnico da Questão 3
├── roteiro_video.md               # Roteiro para vídeo/apresentação
└── requirements.txt               # Dependências
```

## Como executar

Sem dependências externas obrigatórias:

```bash
python3 questão3/agente_med/main.py --demo
```

Modo interativo:

```bash
python3 questão3/agente_med/main.py
```

Comandos disponíveis no chat:

```text
/ajuda
/regras
/hipoteses
/casos
/bayes febre tosse falta_ar
/cbr febre tosse falta_ar
/forward febre tosse falta_ar
/sair
```

## Modelo aberto e gratuito já configurado

O projeto já vem configurado para usar **Ollama + `llama3.2:3b`** por padrão. É um modelo aberto/gratuito, roda localmente e não precisa de chave de API.

Primeira vez na máquina:

```bash
ollama pull llama3.2:3b
```

Depois, execute normalmente:

```bash
python3 questão3/agente_med/main.py
```

Para escolher outro modelo local do Ollama:

```bash
export AGENTEMED_OLLAMA_MODEL="mistral"
python3 questão3/agente_med/main.py
```

Se o Ollama não estiver aberto ou o modelo não estiver baixado, o agente continua respondendo com o modo local explicável.

## Testes

```bash
python3 -m unittest discover -s questão3/tests -v
```
