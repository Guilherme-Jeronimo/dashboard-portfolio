from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Facebook - Reach, Engagement and Action", layout="wide")


ARQUIVOS_CANDIDATOS = [
    "Facebook_Aug-Sep_2025_dummy.xlsx",
    "data/Facebook_Aug-Sep_2025_dummy.xlsx",
]


def encontrar_arquivo():
    for nome in ARQUIVOS_CANDIDATOS:
        caminho = Path(nome)
        if caminho.exists():
            return caminho
    return None


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


def fmt_pct(x, dec=2):
    if x is None or pd.isna(x):
        return "-"
    return f"{x * 100:.{dec}f}%".replace(".", ",")


def normalizar_texto(titulo, descricao):
    titulo = "" if pd.isna(titulo) else str(titulo).replace("\n", " ").strip()
    descricao = "" if pd.isna(descricao) else str(descricao).replace("\n", " ").strip()

    if titulo and descricao and descricao not in titulo:
        return f"{titulo} {descricao}"
    if titulo:
        return titulo
    if descricao:
        return descricao
    return "(No text in post)"


def parse_publish_time(valor):
    if pd.isna(valor):
        return pd.NaT

    s = str(valor).strip()
    if not s:
        return pd.NaT

    # ISO yyyy-mm-dd HH:MM:SS
    if "-" in s[:10]:
        dt = pd.to_datetime(s, format="%Y-%m-%d %H:%M:%S", errors="coerce")
        if pd.notna(dt):
            return dt

    # Slash formats: month/day/year
    formatos_slash = [
        "%m/%d/%Y %H:%M",
        "%m/%d/%y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%y %H:%M:%S",
    ]
    for fmt in formatos_slash:
        dt = pd.to_datetime(s, format=fmt, errors="coerce")
        if pd.notna(dt):
            return dt

    return pd.to_datetime(s, errors="coerce")


def media_ponderada(df, col_valor, col_peso):
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

    # dates
    df["Publish time"] = df["Publish time"].apply(parse_publish_time)
    df = df[df["Publish time"].notna()].copy()

    df["ano"] = df["Publish time"].dt.year
    df["mes"] = df["Publish time"].dt.month

    # keep only September 2025
    df = df[(df["ano"] == 2025) & (df["mes"] == 9)].copy()

    colunas_numericas = [
        "Duration (sec)",
        "Views",
        "Reach",
        "Reactions, Comments and Shares",
        "Reactions",
        "Comments",
        "Shares",
        "Total clicks",
        "Other Clicks",
        "Matched Audience Targeting Consumption (Photo Click)",
        "Negative feedback from users: Hide all",
        "Seconds viewed",
        "Average Seconds viewed",
        "Estimated earnings (USD)",
        "Ad impressions",
        "Ad CPM (USD)",
    ]

    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in [
        "Views", "Reach", "Reactions", "Comments", "Shares",
        "Total clicks", "Average Seconds viewed", "Duration (sec)"
    ]:
        df[col] = df[col].fillna(0)

    # remove posts without delivery
    df = df[(df["Reach"] > 1) | (df["Views"] > 1)].copy()

    # text and type
    df["texto_post"] = df.apply(
        lambda row: normalizar_texto(row.get("Title"), row.get("Description")),
        axis=1
    )
    df["tipo_post"] = df["Post type"].fillna("No type").astype(str)

    # interactions and rates
    df["interacoes"] = (
        df["Reactions"].fillna(0)
        + df["Comments"].fillna(0)
        + df["Shares"].fillna(0)
    )

    df["engagement_rate"] = (
        df["interacoes"] / df["Reach"].replace(0, pd.NA)
    )

    df["clicks_por_1000_reach"] = (
        df["Total clicks"] / df["Reach"].replace(0, pd.NA)
    ) * 1000

    df["shares_por_1000_reach"] = (
        df["Shares"] / df["Reach"].replace(0, pd.NA)
    ) * 1000

    df["reactions_por_1000_reach"] = (
        df["Reactions"] / df["Reach"].replace(0, pd.NA)
    ) * 1000

    return df, caminho


def resumo(df):
    soma_views = df["Views"].sum()
    soma_reach = df["Reach"].sum()
    base_video = df[df["Views"] > 0].copy()

    return {
        "posts": len(df),
        "views": soma_views,
        "reach": soma_reach,
        "interacoes": df["interacoes"].sum(),
        "engagement_rate": (df["interacoes"].sum() / soma_reach) if soma_reach else None,
        "reactions": df["Reactions"].sum(),
        "comments": df["Comments"].sum(),
        "shares": df["Shares"].sum(),
        "clicks": df["Total clicks"].sum(),
        "clicks_por_1000": (df["Total clicks"].sum() / soma_reach * 1000) if soma_reach else None,
        "shares_por_1000": (df["Shares"].sum() / soma_reach * 1000) if soma_reach else None,
        "avg_seconds_viewed": media_ponderada(base_video, "Average Seconds viewed", "Views"),
    }


df, caminho = carregar_dados()

st.title("Facebook - Reach, Engagement and Action")
st.caption("Analytical view for September 2025")

if df is None or df.empty:
    st.error("There are no posts in September 2025 after cleaning.")
    st.stop()

res_set = resumo(df)

st.caption(f"Loaded file: {caminho}")
st.caption(f"Clean base: {len(df)} valid posts in September 2025.")

# Quality/engagement score within September
df["score_qualidade_engajamento"] = (
    df["engagement_rate"].rank(pct=True) * 0.4
    + df["reactions_por_1000_reach"].rank(pct=True) * 0.3
    + df["clicks_por_1000_reach"].rank(pct=True) * 0.3
) * 100

# Main KPIs (September only)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Posts", fmt_int(res_set["posts"]))
k2.metric("Views", fmt_int(res_set["views"]))
k3.metric("Reach", fmt_int(res_set["reach"]))
k4.metric("Engagement rate", fmt_pct(res_set["engagement_rate"], 2))
k5.metric("Clicks per 1,000 reach", fmt_float(res_set["clicks_por_1000"], 2))

st.metric(
    label="Average seconds viewed",
    value=fmt_seg(res_set["avg_seconds_viewed"], 1)
)

# Engagement rate by post (top 10 in reach)
st.markdown("### Engagement rate of the most distributed posts in September")

eng_top = df.copy()
eng_top["Engagement rate (%)"] = eng_top["engagement_rate"] * 100
eng_top = eng_top.sort_values("Reach", ascending=False).head(10)
eng_top["short_text"] = eng_top["texto_post"].astype(str).str.slice(0, 55)

fig_eng = px.bar(
    eng_top.sort_values("Engagement rate (%)", ascending=True),
    x="Engagement rate (%)",
    y="short_text",
    orientation="h",
    text="Engagement rate (%)",
    title="Engagement rate of the 10 posts with highest reach (September)",
    color_discrete_sequence=["#1877F2"]
)
fig_eng.update_traces(texttemplate="%{text:.1f}")
fig_eng.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Engagement rate (%)")
st.plotly_chart(fig_eng, use_container_width=True)

linha1_col1, linha1_col2 = st.columns(2)
linha2_col1, linha2_col2 = st.columns(2)

# 1) Reach posts
with linha1_col1:
    st.markdown("### 1) Reach posts")
    alcance = df[["texto_post", "Views", "Reach", "tipo_post"]].copy().sort_values("Views", ascending=False).head(5)
    alcance["short_text"] = alcance["texto_post"].astype(str).str.slice(0, 55)

    fig_alc = px.bar(
        alcance.sort_values("Views", ascending=True),
        x="Views",
        y="short_text",
        orientation="h",
        text="Views",
        title="Top 5 posts by views (September)",
        color_discrete_sequence=["#1877F2"]
    )
    fig_alc.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Views")
    st.plotly_chart(fig_alc, use_container_width=True)

# 2) Engagement / quality posts
with linha1_col2:
    st.markdown("### 2) Engagement / quality posts")
    qualidade = df[[
        "texto_post",
        "engagement_rate",
        "reactions_por_1000_reach",
        "clicks_por_1000_reach",
        "score_qualidade_engajamento",
    ]].copy().sort_values("score_qualidade_engajamento", ascending=False).head(5)
    qualidade["short_text"] = qualidade["texto_post"].astype(str).str.slice(0, 55)

    fig_qual = px.bar(
        qualidade.sort_values("score_qualidade_engajamento", ascending=True),
        x="score_qualidade_engajamento",
        y="short_text",
        orientation="h",
        text="score_qualidade_engajamento",
        title="Top 5 posts by engagement quality score (September)",
        color_discrete_sequence=["#111111"]
    )
    fig_qual.update_traces(texttemplate="%{text:.1f}")
    fig_qual.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Engagement quality score")
    st.plotly_chart(fig_qual, use_container_width=True)
    st.caption("Engagement quality score = 40% engagement rate + 30% reactions/1,000 reach + 30% clicks/1,000 reach.")

# 3) Qualified action posts
with linha2_col1:
    st.markdown("### 3) Qualified action posts")
    acao = df[[
        "texto_post",
        "Total clicks",
        "clicks_por_1000_reach",
        "Shares",
        "Comments",
    ]].copy().sort_values("clicks_por_1000_reach", ascending=False).head(5)
    acao["short_text"] = acao["texto_post"].astype(str).str.slice(0, 55)

    fig_acao = px.bar(
        acao.sort_values("clicks_por_1000_reach", ascending=True),
        x="clicks_por_1000_reach",
        y="short_text",
        orientation="h",
        text="clicks_por_1000_reach",
        title="Top 5 posts by clicks per 1,000 reach (September)",
        color_discrete_sequence=["#006d77"]
    )
    fig_acao.update_traces(texttemplate="%{text:.2f}")
    fig_acao.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Clicks per 1,000 reach")
    st.plotly_chart(fig_acao, use_container_width=True)

# 4) Engagement vs action
with linha2_col2:
    st.markdown("### 4) Engagement vs action")
    fig_rel = px.scatter(
        df,
        x="score_qualidade_engajamento",
        y="clicks_por_1000_reach",
        size="Reach",
        hover_name="texto_post",
        title="Engagement quality score vs clicks per 1,000 reach (September)",
        color_discrete_sequence=["#1877F2"]
    )
    fig_rel.update_layout(template="simple_white", height=380, xaxis_title="Engagement quality score", yaxis_title="Clicks per 1,000 reach")
    st.plotly_chart(fig_rel, use_container_width=True)

# Executive reading (September)
melhor_alc = df.loc[df["Views"].idxmax()]
melhor_qual = df.loc[df["score_qualidade_engajamento"].idxmax()]
melhor_acao = df.loc[df["clicks_por_1000_reach"].idxmax()]

st.markdown("### Executive reading for September")
st.markdown(f"- For reach, the highlight was **'{melhor_alc['texto_post'][:90]}...'**, with {fmt_int(melhor_alc['Views'])} views and {fmt_int(melhor_alc['Reach'])} reach.")
st.markdown(f"- For engagement quality, the strongest signal came from **'{melhor_qual['texto_post'][:90]}...'**, with an engagement quality score of {fmt_float(melhor_qual['score_qualidade_engajamento'],1)}.")
st.markdown(f"- For qualified action, the most efficient post was **'{melhor_acao['texto_post'][:90]}...'**, with {fmt_float(melhor_acao['clicks_por_1000_reach'],2)} clicks per 1,000 reach.")

st.markdown("### Suggested actions for October")
st.markdown("- Use the posts with highest views/reach as references for topic and format to scale reach.")
st.markdown("- Repeat patterns from posts with the highest engagement quality score to protect qualified engagement.")
st.markdown("- Reserve action-focused posts inspired by those that generate more clicks per 1,000 reach.")
st.markdown("- Adjust copy, CTA and first seconds of video to increase comments, reactions, shares and average seconds viewed.")

st.markdown("### September base")
tabela = df[[
    "Publish time", "tipo_post", "texto_post",
    "Views", "Reach",
    "Reactions", "Comments", "Shares",
    "Total clicks",
    "engagement_rate",
    "clicks_por_1000_reach",
    "Average Seconds viewed",
]].copy()

tabela.rename(columns={
    "Publish time": "Date",
    "tipo_post": "Type",
    "texto_post": "Post",
    "engagement_rate": "Engagement rate",
    "clicks_por_1000_reach": "Clicks per 1,000 reach",
    "Average Seconds viewed": "Average seconds viewed",
}, inplace=True)

tabela = tabela.sort_values("Views", ascending=False)
st.dataframe(tabela, use_container_width=True, hide_index=True)