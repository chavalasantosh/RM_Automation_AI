from advanced_matching import (
    AdvancedMatchingEngine, Resource, ProjectRequirement,
    Skill, SkillLevel, OutputFormat
)
from datetime import datetime, timedelta

def create_sample_data():
    # Create matching engine
    engine = AdvancedMatchingEngine()

    # Create sample resources with varying skill levels
    resources = [
        Resource(
            id="R1",
            name="John Doe",
            primary_skills=[
                Skill("Python", SkillLevel.PRIMARY, 5.0, 5, 
                      last_used=datetime.now() - timedelta(days=30), projects_count=3),
                Skill("Data Engineering", SkillLevel.PRIMARY, 4.0, 4,
                      last_used=datetime.now() - timedelta(days=60), projects_count=2),
                Skill("Machine Learning", SkillLevel.PRIMARY, 3.0, 4,
                      last_used=datetime.now() - timedelta(days=90), projects_count=1)
            ],
            secondary_skills=[
                Skill("Power BI", SkillLevel.SECONDARY, 2.0, 3,
                      last_used=datetime.now() - timedelta(days=120), projects_count=1),
                Skill("Tableau", SkillLevel.SECONDARY, 1.5, 3,
                      last_used=datetime.now() - timedelta(days=150), projects_count=1),
                Skill("SQL", SkillLevel.SECONDARY, 3.0, 4,
                      last_used=datetime.now() - timedelta(days=45), projects_count=2)
            ],
            certifications=["AWS Data Analytics", "Google Cloud Professional"],
            availability_date=datetime.now(),
            current_status="BENCH",
            location="New York",
            preferred_roles=["Data Engineer", "ML Engineer"],
            notice_period_days=30,
            salary_expectations=120000.0,
            preferred_work_type="FULL_TIME",
            preferred_location="New York"
        ),
        Resource(
            id="R2",
            name="Jane Smith",
            primary_skills=[
                Skill("Python", SkillLevel.PRIMARY, 3.0, 4,
                      last_used=datetime.now() - timedelta(days=15), projects_count=2),
                Skill("Data Analysis", SkillLevel.PRIMARY, 4.0, 5,
                      last_used=datetime.now() - timedelta(days=30), projects_count=3),
                Skill("Power BI", SkillLevel.PRIMARY, 3.0, 4,
                      last_used=datetime.now() - timedelta(days=45), projects_count=2)
            ],
            secondary_skills=[
                Skill("SQL", SkillLevel.SECONDARY, 2.0, 3,
                      last_used=datetime.now() - timedelta(days=60), projects_count=1),
                Skill("Tableau", SkillLevel.SECONDARY, 1.0, 3,
                      last_used=datetime.now() - timedelta(days=90), projects_count=1)
            ],
            certifications=["Microsoft Power BI Expert"],
            availability_date=datetime.now() + timedelta(days=7),
            current_status="BENCH",
            location="San Francisco",
            preferred_roles=["Data Analyst", "Business Analyst"],
            notice_period_days=14,
            salary_expectations=95000.0,
            preferred_work_type="FULL_TIME",
            preferred_location="San Francisco"
        ),
        Resource(
            id="R3",
            name="Mike Johnson",
            primary_skills=[
                Skill("Python", SkillLevel.PRIMARY, 2.0, 3,
                      last_used=datetime.now() - timedelta(days=180), projects_count=1),
                Skill("Data Analysis", SkillLevel.PRIMARY, 1.5, 3,
                      last_used=datetime.now() - timedelta(days=200), projects_count=1)
            ],
            secondary_skills=[
                Skill("Excel", SkillLevel.SECONDARY, 3.0, 4,
                      last_used=datetime.now() - timedelta(days=30), projects_count=2),
                Skill("SQL", SkillLevel.SECONDARY, 1.0, 2,
                      last_used=datetime.now() - timedelta(days=150), projects_count=1)
            ],
            certifications=["Microsoft Office Specialist"],
            availability_date=datetime.now() + timedelta(days=14),
            current_status="BENCH",
            location="Chicago",
            preferred_roles=["Data Analyst", "Business Analyst"],
            notice_period_days=30,
            salary_expectations=75000.0,
            preferred_work_type="FULL_TIME",
            preferred_location="Chicago"
        )
    ]

    # Create sample projects with varying requirements
    projects = [
        ProjectRequirement(
            id="P1",
            title="Senior ML Engineer",
            description="Looking for an experienced ML engineer with strong Python and data engineering skills",
            required_primary_skills=["Python", "Data Engineering", "Machine Learning"],
            required_secondary_skills=["SQL"],
            preferred_skills=["AWS", "Google Cloud"],
            start_date=datetime.now() + timedelta(days=14),
            duration_months=6,
            priority=1,
            location="New York",
            work_type="FULL_TIME",
            budget_range=(100000.0, 150000.0),
            client_name="TechCorp",
            industry="Technology",
            team_size=3
        ),
        ProjectRequirement(
            id="P2",
            title="Data Analyst",
            description="Seeking a data analyst with strong visualization skills",
            required_primary_skills=["Python", "Data Analysis", "Power BI"],
            required_secondary_skills=["SQL", "Tableau"],
            preferred_skills=["QuickSight"],
            start_date=datetime.now() + timedelta(days=7),
            duration_months=3,
            priority=2,
            location="San Francisco",
            work_type="FULL_TIME",
            budget_range=(80000.0, 120000.0),
            client_name="DataCo",
            industry="Finance",
            team_size=2
        ),
        ProjectRequirement(
            id="P3",
            title="Junior Data Analyst",
            description="Entry-level position for data analysis and reporting",
            required_primary_skills=["Data Analysis", "Excel"],
            required_secondary_skills=["SQL"],
            preferred_skills=["Power BI"],
            start_date=datetime.now() + timedelta(days=30),
            duration_months=3,
            priority=3,
            location="Chicago",
            work_type="FULL_TIME",
            budget_range=(60000.0, 80000.0),
            client_name="FinanceCorp",
            industry="Finance",
            team_size=1
        )
    ]

    # Add resources and projects to engine
    for resource in resources:
        engine.add_resource(resource)
    
    for project in projects:
        engine.add_project(project)

    return engine

def main():
    # Create engine with sample data
    engine = create_sample_data()

    # Get all bench resources
    print("\n=== Bench Resources ===")
    bench_resources = engine.get_bench_resources()
    for resource in bench_resources:
        print(f"\nResource: {resource['name']}")
        print("Primary Skills:", [s['name'] for s in resource['primary_skills']])
        print("Secondary Skills:", [s['name'] for s in resource['secondary_skills']])
        print("Location:", resource['location'])
        print("Preferred Work Type:", resource['preferred_work_type'])

    # Get all available projects
    print("\n=== Available Projects ===")
    available_projects = engine.get_available_projects()
    for project in available_projects:
        print(f"\nProject: {project['title']}")
        print("Required Primary Skills:", project['required_primary_skills'])
        print("Required Secondary Skills:", project['required_secondary_skills'])
        print("Location:", project['location'])
        print("Work Type:", project['work_type'])

    # Find matches for each project
    print("\n=== Project Matches ===")
    for project in available_projects:
        print(f"\nFinding matches for project: {project['title']}")
        
        # Automated matching with filters
        print("\nAutomated Matching Results (with filters):")
        filters = {
            "location": project['location'],
            "work_type": project['work_type'],
            "min_experience": 2.0
        }
        matches = engine.find_matches(project['id'], automated=True, filters=filters)
        for match in matches:
            print(f"\nResource: {match['resource_name']}")
            print(f"Match Rank: {match['match_rank']}")
            print(f"Match Score: {match['match_score']:.1f}%")
            print(f"Primary Match: {match['primary_match']:.1f}%")
            print(f"Secondary Match: {match['secondary_match']:.1f}%")
            print(f"Location Match: {match['location_match']:.1f}%")
            print(f"Work Type Match: {match['work_type_match']:.1f}%")

        # Manual review matching
        print("\nManual Review Results:")
        detailed_matches = engine.find_matches(project['id'], automated=False)
        for match in detailed_matches:
            print(f"\nResource: {match['resource_name']}")
            print(f"Match Rank: {match['match_rank']}")
            print(f"Match Score: {match['match_score']:.1f}%")
            print("Skill Gaps:")
            print("  Primary:", match['skill_gaps']['primary_skills'])
            print("  Secondary:", match['skill_gaps']['secondary_skills'])
            print("Recommendation:", match['recommendation'])

        # Export matches in different formats
        print("\nExporting matches in different formats...")
        formats = [
            OutputFormat.JSON,
            OutputFormat.CSV,
            OutputFormat.EXCEL,
            OutputFormat.HTML,
            OutputFormat.VISUAL
        ]
        
        for format in formats:
            output_file = engine.export_matches(project['id'], output_format=format)
            print(f"Exported to {output_file}")

if __name__ == "__main__":
    main() 