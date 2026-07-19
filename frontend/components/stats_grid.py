import streamlit as st


def render_stats_grid(scan_data: dict):
    """
    Render website scan statistics.
    """

    st.subheader("📊 Website Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("H1", scan_data["h1_count"])
        st.metric("Images", scan_data["images"])

    with col2:
        st.metric("H2", scan_data["h2_count"])
        st.metric("Missing Alt", scan_data["missing_alt"])

    with col3:
        st.metric("Internal Links", scan_data["internal_links"])
        st.metric(
            "Robots.txt",
            "✅ Found" if scan_data["robots_found"] else "❌ Missing",
        )

    with col4:
        st.metric(
            "Sitemap",
            "✅ Found" if scan_data["sitemap_found"] else "❌ Missing",
        )

        st.metric(
            "Canonical",
            "✅ Present" if scan_data["canonical"] else "❌ Missing",
        )