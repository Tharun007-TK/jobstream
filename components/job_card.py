"""Job card component for displaying individual job listings."""

import streamlit as st
from datetime import datetime
import html


def render_job_card(job: dict, index: int) -> None:
    """
    Render a single job card.

    Args:
        job: Dictionary containing job details
        index: Card index for unique key
    """
    # Escape HTML in user data
    title = html.escape(str(job.get('title', 'Untitled Position')))
    company = html.escape(str(job.get('company', 'Unknown Company')))
    location = html.escape(str(job.get('location', 'Not specified')))
    source = html.escape(str(job.get('source', 'Unknown')))
    
    # Build optional sections
    remote_badge = '<span class="meta-item remote-badge">🏠 Remote</span>' if job.get('is_remote') else ''
    
    employment_type = job.get('employment_type')
    employment_badge = f'<span class="meta-item">💼 {html.escape(str(employment_type))}</span>' if employment_type else ''
    
    experience = job.get('experience')
    experience_badge = f'<span class="meta-item">📊 {html.escape(str(experience))}</span>' if experience else ''
    
    salary = job.get('salary')
    salary_section = f'<div class="job-salary">💰 {html.escape(str(salary))}</div>' if salary else ''
    
    skills = job.get('skills')
    skills_section = f'<div class="job-skills">{html.escape(str(skills))}</div>' if skills else ''
    
    job_url = job.get('job_url')
    apply_button = f'<a href="{html.escape(str(job_url))}" target="_blank" class="apply-btn">Apply Now →</a>' if job_url else ''
    
    posted_date = _format_date(job.get('posted_date', ''))
    
    # Build the complete HTML card
    card_html = f"""<div class="job-card">
    <div class="job-header">
        <h3 class="job-title">{title}</h3>
        <span class="job-source">{source}</span>
    </div>
    
    <div class="job-company">
        <strong>{company}</strong>
    </div>
    
    <div class="job-meta">
        <span class="meta-item">📍 {location}</span>
        {remote_badge}
        {employment_badge}
        {experience_badge}
    </div>
    
    {salary_section}
    {skills_section}
    
    <div class="job-footer">
        <span class="posted-date">Posted: {posted_date}</span>
        {apply_button}
    </div>
</div>"""
    
    st.markdown(card_html, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def _format_date(date_str: str) -> str:
    """
    Format date string for display.

    Args:
        date_str: Date string

    Returns:
        Formatted date or original string
    """
    if not date_str:
        return "Recently"
    
    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%b %d, %Y")
    except:
        return date_str
