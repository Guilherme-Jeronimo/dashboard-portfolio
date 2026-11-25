from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="YouTube - Reach, Retention and Conversion", layout="wide")


ARQUIVOS_CANDIDATOS = [
    "YouTube_Aug-Sep_2025_dummy.xlsx",
    "YouTube_Aug-Sep_2025_dummy-5.xlsx",
    "data/YouTube_Aug-Sep_2025_dummy.xlsx",
    "data/YouTube_Aug-Sep_2025_dummy-5.xlsx",
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
    if pd.isna(x):
        return "-"
    return f"{int(round(x)):,}".replace(",", ".")


def fmt_float(x, dec=1):
    if x is None or pd.isna(x):
        return "-"
    return f"{x:.{dec}f}".replace(".", ",")


def fmt_pct(x, dec=1):
    if x is None or pd.isna(x):
        return "-"
    return f"{x:.{dec}f}%".replace(".", ",")


def fmt_var(x):
    if x is None or pd.isna(x):
        return "-"
    sinal = "+" if x >= 0 else ""
    return f"{sinal}{x:.1f}%".replace(".", ",")


def media_ponderada(df, col_valor, col_peso="Views"):
    base = df[[col_valor, col_peso]].copy()
    base = base.dropna()
    base = base[base[col_peso] > 0]
    if base.empty:
        return None
    return (base[col_valor] * base[col_peso]).sum() / base[col_peso].sum()


@st.cache_data
def carregar_dados():
    caminho = encontrar_arquivo()
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho)
    df["Video publish time"] = pd.to_datetime(df["Video publish time"], errors="coerce")
    df = df[df["Video publish time"].notna()].copy()

    df["chave_mes"] = df["Video publish time"].dt.strftime("%Y-%m")
    df = df[df["chave_mes"].isin(["2025-08", "2025-09"])].copy()

    colunas_numericas = [
        "Views",
        "Engaged views",
        "Average percentage viewed (%)",
        "Stayed to watch (%)",
        "Returning viewers",
        "Subscribers gained",
        "Watch time (hours)",
        "Impressions click-through rate (%)",
        "Unique viewers",
        "Likes",
        "Shares",
        "Comments added",
    ]

    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["engajamentos"] = (
        df["Likes"].fillna(0)
        + df["Shares"].fillna(0)
        + df["Comments added"].fillna(0)
    )

    df["engaged_view_rate"] = (
        df["Engaged views"] / df["Views"].replace(0, pd.NA)
    ) * 100

    df["returning_viewers_rate"] = (
        df["Returning viewers"] / df["Unique viewers"].replace(0, pd.NA)
    ) * 100

    df["subs_por_1000_views"] = (
        df["Subscribers gained"] / df["Views"].replace(0, pd.NA)
    ) * 1000

    return df, caminho


def resumo(df):
    soma_views = df["Views"].sum()
    soma_unique = df["Unique viewers"].sum()

    return {
        "views": soma_views,
        "engaged_views": df["Engaged views"].sum(),
        "subs": df["Subscribers gained"].sum(),
        "watch_time": df["Watch time (hours)"].sum(),
        "pct_medio_assistido": media_ponderada(df, "Average percentage viewed (%)", "Views"),
        "stayed_to_watch": media_ponderada(df, "Stayed to watch (%)", "Views"),
        "returning_rate": (df["Returning viewers"].sum() / soma_unique * 100) if soma_unique else None,
        "engaged_rate": (df["Engaged views"].sum() / soma_views * 100) if soma_views else None,
        "subs_por_1000": (df["Subscribers gained"].sum() / soma_views * 1000) if soma_views else None,
    }


df, caminho = carregar_dados()

st.title("YouTube - Reach, Retention and Conversion")
st.caption("Analytical view for September 2025")

if df is None:
    st.error("YouTube file not found.")
    st.stop()

agosto = df[df["chave_mes"] == "2025-08"].copy()
setembro = df[df["chave_mes"] == "2025-09"].copy()

res_ago = resumo(agosto)
res_set = resumo(setembro)

# score de qualidade por vídeo (dentro de setembro)
setembro["score_qualidade_retencao"] = (
    setembro["Average percentage viewed (%)"].rank(pct=True) * 0.4
    + setembro["Stayed to watch (%)"].rank(pct=True) * 0.3
    + setembro["engaged_view_rate"].rank(pct=True) * 0.3
) * 100

st.caption(f"Loaded file: {caminho}")

# KPIs principais
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Views", fmt_int(res_set["views"]), fmt_var(pct_change(res_set["views"], res_ago["views"])))
k2.metric("Engaged view rate", fmt_pct(res_set["engaged_rate"], 1), fmt_var(pct_change(res_set["engaged_rate"], res_ago["engaged_rate"])))
k3.metric("Stayed to watch (%)", fmt_pct(res_set["stayed_to_watch"], 1), fmt_var(pct_change(res_set["stayed_to_watch"], res_ago["stayed_to_watch"])))
k4.metric("Subscribers per 1,000 views", fmt_float(res_set["subs_por_1000"], 2), fmt_var(pct_change(res_set["subs_por_1000"], res_ago["subs_por_1000"])))
k5.metric("Average percentage viewed", fmt_pct(res_set["pct_medio_assistido"], 1), fmt_var(pct_change(res_set["pct_medio_assistido"], res_ago["pct_medio_assistido"])))

# Tabela agosto vs setembro
st.markdown("### August vs September")

comparativo_bruto = pd.DataFrame({
    "Metric": [
        "Views",
        "Engaged view rate",
        "Stayed to watch (%)",
        "Subscribers per 1,000 views",
        "Average percentage viewed",
        "Returning viewers rate",
    ],
    "Agosto_valor": [
        res_ago["views"],
        res_ago["engaged_rate"],
        res_ago["stayed_to_watch"],
        res_ago["subs_por_1000"],
        res_ago["pct_medio_assistido"],
        res_ago["returning_rate"],
    ],
    "Setembro_valor": [
        res_set["views"],
        res_set["engaged_rate"],
        res_set["stayed_to_watch"],
        res_set["subs_por_1000"],
        res_set["pct_medio_assistido"],
        res_set["returning_rate"],
    ],
})

comparativo_bruto["Variacao_pct"] = comparativo_bruto.apply(
    lambda row: pct_change(row["Setembro_valor"], row["Agosto_valor"]), axis=1
)

comparativo = pd.DataFrame({
    "Metric": comparativo_bruto["Metric"],
    "August": [
        fmt_int(res_ago["views"]),
        fmt_pct(res_ago["engaged_rate"], 1),
        fmt_pct(res_ago["stayed_to_watch"], 1),
        fmt_float(res_ago["subs_por_1000"], 2),
        fmt_pct(res_ago["pct_medio_assistido"], 1),
        fmt_pct(res_ago["returning_rate"], 1),
    ],
    "September": [
        fmt_int(res_set["views"]),
        fmt_pct(res_set["engaged_rate"], 1),
        fmt_pct(res_set["stayed_to_watch"], 1),
        fmt_float(res_set["subs_por_1000"], 2),
        fmt_pct(res_set["pct_medio_assistido"], 1),
        fmt_pct(res_set["returning_rate"], 1),
    ],
    "Change (%)": [fmt_var(x) for x in comparativo_bruto["Variacao_pct"]],
})

st.dataframe(comparativo, use_container_width=True, hide_index=True)

# Gráfico de variação por KPI
delta_plot = comparativo_bruto.copy()
delta_plot["Direction"] = delta_plot["Variacao_pct"].apply(
    lambda x: "Up" if pd.notna(x) and x >= 0 else "Down"
)

fig_delta = px.bar(
    delta_plot.sort_values("Variacao_pct", ascending=True),
    x="Variacao_pct",
    y="Metric",
    orientation="h",
    text="Variacao_pct",
    color="Direction",
    title="Month-over-month change by KPI (%)",
    color_discrete_map={"Up": "#2ca02c", "Down": "#d62728"},
)
fig_delta.update_traces(texttemplate="%{text:.1f}%")
fig_delta.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Change (%)")
st.plotly_chart(fig_delta, use_container_width=True)

st.caption("Negative values highlight where September underperformed August and should be prioritized for October.")

linha1_col1, linha1_col2 = st.columns(2)
linha2_col1, linha2_col2 = st.columns(2)

# 1) Reach
with linha1_col1:
    st.markdown("### 1) Reach videos")
    alcance = setembro[[
        "Video title", "Views", "Impressions click-through rate (%)", "Watch time (hours)"
    ]].copy().sort_values("Views", ascending=False).head(5)
    alcance["titulo_curto"] = alcance["Video title"].astype(str).str.slice(0, 50)

    fig_alc = px.bar(
        alcance.sort_values("Views", ascending=True),
        x="Views",
        y="titulo_curto",
        orientation="h",
        text="Views",
        title="Top 5 videos by reach (views)",
        color_discrete_sequence=["#cc0000"]
    )
    fig_alc.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Views")
    st.plotly_chart(fig_alc, use_container_width=True)

# 2) Retention / quality
with linha1_col2:
    st.markdown("### 2) Retention / quality videos")
    qualidade = setembro[[
        "Video title",
        "Average percentage viewed (%)",
        "Stayed to watch (%)",
        "engaged_view_rate",
        "score_qualidade_retencao",
    ]].copy().sort_values("score_qualidade_retencao", ascending=False).head(5)
    qualidade["titulo_curto"] = qualidade["Video title"].astype(str).str.slice(0, 50)

    fig_qual = px.bar(
        qualidade.sort_values("score_qualidade_retencao", ascending=True),
        x="score_qualidade_retencao",
        y="titulo_curto",
        orientation="h",
        text="score_qualidade_retencao",
        title="Top 5 videos by retention quality score",
        color_discrete_sequence=["#333333"]
    )
    fig_qual.update_traces(texttemplate="%{text:.1f}")
    fig_qual.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Quality score")
    st.plotly_chart(fig_qual, use_container_width=True)
    st.caption("Retention quality score = 40% average percentage viewed + 30% stayed to watch + 30% engaged view rate (ranking within September).")

# 3) Conversion
with linha2_col1:
    st.markdown("### 3) Conversion videos")
    conversao = setembro[[
        "Video title",
        "Subscribers gained",
        "subs_por_1000_views",
        "Returning viewers",
        "returning_viewers_rate"
    ]].copy().sort_values("subs_por_1000_views", ascending=False).head(5)
    conversao["titulo_curto"] = conversao["Video title"].astype(str).str.slice(0, 50)

    fig_conv = px.bar(
        conversao.sort_values("subs_por_1000_views", ascending=True),
        x="subs_por_1000_views",
        y="titulo_curto",
        orientation="h",
        text="subs_por_1000_views",
        title="Top 5 videos by proportional conversion (subs per 1,000 views)",
        color_discrete_sequence=["#006d77"]
    )
    fig_conv.update_traces(texttemplate="%{text:.2f}")
    fig_conv.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Subscribers per 1,000 views")
    st.plotly_chart(fig_conv, use_container_width=True)

# 4) Quality vs conversion
with linha2_col2:
    st.markdown("### 4) Quality vs conversion")
    fig_rel = px.scatter(
        setembro,
        x="score_qualidade_retencao",
        y="subs_por_1000_views",
        size="Views",
        hover_name="Video title",
        title="Retention quality score vs subs per 1,000 views",
        color_discrete_sequence=["#cc0000"]
    )
    fig_rel.update_layout(
        template="simple_white",
        height=380,
        xaxis_title="Retention quality score",
        yaxis_title="Subscribers per 1,000 views"
    )
    st.plotly_chart(fig_rel, use_container_width=True)

melhor_alc = setembro.loc[setembro["Views"].idxmax()]
melhor_qual = setembro.loc[setembro["score_qualidade_retencao"].idxmax()]
melhor_conv = setembro.loc[setembro["subs_por_1000_views"].idxmax()]

variacoes_dict = {
    "Views": pct_change(res_set["views"], res_ago["views"]),
    "Engaged view rate": pct_change(res_set["engaged_rate"], res_ago["engaged_rate"]),
    "Stayed to watch (%)": pct_change(res_set["stayed_to_watch"], res_ago["stayed_to_watch"]),
    "Subscribers per 1,000 views": pct_change(res_set["subs_por_1000"], res_ago["subs_por_1000"]),
    "Average percentage viewed": pct_change(res_set["pct_medio_assistido"], res_ago["pct_medio_assistido"]),
    "Returning viewers rate": pct_change(res_set["returning_rate"], res_ago["returning_rate"]),
}

quedas = {k: v for k, v in variacoes_dict.items() if v is not None and v < 0}
melhoras = {k: v for k, v in variacoes_dict.items() if v is not None and v > 0}

pior_metrica = min(quedas, key=quedas.get) if quedas else None
melhor_metrica = max(melhoras, key=melhoras.get) if melhoras else None

st.markdown("### Executive summary")
st.markdown(f"- For reach, the September highlight was **'{melhor_alc['Video title']}'**, with {fmt_int(melhor_alc['Views'])} views.")
st.markdown(f"- For consumption quality, the strongest signal came from **'{melhor_qual['Video title']}'**, with a retention quality score of {fmt_float(melhor_qual['score_qualidade_retencao'],1)}.")
st.markdown(f"- For proportional conversion, the highlight was **'{melhor_conv['Video title']}'**, with {fmt_float(melhor_conv['subs_por_1000_views'],2)} subscribers per 1,000 views.")
if pior_metrica:
    st.markdown(f"- The largest month-over-month drop was in **{pior_metrica}** ({fmt_var(variacoes_dict[pior_metrica])}), which should be a priority to fix in October.")
if melhor_metrica:
    st.markdown(f"- The most positive signal was **{melhor_metrica}** ({fmt_var(variacoes_dict[melhor_metrica])}), which is worth protecting and scaling in October.")

st.markdown("### Priorities for October")
st.markdown("- Recover reach with topics and formats that drive high-volume views without sacrificing consumption quality.")
st.markdown("- Scale formats that score well in retention quality and also convert proportionally into subscribers.")
st.markdown("- Use the largest negative month-over-month deltas as a guide for where to act first (e.g., if conversion dropped a lot, revisit CTAs and video type).")
st.markdown("- Avoid assuming that the video with the most views is automatically the best for loyalty; always look at retention and proportional conversion.")

st.markdown("### September base")
tabela = setembro[[
    "Video title",
    "Views",
    "Engaged views",
    "engaged_view_rate",
    "Average percentage viewed (%)",
    "Stayed to watch (%)",
    "score_qualidade_retencao",
    "Returning viewers",
    "returning_viewers_rate",
    "Subscribers gained",
    "subs_por_1000_views",
]].copy()

tabela.rename(columns={
    "Video title": "Video",
    "Engaged views": "Engaged views",
    "engaged_view_rate": "Engaged view rate (%)",
    "Average percentage viewed (%)": "Average percentage viewed",
    "Stayed to watch (%)": "Stayed to watch (%)",
    "score_qualidade_retencao": "Retention quality score",
    "Returning viewers": "Returning viewers",
    "returning_viewers_rate": "Returning viewers rate (%)",
    "Subscribers gained": "Subscribers gained",
    "subs_por_1000_views": "Subscribers per 1,000 views",
}, inplace=True)

tabela = tabela.sort_values("Views", ascending=False)
st.dataframe(tabela, use_container_width=True, hide_index=True)