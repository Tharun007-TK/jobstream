"""UI component for resume uploading."""

import streamlit as st
from services.resume_parser import ResumeParser

def render_resume_upload():
    """Render the resume upload section."""
    st.subheader("📄 Upload Resume")
    
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF or DOCX)", 
        type=['pdf', 'docx'],
        help="Upload your resume to enable auto-matching and ATS scoring"
    )

    if uploaded_file:
        try:
            # Check if we already parsed this specific file to avoid re-parsing on every rerun
            # Simple check by filename
            if (st.session_state.get('resume_filename') != uploaded_file.name):
                with st.spinner("Parsing resume..."):
                    parser = ResumeParser()
                    file_content = uploaded_file.read()
                    
                    # Parse
                    resume_data = parser.parse_file(file_content, uploaded_file.name)
                    
                    # Store in session
                    st.session_state['resume_data'] = resume_data
                    st.session_state['resume_filename'] = uploaded_file.name
                    
                    st.success("Resume parsed successfully!")
            
            # Display summary of parsed data
            if 'resume_data' in st.session_state:
                data = st.session_state['resume_data']
                
                with st.expander("✅ Parsing Summary", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Skills Found", len(data.get('skills', [])))
                    with col2:
                        st.metric("Est. Experience", f"{data.get('years_experience', 0)}+ Years")
                    
                    st.caption(f"**Top Skills:** {', '.join(data.get('skills', [])[:10])}...")
                    
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            
    return st.session_state.get('resume_data')
