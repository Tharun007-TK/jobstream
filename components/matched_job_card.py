"""Component for rendering matched job cards."""

import streamlit as st
from .ats_score_display import render_ats_score

def render_matched_job_card(job: dict, score_data: dict = None):
    """
    Render a job card with added match score context.
    
    Args:
        job: Job dictionary
        score_data: Optional pre-calculated score data (if just showing list)
    """
    # Use existing styles but add match badge
    score = job.get('match_score', 0)
    
    # Color badge
    color = "green" if score >= 80 else "orange" if score >= 50 else "red"
    
    with st.container():
        col1, col2 = st.columns([5, 1])
        
        with col1:
            title = job.get('title', 'Untitled')
            st.markdown(f"### {title}")
            st.markdown(f"**{job.get('company', 'Unknown')}** • {job.get('location', '')}")
            
        with col2:
            st.markdown(f"""
            <div style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 5px; text-align: center;">
                <b>{int(score)}% Match</b>
            </div>
            """, unsafe_allow_html=True)
            
        # Details
        details = []
        if job.get('salary'): details.append(f"💰 {job.get('salary')}")
        if job.get('employment_type'): details.append(f"💼 {job.get('employment_type')}")
        
        if details:
            st.text(" • ".join(details))
            
        # Quick actions
        ac1, ac2 = st.columns([1, 4])
        with ac1:
            if job.get('job_url'):
                st.link_button("Apply Now", job.get('job_url'), use_container_width=True)
        
        with st.expander("Why this match?"):
            if score_data:
                # If passed direct detailed data
                render_ats_score(score_data)
            else:
                st.write("Score based on keyword and skill overlap.")
                st.caption(f"Skills matched: {job.get('skills', 'None listed')}")
        
        st.divider()
