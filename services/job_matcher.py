"""Service for matching jobs to a user's resume."""

from typing import List, Dict
import pandas as pd
from .ats_scorer import ATSScorer

class JobMatcher:
    """Matches and filters jobs based on resume data."""

    def __init__(self):
        self.scorer = ATSScorer()

    def match_jobs(self, resume_data: Dict, jobs_df: pd.DataFrame, threshold: float = 50.0) -> pd.DataFrame:
        """
        Rank jobs by match score against resume.

        Args:
            resume_data: Parsed resume dictionary
            jobs_df: DataFrame of available jobs
            threshold: Minimum score to include (0-100)

        Returns:
            DataFrame with added 'match_score' column, sorted by score
        """
        if jobs_df.empty or not resume_data:
            return jobs_df

        # Calculate score for each job
        scores = []
        for _, job in jobs_df.iterrows():
            # Construct a full text representation of the job for scoring
            # We combine title, description (if we had it), skills, etc.
            # The current scraper might store description separate or not at all.
            # Based on previous file view, we have: title, source, company, location, employment_type, experience, skills
            
            # We don't have full description in the CSV usually, just metadata.
            # We'll use what we have.
            
            job_text = f"{job.get('title', '')} {job.get('skills', '')} {job.get('experience', '')}"
            
            score_data = self.scorer.calculate_score(resume_data, job_text)
            scores.append(score_data['total_score'])

        # Add scores to DF
        result_df = jobs_df.copy()
        result_df['match_score'] = scores

        # Filter and sort
        matches = result_df[result_df['match_score'] >= threshold]
        return matches.sort_values(by='match_score', ascending=False)
