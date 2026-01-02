"""Filter components for the sidebar."""

import streamlit as st
from typing import Tuple, List


def render_filters(locations: List[str], sources: List[str]) -> Tuple[List[str], List[str], str]:
    """
    Render sidebar filters.

    Args:
        locations: Available locations
        sources: Available sources

    Returns:
        Tuple of (selected_locations, selected_sources, remote_filter)
    """
    st.sidebar.header("Filters")
    st.sidebar.markdown("---")

    # Location filter
    st.sidebar.subheader("📍 Location")
    selected_locations = st.sidebar.multiselect(
        "Select locations",
        options=locations,
        default=locations[:3] if len(locations) > 3 else locations,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("")

    # Source filter
    st.sidebar.subheader("📡 Source")
    selected_sources = st.sidebar.multiselect(
        "Select sources",
        options=sources,
        default=sources,
        label_visibility="collapsed"
    )

    st.sidebar.markdown("")

    # Remote/Onsite filter
    st.sidebar.subheader("🏠 Work Type")
    remote_filter = st.sidebar.radio(
        "Work arrangement",
        options=["All", "Remote Only", "Onsite Only"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")

    # Reset button
    if st.sidebar.button("Reset Filters", width="stretch"):
        st.rerun()

    return selected_locations, selected_sources, remote_filter
