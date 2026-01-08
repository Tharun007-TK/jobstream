"""Professional AI/ML Job Scraper - Main Application."""

import streamlit as st
from pathlib import Path
from datetime import datetime
import re
import pandas as pd

from services.data_loader import JobDataLoader
from services.job_matcher import JobMatcher
from services.ats_scorer import ATSScorer
from components.filters import render_filters
from components.resume_upload import render_resume_upload
from components.matched_job_card import render_matched_job_card
from components.ats_score_display import render_ats_score


st.set_page_config(
    page_title="AI/ML Jobs & ATS",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


def clean_html(text):
    """Remove HTML tags and clean text."""
    if not text or text in ['nan', 'None']:
        return None
    text = str(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None


def format_date(date_str):
    """Format date string to human-readable format."""
    if not date_str or date_str in ['nan', 'None', 'Recently']:
        return "Recently"
    try:
        dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return str(date_str)


def render_job_card(job: dict):
    """Render a single job card using Streamlit native components."""
    # ... (Keep existing simple render logic if needed, or use the matched one without score)
    # We'll use the new matched card for consistency but handle missing score
    render_matched_job_card(job)


def main():
    """Main application logic."""
    st.title("AI/ML Job Board & Resume Intelligence")
    
    # Initialize services
    loader = JobDataLoader(data_dir="../data")
    matcher = JobMatcher()
    scorer = ATSScorer()
    
    # --- Resume Upload Section (Main Window) ---
    # We use an expander that is open if no resume is uploaded yet
    has_resume = 'resume_data' in st.session_state and st.session_state['resume_data']
    
    with st.expander("📂 Upload Resume & Profile Analysis", expanded=not has_resume):
        resume_data = render_resume_upload()
    
    if resume_data:
        st.success(f"✅ Profile Active: Matching jobs for skills: {', '.join(resume_data.get('skills', [])[:5])}...")

    # Load Data
    with st.spinner("Loading job listings..."):
        jobs_df = loader.load_latest_jobs()
    
    if jobs_df.empty:
        st.warning("No job data found. Please run the scraper first.")
        st.info("Run: `python -m main` from the job_scraper directory")
        return

    # Main Tabs
    # We merged Smart Match into Job Search, so we might not need a separate tab, 
    # but let's keep ATS Score Check separate.
    tab1, tab2 = st.tabs(["🔍 Job Search & Matches", "📊 ATS Score Simulator"])

    # --- TAB 1: Search & Matches ---
    with tab1:
        st.caption("Browse curated AI/ML positions")
        
        # Filters
        all_locations = loader.get_unique_values(jobs_df, "location")
        all_sources = loader.get_unique_values(jobs_df, "source")
        
        selected_locations, selected_sources, remote_filter = render_filters(
            locations=all_locations,
            sources=all_sources
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            search_clicked = st.button("Search Jobs", type="primary", use_container_width=True, key="search_btn")
        
        # Determine if we show results (default to showing some if resume is there? or wait for click?)
        # Let's wait for click or if 'show_results' is set.
        if search_clicked:
            st.session_state.show_results = True
            
        if st.session_state.get('show_results'):
            remote_only = remote_filter == "Remote Only"
            onsite_only = remote_filter == "Onsite Only"
            
            # 1. Filter Check
            filtered_df = loader.filter_jobs(
                df=jobs_df,
                locations=selected_locations if selected_locations else None,
                sources=selected_sources if selected_sources else None,
                remote_only=remote_only,
                onsite_only=onsite_only
            )
            
            # 2. Match Scoring (if resume exists)
            if resume_data and not filtered_df.empty:
                with st.spinner("Calculating match scores..."):
                    # We match against the filtered list
                    # Use a low threshold to just get scores, we can sort by them
                    filtered_df = matcher.match_jobs(resume_data, filtered_df, threshold=0)
                    # Sort by match score descending
                    filtered_df = filtered_df.sort_values(by='match_score', ascending=False)
            
            st.divider()
            
            # Header stats
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Found {len(filtered_df)} jobs**")
            with c2:
                # CSV Download
                st.download_button(
                    label="📥 Download CSV",
                    data=filtered_df.to_csv(index=False),
                    file_name=f"ai_ml_jobs_matched_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # 3. Render
            if filtered_df.empty:
                st.warning("No jobs match your criteria.")
            else:
                jobs_list = filtered_df.to_dict('records')
                for job in jobs_list:
                    # Pass score awareness (render_matched_job_card handles it if 'match_score' key exists)
                    render_matched_job_card(job)

    # --- TAB 2: ATS Checker ---
    with tab2:
        st.subheader("ATS Score Simulator")
        st.caption("Test your resume against specific job descriptions")
        
        col1, col2 = st.columns(2)
        
        selected_job_title = None
        selected_job_desc = ""
        
        with col1:
            # Option A: Select from list
            job_titles = jobs_df['title'].unique().tolist()
            selected_job_title = st.selectbox("Select a job from our list", ["Select a job..."] + job_titles)
            
            if selected_job_title != "Select a job...":
                job_row = jobs_df[jobs_df['title'] == selected_job_title].iloc[0]
                # Simulating description from available fields
                selected_job_desc = f"{job_row.get('title')} at {job_row.get('company')} \n\nSkills: {job_row.get('skills')} \n\nExperience: {job_row.get('experience')}"
                st.info(f"Loaded details for {selected_job_title}")
        
        with col2:
            # Option B: Paste JD
            custom_jd = st.text_area("Or paste a Job Description here", height=200)
            if custom_jd:
                selected_job_desc = custom_jd
        
        if st.button("Calculate Score", type="primary", key="calc_ats"):
            if not resume_data:
                st.error("Please upload a resume in the panel above first!")
            elif not selected_job_desc:
                st.error("Please select a job or paste a description.")
            else:
                score_result = scorer.calculate_score(resume_data, selected_job_desc)
                render_ats_score(score_result)


if __name__ == "__main__":
    main()
