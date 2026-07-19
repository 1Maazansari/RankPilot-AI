import streamlit as st


def render_score_card(score_data: dict):
    """
    Render the overall SEO score card.
    """

    summary = score_data["summary"]

    st.subheader("🏆 SEO Score")

    score_col, grade_col = st.columns(2)

    with score_col:
        st.metric(
            label="Score",
            value=f'{score_data["score"]}/100'
        )

    with grade_col:
        st.metric(
            label="Grade",
            value=score_data["grade"]
        )

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🔴 Critical", summary["critical"])
    c2.metric("🟠 High", summary["high"])
    c3.metric("🟡 Medium", summary["medium"])
    c4.metric("🟢 Low", summary["low"])