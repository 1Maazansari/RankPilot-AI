import streamlit as st
from services.api import scan_website
from components.score_card import render_score_card
from services.api import scan_website
from components.stats_grid import render_stats_grid
from components.metadata_card import render_metadata_card
from components.issues_table import render_issues_table
from components.ai_recommendations import render_ai_recommendations
from components.charts import render_charts
def load_css():
    with open("frontend/styles/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()
# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="RankPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------
# Hero Section
# -------------------------------
st.title("🚀 RankPilot AI")
st.subheader("AI-Powered SEO Website Auditor")

st.markdown("""
# 🚀 RankPilot AI

### AI-Powered SEO Website Auditor

Analyze any website in seconds and receive AI-powered SEO insights.
""")

st.divider()

# -------------------------------
# URL Input
# -------------------------------
col1, col2 = st.columns([5,1])

with col1:
    website_url = st.text_input(
        "",
        placeholder="https://example.com"
    )

with col2:
    scan_button = st.button(
        "🚀 Scan",
        use_container_width=True
    )


if scan_button:

    if not website_url:
        st.error("Please enter a website URL.")

    else:

        with st.spinner("Scanning website..."):

            try:
                result = scan_website(website_url)

                st.toast("Website scanned successfully! 🎉")

                render_score_card(result["seo"]["score"])

                st.divider()

                render_charts(
                result["seo"]["score"],
                result["seo"]["issues"]
)

                st.divider()

                render_stats_grid(result["scan"])

                st.divider()

                render_metadata_card(result["scan"])

                st.divider()

                render_issues_table(result["seo"]["issues"])

                st.divider()

                render_ai_recommendations(result["ai"]["recommendations"])

                st.divider()

                st.caption(
    "🚀 RankPilot AI • Powered by FastAPI • Gemini • Streamlit"
)
               

            except Exception as e:
                st.error(str(e))