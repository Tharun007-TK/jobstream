"""UI component for displaying ATS scores."""

import streamlit as st

def render_ats_score(score_data: dict):
    """Render the ATS score visualization."""
    if not score_data:
        return

    score = score_data.get('total_score', 0)
    
    # Determine color
    if score >= 80:
        color = "green"
        msg = "Excellent Match! 🚀"
    elif score >= 50:
        color = "orange"
        msg = "Good Match 👍"
    else:
        color = "red"
        msg = "Low Match ⚠️"

    st.markdown(f"""
    <div style="text-align: center; padding: 20px; border-radius: 10px; border: 2px solid {color}; margin-bottom: 20px;">
        <h2>ATS Score</h2>
        <h1 style="color: {color}; font-size: 3em; margin: 0;">{score}%</h1>
        <p style="font-size: 1.2em; font-weight: bold;">{msg}</p>
    </div>
    """, unsafe_allow_html=True)

    # Breakdown
    st.subheader("Score Breakdown")
    breakdown = score_data.get('breakdown', {})
    
    cols = st.columns(3)
    with cols[0]:
        st.metric("Keywords", f"{breakdown.get('keywords', 0)}%")
        st.progress(breakdown.get('keywords', 0) / 100)
    with cols[1]:
        st.metric("Skills", f"{breakdown.get('skills', 0)}%")
        st.progress(breakdown.get('skills', 0) / 100)
    with cols[2]:
        st.metric("Experience", f"{breakdown.get('experience', 0)}%")
        st.progress(breakdown.get('experience', 0) / 100)

    # Missing Skills
    missing = score_data.get('missing_skills', [])
    if missing:
        st.warning(f"**Missing Skills:** {', '.join(missing)}")
        st.caption("Consider adding these to your resume or cover letter if you have them.")
