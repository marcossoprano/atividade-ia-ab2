# Sistema Especialista em Diagnóstico Médico - Dr. IA

Sistema especialista baseado em regras para diagnóstico médico, com motor de inferência híbrido (forward chaining + backward chaining), mecanismo de explicação (por que / como) e integração com DeepSeek LLM via chat interativo.

## Estrutura do Projeto

```
.
├── app.py                 # Aplicação Flask (API REST + Web)
├── inference_engine.py    # Motor de inferência (forward, backward, híbrido)
├── knowledge_base.json    # Base de conhecimento (~80 regras, ~20 doenças)
├── templates/
│   └── index.html         # Interface web interativa
├── requirements.txt       # Dependências Python
└── README.md              # Este arquivo
```

## Base de Conhecimento

- **80 regras** de produção (IF-THEN)
- **20 doenças/hipóteses** diagnósticas
- Fatos com **35+ atributos** de sintomas
- Regras com explicação e tratamento para cada conclusão

### Doenças cobertas

1. Gripe (Influenza)
2. Resfriado Comum
3. COVID-19
4. Pneumonia
5. Dengue
6. Zika Vírus
7. Chikungunya
8. Malária
9. Tuberculose
10. Meningite
11. Hepatite A
12. Hepatite B/C
13. Gastroenterite
14. Apendicite Aguda
15. Faringite Estreptocócica
16. Mononucleose Infecciosa
17. Sinusite
18. Bronquite
19. Asma Brônquica
20. Leptospirose
21. Rubéola
22. Sarampo
23. Varicela (Catapora)
24. Conjuntivite
25. Febre Amarela
26. Hantavirose
27. Febre Reumática
28. Long COVID

## Motor de Inferência

### Forward Chaining
A partir dos fatos informados pelo usuário, aplica todas as regras cujas condições são satisfeitas, propagando novas conclusões até o ponto fixo.

### Backward Chaining
Dado um objetivo (hipótese diagnóstica), busca recursivamente regras que concluem o objetivo e tenta provar suas condições.

### Estratégia Híbrida
1. Forward chaining inicial com fatos do usuário
2. Backward chaining para confirmar hipóteses suspeitas
3. Novo forward chaining com conclusões confirmadas

## Mecanismo de Explicação

- **Por que (Why)**: explica por que determinada pergunta está sendo feita, mostrando as hipóteses em investigação
- **Como (How)**: explica como uma conclusão foi obtida, mostrando as regras disparadas e as condições que as ativaram

## Integração DeepSeek LLM

O chat integrado envia o contexto completo do sistema especialista (fatos, diagnósticos, regras disparadas) para o modelo DeepSeek, permitindo interação natural em linguagem humana.

Para ativar, configure a variável de ambiente:

```bash
export DEEPSEEK_API_KEY="sua-chave-aqui"
```

Sem a chave, o sistema funciona com respostas de fallback baseadas nas regras.

## Instalação e Execução

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. (Opcional) Configurar chave DeepSeek
export DEEPSEEK_API_KEY="sk-..."

# 3. Executar
python app.py
```

Acesse em: http://localhost:5000

## API REST

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/session/new` | POST | Cria nova sessão de consulta |
| `/api/session/{id}/answer` | POST | Envia resposta do usuário |
| `/api/session/{id}/explain/why` | GET | Explica por que a pergunta |
| `/api/session/{id}/explain/how` | GET | Explica como obteve conclusão |
| `/api/session/{id}/result` | GET | Obtém resultado atual |
| `/api/session/{id}/reset` | POST | Reinicia sessão |
| `/api/session/{id}/chat` | POST | Chat com DeepSeek LLM |
| `/api/kb/rules` | GET | Lista todas as regras |
| `/api/kb/hypotheses` | GET | Lista todas as hipóteses |

## Exemplo de Uso

1. Acesse a página inicial
2. Responda às perguntas sobre sintomas
3. Clique em "Por que esta pergunta?" para entender a lógica
4. Veja os diagnósticos identificados
5. Use o chat para tirar dúvidas com o Dr. IA
