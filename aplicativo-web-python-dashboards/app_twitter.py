from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Twitter/X - Reach, Interest and Conversion", layout="wide")


ARQUIVOS_CANDIDATOS = [
    "twitter_post_performance_dummy.xlsx",
    "twitter_post_performance_dummy-4.xlsx",
    "data/twitter_post_performance_dummy.xlsx",
    "data/twitter_post_performance_dummy-4.xlsx",
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


def fmt_pct(x, dec=2):
    if x is None or pd.isna(x):
        return "-"
    return f"{x:.{dec}f}%".replace(".", ",")


def fmt_var(x):
    if x is None or pd.isna(x):
        return "-"
    sinal = "+" if x >= 0 else ""
    return f"{sinal}{x:.1f}%".replace(".", ",")


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
        "Detail expands",
        "Engagement Rate",
        "Engagements",
        "Hashtag clicks",
        "Impressions",
        "Likes",
        "Link clicks",
        "Media views",
        "Permalink clicks",
        "Quote tweets",
        "Replies",
        "Retweets",
        "Shared via email",
        "User follows",
        "Profile clicks",
        "Video views",
    ]

    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # conversational social interactions
    df["interacoes_sociais"] = (
        df["Likes"].fillna(0)
        + df["Replies"].fillna(0)
        + df["Retweets"].fillna(0)
        + df["Quote tweets"].fillna(0)
    )

    # deep interest: open details, profile click, permalink click
    df["interesse_profundo"] = (
        df["Detail expands"].fillna(0)
        + df["Profile clicks"].fillna(0)
        + df["Permalink clicks"].fillna(0)
    )

    # rates per 1,000 impressions
    df["follows_por_mil_imp"] = (
        df["User follows"] / df["Impressions"].replace(0, pd.NA)
    ) * 1000

    df["engagements_por_mil_imp"] = (
        df["Engagements"] / df["Impressions"].replace(0, pd.NA)
    ) * 1000

    df["taxa_interesse_profundo"] = (
        df["interesse_profundo"] / df["Impressions"].replace(0, pd.NA)
    ) * 1000

    # profile click rate (for main KPI)
    df["profile_click_rate"] = (
        df["Profile clicks"] / df["Impressions"].replace(0, pd.NA)
    )

    return df, caminho


def resumo(df):
    imp_sum = df["Impressions"].sum()
    return {
        "posts": len(df),
        "impressions": imp_sum,
        "engagements": df["Engagements"].sum(),
        "eng_rate": df["Engagement Rate"].mean(),
        "profile_clicks": df["Profile clicks"].sum(),
        "link_clicks": df["Link clicks"].sum(),
        "follows": df["User follows"].sum(),
        "follows_por_mil": (df["User follows"].sum() / imp_sum * 1000) if imp_sum else None,
        "profile_click_rate": (df["Profile clicks"].sum() / imp_sum) if imp_sum else None,
        "deep_interest": df["interesse_profundo"].sum(),
        "deep_interest_rate": (df["interesse_profundo"].sum() / imp_sum * 1000) if imp_sum else None,
    }


df, caminho = carregar_dados()

st.title("Twitter/X - Reach, Interest and Conversion")
st.caption("Analytical view for September 2025")

if df is None:
    st.error("Twitter/X file not found.")
    st.stop()

agosto = df[df["chave_mes"] == "2025-08"].copy()
setembro = df[df["chave_mes"] == "2025-09"].copy()

res_ago = resumo(agosto)
res_set = resumo(setembro)

st.caption(f"Loaded file: {caminho}")

# Main KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(
    "Impressions",
    fmt_int(res_set["impressions"]),
    fmt_var(pct_change(res_set["impressions"], res_ago["impressions"]))
)
k2.metric(
    "Engagements",
    fmt_int(res_set["engagements"]),
    fmt_var(pct_change(res_set["engagements"], res_ago["engagements"]))
)
k3.metric(
    "Engagement rate",
    fmt_pct(res_set["eng_rate"], 2),
    fmt_var(pct_change(res_set["eng_rate"], res_ago["eng_rate"]))
)
k4.metric(
    "Profile clicks",
    fmt_int(res_set["profile_clicks"]),
    fmt_var(pct_change(res_set["profile_clicks"], res_ago["profile_clicks"]))
)
k5.metric(
    "Profile click rate",
    fmt_pct(res_set["profile_click_rate"] * 100, 2) if res_set["profile_click_rate"] is not None else "-",
    fmt_var(pct_change(res_set["profile_click_rate"], res_ago["profile_click_rate"]))
)

# August vs September comparison
st.markdown("### August vs September")

comparativo_bruto = pd.DataFrame({
    "Metric": [
        "Posts",
        "Impressions",
        "Engagements",
        "Engagement rate",
        "Profile clicks",
        "Profile click rate",
        "User follows",
        "Follows per 1,000 impressions",
        "Deep interest rate",
    ],
    "August_value": [
        res_ago["posts"],
        res_ago["impressions"],
        res_ago["engagements"],
        res_ago["eng_rate"],
        res_ago["profile_clicks"],
        res_ago["profile_click_rate"],
        res_ago["follows"],
        res_ago["follows_por_mil"],
        res_ago["deep_interest_rate"],
    ],
    "September_value": [
        res_set["posts"],
        res_set["impressions"],
        res_set["engagements"],
        res_set["eng_rate"],
        res_set["profile_clicks"],
        res_set["profile_click_rate"],
        res_set["follows"],
        res_set["follows_por_mil"],
        res_set["deep_interest_rate"],
    ],
})

comparativo_bruto["Change_pct"] = comparativo_bruto.apply(
    lambda row: pct_change(row["September_value"], row["August_value"]), axis=1
)

comparativo = pd.DataFrame({
    "Metric": comparativo_bruto["Metric"],
    "August": [
        fmt_int(res_ago["posts"]),
        fmt_int(res_ago["impressions"]),
        fmt_int(res_ago["engagements"]),
        fmt_pct(res_ago["eng_rate"], 2),
        fmt_int(res_ago["profile_clicks"]),
        fmt_pct(res_ago["profile_click_rate"] * 100, 2) if res_ago["profile_click_rate"] is not None else "-",
        fmt_int(res_ago["follows"]),
        fmt_float(res_ago["follows_por_mil"], 2),
        fmt_float(res_ago["deep_interest_rate"], 2),
    ],
    "September": [
        fmt_int(res_set["posts"]),
        fmt_int(res_set["impressions"]),
        fmt_int(res_set["engagements"]),
        fmt_pct(res_set["eng_rate"], 2),
        fmt_int(res_set["profile_clicks"]),
        fmt_pct(res_set["profile_click_rate"] * 100, 2) if res_set["profile_click_rate"] is not None else "-",
        fmt_int(res_set["follows"]),
        fmt_float(res_set["follows_por_mil"], 2),
        fmt_float(res_set["deep_interest_rate"], 2),
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
fig_delta.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Change (%)")
st.plotly_chart(fig_delta, use_container_width=True)

st.caption("Negative values highlight where September underperformed August and should be prioritized for October.")

linha1_col1, linha1_col2 = st.columns(2)
linha2_col1, linha2_col2 = st.columns(2)

# 1) Reach posts
with linha1_col1:
    st.markdown("### 1) Reach posts")
    alcance = setembro[[
        "Post Message", "Impressions", "Engagements", "Engagement Rate"
    ]].copy().sort_values("Impressions", ascending=False).head(5)
    alcance["short_text"] = alcance["Post Message"].astype(str).str.slice(0, 55)

    fig_alc = px.bar(
        alcance.sort_values("Impressions", ascending=True),
        x="Impressions",
        y="short_text",
        orientation="h",
        text="Impressions",
        title="Top 5 posts by impressions",
        color_discrete_sequence=["#1DA1F2"]
    )
    fig_alc.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Impressions")
    st.plotly_chart(fig_alc, use_container_width=True)

# 2) Engagement posts
with linha1_col2:
    st.markdown("### 2) Engagement posts")
    eng = setembro[[
        "Post Message", "Engagements", "Engagement Rate", "interacoes_sociais"
    ]].copy().sort_values("Engagements", ascending=False).head(5)
    eng["short_text"] = eng["Post Message"].astype(str).str.slice(0, 55)

    fig_eng = px.bar(
        eng.sort_values("Engagements", ascending=True),
        x="Engagements",
        y="short_text",
        orientation="h",
        text="Engagements",
        title="Top 5 posts by engagements",
        color_discrete_sequence=["#111111"]
    )
    fig_eng.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Engagements")
    st.plotly_chart(fig_eng, use_container_width=True)

# 3) Deep interest posts
with linha2_col1:
    st.markdown("### 3) Deep interest posts")
    interesse = setembro[[
        "Post Message", "Detail expands", "Profile clicks", "Permalink clicks", "taxa_interesse_profundo"
    ]].copy().sort_values("taxa_interesse_profundo", ascending=False).head(5)
    interesse["short_text"] = interesse["Post Message"].astype(str).str.slice(0, 55)

    fig_int = px.bar(
        interesse.sort_values("taxa_interesse_profundo", ascending=True),
        x="taxa_interesse_profundo",
        y="short_text",
        orientation="h",
        text="taxa_interesse_profundo",
        title="Top 5 posts by deep interest (per 1,000 impressions)",
        color_discrete_sequence=["#ff7f0e"]
    )
    fig_int.update_traces(texttemplate="%{text:.2f}")
    fig_int.update_layout(template="simple_white", height=380, yaxis_title="", xaxis_title="Deep interest actions per 1,000 impressions")
    st.plotly_chart(fig_int, use_container_width=True)
    st.caption("Deep interest = detail expands + profile clicks + permalink clicks, normalized per 1,000 impressions.")

# 4) Interest vs conversion
with linha2_col2:
    st.markdown("### 4) Interest vs conversion")
    fig_rel = px.scatter(
        setembro,
        x="Profile clicks",
        y="User follows",
        size="Impressions",
        hover_name="Post Message",
        title="Profile clicks vs user follows",
        color_discrete_sequence=["#1DA1F2"]
    )
    fig_rel.update_layout(
        template="simple_white",
        height=380,
        xaxis_title="Profile clicks",
        yaxis_title="User follows"
    )
    st.plotly_chart(fig_rel, use_container_width=True)

# September highlights
melhor_alc = setembro.loc[setembro["Impressions"].idxmax()]
melhor_eng = setembro.loc[setembro["Engagements"].idxmax()]
melhor_prof = setembro.loc[setembro["taxa_interesse_profundo"].idxmax()]
melhor_follow = setembro.loc[setembro["follows_por_mil_imp"].idxmax()]

variacoes_dict = {
    "Impressions": pct_change(res_set["impressions"], res_ago["impressions"]),
    "Engagements": pct_change(res_set["engagements"], res_ago["engagements"]),
    "Engagement rate": pct_change(res_set["eng_rate"], res_ago["eng_rate"]),
    "Profile click rate": pct_change(res_set["profile_click_rate"], res_ago["profile_click_rate"]),
    "Follows per 1,000 impressions": pct_change(res_set["follows_por_mil"], res_ago["follows_por_mil"]),
    "Deep interest rate": pct_change(res_set["deep_interest_rate"], res_ago["deep_interest_rate"]),
}

quedas = {k: v for k, v in variacoes_dict.items() if v is not None and v < 0}
melhoras = {k: v for k, v in variacoes_dict.items() if v is not None and v > 0}

pior_metrica = min(quedas, key=quedas.get) if quedas else None
melhor_metrica = max(melhoras, key=melhoras.get) if melhoras else None

# Executive reading
st.markdown("### Executive reading (August → September)")
st.markdown(f"- For reach, the September highlight was **'{str(melhor_alc['Post Message'])[:90]}...'**, with {fmt_int(melhor_alc['Impressions'])} impressions.")
st.markdown(f"- For raw engagements, the main post was **'{str(melhor_eng['Post Message'])[:90]}...'**, with {fmt_int(melhor_eng['Engagements'])} engagements.")
st.markdown(f"- For deep interest, the highlight was **'{str(melhor_prof['Post Message'])[:90]}...'**, with {fmt_float(melhor_prof['taxa_interesse_profundo'],2)} deep-interest actions per 1,000 impressions.")
st.markdown(f"- For proportional conversion, the post that best turned reach into follows was **'{str(melhor_follow['Post Message'])[:90]}...'**, with {fmt_float(melhor_follow['follows_por_mil_imp'],2)} follows per 1,000 impressions.")
if pior_metrica:
    st.markdown(f"- The largest month-over-month drop was in **{pior_metrica}** ({fmt_var(variacoes_dict[pior_metrica])}), which should be a priority to fix in October.")
if melhor_metrica:
    st.markdown(f"- The strongest relative gain was in **{melhor_metrica}** ({fmt_var(variacoes_dict[melhor_metrica])}), suggesting a Twitter/X use case to protect and scale.")

# Actions for October
st.markdown("### Suggested actions for October")
st.markdown("- Use the highest reach posts as references for topic and creative to recover impressions, without repeating the exact same piece.")
st.markdown("- Replicate patterns from posts with the highest deep interest (more profile clicks/detail expands) in threads and content that require detailed reading.")
st.markdown("- Reserve part of the calendar for conversion-focused posts, inspired by those with higher follows per 1,000 impressions.")
st.markdown("- Clearly differentiate awareness posts (aiming for reach) from action posts (aiming for clicks or follows) in the October plan.")
st.markdown("- Monitor early in the month whether engagement rate and profile click rate start to improve vs August/September, adjusting tone and format quickly if needed.")

# September base table
st.markdown("### September base")
tabela = setembro[[
    "Date (GMT)",
    "Post Type",
    "Post Message",
    "Impressions",
    "Engagements",
    "Engagement Rate",
    "Detail expands",
    "Profile clicks",
    "Link clicks",
    "User follows",
    "follows_por_mil_imp",
    "taxa_interesse_profundo",
]].copy()

tabela.rename(columns={
    "Date (GMT)": "Date",
    "Post Type": "Type",
    "Post Message": "Post",
    "Engagement Rate": "Engagement rate",
    "Detail expands": "Detail expands",
    "Profile clicks": "Profile clicks",
    "Link clicks": "Link clicks",
    "User follows": "User follows",
    "follows_por_mil_imp": "Follows per 1,000 impressions",
    "taxa_interesse_profundo": "Deep interest rate (per 1,000 imp.)",
}, inplace=True)

tabela = tabela.sort_values("Impressions", ascending=False)
st.dataframe(tabela, use_container_width=True, hide_index=True)