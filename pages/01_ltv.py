import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

from data.db import get_engine
from data.queries_ltv import SQL_LTV
from components.kpi_cards import render_kpi_row, section_title, page_header, fmt_brl, fmt_pct, fmt_num

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LTV de Clientes | EStaff",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Carregando dados de clientes...")
def load() -> pd.DataFrame:
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(SQL_LTV, conn)

    df = df.rename(columns={
        "ID": "customer_id",
        "NAME": "company",
        "lifespanMonths": "life_months",
    })

    return df

df_all = load()

# ── Sidebar ───────────────────────────────────────────────────────────────────
#with st.sidebar:
    #st.markdown("## Filtros — LTV")

    #life_min = int(df_all["life_months"].min())
    #life_max = int(df_all["life_months"].max())
    #sel_life = st.slider(
        #"Vida útil (meses)",
        #min_value=life_min,
        #max_value=life_max,
        #value=(life_min, life_max),
    #)

    #ltv_min = float(df_all["ltv"].min())
    #ltv_max = float(df_all["ltv"].max())
    #sel_ltv = st.slider(
        #"Faixa de LTV (R$)",
        #min_value=ltv_min,
        #max_value=ltv_max,
        #value=(ltv_min, ltv_max),
        #format="R$%.0f",
    #)

    #st.markdown("---")
    #st.caption("Dashboard de Vendas v1.0\nEStaff © 2025")

# ── Filter ────────────────────────────────────────────────────────────────────
df = df_all.copy()
#df = df[df["life_months"].between(sel_life[0], sel_life[1])]
#df = df[df["ltv"].between(sel_ltv[0], sel_ltv[1])]

# ── Header ────────────────────────────────────────────────────────────────────
page_header("LTV de Clientes", "Customer Lifetime Value")

# ── KPIs ──────────────────────────────────────────────────────────────────────
avg_ltv        = df["ltv"].mean()
median_ltv     = df["ltv"].median()
high_value     = (df["ltv"] >= 10_000).sum()
high_value_pct = high_value / len(df) * 100 if len(df) else 0
avg_life       = df["life_months"].mean()

render_kpi_row([
    {"label": "LTV Médio",            "value": fmt_brl(avg_ltv),
     "help": "Média do LTV calculado: receita × percentual de comissão"},
    {"label": "LTV Mediano",          "value": fmt_brl(median_ltv),
     "help": "Mediana do LTV — menos sensível a outliers"},
    {"label": "Clientes LTV > R$10k", "value": fmt_num(high_value),
     "delta": fmt_pct(high_value_pct),
     "help": "Clientes com alto valor de vida"},
    {"label": "Vida Útil Média",      "value": f"{avg_life:.0f} meses",
     "help": "Diferença em meses entre primeiro e último checkin"},
])

st.markdown("---")

# ── Top 20 Clientes — Bar Chart Horizontal ────────────────────────────────────
section_title("Top 20 Clientes por LTV")

top20 = (
    df[["company", "ltv"]]
    .sort_values("ltv", ascending=True)
    .tail(20)
)

fig_top20 = go.Figure(go.Bar(
    x=top20["ltv"],
    y=top20["company"],
    orientation="h",
    marker=dict(
        color=top20["ltv"],
        colorscale="Blues",
        showscale=False,
    ),
    hovertemplate="<b>%{y}</b><br>LTV: R$ %{x:,.0f}<extra></extra>",
    text=top20["ltv"].apply(lambda v: f"R$ {v:,.0f}"),
    textposition="outside",
    cliponaxis=False,
))

fig_top20.update_layout(
    height=600,
    margin=dict(t=20, b=40, l=200, r=120),
    xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", title="LTV (R$)"),
    yaxis=dict(showgrid=False),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig_top20, use_container_width=True)

st.markdown("---")

# ── Concentração de LTV ───────────────────────────────────────────────────────
section_title("Concentração de LTV")

df_sorted = df.sort_values("ltv", ascending=False).reset_index(drop=True)
df_sorted["ltv_acumulado_pct"] = df_sorted["ltv"].cumsum() / df_sorted["ltv"].sum() * 100
df_sorted["clientes_pct"]      = (df_sorted.index + 1) / len(df_sorted) * 100

top10_pct = df_sorted[df_sorted["clientes_pct"] <= 10]["ltv_acumulado_pct"].max()
top20_pct = df_sorted[df_sorted["clientes_pct"] <= 20]["ltv_acumulado_pct"].max()

col1, col2, col3 = st.columns(3)
col1.metric("Top 10% clientes representam", f"{top10_pct:.1f}% do LTV total")
col2.metric("Top 20% clientes representam", f"{top20_pct:.1f}% do LTV total")
col3.metric("Total de clientes ativos",     fmt_num(len(df)))

st.markdown("---")

# ── Tabela — Clientes por Faixa de Vida Útil ─────────────────────────────────
section_title("Clientes por Faixa de Relacionamento")

bins   = [0, 3, 6, 12, 24, float("inf")]
labels = ["0–3 meses", "3–6 meses", "6–12 meses", "12–24 meses", "24+ meses"]
df["faixa_vida"] = pd.cut(df["life_months"], bins=bins, labels=labels, right=True)

faixa_ltv = (
    df.groupby("faixa_vida", observed=True)
    .agg(ltv_medio=("ltv", "mean"), clientes=("ltv", "count"))
    .reset_index()
    .rename(columns={"faixa_vida": "Faixa", "ltv_medio": "LTV Médio (R$)", "clientes": "Clientes"})
)
faixa_ltv["LTV Médio (R$)"] = faixa_ltv["LTV Médio (R$)"].round(0)

st.dataframe(
    faixa_ltv[["Faixa", "Clientes", "LTV Médio (R$)"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "LTV Médio (R$)": st.column_config.NumberColumn(format="R$ %.2f"),
    },
)

st.markdown("---")

# ── Ranking Completo ──────────────────────────────────────────────────────────
section_title("Ranking Completo de Clientes por LTV")

df_rank = (
    df[["customer_id", "company", "ltv", "life_months"]]
    .sort_values("ltv", ascending=False)
    .reset_index(drop=True)
)
df_rank.index += 1
df_rank["ltv_pct"]      = (df_rank["ltv"] / df_rank["ltv"].sum() * 100).round(2)
df_rank["ltv_acum_pct"] = df_rank["ltv_pct"].cumsum().round(2)
df_rank.columns = ["ID", "Empresa", "LTV (R$)", "Vida Útil (meses)", "% do Total", "% Acumulado"]

busca = st.text_input("", placeholder="Digite o nome do cliente...")
if busca:
    df_rank = df_rank[df_rank["Empresa"].str.contains(busca, case=False, na=False)]

st.dataframe(
    df_rank,
    use_container_width=True,
    column_config={
        "LTV (R$)":    st.column_config.NumberColumn(format="R$ %.2f"),
        "% do Total":  st.column_config.NumberColumn(format="%.2f%%"),
        "% Acumulado": st.column_config.NumberColumn(format="%.2f%%"),
    },
)