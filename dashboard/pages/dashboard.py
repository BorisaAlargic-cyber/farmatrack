"""Dashboard overview page."""

import streamlit as st
from dashboard import api_client as api


_CSS = """
<style>
.kpi-card {
    background: #fdfaf5;
    border: 1px solid #d8cdb8;
    border-radius: 12px;
    padding: 18px 20px 14px 20px;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: #9a8d7e;
    margin-bottom: 6px;
    font-weight: 500;
}
.kpi-val {
    font-size: 30px;
    font-weight: 600;
    color: #3a3228;
    line-height: 1;
    font-family: Georgia, serif;
}
.kpi-unit { font-size: 12px; color: #6b5d4e; margin-top: 4px; }
.kpi-delta-up      { font-size: 11px; color: #6a8c3a; margin-top: 6px; }
.kpi-delta-down    { font-size: 11px; color: #a05040; margin-top: 6px; }
.kpi-delta-neutral { font-size: 11px; color: #9a8d7e; margin-top: 6px; }

.panel-title {
    font-size: 14px;
    font-weight: 500;
    color: #3a3228;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ede6d6;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.panel-link { font-size: 12px; color: #7a8c45; text-decoration: none; }

.tag-id {
    font-family: monospace;
    font-size: 11px;
    background: #f5f0e8;
    border: 1px solid #d8cdb8;
    padding: 2px 7px;
    border-radius: 4px;
    color: #6b5d4e;
    white-space: nowrap;
}
.status-ok    { font-size: 11px; padding: 2px 9px; border-radius: 20px; background: #e8f0d0; color: #4a6e1a; font-weight: 500; }
.status-watch { font-size: 11px; padding: 2px 9px; border-radius: 20px; background: #f2e8cc; color: #7a5e1a; font-weight: 500; }
.status-alert { font-size: 11px; padding: 2px 9px; border-radius: 20px; background: #f5e0d8; color: #8a3820; font-weight: 500; }

.pig-tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.pig-tbl th {
    text-align: left;
    padding: 6px 6px 6px 0;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9a8d7e;
    font-weight: 400;
    border-bottom: 1px solid #ede6d6;
}
.pig-tbl td {
    padding: 9px 6px 9px 0;
    border-bottom: 1px solid #ede6d6;
    color: #3a3228;
    vertical-align: middle;
}
.pig-tbl tr:last-child td { border-bottom: none; }

.chart-wrap {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    height: 100px;
    padding: 8px 0 4px 0;
}
.bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; height: 100%; justify-content: flex-end; }
.bar-fill { width: 100%; border-radius: 4px 4px 0 0; background: #c8d49a; min-height: 4px; }
.bar-fill.hi { background: #7a8c45; }
.bar-lbl { font-size: 10px; color: #9a8d7e; }
.chart-footer { font-size: 11px; color: #9a8d7e; padding-top: 6px; border-top: 1px solid #ede6d6; display: flex; justify-content: space-between; }

.feed-item { display: flex; gap: 10px; padding: 10px 0; border-bottom: 1px solid #ede6d6; align-items: flex-start; }
.feed-item:last-child { border-bottom: none; }
.dot-red   { width: 7px; height: 7px; border-radius: 50%; background: #c07060; flex-shrink: 0; margin-top: 5px; }
.dot-green { width: 7px; height: 7px; border-radius: 50%; background: #9aab5e; flex-shrink: 0; margin-top: 5px; }
.dot-amber { width: 7px; height: 7px; border-radius: 50%; background: #c8a95e; flex-shrink: 0; margin-top: 5px; }
.feed-text { font-size: 13px; color: #6b5d4e; line-height: 1.4; }
.feed-date { font-size: 11px; color: #9a8d7e; margin-top: 2px; }

.farrow-tbl { width: 100%; border-collapse: collapse; font-size: 13px; }
.farrow-tbl th {
    text-align: left;
    padding: 7px 8px 7px 0;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9a8d7e;
    font-weight: 400;
    border-bottom: 1px solid #ede6d6;
}
.farrow-tbl td {
    padding: 10px 8px 10px 0;
    border-bottom: 1px solid #ede6d6;
    color: #3a3228;
    vertical-align: middle;
}
.farrow-tbl tr:last-child td { border-bottom: none; }
.badge-today    { font-size: 11px; padding: 2px 9px; border-radius: 20px; background: #f5e0d8; color: #8a3820; font-weight: 500; }
.badge-soon     { font-size: 11px; padding: 2px 9px; border-radius: 20px; background: #f2e8cc; color: #7a5e1a; font-weight: 500; }
.badge-upcoming { font-size: 11px; padding: 2px 9px; border-radius: 20px; background: #e8f0d0; color: #4a6e1a; font-weight: 500; }
.badge-overdue  { font-size: 11px; padding: 2px 9px; border-radius: 20px; background: #f5e0d8; color: #8a3820; font-weight: 600; }
</style>
"""

_FILTERS = {"Today": 0, "Next 7 Days": 7, "Next Month": 30, "Next 3 Months": 90}


def _kpi_card(label, value, unit, delta="", delta_type="neutral", border_color="#c8d49a"):
    delta_html = f'<div class="kpi-delta-{delta_type}">{delta}</div>' if delta else ""
    return f"""
<div class="kpi-card" style="border-top:3px solid {border_color};">
    <div class="kpi-label">{label}</div>
    <div class="kpi-val">{value}</div>
    <div class="kpi-unit">{unit}</div>
    {delta_html}
</div>"""


def _status_pill(status):
    if status in ("sick", "quarantined"):
        return f'<span class="status-alert">{status.title()}</span>'
    if status == "treated":
        return '<span class="status-watch">Monitor</span>'
    return '<span class="status-ok">Healthy</span>'


def _days_badge(days_left):
    if days_left < 0:
        return f'<span class="badge-overdue">Overdue {abs(days_left)}d</span>'
    if days_left == 0:
        return '<span class="badge-today">Today</span>'
    if days_left <= 3:
        return f'<span class="badge-today">In {days_left}d</span>'
    if days_left <= 14:
        return f'<span class="badge-soon">In {days_left}d</span>'
    return f'<span class="badge-upcoming">In {days_left}d</span>'


def render():
    st.markdown(_CSS, unsafe_allow_html=True)

    try:
        data = api.get_summary()
        recent_pigs = api.get_recent_pigs()
        weekly = api.get_weekly_piglets()
        activity = api.get_recent_activity()
    except Exception as e:
        st.error(f"Could not load dashboard: {e}")
        return

    warnings = data.get("sick_or_quarantined", 0)
    piglets_week = data.get("piglets_this_week", 0)

    # ── Header ──────────────────────────────────────────────
    h1, h2 = st.columns([4, 1])
    with h1:
        st.markdown("<h2 style='font-size:1.5rem;font-weight:500;color:#3a3228;margin:0 0 20px 0;font-family:Georgia,serif;'>Dashboard</h2>", unsafe_allow_html=True)
    with h2:
        warn_bg     = "#f2e8cc" if warnings > 0 else "#eef2dc"
        warn_border = "#c8a95e" if warnings > 0 else "#c8d49a"
        warn_color  = "#7a5e1a" if warnings > 0 else "#7a8c45"
        warn_icon   = "⚠" if warnings > 0 else "✓"
        st.markdown(
            f"<div style='background:{warn_bg};color:{warn_color};font-size:12px;font-weight:500;"
            f"padding:6px 12px;border-radius:20px;border:1px solid {warn_border};"
            f"text-align:center;margin-top:6px;'>{warn_icon} {warnings} warning{'s' if warnings != 1 else ''}</div>",
            unsafe_allow_html=True,
        )

    # ── KPI row (3 cards) ────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    total    = data["total_active_pigs"]
    watch    = data["sick_or_quarantined"]
    farrow_n = data["total_farrowings"]

    with c1:
        st.markdown(_kpi_card("Total Pigs", total, "active animals", border_color="#9aab5e"), unsafe_allow_html=True)
    with c2:
        delta = f"↓ {watch} require attention" if watch > 0 else "All healthy"
        dtype = "down" if watch > 0 else "up"
        st.markdown(_kpi_card("Under Watch", watch, "sick or quarantined", delta=delta, delta_type=dtype, border_color="#c8a95e"), unsafe_allow_html=True)
    with c3:
        delta3 = f"↑ {piglets_week} piglets this week" if piglets_week else "none this week"
        dtype3 = "up" if piglets_week else "neutral"
        st.markdown(_kpi_card("Farrowings", farrow_n, "recorded total", delta=delta3, delta_type=dtype3, border_color="#9aab5e"), unsafe_allow_html=True)

    st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

    # ── Upcoming Farrowings ──────────────────────────────────
    with st.container(border=True):
        st.markdown('<div class="panel-title">Upcoming Farrowings</div>', unsafe_allow_html=True)

        selected = st.radio(
            "filter",
            list(_FILTERS.keys()),
            index=1,
            horizontal=True,
            label_visibility="collapsed",
        )
        days_ahead = _FILTERS[selected]

        try:
            upcoming = api.list_upcoming_farrowings(days_ahead=days_ahead)
        except Exception as e:
            st.error(str(e))
            upcoming = []

        if upcoming:
            rows = ""
            for u in upcoming:
                rows += f"""<tr>
  <td><span class="tag-id">{u['ear_tag']}</span></td>
  <td style="color:#6b5d4e;">{u.get('pen') or '—'}</td>
  <td style="color:#6b5d4e;">{u.get('insemination_date') or '—'}</td>
  <td style="color:#3a3228;">{u.get('expected_farrowing_date') or '—'}</td>
  <td>{_days_badge(u['days_left'])}</td>
</tr>"""
            st.markdown(f"""
<table class="farrow-tbl">
  <thead><tr>
    <th>Ear Tag</th><th>Pen</th><th>Insemination</th><th>Expected</th><th>Status</th>
  </tr></thead>
  <tbody>{rows}</tbody>
</table>
<div style="font-size:11px;color:#9a8d7e;margin-top:8px;">{len(upcoming)} sow(s) found</div>
""", unsafe_allow_html=True)
        else:
            st.info(f"No upcoming farrowings for: **{selected}**")

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

    # ── Lower grid ───────────────────────────────────────────
    left, right = st.columns(2, gap="medium")

    with left:
        with st.container(border=True):
            st.markdown("""
<div class="panel-title">
    Recent Records
    <a href="?page=herd" class="panel-link" target="_self">View all →</a>
</div>""", unsafe_allow_html=True)

            if recent_pigs:
                rows = ""
                for p in recent_pigs:
                    tag  = p["ear_tag"]
                    pen  = p.get("pen") or "—"
                    wt   = f"{p['weight_kg']:.0f} kg" if p.get("weight_kg") else "—"
                    pill = _status_pill(p.get("health_status", "healthy"))
                    rows += f"""<tr>
  <td><span class="tag-id">{tag}</span></td>
  <td style="color:#6b5d4e;">{pen}</td>
  <td>{wt}</td>
  <td>{pill}</td>
</tr>"""
                st.markdown(f"""
<table class="pig-tbl">
  <thead><tr><th>Tag ID</th><th>Pen</th><th>Weight</th><th>Status</th></tr></thead>
  <tbody>{rows}</tbody>
</table>""", unsafe_allow_html=True)
            else:
                st.caption("No pigs registered yet.")

    with right:
        with st.container(border=True):
            st.markdown("""
<div class="panel-title">
    Piglets Born
    <span style="font-size:11px;color:#9a8d7e;">last 7 weeks</span>
</div>""", unsafe_allow_html=True)

            max_val = max((w["piglets"] for w in weekly), default=1) or 1
            bars = ""
            for i, w in enumerate(weekly):
                pct = max(int(w["piglets"] / max_val * 100), 4 if w["piglets"] > 0 else 0)
                hi  = "hi" if i == len(weekly) - 1 else ""
                bars += f'<div class="bar-col"><div class="bar-fill {hi}" style="height:{pct}%;"></div><div class="bar-lbl">{w["week"]}</div></div>'

            total_piglets = sum(w["piglets"] for w in weekly)
            st.markdown(f"""
<div class="chart-wrap">{bars}</div>
<div class="chart-footer">
    <span>{total_piglets} piglets total</span>
    <span>{weekly[-1]["piglets"] if weekly else 0} this week</span>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="panel-title">Recent Activity</div>', unsafe_allow_html=True)

            if activity:
                feed = ""
                for item in activity:
                    feed += f"""
<div class="feed-item">
    <div class="dot-{item['dot']}"></div>
    <div>
        <div class="feed-text">{item['text']}</div>
        <div class="feed-date">{item['date']}</div>
    </div>
</div>"""
                st.markdown(feed, unsafe_allow_html=True)
            else:
                st.caption("No health records yet.")
