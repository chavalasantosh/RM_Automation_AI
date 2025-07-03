import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from typing import List, Dict, Any
from datetime import datetime
from .skill_categories import SkillCategory, SkillLevel, Skill

class MatchVisualizer:
    """Class for creating visualizations of match results."""
    
    def __init__(self):
        """Initialize the visualizer with default settings."""
        plt.style.use('default')  # Use default style instead of seaborn
        self.colors = plt.cm.Set3(np.linspace(0, 1, 8))  # Use Set3 colormap instead of seaborn palette
        
        # Define color maps for different categories
        self.category_colors = {
            SkillCategory.PROGRAMMING: '#FF6B6B',
            SkillCategory.ML_FRAMEWORKS: '#4ECDC4',
            SkillCategory.DEEP_LEARNING: '#45B7D1',
            SkillCategory.DATA_SCIENCE: '#96CEB4',
            SkillCategory.CLOUD: '#FFEEAD',
            SkillCategory.DEVOPS: '#D4A5A5',
            SkillCategory.SPECIALIZED: '#9B59B6'
        }
        
        # Define level colors
        self.level_colors = {
            SkillLevel.BEGINNER: '#E0E0E0',
            SkillLevel.INTERMEDIATE: '#90CAF9',
            SkillLevel.ADVANCED: '#4CAF50',
            SkillLevel.EXPERT: '#F44336'
        }
    
    def create_skill_heatmap(self, job_skills: List[Skill], candidate_skills: List[Skill]) -> plt.Figure:
        """Create a heatmap comparing job and candidate skills"""
        print(f"[DEBUG] create_skill_heatmap called with job_skills={job_skills}, candidate_skills={candidate_skills}")
        job_skill_names = [s.name.lower() for s in job_skills]
        candidate_skill_names = [s.name.lower() for s in candidate_skills]
        
        if not job_skill_names or not candidate_skill_names:
            print("[DEBUG] No job or candidate skills provided to heatmap.")
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No skills to compare', ha='center', va='center')
            print(f"[DEBUG] Returning fig (no skills): {fig}")
            return fig
        
        overlap = set(job_skill_names) & set(candidate_skill_names)
        if not overlap:
            print(f"[DEBUG] No overlapping skills between job ({job_skill_names}) and candidate ({candidate_skill_names})")
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, 'No overlapping skills', ha='center', va='center')
            print(f"[DEBUG] Returning fig (no overlap): {fig}")
            return fig
        
        # Create a matrix of skills by category and level
        categories = list(SkillCategory)
        levels = list(SkillLevel)
        matrix = np.zeros((len(categories), len(levels)))
        
        # Fill the matrix with experience values for matching skills
        for skill in job_skills:
            if skill.name.lower() in candidate_skill_names:
                cat_idx = categories.index(skill.category)
                level_idx = levels.index(skill.level)
                matrix[cat_idx, level_idx] = skill.years_of_experience
        
        # Create the heatmap
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(matrix, 
                   annot=True, 
                   fmt='.1f',
                   cmap='YlOrRd',
                   xticklabels=[level.value for level in levels],
                   yticklabels=[cat.value for cat in categories],
                   ax=ax)
        
        ax.set_title("Skill Overlap Heatmap", pad=20)
        ax.set_xlabel('Skill Level')
        ax.set_ylabel('Category')
        
        # Add total experience per category
        totals = matrix.sum(axis=1)
        for i, total in enumerate(totals):
            if total > 0:
                ax.text(len(levels) + 0.5, i + 0.5, f'Total: {total:.1f}y',
                       va='center', ha='left')
        
        plt.tight_layout()
        return fig
            
    def create_experience_timeline(self, skills: List[Skill]) -> plt.Figure:
        """Create a timeline of experience for each skill"""
        # Sort skills by experience
        sorted_skills = sorted(skills, key=lambda x: x.years_of_experience, reverse=True)
        
        # Prepare data
        skill_names = [skill.name for skill in sorted_skills]
        experience = [skill.years_of_experience for skill in sorted_skills]
        categories = [skill.category.value for skill in sorted_skills]
        levels = [skill.level.value for skill in sorted_skills]
        
        # Create figure with larger size and better spacing
        fig, ax = plt.subplots(figsize=(12, max(6, len(skills) * 0.5)))
        
        # Create horizontal bar chart with category-based colors
        bars = ax.barh(skill_names, experience,
                      color=[self.category_colors[skill.category] for skill in sorted_skills])
        
        # Add category and level information to y-axis labels
        y_labels = [f"{name}\n({cat}, {level})" for name, cat, level in zip(skill_names, categories, levels)]
        ax.set_yticks(range(len(skill_names)))
        ax.set_yticklabels(y_labels)
        
        # Customize appearance
        ax.set_xlabel('Years of Experience')
        ax.set_title('Experience Timeline', pad=20)
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   f'{width:.1f} years',
                   ha='left', va='center')
        
        # Add grid for better readability
        ax.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # Add summary statistics
        total_exp = sum(experience)
        avg_exp = total_exp / len(experience) if experience else 0
        ax.text(0.02, 0.02,
               f'Total Experience: {total_exp:.1f} years\nAverage Experience: {avg_exp:.1f} years',
               transform=ax.transAxes,
               fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
            
    def create_skill_distribution(self, skills: List[Skill]) -> plt.Figure:
        """Create a pie chart showing distribution of skills by category"""
        # Count skills by category
        categories = {}
        for skill in skills:
            categories[skill.category] = categories.get(skill.category, 0) + 1
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(categories.values(),
               labels=[cat.value for cat in categories.keys()],
               autopct='%1.1f%%',
               colors=[self.category_colors[cat] for cat in categories.keys()])
        
        plt.title('Skill Distribution by Category')
        plt.tight_layout()
        return fig
            
    def _skill_level_to_number(self, level: SkillLevel) -> float:
        """Convert skill level to numerical value"""
        level_map = {
            SkillLevel.BEGINNER: 1.0,
            SkillLevel.INTERMEDIATE: 2.0,
            SkillLevel.ADVANCED: 3.0,
            SkillLevel.EXPERT: 4.0
        }
        return level_map.get(level, 0.0)
    
    def create_skill_heatmap(self, skills: List[Skill], title: str = "Skill Heatmap"):
        """
        Create a heatmap of skills by category and level.
        
        Args:
            skills: List of Skill objects
            title: Title for the plot
        """
        # Create a matrix of skills by category and level
        categories = list(SkillCategory)
        levels = list(SkillLevel)
        matrix = np.zeros((len(categories), len(levels)))
        
        # Fill the matrix with experience values
        for skill in skills:
            cat_idx = categories.index(skill.category)
            level_idx = levels.index(skill.level)
            matrix[cat_idx, level_idx] = skill.years_of_experience
        
        # Create the heatmap
        plt.figure(figsize=(12, 8))
        sns.heatmap(matrix, 
                   annot=True, 
                   fmt='.1f',
                   cmap='YlOrRd',
                   xticklabels=[level.value for level in levels],
                   yticklabels=[cat.value for cat in categories])
        
        plt.title(title, pad=20)
        plt.xlabel('Skill Level')
        plt.ylabel('Category')
        
        # Add total experience per category
        totals = matrix.sum(axis=1)
        for i, total in enumerate(totals):
            if total > 0:
                plt.text(len(levels) + 0.5, i + 0.5, f'Total: {total:.1f}y',
                        va='center', ha='left')
        
        plt.tight_layout()
        plt.show()
    
    def create_experience_timeline(self, skills: List[Skill], title: str = "Experience Timeline"):
        """
        Create a horizontal bar chart showing years of experience for each skill.
        
        Args:
            skills: List of Skill objects
            title: Title for the plot
        """
        # Sort skills by experience
        sorted_skills = sorted(skills, key=lambda x: x.years_of_experience, reverse=True)
        
        # Prepare data
        skill_names = [skill.name for skill in sorted_skills]
        experience = [skill.years_of_experience for skill in sorted_skills]
        categories = [skill.category.value for skill in sorted_skills]
        levels = [skill.level.value for skill in sorted_skills]
        
        # Create figure with larger size and better spacing
        plt.figure(figsize=(12, max(6, len(skills) * 0.5)))
        
        # Create horizontal bar chart with category-based colors
        bars = plt.barh(skill_names, experience,
                       color=[self.category_colors[skill.category] for skill in sorted_skills])
        
        # Add category and level information to y-axis labels
        y_labels = [f"{name}\n({cat}, {level})" for name, cat, level in zip(skill_names, categories, levels)]
        plt.yticks(range(len(skill_names)), y_labels)
        
        # Customize appearance
        plt.xlabel('Years of Experience')
        plt.title(title, pad=20)
        
        # Add value labels on bars
        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                    f'{width:.1f} years',
                    ha='left', va='center')
        
        # Add grid for better readability
        plt.grid(True, axis='x', linestyle='--', alpha=0.7)
        
        # Add summary statistics
        total_exp = sum(experience)
        avg_exp = total_exp / len(experience) if experience else 0
        plt.figtext(0.02, 0.02,
                   f'Total Experience: {total_exp:.1f} years\nAverage Experience: {avg_exp:.1f} years',
                   fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
    
    def create_skill_gap_analysis(self, matching_skills: List[Skill], missing_skills: List[str], title: str = "Skill Gap Analysis"):
        """
        Create a visualization of skill gaps.
        
        Args:
            matching_skills: List of matching Skill objects
            missing_skills: List of missing skill names
            title: Title for the plot
        """
        # Prepare data
        matching_count = len(matching_skills)
        missing_count = len(missing_skills)
        total = matching_count + missing_count
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create pie chart
        plt.pie([matching_count, missing_count],
                labels=['Matching Skills', 'Missing Skills'],
                colors=['#4CAF50', '#F44336'],
                autopct='%1.1f%%',
                startangle=90)
        
        plt.title(title, pad=20)
        
        # Add legend with skill names
        legend_elements = []
        if matching_skills:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                            markerfacecolor='#4CAF50', markersize=10,
                                            label='Matching Skills:'))
            for skill in matching_skills:
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                                markerfacecolor='#4CAF50', markersize=8,
                                                label=f'  {skill.name} ({skill.level.value})'))
        
        if missing_skills:
            legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                            markerfacecolor='#F44336', markersize=10,
                                            label='Missing Skills:'))
            for skill in missing_skills:
                legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                                markerfacecolor='#F44336', markersize=8,
                                                label=f'  {skill}'))
        
        plt.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5))
        
        plt.tight_layout()
        plt.show()
    
    def create_certification_radar(self, certifications: List[str], title: str = "Certification Radar"):
        """
        Create a radar chart of certifications.
        
        Args:
            certifications: List of certification names
            title: Title for the plot
        """
        if not certifications:
            print(f"No certifications found for radar chart: {title}")
            return
            
        # Create categories for certifications
        categories = ['Cloud', 'ML', 'Data Science', 'DevOps', 'Security']
        
        # Initialize scores
        scores = [0] * len(categories)
        
        # Update scores based on certifications
        for cert in certifications:
            cert_lower = cert.lower()
            if 'aws' in cert_lower or 'azure' in cert_lower or 'gcp' in cert_lower:
                scores[0] += 1
            elif 'ml' in cert_lower or 'ai' in cert_lower:
                scores[1] += 1
            elif 'data' in cert_lower:
                scores[2] += 1
            elif 'devops' in cert_lower:
                scores[3] += 1
            elif 'security' in cert_lower:
                scores[4] += 1
        
        # Create the radar chart
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
        scores = np.concatenate((scores, [scores[0]]))  # Close the loop
        angles = np.concatenate((angles, [angles[0]]))  # Close the loop
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Plot the data
        ax.plot(angles, scores, 'o-', linewidth=2, color='#4CAF50')
        ax.fill(angles, scores, alpha=0.25, color='#4CAF50')
        
        # Set the category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        # Set the y-axis limits and labels
        ax.set_ylim(0, max(scores) + 0.5)
        ax.set_yticks(range(int(max(scores)) + 1))
        ax.set_yticklabels([str(i) for i in range(int(max(scores)) + 1)])
        
        # Add certification names to the plot
        cert_text = "\n".join([f"• {cert}" for cert in certifications])
        plt.figtext(0.02, 0.02, f"Certifications:\n{cert_text}",
                   fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
        
        plt.title(title, pad=20)
        plt.tight_layout()
        plt.show()
    
    def create_match_comparison(self, candidates: List[Dict[str, Any]], title: str = "Candidate Comparison"):
        """
        Create a bar chart comparing candidates based on their match scores.
        
        Args:
            candidates: List of candidate dictionaries with match scores
            title: Title for the plot
        """
        # Extract data
        names = [c['name'] for c in candidates]
        scores = [c['match_score'] * 100 for c in candidates]  # Convert to percentage
        
        # Create figure
        plt.figure(figsize=(10, 6))
        
        # Create bar chart
        bars = plt.bar(names, scores, color='#4CAF50')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%',
                    ha='center', va='bottom')
        
        plt.title(title)
        plt.xlabel('Candidate')
        plt.ylabel('Match Score (%)')
        plt.ylim(0, 100)  # Set y-axis limit to 100%
        
        # Add grid
        plt.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.show() 