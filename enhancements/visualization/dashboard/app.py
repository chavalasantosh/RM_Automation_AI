"""
Offline Streamlit Dashboard for RME
Provides interactive visualization and analysis of match results.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import sys
import pathlib
from ..excel_generator import ExcelReport

# Add the parent directory to the path so we can import from enhancements
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent))

def load_match_results(results_dir: str = "output") -> List[Dict]:
    """Load match results from the output directory."""
    results = []
    for file in os.listdir(results_dir):
        if file.endswith('.json'):
            with open(os.path.join(results_dir, file), 'r') as f:
                results.append(json.load(f))
    return results

def create_match_summary_df(results: List[Dict]) -> pd.DataFrame:
    """Create a summary DataFrame from match results."""
    data = []
    for result in results:
        data.append({
            'Job': result['job'],
            'Candidate': result['profile'],
            'Match Score': result['match_score'],
            'Experience Match': result['matching_criteria']['experience_match'],
            'Certification Match': result['matching_criteria']['certification_match'],
            'Availability Match': result['matching_criteria']['availability_match']
        })
    return pd.DataFrame(data)

def create_skill_matrix_df(results: List[Dict]) -> pd.DataFrame:
    """Create a skill matrix DataFrame from match results."""
    data = []
    for result in results:
        job_data = result['job_data']
        profile_data = result['profile_data']
        
        required_skills = set(job_data.get('required_skills', []))
        profile_skills = set(profile_data.get('skills', []))
        matching_skills = required_skills.intersection(profile_skills)
        missing_skills = required_skills - profile_skills
        
        data.append({
            'Job': result['job'],
            'Candidate': result['profile'],
            'Required Skills': ', '.join(required_skills),
            'Matching Skills': ', '.join(matching_skills),
            'Missing Skills': ', '.join(missing_skills),
            'Match Score': result['match_score']
        })
    return pd.DataFrame(data)

def create_experience_timeline_df(results: List[Dict]) -> pd.DataFrame:
    """Create an experience timeline DataFrame from match results."""
    data = []
    for result in results:
        profile_data = result['profile_data']
        data.append({
            'Candidate': result['profile'],
            'Experience (Years)': profile_data.get('years_of_experience', 0),
            'Education': profile_data.get('education', 'N/A'),
            'Match Score': result['match_score']
        })
    return pd.DataFrame(data)

def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="RME Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("Resume Matching Engine Dashboard")
    st.sidebar.title("Navigation")
    
    # Load data
    try:
        results = load_match_results()
        if not results:
            st.error("No match results found in the output directory!")
            return
    except Exception as e:
        st.error(f"Error loading match results: {str(e)}")
        return
    
    # Create DataFrames
    summary_df = create_match_summary_df(results)
    skill_matrix_df = create_skill_matrix_df(results)
    experience_df = create_experience_timeline_df(results)
    
    # Navigation
    page = st.sidebar.radio(
        "Select View",
        ["Overview", "Skill Analysis", "Experience Analysis", "Detailed Results", "Export"]
    )
    
    # Export functionality in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Export Options")
    if st.sidebar.button("Export to Excel"):
        try:
            excel_report = ExcelReport(results)
            output_file = excel_report.generate()
            st.sidebar.success(f"Report generated: {output_file}")
            
            # Provide download button
            with open(output_file, 'rb') as f:
                st.sidebar.download_button(
                    label="Download Excel Report",
                    data=f,
                    file_name=os.path.basename(output_file),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception as e:
            st.sidebar.error(f"Error generating report: {str(e)}")
    
    if page == "Export":
        st.header("Export Options")
        
        # Export settings
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Report Settings")
            include_summary = st.checkbox("Include Executive Summary", value=True)
            include_skills = st.checkbox("Include Skill Analysis", value=True)
            include_candidates = st.checkbox("Include Candidate Details", value=True)
            
        with col2:
            st.subheader("Export Format")
            export_format = st.radio(
                "Select Format",
                ["Excel (Detailed Report)", "CSV (Simple Export)"]
            )
            
        if st.button("Generate Report"):
            if export_format == "Excel (Detailed Report)":
                try:
                    excel_report = ExcelReport(results)
                    output_file = excel_report.generate()
                    st.success(f"Report generated: {output_file}")
                    
                    # Provide download button
                    with open(output_file, 'rb') as f:
                        st.download_button(
                            label="Download Excel Report",
                            data=f,
                            file_name=os.path.basename(output_file),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
            else:
                # CSV Export
                try:
                    # Create a temporary CSV file
                    csv_file = "temp/match_results.csv"
                    os.makedirs("temp", exist_ok=True)
                    
                    # Export summary data
                    summary_df.to_csv(csv_file, index=False)
                    
                    st.success("CSV file generated successfully!")
                    
                    # Provide download button
                    with open(csv_file, 'rb') as f:
                        st.download_button(
                            label="Download CSV",
                            data=f,
                            file_name="match_results.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Error generating CSV: {str(e)}")
    
    elif page == "Overview":
        st.header("Match Overview")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Matches", len(results))
        with col2:
            perfect_matches = sum(1 for r in results if r['match_score'] > 80)
            st.metric("Perfect Matches", perfect_matches)
        with col3:
            avg_score = summary_df['Match Score'].mean()
            st.metric("Average Match Score", f"{avg_score:.1f}%")
        
        # Match score distribution
        st.subheader("Match Score Distribution")
        fig = px.histogram(
            summary_df,
            x="Match Score",
            nbins=20,
            title="Distribution of Match Scores"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Match overview table
        st.subheader("Match Overview")
        st.dataframe(
            summary_df.style.background_gradient(subset=['Match Score'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Add new features
        st.subheader("Match Score Trends")
        fig = px.line(
            summary_df.sort_values('Match Score'),
            y='Match Score',
            title="Match Score Distribution (Sorted)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add match quality distribution
        st.subheader("Match Quality Distribution")
        quality_bins = pd.cut(
            summary_df['Match Score'],
            bins=[0, 40, 60, 80, 100],
            labels=['Poor', 'Moderate', 'Good', 'Excellent']
        )
        quality_counts = quality_bins.value_counts()
        
        fig = px.pie(
            values=quality_counts.values,
            names=quality_counts.index,
            title="Match Quality Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif page == "Skill Analysis":
        st.header("Skill Analysis")
        
        # Skill match heatmap
        st.subheader("Skill Match Heatmap")
        pivot_df = skill_matrix_df.pivot_table(
            values='Match Score',
            index='Candidate',
            columns='Job',
            aggfunc='mean'
        ).fillna(0)
        
        fig = px.imshow(
            pivot_df,
            text_auto=True,
            aspect="auto",
            title="Skill Match Heatmap"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Skill matrix
        st.subheader("Detailed Skill Matrix")
        st.dataframe(skill_matrix_df, use_container_width=True)
        
        # Missing skills analysis
        st.subheader("Missing Skills Analysis")
        missing_skills = skill_matrix_df['Missing Skills'].str.split(', ').explode()
        missing_skills = missing_skills[missing_skills != '']
        if not missing_skills.empty:
            fig = px.bar(
                missing_skills.value_counts(),
                title="Most Common Missing Skills"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Add new features
        st.subheader("Skill Coverage Analysis")
        skill_coverage = skill_matrix_df['Matching Skills'].str.split(', ').apply(len) / \
                        skill_matrix_df['Required Skills'].str.split(', ').apply(len) * 100
        
        fig = px.histogram(
            x=skill_coverage,
            nbins=20,
            title="Skill Coverage Distribution",
            labels={'x': 'Skill Coverage (%)', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add skill gap analysis
        st.subheader("Top Missing Skills")
        missing_skills = skill_matrix_df['Missing Skills'].str.split(', ').explode()
        missing_skills = missing_skills[missing_skills != '']
        if not missing_skills.empty:
            top_missing = missing_skills.value_counts().head(10)
            fig = px.bar(
                x=top_missing.index,
                y=top_missing.values,
                title="Top 10 Missing Skills",
                labels={'x': 'Skill', 'y': 'Frequency'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
    elif page == "Experience Analysis":
        st.header("Experience Analysis")
        
        # Experience vs Match Score
        st.subheader("Experience vs Match Score")
        fig = px.scatter(
            experience_df,
            x="Experience (Years)",
            y="Match Score",
            color="Education",
            size="Match Score",
            hover_data=["Candidate"],
            title="Experience vs Match Score"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Education distribution
        st.subheader("Education Distribution")
        fig = px.pie(
            experience_df,
            names="Education",
            title="Education Level Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Experience timeline
        st.subheader("Experience Timeline")
        fig = px.bar(
            experience_df,
            x="Candidate",
            y="Experience (Years)",
            color="Match Score",
            title="Candidate Experience Timeline"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add new features
        st.subheader("Experience vs Match Score Correlation")
        correlation = experience_df['Experience (Years)'].corr(experience_df['Match Score'])
        st.metric("Experience-Match Correlation", f"{correlation:.2f}")
        
        # Add education level analysis
        st.subheader("Education Level Impact")
        education_impact = experience_df.groupby('Education')['Match Score'].agg(['mean', 'count'])
        education_impact = education_impact.reset_index()
        
        fig = px.bar(
            education_impact,
            x='Education',
            y='mean',
            title="Average Match Score by Education Level",
            labels={'mean': 'Average Match Score (%)', 'Education': 'Education Level'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:  # Detailed Results
        st.header("Detailed Results")
        
        # Filter options
        st.sidebar.subheader("Filters")
        min_score = st.sidebar.slider(
            "Minimum Match Score",
            min_value=0,
            max_value=100,
            value=0
        )
        
        # Filter results
        filtered_df = summary_df[summary_df['Match Score'] >= min_score]
        
        # Detailed results table
        st.subheader("Detailed Match Results")
        st.dataframe(
            filtered_df.style.background_gradient(subset=['Match Score'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Add new features
        st.subheader("Advanced Filtering")
        col1, col2 = st.columns(2)
        with col1:
            min_experience = st.slider(
                "Minimum Experience (Years)",
                min_value=0,
                max_value=int(experience_df['Experience (Years)'].max()),
                value=0
            )
        with col2:
            min_skills = st.slider(
                "Minimum Required Skills",
                min_value=0,
                max_value=int(skill_matrix_df['Required Skills'].str.split(', ').apply(len).max()),
                value=0
            )
        
        # Apply filters
        filtered_df = summary_df[
            (summary_df['Match Score'] >= min_score) &
            (experience_df['Experience (Years)'] >= min_experience) &
            (skill_matrix_df['Required Skills'].str.split(', ').apply(len) >= min_skills)
        ]
        
        # Show filtered results
        st.subheader("Filtered Results")
        st.dataframe(
            filtered_df.style.background_gradient(subset=['Match Score'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Add match insights
        if not filtered_df.empty:
            st.subheader("Match Insights")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Average Match Score",
                    f"{filtered_df['Match Score'].mean():.1f}%"
                )
            with col2:
                st.metric(
                    "Perfect Matches",
                    f"{sum(filtered_df['Match Score'] > 80)}"
                )
            with col3:
                st.metric(
                    "Total Matches",
                    len(filtered_df)
                )

if __name__ == "__main__":
    main() 