"""ATS Scoring service for comparing resumes to job descriptions."""

from typing import Dict, List, Set, Tuple
import re

class ATSScorer:
    """Calculates ATS scores by comparing resume data against job details."""

    def calculate_score(self, resume_data: Dict, job_description: str) -> Dict:
        """
        Calculate ATS score for a resume against a job description.

        Args:
            resume_data: Dictionary containing parsed resume info (skills, text, etc.)
            job_description: Full text of the job description

        Returns:
            Dictionary containing total score and breakdown
        """
        job_text_lower = job_description.lower()
        resume_text_lower = resume_data.get('raw_text', '').lower()
        
        # 1. Keyword Matching (40%)
        # Extract potential keywords from job description (simple frequency/presence)
        # In a real app, this would use NLP keyword extraction
        job_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_data.get('raw_text', ''))
        
        keyword_match_score = self._calculate_overlap(job_keywords, resume_keywords)
        
        # 2. Skills Matching (35%)
        # We assume job description contains skills. 
        # Ideally we'd parse skills from JD too, but for now we look for ResumeParser.COMMON_SKILLS in JD matched against resume skills
        resume_skills = set(resume_data.get('skills', []))
        
        # Find which common skills appear in the job description
        # We need to import the skills list or pass it in. Ideally passed in.
        # For simplicity, we just look for words in JD that match resume skills to see relevance,
        # AND we check if resume skills are present in JD.
        
        # Better approach: Find "required" skills in JD (simulated by finding common tech terms in JD)
        jd_skills = self._extract_skills_from_text(job_text_lower, resume_data.get('skills', []))
        
        if not jd_skills:
            # If no skills found in JD, fall back to keyword match
            skill_match_score = keyword_match_score
        else:
            skill_overlap = resume_skills.intersection(jd_skills)
            skill_match_score = (len(skill_overlap) / len(jd_skills)) * 100 if jd_skills else 0

        # 3. Experience/Context Match (25%)
        # Simple length/complexity check + experience years if available
        # This is a heuristic placeholder
        exp_score = 0
        
        # Check for experience years mention in JD
        jd_years = self._extract_years_req(job_text_lower)
        resume_years = resume_data.get('years_experience', 0)
        
        if jd_years > 0:
            if resume_years >= jd_years:
                exp_score = 100
            else:
                exp_score = (resume_years / jd_years) * 100
        else:
            # If no years specified, give a base score based on resume length/richness
            word_count = resume_data.get('word_count', 0)
            exp_score = min(100, (word_count / 500) * 100) # 500 words is a decent resume

        # Weighted Total
        total_score = (
            (keyword_match_score * 0.4) +
            (skill_match_score * 0.35) +
            (exp_score * 0.25)
        )

        return {
            "total_score": round(total_score, 1),
            "breakdown": {
                "keywords": round(keyword_match_score, 1),
                "skills": round(skill_match_score, 1),
                "experience": round(exp_score, 1)
            },
            "missing_skills": list(jd_skills - resume_skills),
            "matched_skills": list(resume_skills.intersection(jd_skills))
        }

    def _extract_keywords(self, text: str) -> Set[str]:
        """Simple keyword extraction (non-stop words)."""
        # Very basic stop words list
        stop_words = {
            'and', 'the', 'is', 'in', 'at', 'of', 'or', 'for', 'with', 'to', 'a', 'an', 
            'as', 'by', 'on', 'are', 'be', 'will', 'that', 'this', 'from', 'it', 'we', 'us'
        }
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return set([w for w in words if w not in stop_words])

    def _calculate_overlap(self, set_a: Set, set_b: Set) -> float:
        """Calculate percentage of set_a found in set_b."""
        if not set_a:
            return 0.0
        overlap = set_a.intersection(set_b)
        return (len(overlap) / len(set_a)) * 100

    def _extract_skills_from_text(self, text: str, known_skills: List[str]) -> Set[str]:
        """
        Identify known skills present in text. 
        Using the skills found in resume as a corpus of 'valid tech words' 
        plus potentially others if we had a global list.
        For now, we check which of the resume's 'known universe' of skills are in the JD.
        NOTE: This limits us to only finding skills the parser knows about.
        """
        # Ideally, we should import common skills from ResumeParser, but to avoid circular import
        # we can just use regex for the words that look like technical terms or pass them in.
        # Here we'll just scan for the skills the resume parser identified as "tech skills" 
        # to see if they are in the JD (relevance)
        # BUT we also need to find skills in JD that the resume *doesn't* have.
        # So we really need that global list here too.
        
        # Quick fix: Redefine a small set or reliance on input
        # We will do a simple word match against the extracted keywords from earlier
        # assuming technical skills are usually captured there.
        return set() # Placeholder - logic handled in calculate_score via set operations if we had the list.
        
        # Real implementation:
        # We will try to match the keywords in JD against a provided 'all_skills' set if passed,
        # or we'll just use the intersection of keywords logic as a proxy.
        # Let's improve this by actually moving the skill list to a shared constant or just duplicating for now.
        
        common_tech = {
            'python', 'java', 'c++', 'javascript', 'typescript', 'react', 'angular',
            'vue', 'node.js', 'django', 'flask', 'fastapi', 'sql', 'mysql', 'postgresql',
            'mongodb', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'ci/cd',
            'machine learning', 'deep learning', 'nlp', 'pytorch', 'tensorflow',
            'scikit-learn', 'pandas', 'numpy', 'data analysis', 'rest api'
        }
        
        found = set()
        for skill in common_tech:
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                found.add(skill)
        return found

    def _extract_years_req(self, text: str) -> int:
        """Extract required years of experience from JD."""
        matches = re.findall(r'(\d+)\+?\s*years?', text)
        if matches:
            try:
                return min([int(x) for x in matches]) # Assume minimum requirement is what we care about
            except:
                return 0
        return 0
