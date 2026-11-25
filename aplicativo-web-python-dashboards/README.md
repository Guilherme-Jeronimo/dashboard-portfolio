# 📊 Social Media Analytics – Valorant Performance (Setembro/2025)

Aplicação web interativa desenvolvida em **Python** e **Streamlit** para análise de desempenho orgânico multiplataforma (Instagram, TikTok, X/Twitter, Facebook e YouTube), acompanhada de estudo de caso executivo (*Data Insights Team Business Case*).

---

## 🎯 Objetivo do Projeto

Consolidar métricas de redes sociais em uma plataforma analítica única para avaliar o funil de **Alcance (Reach)**, **Engajamento (Engagement)**, **Retenção (Retention)** e **Conversão/Ação (Action)**, além de transformar os dados brutos em recomendações estratégicas para o ciclo seguinte (Outubro).

---

## 🏗️ Estrutura da Aplicação

O projeto é dividido em módulos analíticos independentes integrados a um painel principal:

* **`app_main.py`**: Visão consolidada *Cross-platform* com cálculo de **Total Score (0–1)** por rede e comparativo de alcance, engajamento proporcional e ações por 1.000 alcances.
* **`app_instagram.py`**: Análise de volume, taxa de salvamentos (`Saves per 1,000 views`), crescimento de seguidores e ranking *Top 5 Posts* por visualizações, qualidade de engajamento (`Engagement Quality Score`) e conversão.
* **`app_tiktok.py`**: Monitoramento de retenção em vídeos curtos (`Full video watched rate`), tempo médio assistido e taxa de compartilhamentos.
* **`app_twitter.py`**: Análise de impressões, engajamento rápido e funil de cliques no perfil (`Profile click rate`).
* **`app_facebook.py`**: Avaliação de eficiência de conversão (`Clicks per 1,000 reach`) e dispersão entre qualidade de engajamento e cliques.
* **`app_youtube.py`**: Diagnóstico de vídeos longos focado em retenção média (`Average percentage viewed`) e fidelidade da base (`Returning viewers rate`).

---

## 💡 Principais Insights do Estudo de Caso (Setembro 2025)

* **Liderança de Ecossistema (Instagram):** Maior pontuação geral (**0.60 Total Score**), impulsionada por **2,77 milhões de views (+65,8% MoM)**, **969,6 mil de alcance (+84,2%)** e **124 mil interações totais**.
* **Explosão de Engajamento (X/Twitter):** Crescimento de **+168%** em engajamentos (**22,7 mil**) e **+600%** em novos seguidores, destacando-se como canal de resposta rápida a atualizações do jogo.
* **Paradoxo do Vídeo (TikTok & YouTube):** Apesar da retração em métricas superficiais de view/engajamento, o público remanescente apresentou alta retenção — alta de **+22%** na taxa de vídeos assistidos até o fim no TikTok e **+28,1%** em espectadores recorrentes no YouTube (com **81,6%** de porcentagem média assistida).
* **Anomalia de Conversão (Facebook):** Mesmo com o menor alcance do ecossistema (**15,1 mil**), liderou disparado em conversão com **127,40 cliques por 1.000 alcances** (quase 9x acima do 2º colocado, TikTok, com 14,72), atuando como funil qualificado de alta intenção.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Framework Web:** Streamlit
* **Manipulação e Análise de Dados:** Pandas, NumPy, Regex
* **Visualização de Dados:** Matplotlib / Altair
* **Storytelling Executivo:** Apresentação em PDF disponível neste diretório

---

## 🚀 Como Executar Localmente

1. Clone o repositório e acesse esta pasta:
   ```bash
   git clone [https://github.com/PetreaConcreto/dashboard-portfolio.git](https://github.com/PetreaConcreto/dashboard-portfolio.git)
   cd dashboard-portfolio/streamlit-redes-sociais
