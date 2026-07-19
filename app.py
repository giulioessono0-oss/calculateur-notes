import streamlit as st
import pandas as pd
from translations import TRANSLATIONS

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Syfer – Grade Calculator",
    page_icon="📊",
    layout="centered",
)

# ── Language selector ─────────────────────────────────────────────────────────
LANG_OPTIONS = {
    "Français 🇫🇷": "fr",
    "English 🇬🇧":  "en",
    "Italiano 🇮🇹": "it",
}

lang_label = st.selectbox(
    "🌐 Langue / Language / Lingua",
    options=list(LANG_OPTIONS.keys()),
    key="lang_selector",
)
lang = LANG_OPTIONS[lang_label]
T = TRANSLATIONS[lang]

# ── Title ─────────────────────────────────────────────────────────────────────
st.title(T["app_title"])
st.markdown(T["subtitle"])

# ── Student name ──────────────────────────────────────────────────────────────
name = st.text_input(T["name_label"], placeholder=T["name_placeholder"], key="student_name")

st.divider()

# ── Subject definitions (from translation file) ───────────────────────────────
subjects   = T["subjects"]                          # list of (name, coef)
total_coef = sum(coef for _, coef in subjects)      # always 26
max_total  = 20.0 * total_coef                      # 520.0

# ── Score inputs ──────────────────────────────────────────────────────────────
# BUG FIX: keys are index-based ("score_0" … "score_7") so scores are preserved
# when the user switches language — the subject names change but the values stay.
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
            key=f"score_{i}",          # ← stable key, not tied to language
        )
        scores[subject] = score

st.divider()

# ── Calculate ─────────────────────────────────────────────────────────────────
if st.button(T["btn_calculate"], use_container_width=True, type="primary"):

    if not name.strip():
        st.warning(T["warn_name"])
    else:
        weighted_scores = {subj: scores[subj] * coef for subj, coef in subjects}
        total   = sum(weighted_scores.values())
        average = total / total_coef

        st.subheader(f"{T['results_for']} **{name.strip()}**")

        # ── Breakdown table (dataframe avoids markdown pipe/alignment bugs) ───
        st.markdown(T["breakdown_title"])

        df = pd.DataFrame(
            [
                {
                    T["col_subject"]:  subj,
                    T["col_mark"]:     f"{scores[subj]:.1f}",
                    T["col_coef"]:     coef,
                    T["col_weighted"]: f"{weighted_scores[subj]:.1f}",
                }
                for subj, coef in subjects
            ]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()

        # ── Summary metrics ───────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        m1.metric(T["metric_total"],   f"{total:.1f} / {int(max_total)}")
        m2.metric(T["metric_average"], f"{average:.2f}")
        m3.metric(T["metric_coef"],    total_coef)

        # ── Progress bar ──────────────────────────────────────────────────────
        # BUG FIX: clamp to [0.0, 1.0] so st.progress never raises ValueError
        pct = max(0.0, min(1.0, total / max_total))
        st.progress(pct, text=f"{T['progress_label']}: {pct * 100:.1f}%")

        st.divider()

        # ── Pass / fail verdict ───────────────────────────────────────────────
        # BUG FIX: threshold was 140 (from buggy original with only 4 subjects).
        # Correct threshold = average of 10/20 × total_coef = 10 × 26 = 260.
        PASS_THRESHOLD = 10.0 * total_coef   # 260 — scales automatically if coefs change

        fmt = dict(name=name.strip(), total=f"{total:.1f}", avg=f"{average:.2f}")
        if total >= PASS_THRESHOLD:
            st.success(T["pass_msg"].format(**fmt))
        else:
            st.error(T["fail_msg"].format(**fmt))

        # ── Per-subject performance ───────────────────────────────────────────
        st.markdown(T["perf_title"])
        for subj, _ in subjects:
            mark  = scores[subj]
            # BUG FIX: clamp progress value so 0-input never produces a float
            # outside [0.0, 1.0] due to floating-point drift
            pct_s = max(0.0, min(1.0, mark / 20.0))
            if mark >= 14:
                label = T["perf_good"]
            elif mark >= 10:
                label = T["perf_avg"]
            else:
                label = T["perf_bad"]
            st.progress(pct_s, text=f"{subj}: {mark:.1f}/20  {label}")

    
