from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Instagram - Reach, Engagement and Action", layout="wide")


ARQUIVOS_CANDIDATOS = [
    "Instagram_Aug-Sep_2025_dummy.xlsx",
    "Instagram_Aug-Sep_2025_dummy-2.xlsx",
    "data/Instagram_Aug-Sep_2025_dummy.xlsx",
    "data/Instagram_Aug-Sep_2025_dummy-2.xlsx",
]


def encontrar_arquivo():
    for nome in ARQUIVOS_CANDIDATOS:
        caminho = Path(nome)
        if caminho.exists():
            return caminho
    return None


def pct_change(novo, antigo):
    if pd.isna(antigo) or antigo == 0:
        return None
    return ((novo - antigo) / antigo) * 100


def fmt_int(x):
    if x is None or pd.isna(x):
        return "-"
    return f"{int(round(x)):,}".replace(",", ".")


def fmt_float(x, dec=1):
    if x is None or pd.isna(x):
        return "-"
    return f"{x:.{dec}f}".replace(".", ",")


def fmt_pct(x, dec=2):
    if x is None or pd.isna(x):
        return "-"
    return f"{x * 100:.{dec}f}%".replace(".", ",")


def fmt_var(x):
    if x is None or pd.isna(x):
        return "-"
    sinal = "+" if x >= 0 else ""
    return f"{sinal}{x:.1f}%".replace(".", ",")


def normalizar_texto(x):
    if pd.isna(x):
        return "(No description)"
    x = str(x).strip()
    if x == "":
        return "(No description)"
    return x


@st.cache_data
def carregar_dados():
    caminho = encontrar_arquivo()
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho, sheet_name=0)
    # Publish time may come in different formats
    df["Publish time"] = pd.to_datetime(df["Publish time"], errors="coerce")
    df = df[df["Publish time"].notna()].copy()

    df["chave_mes"] = df["Publish time"].dt.strftime("%Y-%m")
    df = df[df["chave_mes"].isin(["2025-08", "2025-09"])].copy()

    colunas_numericas = [
        "Views",
        "Likes",
        "Shares",
        "Comments",
        "Saves",
        "Reach",
        "Follows",
        "Duration (sec)",
    ]

    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["descricao_normalizada"] = df["Description"].apply(normalizar_texto)

    # Raw engagement
    df["interacoes"] = (
        df["Likes"].fillna(0)
        + df["Comments"].fillna(0)
        + df["Shares"].fillna(0)
        + df["Saves"].fillna(0)
    )

    # Rates
    df["engagement_rate"] = (
        df["interacoes"] / df["Reach"].replace(0, pd.NA)
    )

    df["saves_por_1000_views"] = (
        df["Saves"] / df["Views"].replace(0, pd.NA)
    ) * 1000

    df["follows_por_1000_reach"] = (
        df["Follows"] / df["Reach"].replace(0, pd.NA)
    ) * 1000

    df["likes_por_1000_views"] = (
        df["Likes"] / df["Views"].replace(0, pd.NA)
    ) * 1000

    return df, caminho


def resumo(df):
    soma_views = df["Views"].sum()
    soma_reach = df["Reach"].sum()

    return {
        "posts": len(df),
        "views": soma_views,
        "reach": soma_reach,
        "engagement_rate": (df["interacoes"].sum() / soma_reach) if soma_reach else None,
        "likes": df["Likes"].sum(),
        "comments": df["Comments"].sum(),
        "saves": df["Saves"].sum(),
        "follows": df["Follows"].sum(),
        "saves_por_1000": (df["Saves"].sum() / soma_views * 1000) if soma_views else None,
        "follows_por_1000": (df["Follows"].sum() / soma_reach * 1000) if soma_reach else None,
    }


df, caminho = carregar_dados()

st.title("Instagram - Reach, Engagement and Action")
st.caption("Analytical view for September 2025")

if df is None:
    st.error("Instagram file not found.")
    st.stop()

agosto = df[df["chave_mes"] == "2025-08"].copy()
setembro = df[df["chave_mes"] == "2025-09"].copy()

res_ago = resumo(agosto)
res_set = resumo(setembro)

# Engagement/quality score per post in September
setembro["score_qualidade_engajamento"] = (
    setembro["engagement_rate"].rank(pct=True) * 0.4
    + setembro["likes_por_1000_views"].rank(pct=True) * 0.3
    + setembro["saves_por_1000_views"].rank(pct=True) * 0.3
) * 100

st.caption(f"Loaded file: {caminho}")

# Main KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(
    "Views",
    fmt_int(res_set["views"]),
    fmt_var(pct_change(res_set["views"], res_ago["views"]))
)
k2.metric(
    "Reach",
    fmt_int(res_set["reach"]),
    fmt_var(pct_change(res_set["reach"], res_ago["reach"]))
)
k3.metric(
    "Engagement rate",
    fmt_pct(res_set["engagement_rate"], 2),
    fmt_var(pct_change(res_set["engagement_rate"], res_ago["engagement_rate"]))
)
k4.metric(
    "Saves per 1,000 views",
    fmt_float(res_set["saves_por_1000"], 2),
    fmt_var(pct_change(res_set["saves_por_1000"], res_ago["saves_por_1000"]))
)
k5.metric(
    "Follows per 1,000 reach",
    fmt_float(res_set["follows_por_1000"], 2),
    fmt_var(pct_change(res_set["follows_por_1000"], res_ago["follows_por_1000"]))
)

# August vs September comparison
st.markdown("### August vs September")

comparativo_bruto = pd.DataFrame({
    "Metric": [
        "Posts",
        "Views",
        "Reach",
        "Engagement rate",
        "Likes",
        "Comments",
        "Saves",
        "Follows",
        "Saves per 1,000 views",
        "Follows per 1,000 reach",
    ],
    "August_value": [
        res_ago["posts"],
        res_ago["views"],
        res_ago["reach"],
        res_ago["engagement_rate"],
        res_ago["likes"],
        res_ago["comments"],
        res_ago["saves"],
        res_ago["follows"],
        res_ago["saves_por_1000"],
        res_ago["follows_por_1000"],
    ],
    "September_value": [
        res_set["posts"],
        res_set["views"],
        res_set["reach"],
        res_set["engagement_rate"],
        res_set["likes"],
        res_set["comments"],
        res_set["saves"],
        res_set["follows"],
        res_set["saves_por_1000"],
        res_set["follows_por_1000"],
    ],
})

comparativo_bruto["Change_pct"] = comparativo_bruto.apply(
    lambda row: pct_change(row["September_value"], row["August_value"]), axis=1
)

comparativo = pd.DataFrame({
    "Metric": comparativo_bruto["Metric"],
    "August": [
        fmt_int(res_ago["posts"]),
        fmt_int(res_ago["views"]),
        fmt_int(res_ago["reach"]),
        fmt_pct(res_ago["engagement_rate"], 2),
        fmt_int(res_ago["likes"]),
        fmt_int(res_ago["comments"]),
        fmt_int(res_ago["saves"]),
        fmt_int(res_ago["follows"]),
        fmt_float(res_ago["saves_por_1000"], 2),
        fmt_float(res_ago["follows_por_1000"], 2),
    ],
    "September": [
        fmt_int(res_set["posts"]),
        fmt_int(res_set["views"]),
        fmt_int(res_set["reach"]),
        fmt_pct(res_set["engagement_rate"], 2),
        fmt_int(res_set["likes"]),
        fmt_int(res_set["comments"]),
        fmt_int(res_set["saves"]),
        fmt_int(res_set["follows"]),
        fmt_float(res_set["saves_por_1000"], 2),
        fmt_float(res_set["follows_por_1000"], 2),
    ],
    "Change (%)": [fmt_var(x) for x in comparativo_bruto["Change_pct"]],
})

st.dataframe(comparativo, use_container_width=True, hide_index=True)

# Month-over-month change chart
delta_plot = comparativo_bruto.copy()
delta_plot["Direction"] = delta_plot["Change_pct"].apply(
    lambda x: "Up" if pd.notna(x) and x >= 0 else "Down"
)

fig_delta = px.bar(
    delta_plot.sort_values("Change_pct", ascending=True),
    x="Change_pct",
    y="Metric",
    orientation="h",
    text="Change_pct",
    color="Direction",
    title="Month-over-month change by KPI (%)",
    color_discrete_map={"Up": "#2ca02c", "Down": "#d62728"},
)
fig_delta.update_traces(texttemplate="%{text:.1f}%")
fig_delta.update_layout(
    template="simple_white",
    height=380,
    yaxis_title="",
    xaxis_title="Change (%)"
)
st.plotly_chart(fig_delta, use_container_width=True)

st.caption("Negative values highlight where September underperformed August and signal the main watchpoints for October.")

linha1_col1, linha1_col2 = st.columns(2)
linha2_col1, linha2_col2 = st.columns(2)

# 1) Reach posts
with linha1_col1:
    st.markdown("### 1) Reach posts")
    alcance = setembro[[
        "descricao_normalizada",
        "Views",
        "Reach",
        "Post type",
    ]].copy().sort_values("Views", ascending=False).head(5)
    alcance["short_text"] = alcance["descricao_normalizada"].astype(str).str.slice(0, 55)

    fig_alc = px.bar(
        alcance.sort_values("Views", ascending=True),
        x="Views",
        y="short_text",
        orientation="h",
        text="Views",
        title="Top 5 posts by views",
        color_discrete_sequence=["#C13584"]
    )
    fig_alc.update_layout(
        template="simple_white",
        height=380,
        yaxis_title="",
        xaxis_title="Views"
    )
    st.plotly_chart(fig_alc, use_container_width=True)

# 2) Engagement / quality posts
with linha1_col2:
    st.markdown("### 2) Engagement / quality posts")
    qualidade = setembro[[
        "descricao_normalizada",
        "engagement_rate",
        "likes_por_1000_views",
        "saves_por_1000_views",
        "score_qualidade_engajamento",
    ]].copy().sort_values("score_qualidade_engajamento", ascending=False).head(5)
    qualidade["short_text"] = qualidade["descricao_normalizada"].astype(str).str.slice(0, 55)

    fig_qual = px.bar(
        qualidade.sort_values("score_qualidade_engajamento", ascending=True),
        x="score_qualidade_engajamento",
        y="short_text",
        orientation="h",
        text="score_qualidade_engajamento",
        title="Top 5 posts by engagement quality score",
        color_discrete_sequence=["#111111"]
    )
    fig_qual.update_traces(texttemplate="%{text:.1f}")
    fig_qual.update_layout(
        template="simple_white",
        height=380,
        yaxis_title="",
        xaxis_title="Engagement quality score"
    )
    st.plotly_chart(fig_qual, use_container_width=True)
    st.caption("Engagement quality score = 40% engagement rate + 30% likes/1,000 views + 30% saves/1,000 views (ranking within September).")

# 3) Action (follows) posts
with linha2_col1:
    st.markdown("### 3) Action posts (follows)")
    acao = setembro[[
        "descricao_normalizada",
        "Follows",
        "follows_por_1000_reach",
        "Reach",
    ]].copy().sort_values("follows_por_1000_reach", ascending=False).head(5)
    acao["short_text"] = acao["descricao_normalizada"].astype(str).str.slice(0, 55)

    fig_acao = px.bar(
        acao.sort_values("follows_por_1000_reach", ascending=True),
        x="follows_por_1000_reach",
        y="short_text",
        orientation="h",
        text="follows_por_1000_reach",
        title="Top 5 posts by follows per 1,000 reach",
        color_discrete_sequence=["#006d77"]
    )
    fig_acao.update_traces(texttemplate="%{text:.2f}")
    fig_acao.update_layout(
        template="simple_white",
        height=380,
        yaxis_title="",
        xaxis_title="Follows per 1,000 reach"
    )
    st.plotly_chart(fig_acao, use_container_width=True)

# 4) Engagement vs action
with linha2_col2:
    st.markdown("### 4) Engagement vs action")
    fig_rel = px.scatter(
        setembro,
        x="score_qualidade_engajamento",
        y="follows_por_1000_reach",
        size="Reach",
        hover_name="descricao_normalizada",
        title="Engagement quality score vs follows per 1,000 reach",
        color_discrete_sequence=["#C13584"]
    )
    fig_rel.update_layout(
        template="simple_white",
        height=380,
        xaxis_title="Engagement quality score",
        yaxis_title="Follows per 1,000 reach"
    )
    st.plotly_chart(fig_rel, use_container_width=True)

# Highlights and executive reading
melhor_alc = setembro.loc[setembro["Views"].idxmax()]
melhor_qual = setembro.loc[setembro["score_qualidade_engajamento"].idxmax()]
melhor_follow = setembro.loc[setembro["follows_por_1000_reach"].idxmax()]

variacoes_dict = {
    "Views": pct_change(res_set["views"], res_ago["views"]),
    "Reach": pct_change(res_set["reach"], res_ago["reach"]),
    "Engagement rate": pct_change(res_set["engagement_rate"], res_ago["engagement_rate"]),
    "Saves per 1,000 views": pct_change(res_set["saves_por_1000"], res_ago["saves_por_1000"]),
    "Follows per 1,000 reach": pct_change(res_set["follows_por_1000"], res_ago["follows_por_1000"]),
}

quedas = {k: v for k, v in variacoes_dict.items() if v is not None and v < 0}
melhoras = {k: v for k, v in variacoes_dict.items() if v is not None and v > 0}

pior_metrica = min(quedas, key=quedas.get) if quedas else None
melhor_metrica = max(melhoras, key=melhoras.get) if melhoras else None

st.markdown("### Executive reading (August → September)")
st.markdown(f"- For reach, the September highlight was **'{melhor_alc['descricao_normalizada'][:90]}...'**, with {fmt_int(melhor_alc['Views'])} views and {fmt_int(melhor_alc['Reach'])} reach.")
st.markdown(f"- For proportional engagement, the strongest signal came from **'{melhor_qual['descricao_normalizada'][:90]}...'**, with an engagement quality score of {fmt_float(melhor_qual['score_qualidade_engajamento'],1)}.")
st.markdown(f"- For conversion to followers, the most efficient post was **'{melhor_follow['descricao_normalizada'][:90]}...'**, with {fmt_float(melhor_follow['follows_por_1000_reach'],2)} follows per 1,000 reach.")
if pior_metrica:
    st.markdown(f"- The largest month-over-month drop was in **{pior_metrica}** ({fmt_var(variacoes_dict[pior_metrica])}), which should be a priority to fix in October.")
if melhor_metrica:
    st.markdown(f"- The strongest relative gain was in **{melhor_metrica}** ({fmt_var(variacoes_dict[melhor_metrica])}), indicating an Instagram usage pattern to protect and scale.")

st.markdown("### Suggested actions for October")
st.markdown("- Use the posts with highest views/reach as references for topic and format to recover or scale reach.")
st.markdown("- Repeat patterns from posts that perform well on engagement quality score (high interaction rate and good combination of likes and saves).")
st.markdown("- Reserve posts focused on conversion, inspired by those with the highest follows per 1,000 reach.")
st.markdown("- If engagement rate dropped, adjust creatives to encourage more comments, saves and shares, especially on the highest-reach posts.")
st.markdown("- Assess whether the mix between reels, images and carousels is helping or hindering the combination of reach + engagement + follows.")

st.markdown("### September base")
tabela = setembro[[
    "Publish time",
    "Post type",
    "descricao_normalizada",
    "Views",
    "Reach",
    "Likes",
    "Comments",
    "Shares",
    "Saves",
    "Follows",
    "engagement_rate",
    "saves_por_1000_views",
    "follows_por_1000_reach",
]].copy()

tabela.rename(columns={
    "Publish time": "Date",
    "Post type": "Type",
    "descricao_normalizada": "Post",
    "Views": "Views",
    "Reach": "Reach",
    "Likes": "Likes",
    "Comments": "Comments",
    "Shares": "Shares",
    "Saves": "Saves",
    "Follows": "Follows",
    "engagement_rate": "Engagement rate",
    "saves_por_1000_views": "Saves per 1,000 views",
    "follows_por_1000_reach": "Follows per 1,000 reach",
}, inplace=True)

tabela = tabela.sort_values("Views", ascending=False)
st.dataframe(tabela, use_container_width=True, hide_index=True)