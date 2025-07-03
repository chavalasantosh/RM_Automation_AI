"""
RME Dashboard Package
Provides interactive visualization and analysis of match results.
"""

from .app import main as run_dashboard
from .app import load_match_results, create_match_summary_df, create_skill_matrix_df, create_experience_timeline_df

__version__ = '1.0.0'
__all__ = ['run_dashboard', 'load_match_results', 'create_match_summary_df', 'create_skill_matrix_df', 'create_experience_timeline_df'] 