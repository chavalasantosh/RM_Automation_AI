from skill_categories import SkillRegistry, SkillCategory, SkillLevel

def main():
    # Initialize the skill registry
    registry = SkillRegistry()
    
    print("\n=== Advanced Skill Registry Queries ===\n")
    
    # Example 1: Find skills with multiple tags
    print("1. Skills with both 'popular' and 'emerging' tags:")
    popular_emerging = registry.get_skills_by_multiple_tags(['popular', 'emerging'], match_all=True)
    for skill in popular_emerging:
        print(f"- {skill.name} (Tags: {skill.tags})")
    
    # Example 2: Find skills with specific experience range
    print("\n2. Advanced level skills:")
    advanced_skills = registry.get_skills_by_level(SkillLevel.ADVANCED)
    for skill in advanced_skills:
        print(f"- {skill.name} (Level: {skill.level.value})")
    
    # Example 3: Complex query combining multiple criteria
    print("\n3. DevOps skills with specific criteria:")
    devops_skills = registry.get_skills_by_combined_criteria(
        categories=[SkillCategory.DEVOPS],
        levels=[SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED],
        tags=['popular'],
        match_all_tags=False
    )
    for skill in devops_skills:
        print(f"- {skill.name} (Level: {skill.level.value}, Tags: {skill.tags})")
    
    # Example 4: Search for skills using natural language
    print("\n4. Skills related to 'cloud':")
    cloud_skills = registry.search_skills('cloud')
    for skill in cloud_skills:
        print(f"- {skill.name} (Description: {skill.description})")
    
    # Example 5: Find high-demand skills
    print("\n5. High-demand skills:")
    high_demand_skills = registry.get_skills_by_multiple_tags(['high-demand'], match_all=True)
    for skill in high_demand_skills:
        print(f"- {skill.name} (Tags: {skill.tags})")

if __name__ == "__main__":
    main() 