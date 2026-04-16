import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

BLUE = "#1B3A6B"
ORANGE = "#FF6B35"
LIGHT_BLUE = "#4A7FC1"
PALETTE = [BLUE, ORANGE, LIGHT_BLUE, "#2ECC71", "#9B59B6", "#F39C12"]

LAYOUT_BASE = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#374151"),
    margin=dict(l=16, r=16, t=40, b=16),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)


def _apply_base(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**LAYOUT_BASE, title=dict(text=title, font=dict(size=14, color=BLUE, weight="bold")))
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#F1F5F9", zeroline=False)
    return fig


# ── Line chart ───────────────────────────────────────────────────────────────

def line_revenue(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y],
        mode="lines+markers",
        line=dict(color=BLUE, width=2.5),
        marker=dict(color=BLUE, size=6),
        fill="tozeroy",
        fillcolor="rgba(27,58,107,0.08)",
        name="Receita",
    ))
    return _apply_base(fig, title)


# ── Bar chart ─────────────────────────────────────────────────────────────────

def bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: str = BLUE,
    orientation: str = "v",
    text_auto: bool = True,
) -> go.Figure:
    if orientation == "h":
        fig = go.Figure(go.Bar(
            x=df[y], y=df[x],
            orientation="h",
            marker_color=color,
            text=df[y].apply(lambda v: f"{v:,.0f}") if text_auto else None,
            textposition="outside",
        ))
    else:
        fig = go.Figure(go.Bar(
            x=df[x], y=df[y],
            marker_color=color,
            text=df[y].apply(lambda v: f"{v:,.0f}") if text_auto else None,
            textposition="outside",
        ))
    return _apply_base(fig, title)


def bar_grouped(df: pd.DataFrame, x: str, columns: list[str], title: str = "") -> go.Figure:
    fig = go.Figure()
    for col, clr in zip(columns, PALETTE):
        fig.add_trace(go.Bar(name=col, x=df[x], y=df[col], marker_color=clr))
    fig.update_layout(barmode="group")
    return _apply_base(fig, title)


# ── Funnel ────────────────────────────────────────────────────────────────────

def funnel_chart(stages: list[str], values: list[int], title: str = "") -> go.Figure:
    colors = [
        "#1B3A6B", "#2556A0", "#3A74C9", "#5B93DC",
        "#85B4E8", "#FF6B35", "#E84545",
    ]
    fig = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker=dict(color=colors[:len(stages)]),
        connector=dict(line=dict(color="#CBD5E1", width=1)),
    ))
    fig.update_layout(**LAYOUT_BASE, title=dict(text=title, font=dict(size=14, color=BLUE, weight="bold")))
    return fig


# ── Histogram ─────────────────────────────────────────────────────────────────

def histogram(df: pd.DataFrame, x: str, title: str = "", nbins: int = 30) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=df[x], nbinsx=nbins,
        marker_color=BLUE,
        opacity=0.85,
    ))
    fig.update_layout(**LAYOUT_BASE, title=dict(text=title, font=dict(size=14, color=BLUE, weight="bold")))
    fig.update_yaxes(title_text="Nº de clientes")
    return fig


# ── Cohort heatmap ────────────────────────────────────────────────────────────

def cohort_heatmap(df: pd.DataFrame, title: str = "") -> go.Figure:
    fig = go.Figure(go.Heatmap(
        z=df.values,
        x=[f"M+{i}" for i in range(df.shape[1])],
        y=df.index.astype(str),
        colorscale=[[0, "#EBF4FF"], [1, "#1B3A6B"]],
        text=np.where(df.values > 0, (df.values * 100).round(0).astype(int).astype(str) + "%", ""),
        texttemplate="%{text}",
        showscale=True,
        zmin=0, zmax=1,
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        title=dict(text=title, font=dict(size=14, color=BLUE, weight="bold")),
        height=350,
    )
    return fig


# ── Scatter ───────────────────────────────────────────────────────────────────

def scatter_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    color_col: str | None = None,
    size_col: str | None = None,
    title: str = "",
    hover_data: list[str] | None = None,
) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y,
        color=color_col,
        size=size_col,
        hover_data=hover_data,
        color_discrete_sequence=PALETTE,
        opacity=0.7,
    )
    return _apply_base(fig, title)


# ── Conversion rate bar ───────────────────────────────────────────────────────

def conversion_bars(stages: list[str], rates: list[float], title: str = "") -> go.Figure:
    colors = [BLUE if r >= 0.5 else ORANGE for r in rates]
    fig = go.Figure(go.Bar(
        x=stages,
        y=[r * 100 for r in rates],
        marker_color=colors,
        text=[f"{r*100:.1f}%" for r in rates],
        textposition="outside",
    ))
    fig.update_yaxes(title_text="Taxa de conversão (%)", range=[0, 115])
    return _apply_base(fig, title)
