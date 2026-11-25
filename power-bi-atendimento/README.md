# 📊 Dashboard Operacional – Telemarketing & Atendimento

Projeto de Business Intelligence desenvolvido no **Power BI** para acompanhamento operacional de uma central de atendimento e telemarketing, com foco em **recuperação financeira**, **eficiência na resolução no primeiro contato (FCR)** e **inteligência de tempo (Time Intelligence)**.

<img width="1561" height="872" alt="dashboard-telemarketing" src="https://github.com/user-attachments/assets/40c2deaa-8191-4c2b-9bd7-d3273c819f1b" />


---

## 🎯 Objetivo do Projeto

Fornecer à gestão operacional uma visão consolidada e interativa do desempenho das filas de atendimento (Cobrança, Retenção, Backoffice, Suporte e Ouvidoria), permitindo monitorar:
* O volume financeiro recuperado no período total, no mês atual (**MTD**) e a comparação com o mesmo período do mês anterior (**PMTD**).
* O ranking de contribuição financeira por fila de atendimento.
* O atingimento das metas de **FCR (First Call Resolution)**, desvios percentuais e evolução diária (**D-1**).

---

## 🏗️ Arquitetura e Modelagem de Dados (Star Schema)

A base de dados (`Base_CallCenter_DAX_Treinamento.xlsx`) contempla **12.915 interações** registradas entre **15/11/2025 e 12/02/2026**, estruturada em modelo **Star Schema** com 2 tabelas fato e 4 dimensões:

| Tabela | Tipo | Descrição | Registros |
| :--- | :--- | :--- | :---: |
| **`F_Interacoes`** | Fato | Histórico detalhado de atendimentos (canal, motivo, tempos de espera/AHT, FCR, CSAT, valor recuperado e custo). | 12.915 |
| **`F_Metas`** | Fato | Metas diárias estipuladas por fila para CSAT, FCR, Rechamada e AHT. | 450 |
| **`D_Data`** | Dimensão | Calendário completo com atributos de ano, mês, dia e dia da semana. | 90 |
| **`D_Filas`** | Dimensão | Cadastro das 5 filas operacionais (Cobrança, Retenção, Backoffice, Suporte e Ouvidoria) e SLA alvo. | 5 |
| **`D_Agentes`** | Dimensão | Cadastro dos 28 operadores, turno, senioridade e fila principal. | 28 |
| **`D_Clientes`** | Dimensão | Base de 420 clientes segmentados por perfil (PF/PJ) e região. | 420 |

---

## 📈 Principais Indicadores (KPIs) e Medidas DAX

O relatório utiliza medidas dinâmicas em **DAX** para análises comparativas e condicionais:

* **Gestão Financeira & Time Intelligence:**
  * `Valor Total Recuperado`: Soma total recuperada nas negociações (**R$ 762,27 Mil** no período geral).
  * `Valor Recuperado MTD` & `PMTD`: Acumulado no mês corrente (**R$ 103,95 Mil**) versus o mesmo intervalo do mês anterior (**R$ 261,16 Mil**) usando funções como `TOTALMTD` e `DATEADD`/`SAMEPERIODLASTYEAR`.
  * `Crescimento % MTD/PMTD`: Variação percentual comparativa (**-60,20%**).
  * `Ranking F/VTR`: Classificação dinâmica das filas por volume recuperado utilizando `RANKX` (liderado por **Cobrança** com **R$ 387.867,33** e **Retenção** com **R$ 296.214,84**).
* **Qualidade & Resolução (FCR):**
  * `FCR %`: Taxa de resolução no primeiro contato (**63,34%**).
  * `Meta FCR` & `Desvio FCR %`: Comparação direta com a meta operacional (**79,00%**), apontando desvio de **-19,83%**.
  * `Status FCR`: Indicador dinâmico com alerta visual (*Abaixo da Meta* / *Dentro da Meta*).
  * `FCR % vs FCR % (D-1)`: Série temporal comparando o desempenho diário com o dia imediatamente anterior.

---

## 🖥️ Estrutura do Relatório

* **Visão Analítica (Página 1):** Matriz de acompanhamento diário com acumulados (`MTD`, `PMTD`, variação absoluta/percentual e acumulado D-1), cartões de participação por fila e indicadores detalhados de variação diária de FCR.
* **Dashboard Executivo (Página 2):** Painel visual com cartões de KPIs, tabela de ranking por fila, gráfico de linhas comparativo (`FCR %` vs `D-1`), indicadores de status e segmentadores interativos por **Fila** e **Data**.

---

## 🛠️ Ferramentas Utilizadas

* **Power BI Desktop** (ETL via Power Query, Modelagem Star Schema e cálculos em DAX)
* **Microsoft Excel** (Base de dados estruturada)
* **Design de Interface (UI/UX):** Layout limpo com cartões elevados, hierarquia visual de KPIs e alertas de status por cor.

---

## 📂 Como Visualizar

1. Faça o download do arquivo `.pbix` disponível neste repositório.
2. Abra o arquivo utilizando o **Power BI Desktop**.
3. Utilize os filtros laterais (**Selecione a Fila** e **Selecione a Data**) para explorar os indicadores de forma dinâmica.
