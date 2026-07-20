
"""
Bloc Grade Calculator — Streamlit Web App
Weighted average for: Math (×5), Physics (×3), Computer Science (×3), A-Math (×3),Boilogy (*3),Geography (*3),Economics (*3)
Total coefficient = 23
"""


import streamlit as st

# ── Constants ─────────────────────────────────────────────────────────────────
SUBJECTS = {
    "Math": 5,
    "Physics": 3,
    "Computer Science": 3,
    "A-Math": 3,
    "Boilogy": 3,
    "Geography": 3,
    "Economics": 3,
    "French": 5,
    "English": 5,
}
TOTAL_COEFF = sum(SUBJECTS.values())  # 14
MAX_MARK = 20.0


def grade_info(average: float) -> tuple[str, str]:
    """Return (label, streamlit message type) based on average."""
    if average >= 16:
        return "🏆 Excellent!", "success"
    elif average >= 14:
        return "✅ Good pass!", "success"
    elif average >= 10:
        return "⚠️ Atleast you pass", "progress"
    else:
        return "❌ Not yet — keep going!", "error"


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bloc Grade Calculator",
    page_icon="🎓",
    layout="centered",
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🎓 Bloc Grade Calculator")
st.caption("Calculates your weighted average across (subject) subjects.")
st.divider()

# ── Student name ───────────────────────────────────────────────────────────────
name = st.text_input("Your name", placeholder="Enter your name…")

st.subheader("Enter your marks (out of 20)")

# ── Mark sliders ───────────────────────────────────────────────────────────────
cols = st.columns(2)
marks: dict[str, float] = {}

for i, (subject, coeff) in enumerate(SUBJECTS.items()):
    with cols[i % 2]:
        marks[subject] = st.slider(
            f"{subject}  _(coefficient ×{coeff})_",
            min_value=0.0,
            max_value=MAX_MARK,
            value=10.0,
            step=0.5,
            key=subject,
        )

st.divider()

# ── Calculate button ───────────────────────────────────────────────────────────
if st.button("Calculate my average", type="primary", use_container_width=True):
    weighted_total = sum(marks[s] * SUBJECTS[s] for s in SUBJECTS)
    average = weighted_total / TOTAL_COEFF
    label, msg_type = grade_info(average)
    display_name = name.strip() if name.strip() else "Student"

    st.subheader(f"Results for {display_name}")

    # KPI metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Weighted Total", f"{weighted_total:.1f} / {TOTAL_COEFF * MAX_MARK:.0f}")
    m2.metric("Average", f"{average:.2f} / {MAX_MARK:.0f}")
    m3.metric("Grade", label)

    # Breakdown table
    st.subheader("Breakdown")
    st.table(
        [
            {
                "Subject": subject,
                "Mark (/20)": marks[subject],
                "Coefficient": f"×{coeff}",
                "Weighted score": marks[subject] * coeff,
            }
            for subject, coeff in SUBJECTS.items()
        ]
    )

    # Progress bar
    st.subheader("Overall progress")
    st.progress(average / MAX_MARK, text=f"{average:.2f} / 20")

    # Feedback message
    feedback = {
        "success": (
            f"🏆 Outstanding, {display_name}! You're at the top of your class."
            if average >= 16
            else f"✅ Well done, {display_name}! You've passed with a solid result."
        ),
        "warning": f"⚠️ You're passing, {display_name}, but there's room to improve!",
        "error": f"❌ Not there yet, {display_name}. Don't give up — you can do better!",
    }
    getattr(st, msg_type)(feedback.get(msg_type, label))

    st.caption(
        "Adjust any slider above and click **Calculate** again to see how your score changes."
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Built by Giulio 2K · Syfer Grade Calculator")
