"""Resume parsing service for extracting data from PDF and DOCX files."""

import fitz  # PyMuPDF
import docx
import re
from typing import Dict, List, Optional
import io

class ResumeParser:
    """Parses resume files and extracts structured data."""

    # Common technical skills to look for
    COMMON_SKILLS = {
        'python', 'java', 'c++', 'javascript', 'typescript', 'react', 'angular',
        'vue', 'node.js', 'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql',
        'mongodb', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'ci/cd',
        'machine learning', 'deep learning', 'nlp', 'pytorch', 'tensorflow',
        'scikit-learn', 'pandas', 'numpy', 'data analysis', 'rest api', 'graphql',
        'html', 'css', 'sass', 'less', 'redux', 'mobx', 'next.js', 'nuxt.js',
        'elasticsearch', 'redis', 'rabbitmq', 'kafka', 'linux', 'bash', 'shell'
    }

    def parse_file(self, file_content: bytes, filename: str) -> Dict:
        """
        Parse a resume file and extract data.

        Args:
            file_content: Raw bytes of the uploaded file
            filename: Name of the file (to determine type)

        Returns:
            Dictionary containing extracted data
        """
        text = ""
        if filename.lower().endswith('.pdf'):
            text = self._extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            text = self._extract_text_from_docx(file_content)
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX.")

        return self._extract_info(text)

    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""

    def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX bytes."""
        try:
            doc = docx.Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return ""

    def _extract_info(self, text: str) -> Dict:
        """Extract structured info from raw text."""
        # Normalize text
        text_lower = text.lower()
        
        # Extract skills
        found_skills = [
            skill for skill in self.COMMON_SKILLS 
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower)
        ]

        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        email = emails[0] if emails else None

        # Rough experience estimation (looking for years)
        # This is primitive; real extraction is much harder
        years_pattern = r'(\d+)\+?\s*years?'
        years_matches = re.findall(years_pattern, text_lower)
        max_years = 0
        if years_matches:
            try:
                max_years = max([int(y) for y in years_matches if int(y) < 40])
            except:
                pass

        return {
            "raw_text": text,
            "skills": sorted(list(set(found_skills))),
            "email": email,
            "years_experience": max_years,
            "word_count": len(text.split())
        }
