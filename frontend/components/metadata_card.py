import streamlit as st


def render_metadata_card(scan_data: dict):
    """
    Render metadata information.
    """

    st.subheader("📝 Metadata")

    st.write(f"**Title:** {scan_data['title'] or 'Not Found'}")

    st.write(f"**Meta Description:** {scan_data['meta_description'] or 'Not Found'}")

    st.write(f"**Canonical URL:** {scan_data['canonical'] or 'Not Found'}")

    st.write(f"**Meta Robots:** {scan_data['meta_robots'] or 'Not Found'}")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Language", scan_data["language"] or "Unknown")

    with col2:
        st.metric("Charset", scan_data["charset"] or "Unknown")