import streamlit as st


def render_ai_recommendations(recommendations: list):
    """
    Render AI-generated recommendations.
    """

    st.subheader("🤖 AI Recommendations")

    if not recommendations:
        st.info("No AI recommendations available.")
        return

    priority_colors = {
        1: "🔴 High Priority",
        2: "🟠 Medium Priority",
        3: "🟢 Low Priority",
    }

    for recommendation in recommendations:

        with st.container(border=True):

            st.markdown(f"### {recommendation['title']}")

            st.markdown(
                f"**Priority:** {priority_colors.get(recommendation['priority'], '⚪ Normal')}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**📈 Impact**")
                st.write(recommendation["impact"])

            with col2:
                st.markdown(f"**⏱ Estimated Effort**")
                st.write(recommendation["estimated_effort"])

            st.markdown("**💡 Why?**")
            st.write(recommendation["reason"])

            st.markdown("**🛠 Recommended Action**")
            st.success(recommendation["action"])