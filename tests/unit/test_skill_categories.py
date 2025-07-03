import pytest
from src.skill_categories import SkillLevel, SkillCategory, Skill, SkillRegistry

def test_skilllevel_enum():
    assert SkillLevel.BEGINNER.value == "BEGINNER"
    assert SkillLevel.INTERMEDIATE.value == "INTERMEDIATE"
    assert SkillLevel.ADVANCED.value == "ADVANCED"
    assert SkillLevel.EXPERT.value == "EXPERT"

def test_skillcategory_enum():
    assert SkillCategory.PROGRAMMING.value == "PROGRAMMING"
    assert SkillCategory.ML_FRAMEWORKS.value == "ML_FRAMEWORKS"
    assert SkillCategory.DEEP_LEARNING.value == "DEEP_LEARNING"
    assert SkillCategory.DATA_SCIENCE.value == "DATA_SCIENCE"
    assert SkillCategory.CLOUD.value == "CLOUD"
    assert SkillCategory.DEVOPS.value == "DEVOPS"
    assert SkillCategory.SPECIALIZED.value == "SPECIALIZED"

def test_skill_dataclass():
    skill = Skill(name="Python", category=SkillCategory.PROGRAMMING, level=SkillLevel.ADVANCED, years_of_experience=5.0, description="A programming language")
    assert skill.name == "Python"
    assert skill.category == SkillCategory.PROGRAMMING
    assert skill.level == SkillLevel.ADVANCED
    assert skill.years_of_experience == 5.0
    assert skill.description == "A programming language"

def test_skillregistry_initialization():
    registry = SkillRegistry()
    all_skills = registry.get_all_skills()
    assert len(all_skills) > 0
    assert any(s.name == "Python" for s in all_skills)

def test_add_and_get_skill():
    registry = SkillRegistry()
    new_skill = Skill("Go", SkillCategory.PROGRAMMING, SkillLevel.BEGINNER)
    registry.add_skill(new_skill)
    assert registry.get_skill("Go") == new_skill
    # Overwrite test (case-insensitive)
    updated_skill = Skill("go", SkillCategory.PROGRAMMING, SkillLevel.ADVANCED)
    registry.add_skill(updated_skill)
    assert registry.get_skill("GO") == updated_skill

def test_get_skills_by_category():
    registry = SkillRegistry()
    programming_skills = registry.get_skills_by_category(SkillCategory.PROGRAMMING)
    assert all(s.category == SkillCategory.PROGRAMMING for s in programming_skills)
    assert any(s.name == "Python" for s in programming_skills)

def test_get_skills_by_level():
    registry = SkillRegistry()
    advanced_skills = registry.get_skills_by_level(SkillLevel.ADVANCED)
    assert all(s.level == SkillLevel.ADVANCED for s in advanced_skills)
    assert any(s.name == "C++" for s in advanced_skills)

def test_get_all_skills():
    registry = SkillRegistry()
    all_skills = registry.get_all_skills()
    assert isinstance(all_skills, list)
    assert len(all_skills) > 0

def test_get_skill_gaps():
    registry = SkillRegistry()
    required = ["Python", "TensorFlow", "Go"]
    candidate = ["Python", "Go"]
    gaps = registry.get_skill_gaps(required, candidate)
    assert "tensorflow" in gaps
    assert "python" not in gaps
    assert "go" not in gaps

def test_get_skill_gaps_empty():
    registry = SkillRegistry()
    gaps = registry.get_skill_gaps([], [])
    assert gaps == []

def test_get_skill_gaps_required_not_in_candidate():
    registry = SkillRegistry()
    required = ["Python", "Java", "C++"]
    candidate = []
    gaps = registry.get_skill_gaps(required, candidate)
    assert set(gaps) == {"python", "java", "c++"}

def test_get_skills_by_tag_and_alias():
    registry = SkillRegistry()
    # Test tag
    devops_skills = registry.get_skills_by_tag('popular')
    assert any('Agile Methodologies' == s.name for s in devops_skills)
    # Test alias
    agile_skills = registry.get_skills_by_alias('Agile')
    assert any('Agile Methodologies' == s.name for s in agile_skills) 