import streamlit as st


def render_kpi_row(metrics: list[dict]) -> None:
    """Render a horizontal row of KPI cards.

    Each dict in *metrics* accepts:
        label   : str   — card title
        value   : str   — formatted main value
        delta   : str   — optional delta string (e.g. '+12%')
        help    : str   — optional tooltip text
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            st.metric(
                label=m["label"],
                value=m["value"],
                delta=m.get("delta"),
                help=m.get("help"),
            )


def section_title(title: str) -> None:
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)


def page_header(title: str, badge: str = "") -> None:
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    st.markdown(
        f'<div class="page-header"><h1>{title}</h1>{badge_html}</div>',
        unsafe_allow_html=True,
    )


def fmt_brl(value: float) -> str:
    """Format a float as Brazilian Real currency string."""
    if value >= 1_000_000:
        return f"R$ {value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"R$ {value/1_000:.1f}k"
    return f"R$ {value:,.0f}"


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def fmt_num(value: float) -> str:
    return f"{value:,.0f}"
