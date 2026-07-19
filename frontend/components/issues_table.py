import streamlit as st
import pandas as pd


def render_issues_table(issues: list):
    """
    Render SEO issues in a table.
    """

    st.subheader("🚨 SEO Issues")

    if not issues:
        st.success("🎉 No SEO issues found!")
        return

    rows = []

    severity_icons = {
        "critical": "🔴 Critical",
        "high": "🟠 High",
        "medium": "🟡 Medium",
        "low": "🟢 Low",
    }

    for issue in issues:
        rows.append({
            "Severity": severity_icons.get(
                issue["severity"],
                issue["severity"].title()
            ),
            "Category": issue["category"].title(),
            "Issue": issue["message"],
            "Recommendation": issue["recommendation"],
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )