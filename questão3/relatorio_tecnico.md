# Relatório Técnico - Questão 3

## Sistema de Agente Inteligente Baseado em LLM

**Disciplina:** Inteligência Artificial  
**Questão:** 3 - Aplicação envolvendo agentes baseados em LLM  
**Sistema:** AgenteMed  
**Finalidade:** Demonstração acadêmica de agente conversacional com inferência local explicável

---

## 1. Visão Geral

O AgenteMed é um agente conversacional educacional para triagem médica simulada. A aplicação recebe descrições livres de sintomas, detecta sinais clínicos relevantes, executa inferências locais e produz uma resposta estruturada em linguagem natural.

O agente foi projetado para funcionar em dois modos:

1. **Modo com modelo aberto local:** usa Ollama com `llama3.2:3b` por padrão, sem chave de API.
2. **Modo local de demonstração:** usa um gerador determinístico de resposta, preservando a explicabilidade quando o Ollama não está disponível.

Essa decisão garante que a apresentação e a correção possam ser executadas sem serviços pagos. Depois que o modelo é baixado, a execução não depende de internet.

---

## 2. Arquitetura

```text
Usuário
  |
  v
CLI do AgenteMed
  |
  v
Orquestrador do Agente
  |
  +--> Detecção de sintomas por termos e sinônimos
  +--> Encadeamento para frente com regras SE-ENTAO
  +--> Encadeamento para trás para testar hipóteses
  +--> Inferência bayesiana simplificada
  +--> Busca CBR por similaridade de Jaccard
  |
  v
Contexto estruturado
  |
  +--> LLM aberto local via Ollama
  +--> Fallback local explicável
  |
  v
Resposta final com análise, explicação e recomendação de segurança
```

Arquivos principais:

- `agente_med/main.py`: interface de linha de comando.
- `agente_med/agent.py`: coordena inferência local e chamada LLM.
- `agente_med/inference.py`: implementa regras, Bayes, CBR e explicação.
- `agente_med/llm_client.py`: integra Ollama local e provedores externos opcionais.
- `agente_med/data/knowledge_base.json`: base de conhecimento.

---

## 3. Modelagem do Agente

O agente segue o ciclo:

1. **Percepção:** recebe texto em linguagem natural.
2. **Extração:** identifica sintomas por normalização de texto, acentos e sinônimos.
3. **Raciocínio:** executa motores simbólicos, probabilísticos e baseados em casos.
4. **Planejamento da resposta:** seleciona hipóteses e pergunta de seguimento.
5. **Comunicação:** envia contexto a um LLM ou usa fallback local.

O prompt do agente instrui o modelo a:

- não afirmar diagnóstico definitivo;
- usar os resultados computados localmente como fonte principal;
- explicar o "por quê" de perguntas adicionais;
- explicar "como" chegou às conclusões;
- destacar sinais de urgência.

---

## 4. Base de Conhecimento

A base JSON contém:

- **30 sintomas/eventos clínicos** com rótulos e sinônimos.
- **20 regras SE-ENTAO** com confiança, explicação e hipótese associada.
- **7 hipóteses clínicas** para agrupamento de conclusões.
- **Rede bayesiana simplificada** com 9 condições e probabilidades condicionais.
- **18 casos CBR fictícios** com sintomas, diagnóstico e recomendação.

Exemplo de regra:

```json
{
  "id": "R01",
  "conditions": ["febre", "tosse", "falta_ar"],
  "conclusion": "suspeita_covid",
  "confidence": 0.85
}
```

---

## 5. Métodos de Inferência

### 5.1 Encadeamento para frente

A partir dos sintomas detectados, o sistema dispara todas as regras cujas condições são satisfeitas. O processo continua até nenhuma nova conclusão ser adicionada.

Exemplo:

```text
Entrada: febre, tosse, falta_ar
R01: SE febre E tosse E falta_ar ENTAO suspeita_covid
Conclusão: suspeita_covid
```

### 5.2 Encadeamento para trás

Para cada hipótese, o sistema tenta provar uma das conclusões que a sustentam. Se a hipótese "H3 - Emergência cardiovascular" depende de `alerta_cardiaco`, o motor busca regras que concluem `alerta_cardiaco` e verifica se seus fatos estão presentes.

### 5.3 Inferência bayesiana

O cálculo usa Naive Bayes:

```text
P(doença | sintomas) proporcional a P(doença) * produto P(sintoma | doença)
```

Os valores são normalizados para somarem 100%.

### 5.4 CBR

A busca por casos usa similaridade de Jaccard:

```text
similaridade = |sintomas_usuario ∩ sintomas_caso| / |sintomas_usuario ∪ sintomas_caso|
```

O sistema retorna os três casos mais próximos.

---

## 6. Interface

A interface é uma CLI conversacional. O usuário pode escrever sintomas livremente ou usar comandos diretos:

```text
/regras
/hipoteses
/casos
/bayes febre tosse falta_ar
/cbr febre tosse falta_ar
/forward febre tosse falta_ar
```

O modo demonstração é executado por:

```bash
python3 questão3/agente_med/main.py --demo
```

---

## 7. Exemplo de Execução

Entrada:

```text
Tenho febre, tosse e falta de ar há três dias.
```

Processamento:

1. Sintomas detectados: `febre`, `tosse`, `falta_ar`.
2. Regra R01 disparada: `suspeita_covid`.
3. Bayes calcula probabilidades para COVID-19, influenza, asma e demais doenças.
4. CBR recupera casos respiratórios similares.
5. O agente gera resposta com hipótese, justificativa e pergunta de seguimento.

Saída esperada:

```text
Sintomas detectados: febre, tosse, falta_ar.
Regra R01 disparou suspeita_covid com confiança de 85%.
Perguntaria sobre falta de ar progressiva, perda de olfato e sinais de gravidade.
Procure atendimento se houver piora respiratória.
```

---

## 8. Testes

Foram criados testes automatizados para:

- detecção de sintomas com acentos e sinônimos;
- disparo de regra por forward chaining;
- normalização das probabilidades bayesianas;
- recuperação CBR de casos similares;
- reconhecimento de exposição sexual sem preservativo;
- reconhecimento de sangramento ocular;
- resposta local com aviso de segurança.

Comando:

```bash
python3 -m unittest discover -s questão3/tests -v
```

---

## 9. Limitações

1. A detecção de sintomas é baseada em palavras-chave, não em NER clínico avançado.
2. A rede bayesiana usa independência condicional simplificada.
3. Os casos e probabilidades são fictícios e servem apenas para demonstração.
4. O modo com LLM depende do Ollama estar instalado e do modelo local estar baixado.
5. O sistema não deve ser usado para diagnóstico real.

---

## 10. Conclusão

O AgenteMed atende à Questão 3 ao implementar uma aplicação prática com agente conversacional baseado em LLM, enriquecido por inferências locais. A solução inclui código-fonte, base de conhecimento, relatório técnico, testes e roteiro de apresentação, mantendo funcionamento demonstrável mesmo sem acesso a API externa.
