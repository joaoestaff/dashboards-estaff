import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from pathlib import Path

from data.db import get_engine
from data.queries_funil import SQL_CHURNS, SQL_PENDENTES, SQL_ATENDIMENTO, SQL_IMPLANTACAO
from components.kpi_cards import section_title, page_header, fmt_pct, fmt_num

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Funil de Leads | EStaff",
    page_icon="🔻",
    layout="wide",
    initial_sidebar_state="collapsed",
)

css_path = Path(__file__).parent / "styles" / "custom.css"
st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner="Carregando dados do banco...")
def load_funil():
    engine = get_engine()
    with engine.connect() as conn:
        pend  = pd.read_sql(SQL_PENDENTES,    conn)
        atend = pd.read_sql(SQL_ATENDIMENTO,  conn)
        impl  = pd.read_sql(SQL_IMPLANTACAO,  conn)
        churn = pd.read_sql(SQL_CHURNS,       conn)
    return pend, atend, impl, churn

try:
    df_pend, df_atend, df_impl, df_churn = load_funil()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")
    st.info("Verifique as variáveis no arquivo `.env` (DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD).")
    st.stop()

# Garantir DATA_CRIACAO como datetime em todos os DFs
for _df in [df_pend, df_atend, df_impl, df_churn]:
    if "DATA_CRIACAO" in _df.columns:
        _df["DATA_CRIACAO"] = pd.to_datetime(_df["DATA_CRIACAO"], errors="coerce")

# ── Filtros desativados (sidebar removida) ────────────────────────────────────
sel_resp = "Todos"
sel_uf   = "Todos"

# ── Logo ─────────────────────────────────────────────────────────────────────
st.image("Imagem1.png", width=140)

# ── Header ────────────────────────────────────────────────────────────────────
page_header("Funil Comercial", "Operacional")

# ── Filtro de período ─────────────────────────────────────────────────────────
all_dates = pd.concat([
    df_pend["DATA_CRIACAO"], df_atend["DATA_CRIACAO"], df_impl["DATA_CRIACAO"]
]).dropna()

date_min = all_dates.min().date()
date_max = all_dates.max().date()

col_f1, col_f2, col_f3 = st.columns([1, 1, 4])
with col_f1:
    data_ini = st.date_input("De", value=date_min, min_value=date_min, max_value=date_max)
with col_f2:
    data_fim = st.date_input("Até", value=date_max, min_value=date_min, max_value=date_max)

st.markdown("<div style='margin-bottom:8px'></div>", unsafe_allow_html=True)

# ── Filtros aplicados ─────────────────────────────────────────────────────────
def filtrar_periodo(df):
    if "DATA_CRIACAO" not in df.columns:
        return df
    return df[
        (df["DATA_CRIACAO"].dt.date >= data_ini) &
        (df["DATA_CRIACAO"].dt.date <= data_fim)
    ]

df_pend  = filtrar_periodo(df_pend)
df_atend = filtrar_periodo(df_atend)
df_impl  = filtrar_periodo(df_impl)
df_churn = filtrar_periodo(df_churn) if "DATA_CRIACAO" in df_churn.columns else df_churn

total  = len(df_pend) + len(df_atend) + len(df_impl)
ativos = len(df_atend) + len(df_impl)

# ── Estilos compartilhados ────────────────────────────────────────────────────
PANEL = (
    "background:#F8FAFC;border:1px solid #E2E8F0;"
    "border-left:4px solid #1B3A6B;border-radius:10px;padding:18px 20px;"
)
LABEL_STYLE = (
    "font-size:0.78rem;font-weight:700;text-transform:uppercase;"
    "letter-spacing:0.07em;color:#64748B;margin:0 0 6px 0;"
)
VALUE_STYLE = "font-size:1.5rem;font-weight:700;color:#1B3A6B;margin:0 0 2px 0;"
HELP_STYLE  = "font-size:0.70rem;color:#535c69;margin:0;"

# ── KPIs ──────────────────────────────────────────────────────────────────────
taxa_conv   = len(df_impl) / total * 100 if total else 0
taxa_impl   = len(df_impl) / ativos * 100 if ativos else 0
nao_atend   = len(df_pend) / total * 100 if total else 0
taxa_avanco = ativos / total * 100 if total else 0

def _kpi_card(label, value, help_text):
    return (
        f'<div style="background:#fff;border:1px solid #E2E8F0;border-radius:8px;'
        f'padding:14px 12px;text-align:center;flex:1;">'
        f'<p style="{LABEL_STYLE}">{label}</p>'
        f'<p style="{VALUE_STYLE}">{value}</p>'
        f'<p style="{HELP_STYLE}">{help_text}</p>'
        f'</div>'
    )

def _kpi_span(label, value, help_text, span):
    return (
        f'<div style="grid-column:span {span};background:#fff;border:1px solid #E2E8F0;'
        f'border-radius:8px;padding:14px 12px;text-align:center;">'
        f'<p style="{LABEL_STYLE}">{label}</p>'
        f'<p style="{VALUE_STYLE}">{value}</p>'
        f'<p style="{HELP_STYLE}">{help_text}</p>'
        f'</div>'
    )

kpi_cards = (
    _kpi_span("Taxa de Conversão",    fmt_pct(taxa_conv),      "Lead → Implantação",              2) +
    _kpi_span("Taxa em Implantação",  fmt_pct(taxa_impl),      "Sobre ativos (excl. pendentes)",  2) +
    _kpi_span("Em Atendimento",       fmt_num(len(df_atend)),  "Leads em processo comercial",     2) +
    _kpi_span("Não Atendimento",      fmt_pct(nao_atend),      "% de leads pendentes",            3) +
    _kpi_span("Taxa de Avanço Total", fmt_pct(taxa_avanco),    "Leads além do estágio inicial",   3)
)

# ── Resumo por status ────────────────────────────────────────────────────────
STATUS_CONFIG = [
    ("1. Sem atendimento",  "#F59E0B"),
    ("2. Em contato",          "#3B82F6"),
    ("3. Reunião agendada",    "#6366F1"),
    ("4. Em negociação",       "#8B5CF6"),
    ("5. Contrato enviado",    "#EC4899"),
    ("6. Fase de implantação", "#10B981"),
    ("7. Estabilização",       "#059669"),
    ("8. Em operação",         "#047857"),
    ("9. Perdido",             "#DC2626"),
]

all_status = pd.concat([
    df_pend["Status_Comercial"],
    df_atend["Status_Comercial"],
    df_impl["Status_Comercial"],
]).fillna("1. Sem atendimento")

status_counts = all_status.value_counts()

def _row(label, n, color):
    pct = fmt_pct(n / total * 100) if total else "0.0%"
    return (
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:center;margin-bottom:7px;">'
        f'<span style="color:#374151;font-size:0.9rem;">{label}</span>'
        f'<span style="font-weight:700;color:{color};font-size:0.9rem;">'
        f'{n} <span style="color:#94A3B8;font-weight:400">({pct})</span>'
        f'</span></div>'
    )

summary_rows = "".join(
    _row(label, int(status_counts.get(label, 0)), color)
    for label, color in STATUS_CONFIG
)

col_kpis, col_summary = st.columns([3, 1], gap="large")

with col_kpis:
    st.markdown(
        f'<div style="{PANEL}">'
        f'<p style="{LABEL_STYLE}margin-bottom:14px;">Indicadores</p>'
        f'<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;">{kpi_cards}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_summary:
    st.markdown(
        f'<div style="{PANEL}">'
        f'<p style="{LABEL_STYLE}margin-bottom:14px;">Resumo por Status</p>'
        f'{summary_rows}'
        f'<hr style="border:none;border-top:1px solid #E2E8F0;margin:8px 0;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span style="color:#374151;font-size:0.84rem;font-weight:700;">Total</span>'
        f'<span style="font-weight:700;color:#1B3A6B;font-size:1.05rem;">{total}</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Tabelas ───────────────────────────────────────────────────────────────────
def show_table(df: pd.DataFrame, cols: list[str], height: int = 300) -> None:
    if df.empty:
        st.info("Nenhum lead nesta categoria para os filtros selecionados.")
        return
    existing = [c for c in cols if c in df.columns]
    st.dataframe(
        df[existing].reset_index(drop=True),
        use_container_width=True,
        height=height,
    )


def show_table_with_sla(df: pd.DataFrame, cols: list[str], sla_col: str = "SLA_Ultimo_Status", height: int = 300) -> None:
    if df.empty:
        st.info("Nenhum lead nesta categoria para os filtros selecionados.")
        return
    existing = [c for c in cols if c in df.columns]
    display_df = df[existing].reset_index(drop=True)

    if sla_col in display_df.columns:
        def _parse_sla(value):
            if pd.isna(value):
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                value = value.strip()
                if value == "":
                    return 0.0
                try:
                    return float(value)
                except ValueError:
                    pass
                try:
                    td = pd.to_timedelta(value)
                    return td / pd.Timedelta(days=1)
                except Exception:
                    pass
            if isinstance(value, pd.Timedelta):
                return value / pd.Timedelta(days=1)
            return 0.0

        def _highlight_sla(row):
            sla_value = _parse_sla(row[sla_col])
            if sla_value > 1:
                return ["background-color: #fef3c7"] * len(row)
            return [""] * len(row)

        styled = display_df.style.apply(_highlight_sla, axis=1)
        st.dataframe(
            styled,
            use_container_width=True,
            height=height,
        )
    else:
        st.dataframe(
            display_df,
            use_container_width=True,
            height=height,
        )

section_title(f"Leads Pendentes  ·  {len(df_pend)} registros")
show_table(df_pend, [
    "ID_Casa", "Casa", "Razão Social", "CITY", "UF",
    "CNPJ", "Telefone", "DATA_CRIACAO",
])

section_title(f"Leads em Atendimento  ·  {len(df_atend)} registros")
show_table_with_sla(df_atend, [
    "ID_Casa", "Casa", "Status_Comercial", "Usuario_Responsavel",
    "Data_Mudanca_Status", "SLA_Ultimo_Status", "CNPJ", "Telefone", "DATA_CRIACAO",
])

section_title(f"Leads em Implantação  ·  {len(df_impl)} registros")
show_table(df_impl, [
    "ID_Casa", "Casa", "Status_Comercial", "Usuario_Responsavel",
    "Data_Mudanca_Status", "CNPJ", "Telefone", "DATA_CRIACAO",
])

st.markdown("---")

# ── Acompanhamento Churns ─────────────────────────────────────────────────────
st.markdown('<h2 style="font-size:1.8rem; margin-bottom:16px;">Acompanhamento Churns</h2>', unsafe_allow_html=True)

# Filtro menor (alinhado à esquerda)
col_filter, _ = st.columns([1, 3])
with col_filter:
    status_churn_options = ["Todos"] + sorted(df_churn["Status_Cliente"].dropna().unique().tolist()) if not df_churn.empty else ["Todos"]
    sel_status_churn = st.selectbox("Filtrar por Status", status_churn_options, key="churn_status")

if sel_status_churn != "Todos":
    df_churn_filtered = df_churn[df_churn["Status_Cliente"] == sel_status_churn].copy()
else:
    df_churn_filtered = df_churn.copy()

CHURN_CONFIG = [
    ("Ativo",    "#10B981"),
    ("Em Risco", "#F59E0B"),
    ("Churn",    "#DC2626"),
]

churn_counts = df_churn_filtered["Status_Cliente"].value_counts() if not df_churn_filtered.empty else pd.Series(dtype=int)


def _highlight_risco(row):
    if row.get("Status_Cliente") == "Em Risco":
        return ["background-color: #fef3c7"] * len(row)
    return [""] * len(row)


def _format_churn_display(df):
    df_display = df.copy()
    if "TAXA_%%" in df_display.columns:
        df_display.rename(columns={"TAXA_%%": "TAXA_%"}, inplace=True)
    if "TAXA_PCT" in df_display.columns and "TAXA_%" not in df_display.columns:
        df_display.rename(columns={"TAXA_PCT": "TAXA_%"}, inplace=True)

    if "TRANSACIONADO" in df_display.columns:
        df_display["TRANSACIONADO"] = df_display["TRANSACIONADO"].apply(
            lambda x: f"R$ {x:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".") if pd.notna(x) else "R$ 0,00"
        )
    if "TAXA_%" in df_display.columns:
        df_display["TAXA_%"] = df_display["TAXA_%"].apply(
            lambda x: f"{x:.2f}%" if pd.notna(x) else "0,00%"
        )
    return df_display


def show_table_churn(df: pd.DataFrame, cols: list[str], height: int = 400) -> None:
    if df.empty:
        st.info("Nenhum registro para os filtros selecionados.")
        return

    df_display = _format_churn_display(df)
    existing = [c for c in cols if c in df_display.columns]
    if not existing:
        existing = list(df_display.columns)

    st.dataframe(
        df_display[existing].reset_index(drop=True).style.apply(_highlight_risco, axis=1),
        use_container_width=True,
        height=height,
    )


# Fonte igual ao resumo de leads (mais legível)
def _churn_row(label, n, color):
    pct = fmt_pct(n / len(df_churn_filtered) * 100) if len(df_churn_filtered) else "0.0%"
    return (
        f'<div style="display:flex;justify-content:space-between;'
        f'align-items:center;margin-bottom:7px;">'
        f'<span style="color:#374151;font-size:0.9rem;">{label}</span>'
        f'<span style="font-weight:700;color:{color};font-size:0.9rem;">'
        f'{n} <span style="color:#94A3B8;font-weight:400">({pct})</span>'
        f'</span></div>'
    )

churn_rows = "".join(
    _churn_row(label, int(churn_counts.get(label, 0)), color)
    for label, color in CHURN_CONFIG
)

# Layout: resumo à esquerda + tabela à direita
col_churn_summary, col_churn_table = st.columns([1, 3], gap="large")

with col_churn_summary:
    st.markdown("<div style='margin-top:-10px'></div>", unsafe_allow_html=True)

    st.markdown(
        f'<div style="{PANEL}">'
        f'<p style="{LABEL_STYLE}margin-bottom:14px;">Resumo por Status</p>'
        f'{churn_rows}'
        f'<hr style="border:none;border-top:1px solid #E2E8F0;margin:8px 0;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span style="color:#374151;font-size:0.84rem;font-weight:700;">Total</span>'
        f'<span style="font-weight:700;color:#1B3A6B;font-size:1.05rem;">{len(df_churn_filtered)}</span>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

with col_churn_table:
    # Sobe o bloco para alinhar com o filtro
    st.markdown("<div style='margin-top:-35px'></div>", unsafe_allow_html=True)

    section_title(f"Acompanhamento Churns  ·  {len(df_churn_filtered)} registros")

    show_table_churn(
        df_churn_filtered,
        ["company_id", "Cliente", "Primeira_OP", "Ultima_OP", "Ano_Mes",
         "Dias_Sem_OP", "Status_Cliente", "TRANSACIONADO", "TAXA_%"]
    )
