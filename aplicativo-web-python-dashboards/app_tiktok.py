from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="TikTok - Reach, Retention and Action", layout="wide")


ARQUIVOS_CANDIDATOS = [
    "tiktok_business_post_performance_dummy.xlsx",
    "tiktok_business_post_performance_dummy-3.xlsx",
    "data/tiktok_business_post_performance_dummy.xlsx",
    "data/tiktok_business_post_performance_dummy-3.xlsx",
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


def fmt_seg(x, dec=1):
    if x is None or pd.isna(x):
        return "-"
    return f"{x:.{dec}f}s".replace(".", ",")


def fmt_pct_ratio(x, dec=1):
    if x is None or pd.isna(x):
        return "-"
    return f"{x * 100:.{dec}f}%".replace(".", ",")


def fmt_var(x):
    if x is None or pd.isna(x):
        return "-"
    sinal = "+" if x >= 0 else ""
    return f"{sinal}{x:.1f}%".replace(".", ",")


def media_ponderada(df, col_valor, col_peso):
    base = df[[col_valor, col_peso]].copy()
    base = base.dropna()
    base = base[base[col_peso] > 0]
    if base.empty:
        return None
    return (base[col_valor] * base[col_peso]).sum() / base[col_peso].sum()


def normalizar_texto(x):
    if pd.isna(x):
        return "(No text in post)"
    x = str(x).strip()
    if x == "":
        return "(No text in post)"
    return x


@st.cache_data
def carregar_dados():
    caminho = encontrar_arquivo()
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho)
    df["Date (GMT)"] = pd.to_datetime(df["Date (GMT)"], errors="coerce")
    df = df[df["Date (GMT)"].notna()].copy()

    df["chave_mes"] = df["Date (GMT)"].dt.strftime("%Y-%m")
    df = df[df["chave_mes"].isin(["2025-08", "2025-09"])].copy()

    colunas_numericas = [
        "Average time watched",
        "Comments",
        "Engagement Rate",
        "Reactions",
        "Reach",
        "Shares",
        "Time watched",
        "Video Views",
        "Video views: Following",
        "Video views: For You",
        "Video views: Hashtag",
        "Video views: Profile",
        "Video views: Search",
        "Video views: Sound",
        "Full video watched rate",
    ]

    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["texto_post"] = df["Post Message"].apply(normalizar_texto)

    df["interacoes_totais"] = (
        df["Reactions"].fillna(0)
        + df["Comments"].fillna(0)
        + df["Shares"].fillna(0)
    )

    df["shares_por_1000_views"] = (
        df["Shares"] / df["Video Views"].replace(0, pd.NA)
    ) * 1000

    df["reacoes_por_1000_views"] = (
        df["Reactions"] / df["Video Views"].replace(0, pd.NA)
    ) * 1000

    df["comentarios_por_1000_views"] = (
        df["Comments"] / df["Video Views"].replace(0, pd.NA)
    ) * 1000

    return df, caminho


def resumo(df):
    soma_views = df["Video Views"].sum()
    soma_reach = df["Reach"].sum()

    return {
        "posts": len(df),
        "video_views": soma_views,
        "reach": soma_reach,
        "engagement_rate": media_ponderada(df, "Engagement Rate", "Reach"),
        "avg_time_watched": media_ponderada(df, "Average time watched", "Video Views"),
        "full_watch_rate": media_ponderada(df, "Full video watched rate", "Video Views"),
        "shares_por_1000": (df["Shares"].sum() / soma_views * 1000) if soma_views else None,
        "for_you_rate": media_ponderada(df, "Video views: For You", "Video Views"),
        "profile_view_rate": media_ponderada(df, "Video views: Profile", "Video Views"),
    }


df, caminho = carregar_dados()

st.title("TikTok - Reach, Retention and Action")
st.caption("Analytical view for September 2025")

if df is None:
    st.error("TikTok file not found.")
    st.stop()

agosto = df[df["chave_mes"] == "2025-08"].copy()
setembro = df[df["chave_mes"] == "2025-09"].copy()

res_ago = resumo(agosto)
res_set = resumo(setembro)

setembro["score_qualidade_retencao"] = (
    setembro["Average time watched"].rank(pct=True) * 0.4
    + setembro["Full video watched rate"].rank(pct=True) * 0.4
    + setembro["Engagement Rate"].rank(pct=True) * 0.2
) * 100

st.caption(f"Loaded file: {caminho}")

# Main KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(
    "Video views",
    fmt_int(res_set["video_views"]),
    fmt_var(pct_change(res_set["video_views"], res_ago["video_views"]))
)
k2.metric(
    "Reach",
    fmt_int(res_set["reach"]),
    fmt_var(pct_change(res_set["reach"], res_ago["reach"]))
)
k3.metric(
    "Engagement rate",
    fmt_pct_ratio(res_set["engagement_rate"], 2),
    fmt_var(pct_change(res_set["engagement_rate"], res_ago["engagement_rate"]))
)
k4.metric(
    "Average time watched",
    fmt_seg(res_set["avg_time_watched"], 1),
    fmt_var(pct_change(res_set["avg_time_watched"], res_ago["avg_time_watched"]))
)
k5.metric(
    "Full video watched rate",
    fmt_pct_ratio(res_set["full_watch_rate"], 2),
    fmt_var(pct_change(res_set["full_watch_rate"], res_ago["full_watch_rate"]))
)

# August vs September comparison
st.markdown("### August vs September")

comparativo_bruto = pd.DataFrame({
    "Metric": [
        "Posts",
        "Video views",
        "Reach",
        "Engagement rate",
        "Average time watched",
        "Full video watched rate",
        "Shares per 1,000 views",
        "For You rate",
    ],
    "August_value": [
        res_ago["posts"],
        res_ago["video_views"],
        res_ago["reach"],
        res_ago["engagement_rate"],
        res_ago["avg_time_watched"],
        res_ago["full_watch_rate"],
        res_ago["shares_por_1000"],
        res_ago["for_you_rate"],
    ],
    "September_value": [
        res_set["posts"],
        res_set["video_views"],
        res_set["reach"],
        res_set["engagement_rate"],
        res_set["avg_time_watched"],
        res_set["full_watch_rate"],
        res_set["shares_por_1000"],
        res_set["for_you_rate"],
    ],
})

comparativo_bruto["Change_pct"] = comparativo_bruto.apply(
    lambda row: pct_change(row["September_value"], row["August_value"]), axis=1
)

comparativo = pd.DataFrame({
    "Metric": comparativo_bruto["Metric"],
    "August": [
        fmt_int(res_ago["posts"]),
        fmt_int(res_ago["video_views"]),
        fmt_int(res_ago["reach"]),
        fmt_pct_ratio(res_ago["engagement_rate"], 2),
        fmt_seg(res_ago["avg_time_watched"], 1),
        fmt_pct_ratio(res_ago["full_watch_rate"], 2),
        fmt_float(res_ago["shares_por_1000"], 2),
        fmt_pct_ratio(res_ago["for_you_rate"], 1),
    ],
    "September": [
        fmt_int(res_set["posts"]),
        fmt_int(res_set["video_views"]),
        fmt_int(res_set["reach"]),
        fmt_pct_ratio(res_set["engagement_rate"], 2),
        fmt_seg(res_set["avg_time_watched"], 1),
        fmt_pct_ratio(res_set["full_watch_rate"], 2),
        fmt_float(res_set["shares_por_1000"], 2),
        fmt_pct_ratio(res_set["for_you_rate"], 1),
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

st.caption("Negative values highlight where September underperformed August and point to the main focus areas for October.")

linha1_col1, linha1_col2 = st.columns(2)
linha2_col1, linha2_col2 = st.columns(2)

# 1) Reach
with linha1_col1:
    st.markdown("### 1) Reach videos")
    alcance = setembro[[
        "texto_post", "Video Views", "Reach", "Video views: For You"
    ]].copy().sort_values("Video Views", ascending=False).head(5)
    alcance["short_text"] = alcance["texto_post"].astype(str).str.slice(0, 55)

    fig_alc = px.bar(
        alcance.sort_values("Video Views", ascending=True),
        x="Video Views",
        y="short_text",
        orientation="h",
        text="Video Views",
        title="Top 5 videos by reach (video views)",
        color_discrete_sequence=["#111111"]
    )
    fig_alc.update_layout(
        template="simple_white",
        height=380,
        yaxis_title="",
        xaxis_title="Video views"
    )
    st.plotly_chart(fig_alc, use_container_width=True)

# 2) Retention / quality
with linha1_col2:
    st.markdown("### 2) Retention / quality videos")
    qualidade = setembro[[
        "texto_post",
        "Average time watched",
        "Full video watched rate",
        "Engagement Rate",
        "score_qualidade_retencao",
    ]].copy().sort_values("score_qualidade_retencao", ascending=False).head(5)
    qualidade["short_text"] = qualidade["texto_post"].astype(str).str.slice(0, 55)

    fig_qual = px.bar(
        qualidade.sort_values("score_qualidade_retencao", ascending=True),
        x="score_qualidade_retencao",
        y="short_text",
        orientation="h",
        text="score_qualidade_retencao",
        title="Top 5 videos by quality score",
        color_discrete_sequence=["#333333"]
    )
    fig_qual.update_traces(texttemplate="%{text:.1f}")
    fig_qual.update_layout(
        template="simple_white",
        height=380,
        yaxis_title="",
        xaxis_title="Quality score"
    )
    st.plotly_chart(fig_qual, use_container_width=True)
    st.caption("Quality score = 40% average time watched + 40% full video watched rate + 20% engagement rate (ranking within September).")

# 3) Qualified action
with linha2_col1:
    st.markdown("### 3) Qualified action videos")
    acao = setembro[[
        "texto_post",
        "Shares",
        "shares_por_1000_views",
        "Comments",
        "Reactions",
    ]].copy().sort_values("shares_por_1000_views", ascending=False).head(5)
    acao["short_text"] = acao["texto_post"].astype(str).str.slice(0, 55)

    fig_acao = px.bar(
        acao.sort_values("shares_por_1000_views", ascending=True),
        x="shares_por_1000_views",
        y="short_text",
        orientation="h",
        text="shares_por_1000_views",
        title="Top 5 videos by shares per 1,000 views",
        color_discrete_sequence=["#006d77"]
    )
    fig_acao.update_traces(texttemplate="%{text:.2f}")
    fig_acao.update_layout(
        template="simple_white",
        height=380,
        yaxis_title="",
        xaxis_title="Shares per 1,000 views"
    )
    st.plotly_chart(fig_acao, use_container_width=True)

# 4) Quality vs action
with linha2_col2:
    st.markdown("### 4) Quality vs action")
    fig_rel = px.scatter(
        setembro,
        x="score_qualidade_retencao",
        y="shares_por_1000_views",
        size="Video Views",
        hover_name="texto_post",
        title="Quality score vs shares per 1,000 views",
        color_discrete_sequence=["#111111"]
    )
    fig_rel.update_layout(
        template="simple_white",
        height=380,
        xaxis_title="Quality score",
        yaxis_title="Shares per 1,000 views"
    )
    st.plotly_chart(fig_rel, use_container_width=True)

melhor_alc = setembro.loc[setembro["Video Views"].idxmax()]
melhor_qual = setembro.loc[setembro["score_qualidade_retencao"].idxmax()]
melhor_acao = setembro.loc[setembro["shares_por_1000_views"].idxmax()]

variacoes_dict = {
    "Video views": pct_change(res_set["video_views"], res_ago["video_views"]),
    "Reach": pct_change(res_set["reach"], res_ago["reach"]),
    "Engagement rate": pct_change(res_set["engagement_rate"], res_ago["engagement_rate"]),
    "Average time watched": pct_change(res_set["avg_time_watched"], res_ago["avg_time_watched"]),
    "Full video watched rate": pct_change(res_set["full_watch_rate"], res_ago["full_watch_rate"]),
    "Shares per 1,000 views": pct_change(res_set["shares_por_1000"], res_ago["shares_por_1000"]),
    "For You rate": pct_change(res_set["for_you_rate"], res_ago["for_you_rate"]),
}

st.markdown("### Executive reading (August → September)")
st.markdown(f"- The main reach peak in September came from **'{melhor_alc['texto_post'][:90]}...'**, with {fmt_int(melhor_alc['Video Views'])} video views.")
st.markdown(f"- The strongest retention/quality signal came from **'{melhor_qual['texto_post'][:90]}...'**, with a quality score of {fmt_float(melhor_qual['score_qualidade_retencao'],1)}.")
st.markdown(f"- For qualified action, the biggest highlight was **'{melhor_acao['texto_post'][:90]}...'**, with {fmt_float(melhor_acao['shares_por_1000_views'],2)} shares per 1,000 views.")
st.markdown(f"- Video views changed by {fmt_var(variacoes_dict['Video views'])}, while reach changed by {fmt_var(variacoes_dict['Reach'])}.")
st.markdown(f"- In depth of consumption, average time watched moved {fmt_var(variacoes_dict['Average time watched'])} and full video watched rate moved {fmt_var(variacoes_dict['Full video watched rate'])}.")
st.markdown(f"- In algorithmic distribution, the weight of For You changed by {fmt_var(variacoes_dict['For You rate'])}, which helps understand if September gained or lost discovery traction.")

st.markdown("### Suggested actions for October")
st.markdown("- Use the highest reach videos as references for topic, hook and language to recover or expand discovery.")
st.markdown("- Reinforce formats with better quality score, because on TikTok reach without retention tends to lose strength quickly.")
st.markdown("- Prioritize videos with more shares per 1,000 views when the goal is organic propagation.")
st.markdown("- If the For You rate drops, review the first seconds, pacing and clarity of the video promise.")
st.markdown("- If average time watched and full watch rate decline, reduce dispersion and accelerate delivery of the payoff.")
st.markdown("- Separate in the content calendar discovery videos, retention videos and action videos, instead of expecting every piece to play all roles.")

st.markdown("### September base")
tabela = setembro[[
    "Date (GMT)",
    "Post Type",
    "texto_post",
    "Video Views",
    "Reach",
    "Engagement Rate",
    "Average time watched",
    "Full video watched rate",
    "Shares",
    "shares_por_1000_views",
    "Video views: For You",
    "Video views: Profile",
    "Video views: Search",
]].copy()

tabela.rename(columns={
    "Date (GMT)": "Date",
    "Post Type": "Type",
    "texto_post": "Post",
    "Video Views": "Video views",
    "Reach": "Reach",
    "Engagement Rate": "Engagement rate",
    "Average time watched": "Average time watched (s)",
    "Full video watched rate": "Full video watched rate",
    "Shares": "Shares",
    "shares_por_1000_views": "Shares per 1,000 views",
    "Video views: For You": "For You rate",
    "Video views: Profile": "Profile rate",
    "Video views: Search": "Search rate",
}, inplace=True)

tabela = tabela.sort_values("Video views", ascending=False)
st.dataframe(tabela, use_container_width=True, hide_index=True)