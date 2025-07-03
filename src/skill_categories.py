from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from enum import Enum
import yaml
import os

class SkillLevel(Enum):
    """Enum representing different skill levels."""
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"

class SkillCategory(Enum):
    """Enum representing different skill categories."""
    PROGRAMMING = "PROGRAMMING"
    ML_FRAMEWORKS = "ML_FRAMEWORKS"
    DEEP_LEARNING = "DEEP_LEARNING"
    DATA_SCIENCE = "DATA_SCIENCE"
    CLOUD = "CLOUD"
    DEVOPS = "DEVOPS"
    SPECIALIZED = "SPECIALIZED"

@dataclass
class Skill:
    """Data class representing a skill."""
    name: str
    category: SkillCategory
    level: SkillLevel
    years_of_experience: float = 0.0
    description: Optional[str] = None
    tags: List[str] = None
    aliases: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.aliases is None:
            self.aliases = []

class SkillRegistry:
    """
    Registry for managing skills and their categories.
    Loads skills from a YAML file (skills.yaml) if present, for enterprise-grade, data-driven extensibility.
    """
    def __init__(self):
        """Initialize the skill registry."""
        self._skills: List[Skill] = []
        # Try to load YAML from project root
        yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'skills.yaml'))
        if os.path.exists(yaml_path):
            self.load_from_yaml(yaml_path)
        else:
            self._initialize_default_skills('')
    
    def _initialize_default_skills(self, yaml_path: str):
        """Initialize default skills in the registry."""
        # Programming skills
        self.add_skill(Skill("Python", SkillCategory.PROGRAMMING, SkillLevel.INTERMEDIATE))
        self.add_skill(Skill("Java", SkillCategory.PROGRAMMING, SkillLevel.INTERMEDIATE))
        self.add_skill(Skill("C++", SkillCategory.PROGRAMMING, SkillLevel.ADVANCED))
        
        # ML Framework skills
        self.add_skill(Skill("TensorFlow", SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED))
        self.add_skill(Skill("PyTorch", SkillCategory.ML_FRAMEWORKS, SkillLevel.ADVANCED))
        self.add_skill(Skill("Scikit-learn", SkillCategory.ML_FRAMEWORKS, SkillLevel.INTERMEDIATE))
        
        # Deep Learning skills
        self.add_skill(Skill("Deep Learning", SkillCategory.DEEP_LEARNING, SkillLevel.ADVANCED))
        self.add_skill(Skill("Computer Vision", SkillCategory.DEEP_LEARNING, SkillLevel.ADVANCED))
        self.add_skill(Skill("Natural Language Processing", SkillCategory.DEEP_LEARNING, SkillLevel.ADVANCED))
        
        # Data Science skills
        self.add_skill(Skill("Data Analysis", SkillCategory.DATA_SCIENCE, SkillLevel.INTERMEDIATE))
        self.add_skill(Skill("SQL", SkillCategory.DATA_SCIENCE, SkillLevel.INTERMEDIATE))
        self.add_skill(Skill("Data Visualization", SkillCategory.DATA_SCIENCE, SkillLevel.INTERMEDIATE))
        
        # Cloud skills
        self.add_skill(Skill("AWS", SkillCategory.CLOUD, SkillLevel.INTERMEDIATE))
        self.add_skill(Skill("Google Cloud", SkillCategory.CLOUD, SkillLevel.INTERMEDIATE))
        self.add_skill(Skill("Azure", SkillCategory.CLOUD, SkillLevel.INTERMEDIATE))
        
        # DevOps skills
        self.add_skill(Skill("Docker", SkillCategory.DEVOPS, SkillLevel.INTERMEDIATE))
        self.add_skill(Skill("Kubernetes", SkillCategory.DEVOPS, SkillLevel.ADVANCED))
        self.add_skill(Skill("Git", SkillCategory.DEVOPS, SkillLevel.INTERMEDIATE))
        
        # Specialized skills
        self.add_skill(Skill("MLOps", SkillCategory.SPECIALIZED, SkillLevel.ADVANCED))
        self.add_skill(Skill("CUDA", SkillCategory.SPECIALIZED, SkillLevel.ADVANCED))
    
    def add_skill(self, skill: Skill):
        """Add a skill to the registry, overwriting if it already exists by name (case-insensitive)."""
        self._skills = [s for s in self._skills if s.name.lower() != skill.name.lower()]
        self._skills.append(skill)
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """Get a skill by name."""
        for skill in self._skills:
            if skill.name.lower() == name.lower():
                return skill
        return None
    
    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """Get all skills in a category."""
        return [s for s in self._skills if s.category == category]
    
    def get_skills_by_level(self, level: SkillLevel) -> List[Skill]:
        """Get all skills at a specific level."""
        return [s for s in self._skills if s.level == level]
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills in the registry."""
        return self._skills.copy()
    
    def get_skill_gaps(self, required_skills: List[str], candidate_skills: List[str]) -> List[str]:
        """Get skills that are required but not present in candidate's skills."""
        required_set = {s.lower() for s in required_skills}
        candidate_set = {s.lower() for s in candidate_skills}
        return list(required_set - candidate_set)

    def load_from_yaml(self, yaml_path: str):
        """Load skills from a YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        for entry in data.get('skills', []):
            try:
                name = entry['name']
                category = SkillCategory[entry['category'].upper()]
                level = SkillLevel[entry.get('level', 'BEGINNER').upper()]
                years = float(entry.get('years_of_experience', 0.0))
                desc = entry.get('description')
                tags = entry.get('tags', [])
                aliases = entry.get('aliases', [])
                self.add_skill(Skill(name, category, level, years, desc, tags, aliases))
            except Exception as e:
                print(f"Error loading skill {entry}: {e}")

    def get_skills_by_tag(self, tag: str) -> List[Skill]:
        """Return all skills that have the given tag (case-insensitive)."""
        tag_lower = tag.lower()
        return [s for s in self._skills if any(t.lower() == tag_lower for t in (s.tags or []))]

    def get_skills_by_alias(self, alias: str) -> List[Skill]:
        """Return all skills that have the given alias (case-insensitive)."""
        alias_lower = alias.lower()
        return [s for s in self._skills if any(a.lower() == alias_lower for a in (s.aliases or []))]

    def get_skills_by_multiple_tags(self, tags: List[str], match_all: bool = False) -> List[Skill]:
        """
        Return skills that match multiple tags.
        
        Args:
            tags: List of tags to match
            match_all: If True, skills must have all tags. If False, skills must have at least one tag.
        
        Returns:
            List of matching skills
        """
        tags_lower = [t.lower() for t in tags]
        if match_all:
            return [s for s in self._skills if all(t in [tag.lower() for tag in (s.tags or [])] for t in tags_lower)]
        return [s for s in self._skills if any(t in [tag.lower() for tag in (s.tags or [])] for t in tags_lower)]

    def get_skills_by_experience_range(self, min_years: float = 0.0, max_years: float = float('inf')) -> List[Skill]:
        """
        Return skills with years of experience within the specified range.
        
        Args:
            min_years: Minimum years of experience
            max_years: Maximum years of experience
        
        Returns:
            List of matching skills
        """
        return [s for s in self._skills if min_years <= s.years_of_experience <= max_years]

    def get_skills_by_combined_criteria(
        self,
        categories: List[SkillCategory] = None,
        levels: List[SkillLevel] = None,
        tags: List[str] = None,
        min_years: float = 0.0,
        max_years: float = float('inf'),
        match_all_tags: bool = False
    ) -> List[Skill]:
        """
        Advanced query method that combines multiple criteria.
        
        Args:
            categories: List of categories to filter by
            levels: List of skill levels to filter by
            tags: List of tags to filter by
            min_years: Minimum years of experience
            max_years: Maximum years of experience
            match_all_tags: If True, skills must have all specified tags
        
        Returns:
            List of skills matching all specified criteria
        """
        filtered_skills = self._skills.copy()
        
        if categories:
            filtered_skills = [s for s in filtered_skills if s.category in categories]
        
        if levels:
            filtered_skills = [s for s in filtered_skills if s.level in levels]
        
        if tags:
            filtered_skills = self.get_skills_by_multiple_tags(tags, match_all_tags)
        
        filtered_skills = [s for s in filtered_skills if min_years <= s.years_of_experience <= max_years]
        
        return filtered_skills

    def search_skills(self, query: str) -> List[Skill]:
        """
        Search skills by name, description, tags, or aliases.
        
        Args:
            query: Search query string
        
        Returns:
            List of matching skills
        """
        query_lower = query.lower()
        results = []
        
        for skill in self._skills:
            # Check name
            if query_lower in skill.name.lower():
                results.append(skill)
                continue
                
            # Check description
            if skill.description and query_lower in skill.description.lower():
                results.append(skill)
                continue
                
            # Check tags
            if skill.tags and any(query_lower in tag.lower() for tag in skill.tags):
                results.append(skill)
                continue
                
            # Check aliases
            if skill.aliases and any(query_lower in alias.lower() for alias in skill.aliases):
                results.append(skill)
                continue
        
        return results 