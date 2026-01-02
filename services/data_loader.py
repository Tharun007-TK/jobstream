"""Data loading service for job listings."""

import pandas as pd
from pathlib import Path
from typing import Optional


class JobDataLoader:
    """Handles loading and filtering of job data."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the data loader.

        Args:
            data_dir: Directory containing job CSV files
        """
        self.data_dir = Path(data_dir)

    def load_latest_jobs(self) -> pd.DataFrame:
        """
        Load the most recent job data CSV.

        Returns:
            DataFrame with job listings
        """
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            return pd.DataFrame()
        
        # Get the most recent file
        latest_file = max(csv_files, key=lambda p: p.stat().st_mtime)
        
        try:
            df = pd.read_csv(latest_file)
            df = self._clean_data(df)
            return df
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return pd.DataFrame()

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize job data.

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Ensure all required columns exist
        required_cols = [
            "job_id", "title", "company", "location", "employment_type",
            "experience", "skills", "salary", "posted_date",
            "job_url", "source", "remote", "last_updated"
        ]
        
        for col in required_cols:
            if col not in df.columns:
                df[col] = ""
        
        # Fill NaN values
        df = df.fillna("")
        
        # Normalize remote field
        df["remote"] = df["remote"].astype(str).str.lower()
        df["is_remote"] = df["remote"].isin(["true", "1", "yes"])
        
        # Clean company and title
        df["title"] = df["title"].str.strip()
        df["company"] = df["company"].str.strip()
        
        return df

    def filter_jobs(
        self,
        df: pd.DataFrame,
        locations: Optional[list] = None,
        sources: Optional[list] = None,
        remote_only: bool = False,
        onsite_only: bool = False
    ) -> pd.DataFrame:
        """
        Filter jobs based on criteria.

        Args:
            df: DataFrame to filter
            locations: List of locations to include
            sources: List of sources to include
            remote_only: Show only remote jobs
            onsite_only: Show only onsite jobs

        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()

        # Filter by location
        if locations:
            filtered_df = filtered_df[
                filtered_df["location"].isin(locations)
            ]

        # Filter by source
        if sources:
            filtered_df = filtered_df[
                filtered_df["source"].isin(sources)
            ]

        # Filter by remote status
        if remote_only:
            filtered_df = filtered_df[filtered_df["is_remote"] == True]
        elif onsite_only:
            filtered_df = filtered_df[filtered_df["is_remote"] == False]

        return filtered_df

    def get_unique_values(self, df: pd.DataFrame, column: str) -> list:
        """
        Get unique values from a column, sorted.

        Args:
            df: DataFrame
            column: Column name

        Returns:
            Sorted list of unique values
        """
        values = df[column].unique().tolist()
        return sorted([v for v in values if v])
