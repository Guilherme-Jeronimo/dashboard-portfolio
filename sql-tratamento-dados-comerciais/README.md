🗃️ Limpeza e Análise de Dados – Operação Comercial

Projeto de preparação e análise de dados desenvolvido em SQL e SQLite, com foco em qualidade dos dados, desempenho comercial e evolução mensal da receita.

A partir de uma exportação sintética com 102.000 linhas e 30 colunas, o projeto realiza deduplicação, padronização de campos, validação de registros e separação de rejeitados antes de construir os indicadores de negócio.

> Todos os dados são fictícios, gerados para fins educacionais e demonstração de portfólio. Não representam uma empresa real.

---

🎯 Objetivo do Projeto

Transformar uma exportação operacional com inconsistências em uma base adequada para análise, permitindo:

- Identificar e remover versões repetidas do mesmo atendimento.
- Padronizar nomes de agentes, canais, produtos e formatos numéricos.
- Validar datas, valores de venda e duração dos atendimentos.
- Separar registros inválidos sem descartar o histórico bruto.
- Auditar a quantidade de registros recebidos, rejeitados e aproveitados.
- Comparar conversão, ticket médio e receita por minuto entre agentes do mesmo canal.
- Acompanhar receita mensal, crescimento, acumulado e média móvel por equipe.

---

🏗️ Estrutura e Fluxo de Preparação dos Dados

A base `atendimentos_brutos.csv` contém atendimentos de janeiro a dezembro de 2025, distribuídos entre 20 agentes, duas equipes e três canais: Telefone, Chat e WhatsApp.

Cada atendimento possui um identificador. Reexportações podem gerar mais de uma versão do mesmo registro.

O processamento mantém o arquivo original e organiza as etapas em views no SQLite:

```text
atendimentos_brutos
        ↓
atendimentos_deduplicados
        ↓
atendimentos_normalizados
        ↓
atendimentos_classificados
        ├── registros_rejeitados
        └── atendimentos_limpos
                    ↓
          Indicadores e análises
```

| Objeto | Tipo | Finalidade |
| :--- | :--- | :--- |
| `atendimentos_brutos` | Tabela importada | Preservar os registros recebidos, incluindo inconsistências e reexportações. |
| `cadastro_agentes` | View de referência | Relacionar os 20 agentes aos nomes e equipes padronizados. |
| `atendimentos_deduplicados` | View | Manter a versão mais recente de cada atendimento. |
| `atendimentos_normalizados` | View | Padronizar categorias, nomes e representações numéricas. |
| `atendimentos_classificados` | View | Aplicar as regras de validação e identificar o motivo de rejeição. |
| `registros_rejeitados` | View | Disponibilizar registros com erros críticos para revisão. |
| `atendimentos_limpos` | View | Disponibilizar os campos tratados para as consultas analíticas. |

A carga do CSV é manual. As transformações são executadas dentro do SQLite, sem modificar a tabela de origem.

---

🧹 Limpeza, Tratamento e Validação

A base foi criada com problemas deliberados para demonstrar decisões de preparação dos dados.

| Problema identificado | Tratamento aplicado |
| :--- | :--- |
| Múltiplas versões do mesmo atendimento | Deduplicação com `ROW_NUMBER()`, mantendo a atualização mais recente. |
| Atualizações com o mesmo horário | Desempate pelo identificador do registro de origem. |
| Nomes com espaços e caixa inconsistente | Padronização com `TRIM()` e `UPPER()`, seguida de relacionamento com o cadastro de agentes. |
| Canais como `TEL`, ` chat ` e `whatsapp` | Mapeamento para categorias padronizadas com `CASE`. |
| Produtos com diferenças de caixa e espaços | Padronização dos nomes. |
| Valores como `R$ 149,90` | Remoção do símbolo monetário e dos espaços, normalização decimal e conversão numérica. |
| Valores ausentes ou não numéricos | Rejeição do registro, sem presumir que ausência significa venda igual a zero. |
| Vendas negativas | Separação para revisão. |
| Duração com vírgula decimal | Normalização antes da conversão. |
| Duração zero, negativa ou não numérica | Rejeição do registro. |
| Datas inexistentes ou fora de 2025 | Validação e separação dos registros inválidos. |
| Notas de satisfação fora de 1 a 5 | Conversão da nota para `NULL`, preservando o atendimento. |
| Colunas sem uso nos indicadores escolhidos | Exclusão da camada analítica, com preservação na origem. |

O texto numérico é validado antes do `CAST`, evitando que valores como `abc` sejam interpretados como zero pelo SQLite.

O tratamento monetário foi construído para os formatos presentes nesta base, sem separador de milhar.

---

✅ Auditoria de Qualidade dos Dados

O processamento apresentou os seguintes resultados:

| Indicador | Quantidade |
| :--- | ---: |
| Linhas recebidas | 102.000 |
| Versões repetidas removidas | 2.000 |
| Atendimentos únicos após deduplicação | 100.000 |
| Registros rejeitados por erro crítico | 2.673 |
| Atendimentos aproveitados | 97.327 |
| Notas inválidas ou ausentes entre os atendimentos aproveitados | 491 |

### Motivos de rejeição

| Motivo | Registros |
| :--- | ---: |
| Venda ausente ou não numérica | 891 |
| Duração não positiva | 586 |
| Data inválida ou fora do período | 298 |
| Agente ausente ou desconhecido | 250 |
| Venda negativa | 250 |
| Canal desconhecido | 199 |
| Duração ausente ou não numérica | 199 |
| Total | 2.673 |

Cada registro recebe o primeiro motivo crítico identificado. Por isso, a tabela contabiliza registros rejeitados, e não todas as inconsistências que podem coexistir na mesma linha.

As 491 notas inválidas não provocam rejeição dos atendimentos: somente a nota é desconsiderada no cálculo da satisfação média.

---

📈 Indicadores e Análises de Negócio

### Desempenho comercial por agente e canal

A consulta compara agentes dentro do mesmo canal, utilizando:

- Conversão: atendimentos com venda divididos pelo total de atendimentos.
- Ticket médio: receita dividida pela quantidade de atendimentos com venda.
- Receita por minuto: receita dividida pelo tempo total dos atendimentos.
- Referência do canal: receita total dividida pelo tempo total dos grupos elegíveis.
- Diferença percentual: distância entre a receita por minuto do agente e a referência do canal.
- Ranking no canal: classificação pela receita por minuto.
- Satisfação média: média das notas válidas, acompanhada da quantidade de avaliações utilizadas.

São considerados grupos com pelo menos 100 atendimentos por agente e canal. Esse corte é exploratório e não representa um teste de significância estatística.

A apresentação é organizada por equipe e canal, mas o ranking considera todos os agentes do mesmo canal.

### Evolução mensal por equipe

A análise temporal apresenta:

- Receita e volume de atendimentos por mês.
- Receita do mês anterior, utilizando `LAG()`.
- Variação percentual em relação ao mês anterior.
- Receita acumulada no período.
- Média móvel de até três meses, incluindo o mês atual.

A receita total dos registros aproveitados foi de R$ 4.723.215,74.

Como exemplo de leitura, a Equipe A registrou R$ 191.499,05 em janeiro e R$ 164.334,27 em fevereiro, uma queda de 14,19%. A consulta identifica a variação, mas não estabelece sua causa.

---

💻 Organização das Consultas

| Arquivo | Finalidade |
| :--- | :--- |
| [01_preparacao.sql](./consultas/01_preparacao.sql) | Criar as views de deduplicação, normalização, validação e separação dos registros. |
| [02_auditoria_qualidade.sql](./consultas/02_auditoria_qualidade.sql) | Conferir o fluxo de registros e os motivos de rejeição. |
| [03_desempenho_comercial.sql](./consultas/03_desempenho_comercial.sql) | Comparar indicadores comerciais entre agentes e canais. |
| [04_evolucao_mensal.sql](./consultas/04_evolucao_mensal.sql) | Analisar crescimento, receita acumulada e média móvel por equipe. |

### Recursos SQL utilizados

- CTEs para organizar as etapas analíticas.
- `LEFT JOIN` para relacionamento com o cadastro de agentes.
- `CASE` para padronização e regras de qualidade.
- `TRIM`, `UPPER` e `REPLACE` para tratamento de texto.
- `CAST` para conversão de tipos após validação.
- `NULLIF` para proteção contra divisão por zero.
- `ROW_NUMBER` para deduplicação.
- `RANK` para classificação dos agentes.
- `LAG` para comparação entre meses.
- `SUM` e `AVG` com funções de janela para referências, acumulados e médias móveis.

---

📂 Estrutura do Projeto

```text
sql-tratamento-dados-comerciais/
├── README.md
├── dados/
│   └── atendimentos_brutos.csv
├── consultas/
│   ├── 01_preparacao.sql
│   ├── 02_auditoria_qualidade.sql
│   ├── 03_desempenho_comercial.sql
│   └── 04_evolucao_mensal.sql
└── resultados/
    ├── atendimentos_tratados.csv
    ├── registros_rejeitados.csv
    └── resultados.xlsx
```

Os arquivos da pasta `resultados` são saídas para conferência. Não precisam ser importados para executar o projeto.

---

🛠️ Ferramentas Utilizadas

- SQLite: processamento, validação e análise dos dados.
- SQL: criação de views, regras de qualidade e consultas analíticas.
- Python, Pandas e NumPy: geração da base sintética e preparação dos arquivos de demonstração.
- Microsoft Excel: formato de disponibilização dos resultados para consulta.

---

▶️ Como Executar

1. Baixe a [base bruta](./dados/atendimentos_brutos.csv).
2. Importe o arquivo em uma ferramenta compatível com SQLite, como o SQLite Lab.
3. Use `atendimentos_brutos` como nome da tabela.
4. Configure a primeira linha como cabeçalho, separador por vírgula e codificação UTF-8.
5. Preserve os valores brutos como texto na importação, principalmente `venda` e `tempo_min`, para que o SQL realize o tratamento.
6. Execute todo o conteúdo de `01_preparacao.sql`, no mesmo banco em que a base foi importada.
7. Execute as consultas `02`, `03` e `04`, uma de cada vez.
8. Compare as saídas com a [planilha de resultados](./resultados/resultados.xlsx).

O script de preparação pode ser reexecutado: ele recria as views sem alterar os registros da tabela bruta.

---

🔎 Validações e Limitações

As consultas foram executadas em SQLite. Foram conferidos:

- Unicidade dos atendimentos após a deduplicação.
- Durações positivas e vendas não negativas na base limpa.
- Reconciliação entre registros únicos, aproveitados e rejeitados.
- Reconciliação da receita mensal com a receita total tratada.
- Reexecução do script de preparação sem mudança na quantidade de registros aproveitados.

A importação pela interface de um site específico não faz parte desses testes.

O projeto começa no recebimento de um CSV: não inclui extração automatizada de um sistema externo. As regras tratam os problemas introduzidos nesta base, não todos os formatos e erros possíveis.

A comparação dentro de um canal não controla diferenças de produto ou perfil de cliente. Os indicadores são descritivos e não constituem uma avaliação completa dos agentes. A satisfação foi gerada independentemente das demais métricas.

Os dados brutos são preservados para permitir rastreabilidade das transformações e revisão dos registros rejeitados.
