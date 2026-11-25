from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Valorant · Social Media Performance · Sep 2025",
    layout="wide"
)


# -----------------------------
# Utilities
# -----------------------------

def encontrar_arquivo(caminhos):
    for nome in caminhos:
        caminho = Path(nome)
        if caminho.exists():
            return caminho
    return None


def fmt_int(x):
    if x is None or pd.isna(x):
        return "-"
    return f"{int(round(float(x))):,}".replace(",", ".")


def fmt_float(x, dec=2):
    if x is None or pd.isna(x):
        return "-"
    return f"{float(x):.{dec}f}".replace(".", ",")


def fmt_pct(x, dec=2):
    if x is None or pd.isna(x):
        return "-"
    return f"{float(x) * 100:.{dec}f}%".replace(".", ",")


def fmt_seg(x, dec=1):
    if x is None or pd.isna(x):
        return "-"
    return f"{float(x):.{dec}f}s".replace(".", ",")


def pct_change(novo, antigo):
    if antigo is None or pd.isna(antigo) or antigo == 0:
        return None
    return ((novo - antigo) / antigo) * 100


def fmt_var(x):
    if x is None or pd.isna(x):
        return "-"
    sinal = "+" if x >= 0 else ""
    return f"{sinal}{float(x):.1f}%".replace(".", ",")


def media_ponderada(df, col_valor, col_peso):
    base = df[[col_valor, col_peso]].copy()
    base = base.dropna()
    base = base[base[col_peso] > 0]
    if base.empty:
        return None
    return (base[col_valor] * base[col_peso]).sum() / base[col_peso].sum()


# -----------------------------
# Platform loaders (September)
# -----------------------------

@st.cache_data
def load_facebook():
    caminhos = [
        "Facebook_Aug-Sep_2025_dummy.xlsx",
        "data/Facebook_Aug-Sep_2025_dummy.xlsx",
    ]
    caminho = encontrar_arquivo(caminhos)
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho)
    df["Publish time"] = pd.to_datetime(df["Publish time"], errors="coerce")
    df = df[df["Publish time"].notna()].copy()
    df["ano"] = df["Publish time"].dt.year
    df["mes"] = df["Publish time"].dt.month
    df = df[(df["ano"] == 2025) & (df["mes"] == 9)].copy()

    for col in ["Views", "Reach", "Reactions", "Comments", "Shares", "Total clicks"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["interacoes"] = df["Reactions"] + df["Comments"] + df["Shares"]
    df["engagement_rate"] = df["interacoes"] / df["Reach"].replace(0, pd.NA)
    df["clicks_por_1000_reach"] = (
        df["Total clicks"] / df["Reach"].replace(0, pd.NA)
    ) * 1000

    return df, caminho


@st.cache_data
def load_instagram():
    caminhos = [
        "Instagram_Aug-Sep_2025_dummy.xlsx",
        "Instagram_Aug-Sep_2025_dummy-2.xlsx",
        "data/Instagram_Aug-Sep_2025_dummy.xlsx",
        "data/Instagram_Aug-Sep_2025_dummy-2.xlsx",
    ]
    caminho = encontrar_arquivo(caminhos)
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho, sheet_name=0)
    df["Publish time"] = pd.to_datetime(df["Publish time"], errors="coerce")
    df = df[df["Publish time"].notna()].copy()
    df["ano"] = df["Publish time"].dt.year
    df["mes"] = df["Publish time"].dt.month
    df = df[(df["ano"] == 2025) & (df["mes"] == 9)].copy()

    for col in ["Views", "Likes", "Shares", "Comments", "Saves", "Reach", "Follows"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["interacoes"] = (
        df["Likes"] + df["Comments"] + df["Shares"] + df["Saves"]
    )
    df["engagement_rate"] = df["interacoes"] / df["Reach"].replace(0, pd.NA)
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


@st.cache_data
def load_tiktok():
    caminhos = [
        "tiktok_business_post_performance_dummy.xlsx",
        "tiktok_business_post_performance_dummy-3.xlsx",
        "data/tiktok_business_post_performance_dummy.xlsx",
        "data/tiktok_business_post_performance_dummy-3.xlsx",
    ]
    caminho = encontrar_arquivo(caminhos)
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho)
    df["Date (GMT)"] = pd.to_datetime(df["Date (GMT)"], errors="coerce")
    df = df[df["Date (GMT)"].notna()].copy()
    df["ano"] = df["Date (GMT)"].dt.year
    df["mes"] = df["Date (GMT)"].dt.month
    df = df[(df["ano"] == 2025) & (df["mes"] == 9)].copy()

    cols = [
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
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["interacoes_totais"] = (
        df["Reactions"].fillna(0)
        + df["Comments"].fillna(0)
        + df["Shares"].fillna(0)
    )
    df["shares_por_1000_views"] = (
        df["Shares"] / df["Video Views"].replace(0, pd.NA)
    ) * 1000

    return df, caminho


@st.cache_data
def load_youtube():
    caminhos = [
        "YouTube_Aug-Sep_2025_dummy.xlsx",
        "YouTube_Aug-Sep_2025_dummy-5.xlsx",
        "data/YouTube_Aug-Sep_2025_dummy.xlsx",
    ]
    caminho = encontrar_arquivo(caminhos)
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho)
    df["Video publish time"] = pd.to_datetime(df["Video publish time"], errors="coerce")
    df = df[df["Video publish time"].notna()].copy()
    df["ano"] = df["Video publish time"].dt.year
    df["mes"] = df["Video publish time"].dt.month
    df = df[(df["ano"] == 2025) & (df["mes"] == 9)].copy()

    for col in ["Views", "Impressions", "Likes", "Comments", "Shares", "Subscribers gained"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    df["Reach"] = df["Impressions"] if "Impressions" in df.columns else df["Views"]
    df["interacoes"] = df["Likes"] + df["Comments"] + df["Shares"]
    df["engagement_rate"] = df["interacoes"] / df["Reach"].replace(0, pd.NA)

    return df, caminho


@st.cache_data
def load_twitter():
    caminhos = [
        "twitter_post_performance_dummy.xlsx",
        "twitter_post_performance_dummy-4.xlsx",
        "data/twitter_post_performance_dummy.xlsx",
    ]
    caminho = encontrar_arquivo(caminhos)
    if caminho is None:
        return None, None

    df = pd.read_excel(caminho, sheet_name=0)
    if "Date (GMT)" not in df.columns or "Impressions" not in df.columns:
        return None, None

    df["Date (GMT)"] = pd.to_datetime(df["Date (GMT)"], errors="coerce")
    df = df[df["Date (GMT)"].notna()].copy()
    df["ano"] = df["Date (GMT)"].dt.year
    df["mes"] = df["Date (GMT)"].dt.month
    df = df[(df["ano"] == 2025) & (df["mes"] == 9)].copy()

    for col in [
        "Impressions",
        "Likes",
        "Replies",
        "Retweets",
        "Profile clicks",
        "Link clicks",
        "Engagements",
    ]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        else:
            df[col] = 0

    df["Reach"] = df["Impressions"]
    if "Engagement Rate" in df.columns:
        df["engagement_rate"] = pd.to_numeric(df["Engagement Rate"], errors="coerce")
    else:
        df["engagement_rate"] = df["Engagements"] / df["Reach"].replace(0, pd.NA)

    df["interacoes"] = df["Engagements"]
    df["clicks_totais"] = df["Profile clicks"] + df["Link clicks"]

    return df, caminho


# --------------------------------------------------
# CROSS-PLATFORM PAGE
# --------------------------------------------------

def pagina_cross():
    fb_df, _ = load_facebook()
    ig_df, _ = load_instagram()
    tk_df, _ = load_tiktok()
    yt_df, _ = load_youtube()
    tw_df, _ = load_twitter()

    resumos = []

    if fb_df is not None:
        resumos.append({
            "plataforma": "Facebook",
            "posts": len(fb_df),
            "alcance_views": fb_df["Views"].sum(),
            "alcance_reach": fb_df["Reach"].sum(),
            "engagement_rate": (fb_df["interacoes"].sum() / fb_df["Reach"].sum()) if fb_df["Reach"].sum() else None,
            "engagement_int": fb_df["interacoes"].sum(),
            "acao_principal": fb_df["Total clicks"].sum(),
            "acao_por_1000_reach": (fb_df["Total clicks"].sum() / fb_df["Reach"].sum() * 1000) if fb_df["Reach"].sum() else None,
        })

    if ig_df is not None:
        resumos.append({
            "plataforma": "Instagram",
            "posts": len(ig_df),
            "alcance_views": ig_df["Views"].sum(),
            "alcance_reach": ig_df["Reach"].sum(),
            "engagement_rate": (ig_df["interacoes"].sum() / ig_df["Reach"].sum()) if ig_df["Reach"].sum() else None,
            "engagement_int": ig_df["interacoes"].sum(),
            "acao_principal": ig_df["Follows"].sum(),
            "acao_por_1000_reach": (ig_df["Follows"].sum() / ig_df["Reach"].sum() * 1000) if ig_df["Reach"].sum() else None,
        })

    if tk_df is not None:
        resumos.append({
            "plataforma": "TikTok",
            "posts": len(tk_df),
            "alcance_views": tk_df["Video Views"].sum(),
            "alcance_reach": tk_df["Reach"].sum(),
            "engagement_rate": tk_df["Engagement Rate"].mean() if len(tk_df) else None,
            "engagement_int": tk_df["interacoes_totais"].sum(),
            "acao_principal": tk_df["Shares"].sum(),
            "acao_por_1000_reach": (tk_df["Shares"].sum() / tk_df["Reach"].sum() * 1000) if tk_df["Reach"].sum() else None,
        })

    if yt_df is not None:
        resumos.append({
            "plataforma": "YouTube",
            "posts": len(yt_df),
            "alcance_views": yt_df["Views"].sum(),
            "alcance_reach": yt_df["Reach"].sum(),
            "engagement_rate": (yt_df["interacoes"].sum() / yt_df["Reach"].sum()) if yt_df["Reach"].sum() else None,
            "engagement_int": yt_df["interacoes"].sum(),
            "acao_principal": yt_df["Subscribers gained"].sum(),
            "acao_por_1000_reach": (yt_df["Subscribers gained"].sum() / yt_df["Reach"].sum() * 1000) if yt_df["Reach"].sum() else None,
        })

    if tw_df is not None:
        resumos.append({
            "plataforma": "X / Twitter",
            "posts": len(tw_df),
            "alcance_views": tw_df["Reach"].sum(),
            "alcance_reach": tw_df["Reach"].sum(),
            "engagement_rate": tw_df["engagement_rate"].mean() if len(tw_df) else None,
            "engagement_int": tw_df["interacoes"].sum(),
            "acao_principal": tw_df["clicks_totais"].sum(),
            "acao_por_1000_reach": (tw_df["clicks_totais"].sum() / tw_df["Reach"].sum() * 1000) if tw_df["Reach"].sum() else None,
        })

    if not resumos:
        st.error("No platform was loaded.")
        return

    df_cross = pd.DataFrame(resumos)

    def normaliza(col):
        serie = df_cross[col].copy()
        if serie.isna().all():
            return [None] * len(serie)
        mn, mx = serie.min(), serie.max()
        if mn == mx:
            return [0.5] * len(serie)
        return (serie - mn) / (mx - mn)

    df_cross["score_alcance"] = normaliza("alcance_reach")
    df_cross["score_engajamento"] = normaliza("engagement_rate")
    df_cross["score_acao"] = normaliza("acao_por_1000_reach")

    peso_alcance = 0.3
    peso_engajamento = 0.3
    peso_acao = 0.4

    df_cross["score_total"] = (
        df_cross["score_alcance"] * peso_alcance
        + df_cross["score_engajamento"] * peso_engajamento
        + df_cross["score_acao"] * peso_acao
    )

    st.title("Cross-platform - Reach, Engagement and Action")
    st.caption("Platform comparison for September 2025 (organic data).")

    tabela = df_cross[[
        "plataforma",
        "posts",
        "alcance_views",
        "alcance_reach",
        "engagement_rate",
        "engagement_int",
        "acao_principal",
        "acao_por_1000_reach",
        "score_total",
    ]].copy()

    tabela.rename(columns={
        "plataforma": "Platform",
        "posts": "Posts",
        "alcance_views": "Views / Plays",
        "alcance_reach": "Reach / Impressions",
        "engagement_rate": "Engagement rate",
        "engagement_int": "Total interactions",
        "acao_principal": "Main action (follows/clicks/etc.)",
        "acao_por_1000_reach": "Action per 1,000 reach",
        "score_total": "Total score",
    }, inplace=True)

    tabela["Views / Plays"] = tabela["Views / Plays"].apply(fmt_int)
    tabela["Reach / Impressions"] = tabela["Reach / Impressions"].apply(fmt_int)
    tabela["Total interactions"] = tabela["Total interactions"].apply(fmt_int)
    tabela["Main action (follows/clicks/etc.)"] = tabela["Main action (follows/clicks/etc.)"].apply(fmt_int)
    tabela["Engagement rate"] = tabela["Engagement rate"].apply(lambda x: fmt_pct(x, 2))
    tabela["Action per 1,000 reach"] = tabela["Action per 1,000 reach"].apply(lambda x: fmt_float(x, 2))
    tabela["Total score"] = tabela["Total score"].apply(lambda x: fmt_float(x, 2))

    st.markdown("### Platform overview (September)")
    st.dataframe(tabela, use_container_width=True, hide_index=True)

    st.markdown("### Total score by platform")
    fig_score = px.bar(
        df_cross.sort_values("score_total", ascending=True),
        x="score_total",
        y="plataforma",
        orientation="h",
        text="score_total",
        color="plataforma",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_score.update_traces(texttemplate="%{text:.2f}")
    fig_score.update_layout(template="simple_white", height=380, xaxis_title="Total score (0–1)", yaxis_title="")
    st.plotly_chart(fig_score, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Reach")
        fig_alc = px.bar(
            df_cross.sort_values("alcance_reach", ascending=False),
            x="plataforma",
            y="alcance_reach",
            text="alcance_reach",
            color="plataforma",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_alc.update_traces(texttemplate="%{text}", textposition="outside")
        fig_alc.update_layout(template="simple_white", height=350, yaxis_title="Reach / Impressions")
        st.plotly_chart(fig_alc, use_container_width=True)

    with col2:
        st.markdown("#### Proportional engagement")
        fig_eng = px.bar(
            df_cross.sort_values("engagement_rate", ascending=False),
            x="plataforma",
            y="engagement_rate",
            text="engagement_rate",
            color="plataforma",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_eng.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_eng.update_layout(template="simple_white", height=350, yaxis_title="Engagement rate")
        st.plotly_chart(fig_eng, use_container_width=True)

    with col3:
        st.markdown("#### Action per 1,000 reach")
        fig_acao = px.bar(
            df_cross.sort_values("acao_por_1000_reach", ascending=False),
            x="plataforma",
            y="acao_por_1000_reach",
            text="acao_por_1000_reach",
            color="plataforma",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig_acao.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig_acao.update_layout(template="simple_white", height=350, yaxis_title="Action per 1,000 reach")
        st.plotly_chart(fig_acao, use_container_width=True)

    st.markdown("### Cross-platform executive reading")

    melhor_score = df_cross.loc[df_cross["score_total"].idxmax(), "plataforma"]
    pior_score = df_cross.loc[df_cross["score_total"].idxmin(), "plataforma"]
    melhor_acao = df_cross.loc[df_cross["acao_por_1000_reach"].idxmax(), "plataforma"]
    melhor_alcance = df_cross.loc[df_cross["alcance_reach"].idxmax(), "plataforma"]
    melhor_eng = df_cross.loc[df_cross["engagement_rate"].idxmax(), "plataforma"]

    st.markdown(f"- Platform with highest **value/impact generation** (total score): **{melhor_score}**.")
    st.markdown(f"- Highest raw reach: **{melhor_alcance}** (strong discovery engine).")
    st.markdown(f"- Best engagement rate: **{melhor_eng}**, signalling a warmer audience.")
    st.markdown(f"- Highest action per 1,000 reach: **{melhor_acao}**, best use of effort to turn reach into results.")
    st.markdown(f"- Lowest total score: **{pior_score}**, currently less priority for time and creative focus.")

    st.markdown(
        "_Practical interpretation_: focus time first on the platform with the highest value/impact generation, "
        "use the one with highest reach as a discovery engine, and concentrate creative experiments on the platform "
        "that delivers the most action per 1,000 reach, since each content piece tends to generate more results there."
    )


# --------------------------------------------------
# INDIVIDUAL PAGES (summary version)
# --------------------------------------------------

def pagina_instagram():
    df, caminho = load_instagram()
    st.title("Instagram - Reach, Engagement and Action")
    st.caption("Analytical view for September 2025")

    if df is None or df.empty:
        st.error("Instagram file not found or no data in September.")
        return

    st.caption(f"Loaded file: {caminho}")

    soma_views = df["Views"].sum()
    soma_reach = df["Reach"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Posts", fmt_int(len(df)))
    k2.metric("Views", fmt_int(soma_views))
    k3.metric("Reach", fmt_int(soma_reach))
    k4.metric("Engagement rate", fmt_pct((df["interacoes"].sum() / soma_reach) if soma_reach else None, 2))
    k5.metric("Follows per 1,000 reach", fmt_float((df["Follows"].sum() / soma_reach * 1000) if soma_reach else None, 2))

    # here you can plug in the main charts from app_instagram-3.py, filtered to September only


def pagina_tiktok():
    df, caminho = load_tiktok()
    st.title("TikTok - Reach, Retention and Action")
    st.caption("Analytical view for September 2025")

    if df is None or df.empty:
        st.error("TikTok file not found or no data in September.")
        return

    st.caption(f"Loaded file: {caminho}")

    soma_views = df["Video Views"].sum()
    soma_reach = df["Reach"].sum()

    eng_rate = media_ponderada(df, "Engagement Rate", "Reach")
    avg_time = media_ponderada(df, "Average time watched", "Video Views")
    full_watch = media_ponderada(df, "Full video watched rate", "Video Views")
    shares_1000 = (df["Shares"].sum() / soma_views * 1000) if soma_views else None

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Video views", fmt_int(soma_views))
    k2.metric("Reach", fmt_int(soma_reach))
    k3.metric("Engagement rate", fmt_pct(eng_rate, 2))
    k4.metric("Average time watched", fmt_seg(avg_time, 1))
    k5.metric("Shares per 1,000 views", fmt_float(shares_1000, 2))

    # plug in main charts from app_tiktok-4.py, filtered to September only


def pagina_youtube():
    df, caminho = load_youtube()
    st.title("YouTube - Reach, Engagement and Action")
    st.caption("Analytical view for September 2025")

    if df is None or df.empty:
        st.error("YouTube file not found or no data in September.")
        return

    st.caption(f"Loaded file: {caminho}")

    soma_views = df["Views"].sum()
    soma_reach = df["Reach"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Videos", fmt_int(len(df)))
    k2.metric("Views", fmt_int(soma_views))
    k3.metric("Impressions", fmt_int(soma_reach))
    k4.metric("Engagement rate", fmt_pct((df["interacoes"].sum() / soma_reach) if soma_reach else None, 2))
    k5.metric("Subscribers gained", fmt_int(df["Subscribers gained"].sum()))

    # plug in charts from app_youtube-6.py adapted for September


def pagina_facebook():
    df, caminho = load_facebook()
    st.title("Facebook - Reach, Engagement and Action")
    st.caption("Analytical view for September 2025")

    if df is None or df.empty:
        st.error("Facebook file not found or no data in September.")
        return

    st.caption(f"Loaded file: {caminho}")

    soma_views = df["Views"].sum()
    soma_reach = df["Reach"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Posts", fmt_int(len(df)))
    k2.metric("Views", fmt_int(soma_views))
    k3.metric("Reach", fmt_int(soma_reach))
    k4.metric("Engagement rate", fmt_pct((df["interacoes"].sum() / soma_reach) if soma_reach else None, 2))
    k5.metric("Clicks per 1,000 reach", fmt_float((df["Total clicks"].sum() / soma_reach * 1000) if soma_reach else None, 2))

    # plug in charts you already built in app_facebook-2.py


def pagina_twitter():
    df, caminho = load_twitter()
    st.title("X / Twitter - Reach, Engagement and Action")
    st.caption("Analytical view for September 2025")

    if df is None or df.empty:
        st.error("Twitter file not found or no data in September.")
        return

    st.caption(f"Loaded file: {caminho}")

    soma_reach = df["Reach"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Tweets", fmt_int(len(df)))
    k2.metric("Impressions", fmt_int(soma_reach))
    k3.metric("Engagement rate", fmt_pct(df["engagement_rate"].mean() if len(df) else None, 2))
    k4.metric("Engagements", fmt_int(df["interacoes"].sum()))
    k5.metric("Clicks per 1,000 reach", fmt_float((df["clicks_totais"].sum() / soma_reach * 1000) if soma_reach else None, 2))

    # plug in main charts from app_twitter-5.py


# --------------------------------------------------
# SIDEBAR MENU / ROUTING
# --------------------------------------------------

menu = st.sidebar.radio(
    "Select view",
    [
        "Overview (cross-platform)",
        "Instagram",
        "TikTok",
        "YouTube",
        "Facebook",
        "X / Twitter",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Organic data · September 2025")

if menu == "Overview (cross-platform)":
    pagina_cross()
elif menu == "Instagram":
    pagina_instagram()
elif menu == "TikTok":
    pagina_tiktok()
elif menu == "YouTube":
    pagina_youtube()
elif menu == "Facebook":
    pagina_facebook()
elif menu == "X / Twitter":
    pagina_twitter()