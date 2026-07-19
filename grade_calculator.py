import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from translations import TRANSLATIONS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Syfer – Grade Calculator",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS — minimal polish only ─────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        color: white;
        margin-bottom: 0.5rem;
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; }
    .metric-card .label { font-size: 0.85rem; opacity: 0.8; margin-top: 0.2rem; }
    .pass-banner {
        background: linear-gradient(90deg, #0a7c4b, #12b76a);
        border-radius: 10px; padding: 1rem 1.5rem;
        color: white; font-size: 1.1rem; font-weight: 600; text-align: center;
    }
    .fail-banner {
        background: linear-gradient(90deg, #991b1b, #dc2626);
        border-radius: 10px; padding: 1rem 1.5rem;
        color: white; font-size: 1.1rem; font-weight: 600; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Language selector ─────────────────────────────────────────────────────────
LANG_OPTIONS = {
    "Français 🇫🇷": "fr",
    "English 🇬🇧":  "en",
    "Italiano 🇮🇹": "it",
}

col_lang, col_spacer = st.columns([2, 6])
with col_lang:
    lang_label = st.selectbox(
        "🌐 Langue / Language / Lingua",
        options=list(LANG_OPTIONS.keys()),
        key="lang_selector",
    )
lang = LANG_OPTIONS[lang_label]
T   = TRANSLATIONS[lang]

st.title(T["app_title"])
st.markdown(T["subtitle"])
st.divider()

# ── Subject definitions ───────────────────────────────────────────────────────
subjects   = T["subjects"]
total_coef = sum(coef for _, coef in subjects)   # 26
max_total  = 20.0 * total_coef                   # 520.0

# ── Input form ────────────────────────────────────────────────────────────────
with st.form("grade_form"):
    name = st.text_input(
        T["name_label"],
        placeholder=T["name_placeholder"],
        key="student_name",
    )

    st.subheader(T["section_marks"])

    scores: dict[str, float] = {}
    cols = st.columns(2)
    for i, (subject, coef) in enumerate(subjects):
        with cols[i % 2]:
            score = st.number_input(
                f"{subject}  *({T['coef_label']} {coef})*",
                min_value=0.0,
                max_value=20.0,
                value=0.0,
                step=0.5,
                key=f"score_{i}",
            )
            scores[subject] = score

    submitted = st.form_submit_button(
        T["btn_calculate"], use_container_width=True, type="primary"
    )

# ── Results ───────────────────────────────────────────────────────────────────
if submitted:
    if not name.strip():
        st.warning(T["warn_name"])
        st.stop()

    weighted_scores = {subj: scores[subj] * coef for subj, coef in subjects}
    total   = sum(weighted_scores.values())
    average = total / total_coef
    pct     = max(0.0, min(1.0, total / max_total))

    PASS_THRESHOLD = 10.0 * total_coef   # 260

    st.divider()
    st.subheader(f"{T['results_for']} **{name.strip()}**")

    # ── Pass / fail banner ────────────────────────────────────────────────────
    fmt = dict(name=name.strip(), total=f"{total:.1f}", avg=f"{average:.2f}")
    if total >= PASS_THRESHOLD:
        st.markdown(
            f'<div class="pass-banner">{T["pass_msg"].format(**fmt)}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="fail-banner">{T["fail_msg"].format(**fmt)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI cards ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{total:.1f}</div>
            <div class="label">{T["metric_total"]} / {int(max_total)}</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{average:.2f}</div>
            <div class="label">{T["metric_average"]}</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{pct*100:.1f}%</div>
            <div class="label">{T["progress_label"]}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="value">{total_coef}</div>
            <div class="label">{T["metric_coef"]}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts row ────────────────────────────────────────────────────────────
    chart_left, chart_right = st.columns([1, 1])

    # Gauge chart
    with chart_left:
        gauge_color = "#12b76a" if total >= PASS_THRESHOLD else "#dc2626"
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=round(average, 2),
            delta={"reference": 10, "valueformat": ".2f"},
            number={"suffix": "/20", "font": {"size": 36}},
            title={"text": T["metric_average"], "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 20], "tickwidth": 1},
                "bar":  {"color": gauge_color, "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "#e5e7eb",
                "steps": [
                    {"range": [0, 10],  "color": "#fef2f2"},
                    {"range": [10, 14], "color": "#fefce8"},
                    {"range": [14, 20], "color": "#f0fdf4"},
                ],
                "threshold": {
                    "line": {"color": "#6b7280", "width": 3},
                    "thickness": 0.8,
                    "value": 10,
                },
            },
        ))
        fig_gauge.update_layout(
            height=320, margin=dict(t=60, b=20, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)", font_color="#1f2937",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Radar chart
    with chart_right:
        subj_names = [s for s, _ in subjects]
        raw_marks  = [scores[s] for s in subj_names]

        fig_radar = go.Figure(go.Scatterpolar(
            r=raw_marks + [raw_marks[0]],
            theta=subj_names + [subj_names[0]],
            fill="toself",
            fillcolor="rgba(99, 102, 241, 0.2)",
            line=dict(color="#6366f1", width=2),
            marker=dict(size=6, color="#6366f1"),
            name=name.strip(),
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 20], tickfont_size=10),
                angularaxis=dict(tickfont_size=11),
            ),
            height=320,
            margin=dict(t=40, b=20, l=40, r=40),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#1f2937",
            title=dict(text=T["perf_title"].replace("####", "").strip(), font_size=15),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Horizontal bar chart ──────────────────────────────────────────────────
    bar_colors = [
        "#12b76a" if scores[s] >= 14 else "#f59e0b" if scores[s] >= 10 else "#dc2626"
        for s, _ in subjects
    ]
    fig_bar = go.Figure(go.Bar(
        x=[scores[s] for s, _ in subjects],
        y=[s for s, _ in subjects],
        orientation="h",
        marker_color=bar_colors,
        text=[f"{scores[s]:.1f}/20" for s, _ in subjects],
        textposition="outside",
        cliponaxis=False,
    ))
    fig_bar.add_vline(x=10, line_dash="dash", line_color="#6b7280",
                      annotation_text="10/20", annotation_position="top right")
    fig_bar.add_vline(x=14, line_dash="dot",  line_color="#6b7280",
                      annotation_text="14/20", annotation_position="top right")
    fig_bar.update_layout(
        title=dict(text=T["breakdown_title"].replace("####", "").strip(), font_size=15),
        xaxis=dict(range=[0, 22], title="", showgrid=True, gridcolor="#f3f4f6"),
        yaxis=dict(title="", autorange="reversed"),
        height=360,
        margin=dict(t=50, b=20, l=10, r=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#1f2937",
        bargap=0.35,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Detail table ──────────────────────────────────────────────────────────
    with st.expander(T["breakdown_title"].replace("####", "").strip(), expanded=False):
        df = pd.DataFrame([
            {
                T["col_subject"]:  subj,
                T["col_mark"]:     f"{scores[subj]:.1f}",
                T["col_coef"]:     coef,
                T["col_weighted"]: f"{weighted_scores[subj]:.1f}",
            }
            for subj, coef in subjects
        ])
        st.dataframe(df, use_container_width=True, hide_index=True)

