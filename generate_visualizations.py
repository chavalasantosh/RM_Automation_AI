import os
from datetime import datetime
from src.visualizations import MatchVisualizer
from src.skill_categories import Skill, SkillCategory, SkillLevel
import matplotlib.pyplot as plt

def create_sample_skills():
    """Create sample skills for demonstration"""
    return [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("TensorFlow", SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED, 4.0),
        Skill("PyTorch", SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED, 3.5),
        Skill("AWS", SkillCategory.CLOUD, SkillLevel.INTERMEDIATE, 2.0),
        Skill("Docker", SkillCategory.DEVOPS, SkillLevel.INTERMEDIATE, 2.5),
        Skill("Kubernetes", SkillCategory.DEVOPS, SkillLevel.BEGINNER, 1.0),
        Skill("Machine Learning", SkillCategory.ML_FRAMEWORKS, SkillLevel.EXPERT, 6.0),
        Skill("Deep Learning", SkillCategory.DEEP_LEARNING, SkillLevel.ADVANCED, 4.0)
    ]

def create_sample_job_skills():
    """Create sample job requirements"""
    return [
        Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.EXPERT, 5.0),
        Skill("TensorFlow", SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED, 4.0),
        Skill("PyTorch", SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED, 3.0),
        Skill("AWS", SkillCategory.CLOUD, SkillLevel.INTERMEDIATE, 2.0),
        Skill("Docker", SkillCategory.DEVOPS, SkillLevel.INTERMEDIATE, 2.0)
    ]

def save_visualization(fig, filename, output_dir="data/visualizations"):
    """Save a matplotlib figure to a file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.png"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved visualization to: {output_path}")
    plt.close(fig)

def save_current_figure(filename, output_dir="data/visualizations"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename}_{timestamp}.png"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved visualization to: {output_path}")
    plt.close()

def main():
    visualizer = MatchVisualizer()
    candidate_skills = create_sample_skills()
    job_skills = create_sample_job_skills()

    # 1. Skill Heatmap (returns fig)
    print("\nGenerating Skill Heatmap...")
    heatmap = visualizer.create_skill_heatmap(job_skills, candidate_skills)
    save_visualization(heatmap, "skill_heatmap")

    # 2. Experience Timeline (returns fig)
    print("\nGenerating Experience Timeline...")
    timeline = visualizer.create_experience_timeline(candidate_skills)
    save_visualization(timeline, "experience_timeline")

    # 3. Skill Distribution (returns fig)
    print("\nGenerating Skill Distribution...")
    distribution = visualizer.create_skill_distribution(candidate_skills)
    save_visualization(distribution, "skill_distribution")

    # 4. Skill Gap Analysis (calls plt.show, so save current fig)
    print("\nGenerating Skill Gap Analysis...")
    missing_skills = [skill.name for skill in job_skills if not any(s.name == skill.name for s in candidate_skills)]
    matching_skills = [skill for skill in candidate_skills if any(s.name == skill.name for s in job_skills)]
    visualizer.create_skill_gap_analysis(matching_skills, missing_skills)
    save_current_figure("skill_gap_analysis")

    # 5. Certification Radar (calls plt.show, so save current fig)
    print("\nGenerating Certification Radar...")
    certifications = [
        "AWS Certified Machine Learning Specialist",
        "TensorFlow Developer Certificate",
        "Google Cloud Professional Data Engineer",
        "Microsoft Certified: Azure AI Engineer Associate"
    ]
    visualizer.create_certification_radar(certifications)
    save_current_figure("certification_radar")

    # 6. Match Comparison (calls plt.show, so save current fig)
    print("\nGenerating Match Comparison...")
    candidates = [
        {"name": "Candidate A", "match_score": 0.85},
        {"name": "Candidate B", "match_score": 0.75},
        {"name": "Candidate C", "match_score": 0.65},
        {"name": "Candidate D", "match_score": 0.45}
    ]
    visualizer.create_match_comparison(candidates)
    save_current_figure("match_comparison")

    print("\nAll visualizations have been generated and saved!")

if __name__ == "__main__":
    main() 