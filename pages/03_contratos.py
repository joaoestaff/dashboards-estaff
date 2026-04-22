import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

from data.db import get_engine
from data.queries_contratos import SQL_CONTRATOS_PENDENTES, SQL_CONTRATOS_ASSINADOS
from components.kpi_cards import section_title, page_header, fmt_num

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Demonstrativo de Contratos | EStaff",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

css_path = Path(__file__).parent.parent / "styles" / "custom.css"
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="Carregando dados dos contratos...")
def load_contratos():
    engine = get_engine()
    with engine.connect() as conn:
        pendentes = pd.read_sql(SQL_CONTRATOS_PENDENTES, conn)
        assinados = pd.read_sql(SQL_CONTRATOS_ASSINADOS, conn)
    return pendentes, assinados

try:
    df_pendentes, df_assinados = load_contratos()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")
    st.info("Verifique as variáveis no arquivo `.env` (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD).")
    st.stop()

# "Enviados" = pendentes + assinados (total)
df_enviados = pd.concat([df_pendentes, df_assinados], ignore_index=True)

# Garantir datas como datetime
for _df in [df_pendentes, df_assinados]:
    for col in _df.columns:
        if 'DATA' in col.upper():
            _df[col] = pd.to_datetime(_df[col], errors="coerce")

# ── Logo ─────────────────────────────────────────────────────────────────────
st.image("Imagem1.png", width=140)

# ── Header ────────────────────────────────────────────────────────────────────
page_header("Demonstrativo de Contratos", "📄")

# ── KPIs ──────────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Contratos Enviados", len(df_enviados))
with col2:
    st.metric("Pendentes de Assinatura", len(df_pendentes))
with col3:
    st.metric("Contratos Assinados", len(df_assinados))

# ── Gráficos ──────────────────────────────────────────────────────────────────
n_pendentes  = len(df_pendentes)
n_assinados  = len(df_assinados)
n_enviados   = len(df_enviados)

COLORS = {
    "Assinados": "#22c55e",   # verde
    "Pendentes": "#f59e0b",   # âmbar
    "Enviados" : "#6366f1",   # índigo
}

fig = make_subplots(
    rows=1, cols=2,
    specs=[[{"type": "domain"}, {"type": "xy"}]],
    subplot_titles=("Proporção de Status", "Volume por Categoria"),
    horizontal_spacing=0.12,
)

# ── Donut ─────────────────────────────────────────────────────────────────────
fig.add_trace(
    go.Pie(
        labels=["Assinados", "Pendentes"],
        values=[n_assinados, n_pendentes],
        hole=0.55,
        marker_colors=[COLORS["Assinados"], COLORS["Pendentes"]],
        textinfo="label+percent",
        hovertemplate="%{label}: <b>%{value}</b> contratos<extra></extra>",
    ),
    row=1, col=1,
)

# Anotação central do donut
fig.add_annotation(
    x=0.20, y=0.50,                     # centro do subplot esquerdo
    text=f"<b>{n_enviados}</b><br><span style='font-size:11px'>total</span>",
    showarrow=False,
    font=dict(size=18),
    xref="paper", yref="paper",
)

# ── Barras horizontal ─────────────────────────────────────────────────────────
categorias = ["Enviados", "Assinados", "Pendentes"]
valores    = [n_enviados, n_assinados, n_pendentes]
cores      = [COLORS[c] for c in categorias]

fig.add_trace(
    go.Bar(
        x=valores,
        y=categorias,
        orientation="h",
        marker_color=cores,
        text=valores,
        textposition="outside",
        hovertemplate="%{y}: <b>%{x}</b> contratos<extra></extra>",
    ),
    row=1, col=2,
)

fig.update_layout(
    height=320,
    margin=dict(t=50, b=20, l=20, r=40),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    showlegend=False,   
    font=dict(family="Inter, sans-serif", size=13),
)

fig.update_xaxes(showgrid=False, visible=False, row=1, col=2)
fig.update_yaxes(showgrid=False, row=1, col=2)

st.plotly_chart(fig, use_container_width=True)

# ── Tabelas ───────────────────────────────────────────────────────────────────
section_title("Contratos Enviados")
busca = st.text_input(
    "🔍 Buscar contrato",
    placeholder="Digite nome, CPF, status...",
    key="busca_enviados",
)

if busca:
    mask = df_enviados.apply(
        lambda col: col.astype(str).str.contains(busca, case=False, na=False)
    ).any(axis=1)
    df_exibir = df_enviados[mask]
    st.caption(f"{len(df_exibir)} resultado(s) encontrado(s) para **{busca}**")
else:
    df_exibir = df_enviados

st.dataframe(df_exibir, use_container_width=True)

section_title("Contratos Pendentes de Assinatura")
st.dataframe(df_pendentes, use_container_width=True)

section_title("Contratos Assinados")
st.dataframe(df_assinados, use_container_width=True)
