# Relatório Técnico - Sistema Inteligente de Perguntas e Respostas

## 1. Descrição do Domínio

Este sistema foi desenvolvido para identificar **divas pop internacionais** através
de um processo de perguntas e respostas, inspirado no famoso jogo Akinator.

### Artistas Incluídos (20 artistas)

1. Taylor Swift
2. Beyoncé
3. Lady Gaga
4. Rihanna
5. Katy Perry
6. Ariana Grande
7. Britney Spears
8. Madonna
9. Dua Lipa
10. Billie Eilish
11. Selena Gomez
12. Miley Cyrus
13. Christina Aguilera
14. Shakira
15. Jennifer Lopez
16. Olivia Rodrigo
17. Sabrina Carpenter
18. Camila Cabello
19. Lana Del Rey
20. Avril Lavigne

## 2. Estratégia de Representação do Conhecimento

O conhecimento foi representado utilizando uma abordagem **baseada em atributos binários**.
Cada artista é descrita por um conjunto de 20 atributos, cada um com valor
verdadeiro (True) ou falso (False).

### Atributos Utilizados (20 atributos)

1. Ela é norte-americana?
2. Ela está em atividade atualmente?
3. Ela possui Grammy?
4. Ela já atuou em filmes?
5. Ela também é atriz?
6. Ela começou a carreira antes de 2010?
7. Ela é conhecida por música country?
8. Ela é conhecida por música latina?
9. Ela possui ascendência latina?
10. Ela já participou do Super Bowl?
11. Ela é considerada uma artista da geração Z?
12. Ela possui mais de 10 anos de carreira?
13. Ela é compositora das próprias músicas?
14. Ela possui turnê mundial recente?
15. Ela tem mais de 100 milhões de seguidores no Instagram?
16. Ela é conhecida por performances extravagantes?
17. Ela é conhecida por baladas românticas?
18. Ela já integrou grupo musical antes da carreira solo?
19. Ela possui Oscar?
20. Ela possui álbum lançado em 2024 ou posteriormente?

## 3. Estrutura da Base de Conhecimento

A base de conhecimento é armazenada em formato JSON (`knowledge_base.json`) contendo:

- **atributos**: Lista de 20 características utilizadas para diferenciação
- **artistas**: Lista de 20 artistas, cada uma com seus respectivos valores de atributos

### Exemplo de Estrutura de uma Artista

```json
{
    "nome": "Taylor Swift",
    "americana": true,
    "grammy": true,
    "country": true,
    ...
}
```

## 4. Mecanismo de Inferência Utilizado

O sistema implementa um **mecanismo de inferência baseado em eliminação de hipóteses**:

1. **Inicialização**: Começa com todas as 20 artistas como candidatas possíveis
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

- **Total de perguntas realizadas**: 6
- **Hipóteses eliminadas**: 19 de 20
- **Taxa de redução do espaço de busca**: 95.0%
- **Sucesso na identificação**: Sim

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
