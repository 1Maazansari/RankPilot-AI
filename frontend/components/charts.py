import streamlit as st
import plotly.express as px


def render_charts(score_data: dict, issues: list):
    """
    Render dashboard charts.
    """

    st.subheader("📊 SEO Analytics")

    col1, col2 = st.columns(2)

    # -------------------------
    # Chart 1 - SEO Score
    # -------------------------
    with col1:

        score = score_data["score"]

        fig = px.pie(
            names=["SEO Score", "Remaining"],
            values=[score, 100 - score],
            hole=0.65,
            title="SEO Score",
        )

        fig.update_layout(
            showlegend=True,
            margin=dict(l=10, r=10, t=50, b=10),
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # Chart 2 - Issue Severity
    # -------------------------
    with col2:

        severity = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
        }

        for issue in issues:
            sev = issue["severity"].capitalize()
            severity[sev] += 1

        fig = px.bar(
            x=list(severity.keys()),
            y=list(severity.values()),
            title="Issues by Severity",
            labels={
                "x": "Severity",
                "y": "Count",
            },
        )

        fig.update_layout(
            margin=dict(l=10, r=10, t=50, b=10),
        )

        st.plotly_chart(fig, use_container_width=True)