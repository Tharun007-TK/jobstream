"""Professional AI/ML Job Scraper - Main Application."""

import streamlit as st
from pathlib import Path
from datetime import datetime
import re

from services.data_loader import JobDataLoader
from components.filters import render_filters


st.set_page_config(
    page_title="AI/ML Jobs",
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
    with st.container():
        col1, col2 = st.columns([4, 1])
        
        with col1:
            title = clean_html(job.get('title')) or 'Untitled Position'
            st.markdown(f"### {title}")
        
        with col2:
            source = clean_html(job.get('source')) or 'Unknown'
            st.caption(source)
        
        company = clean_html(job.get('company')) or 'Unknown Company'
        st.markdown(f"**{company}**")
        
        meta_parts = []
        location = clean_html(job.get('location'))
        if location:
            meta_parts.append(f"📍 {location}")
        
        if job.get('is_remote'):
            meta_parts.append("🏠 Remote")
        
        employment_type = clean_html(job.get('employment_type'))
        if employment_type:
            meta_parts.append(f"💼 {employment_type}")
        
        experience = clean_html(job.get('experience'))
        if experience:
            meta_parts.append(f"📊 {experience}")
        
        if meta_parts:
            st.text(" • ".join(meta_parts))
        
        salary = clean_html(job.get('salary'))
        if salary:
            st.markdown(f"💰 **{salary}**")
        
        skills = clean_html(job.get('skills'))
        if skills:
            st.caption(f"**Skills:** {skills}")
        
        st.divider()
        
        footer_col1, footer_col2 = st.columns([3, 1])
        
        with footer_col1:
            posted_date = format_date(job.get('posted_date'))
            st.caption(f"Posted: {posted_date}")
        
        with footer_col2:
            job_url = job.get('job_url')
            if job_url and job_url not in ['nan', 'None']:
                st.link_button("View Job", job_url, use_container_width=True)
        
        st.markdown("")


def main():
    """Main application logic."""
    
    st.title("AI/ML Job Opportunities")
    st.caption("Curated positions from top sources")
    st.divider()
    
    loader = JobDataLoader(data_dir="../data")
    
    with st.spinner("Loading job listings..."):
        jobs_df = loader.load_latest_jobs()
    
    if jobs_df.empty:
        st.warning("No job data found. Please run the scraper first.")
        st.info("Run: `python -m main` from the job_scraper directory")
        return
    
    all_locations = loader.get_unique_values(jobs_df, "location")
    all_sources = loader.get_unique_values(jobs_df, "source")
    
    selected_locations, selected_sources, remote_filter = render_filters(
        locations=all_locations,
        sources=all_sources
    )
    
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🔍 Search Jobs", type="primary", use_container_width=True):
            st.session_state.show_results = True
    
    with col2:
        if st.button("Clear Search", use_container_width=True):
            st.session_state.show_results = False
    
    st.divider()
    
    if not st.session_state.show_results:
        st.info("👆 Configure your filters and click **Search Jobs** to view results")
        return
    
    remote_only = remote_filter == "Remote Only"
    onsite_only = remote_filter == "Onsite Only"
    
    filtered_df = loader.filter_jobs(
        df=jobs_df,
        locations=selected_locations if selected_locations else None,
        sources=selected_sources if selected_sources else None,
        remote_only=remote_only,
        onsite_only=onsite_only
    )
    
    if filtered_df.empty:
        st.warning("🔍 No jobs match your filters. Try adjusting your criteria.")
        return
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"Showing **{len(filtered_df):,}** of **{len(jobs_df):,}** jobs")
    
    with col2:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"ai_ml_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.divider()
    
    jobs_list = filtered_df.to_dict('records')
    
    for job in jobs_list:
        render_job_card(job)
    
    st.divider()
    st.caption(f"Displaying {len(filtered_df)} job listings")


if __name__ == "__main__":
    main()
