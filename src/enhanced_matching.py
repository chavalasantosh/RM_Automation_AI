from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple
import pandas as pd
import json
import os
from pathlib import Path
import shutil
import matplotlib.pyplot as plt
import seaborn as sns

class SkillLevel(Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"

class MatchRank(Enum):
    PERFECT = 1    # All primary skills match with high proficiency
    EXCELLENT = 2  # Most primary skills match with good proficiency
    GOOD = 3       # Some primary skills match with moderate proficiency
    MODERATE = 4   # Few primary skills match or low proficiency
    POOR = 5       # No primary skills match or very low proficiency

class ExperienceLevel(Enum):
    SENIOR = "SENIOR"      # 5+ years
    MID_LEVEL = "MID"      # 3-5 years
    JUNIOR = "JUNIOR"      # 1-3 years
    ENTRY = "ENTRY"        # < 1 year

class OutputFormat(Enum):
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    HTML = "html"
    VISUAL = "visual"

@dataclass
class Skill:
    name: str
    level: SkillLevel
    years_experience: float
    proficiency: int  # 1-5 scale
    last_used: Optional[datetime] = None
    projects_count: int = 0
    certifications: List[str] = None
    preferred_roles: List[str] = None

    def get_experience_level(self) -> ExperienceLevel:
        if self.years_experience >= 5:
            return ExperienceLevel.SENIOR
        elif self.years_experience >= 3:
            return ExperienceLevel.MID_LEVEL
        elif self.years_experience >= 1:
            return ExperienceLevel.JUNIOR
        return ExperienceLevel.ENTRY

    def get_recency_score(self) -> float:
        if not self.last_used:
            return 0.5
        days_since_use = (datetime.now() - self.last_used).days
        if days_since_use <= 30:
            return 1.0
        elif days_since_use <= 90:
            return 0.8
        elif days_since_use <= 180:
            return 0.6
        elif days_since_use <= 365:
            return 0.4
        return 0.2

@dataclass
class Resource:
    id: str
    name: str
    primary_skills: List[Skill]
    secondary_skills: List[Skill]
    certifications: List[str]
    availability_date: datetime
    current_status: str
    location: str
    preferred_roles: List[str]
    notice_period_days: int
    salary_expectations: float
    preferred_work_type: str
    preferred_location: str
    total_years_experience: float = 0.0
    preferred_industries: List[str] = None
    preferred_team_size: Tuple[int, int] = None

@dataclass
class ProjectRequirement:
    id: str
    title: str
    description: str
    required_primary_skills: List[str]
    required_secondary_skills: List[str]
    preferred_skills: List[str]
    start_date: datetime
    duration_months: int
    priority: int
    location: str
    work_type: str
    budget_range: Tuple[float, float]
    client_name: str
    industry: str
    team_size: int
    required_experience_level: ExperienceLevel = None
    required_certifications: List[str] = None

class EnhancedMatchingEngine:
    def __init__(self):
        self.resources: Dict[str, Resource] = {}
        self.projects: Dict[str, ProjectRequirement] = {}
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Define fixed filenames for each format
        self.output_files = {
            OutputFormat.JSON: "latest_matches.json",
            OutputFormat.CSV: "latest_matches.csv",
            OutputFormat.EXCEL: "latest_matches.xlsx",
            OutputFormat.HTML: "latest_matches.html",
            OutputFormat.VISUAL: "latest_matches_visual"
        }

        # Define scoring weights
        self.weights = {
            "primary_skills": 0.35,
            "secondary_skills": 0.20,
            "experience": 0.15,
            "location": 0.10,
            "work_type": 0.10,
            "certifications": 0.05,
            "recency": 0.05
        }

    def _clear_old_files(self):
        """Clear old output files before creating new ones."""
        for file_path in self.output_files.values():
            full_path = self.output_dir / file_path
            if full_path.exists():
                if full_path.is_dir():
                    shutil.rmtree(full_path)
                else:
                    full_path.unlink()

    def _calculate_skill_match(self, resource_skills: List[Skill], required_skills: List[str]) -> Tuple[float, Dict]:
        if not required_skills:
            return 0.0, {}
        
        match_details = {
            "matched_skills": [],
            "missing_skills": [],
            "proficiency_scores": [],
            "recency_scores": [],
            "experience_years": []
        }
        
        total_score = 0.0
        for req_skill in required_skills:
            skill_match = next((s for s in resource_skills if s.name == req_skill), None)
            if skill_match:
                match_details["matched_skills"].append(req_skill)
                # Calculate skill score based on proficiency, recency, and experience
                proficiency_score = skill_match.proficiency / 5.0
                recency_score = skill_match.get_recency_score()
                experience_score = min(skill_match.years_experience / 5.0, 1.0)  # Cap at 5 years
                
                skill_score = (
                    proficiency_score * 0.5 +  # 50% weight to proficiency
                    recency_score * 0.3 +      # 30% weight to recency
                    experience_score * 0.2     # 20% weight to experience
                ) * 100
                
                match_details["proficiency_scores"].append(proficiency_score * 100)
                match_details["recency_scores"].append(recency_score * 100)
                match_details["experience_years"].append(skill_match.years_experience)
                total_score += skill_score
            else:
                match_details["missing_skills"].append(req_skill)
        
        return (total_score / len(required_skills)), match_details

    def _calculate_experience_match(self, resource: Resource, project: ProjectRequirement) -> Tuple[float, Dict]:
        if not project.required_experience_level:
            return 100.0, {"level": "Not specified"}
        
        # Calculate weighted experience based on primary skills
        total_weight = 0
        weighted_experience = 0
        for skill in resource.primary_skills:
            weight = skill.proficiency / 5.0  # Use proficiency as weight
            weighted_experience += skill.years_experience * weight
            total_weight += weight
        
        avg_experience = weighted_experience / total_weight if total_weight > 0 else 0
        
        resource_level = ExperienceLevel.SENIOR if avg_experience >= 5 else \
                        ExperienceLevel.MID_LEVEL if avg_experience >= 3 else \
                        ExperienceLevel.JUNIOR if avg_experience >= 1 else \
                        ExperienceLevel.ENTRY
        
        # Calculate match score with more granular scoring
        if resource_level == project.required_experience_level:
            score = 100.0
        elif resource_level.value < project.required_experience_level.value:
            # Penalize for lower experience
            level_diff = project.required_experience_level.value - resource_level.value
            score = max(100.0 - (level_diff * 25.0), 0.0)  # 25% penalty per level
        else:
            # Bonus for higher experience, but not full score
            score = 85.0
            
        return score, {
            "required_level": project.required_experience_level.value,
            "resource_level": resource_level.value,
            "weighted_experience": avg_experience,
            "raw_experience": resource.total_years_experience
        }

    def _calculate_certification_match(self, resource: Resource, project: ProjectRequirement) -> Tuple[float, Dict]:
        if not project.required_certifications:
            return 100.0, {"required": [], "matched": []}
        
        matched_certs = [cert for cert in project.required_certifications if cert in resource.certifications]
        score = (len(matched_certs) / len(project.required_certifications)) * 100
        
        # Add bonus for additional relevant certifications
        additional_certs = [cert for cert in resource.certifications if cert not in project.required_certifications]
        if additional_certs:
            score = min(score + 10.0, 100.0)  # Up to 10% bonus
        
        return score, {
            "required": project.required_certifications,
            "matched": matched_certs,
            "missing": list(set(project.required_certifications) - set(matched_certs)),
            "additional": additional_certs
        }

    def _calculate_location_match(self, resource: Resource, project: ProjectRequirement) -> float:
        if resource.preferred_location == project.location:
            return 100.0
        # Add partial score for nearby locations or remote work
        if project.work_type == "REMOTE":
            return 80.0
        return 0.0

    def _calculate_work_type_match(self, resource: Resource, project: ProjectRequirement) -> float:
        if resource.preferred_work_type == project.work_type:
            return 100.0
        # Add partial score for similar work types
        if (project.work_type == "HYBRID" and resource.preferred_work_type == "ONSITE") or \
           (project.work_type == "ONSITE" and resource.preferred_work_type == "HYBRID"):
            return 75.0
        return 0.0

    def _determine_match_rank(self, primary_match: float, secondary_match: float, 
                            experience_match: float) -> MatchRank:
        # Enhanced ranking criteria
        if primary_match >= 90.0 and experience_match >= 80.0 and secondary_match >= 70.0:
            return MatchRank.PERFECT
        elif primary_match >= 80.0 and experience_match >= 70.0 and secondary_match >= 60.0:
            return MatchRank.EXCELLENT
        elif primary_match >= 60.0 and experience_match >= 50.0 and secondary_match >= 40.0:
            return MatchRank.GOOD
        elif primary_match >= 40.0 and experience_match >= 30.0:
            return MatchRank.MODERATE
        else:
            return MatchRank.POOR

    def _generate_recommendation(self, rank: MatchRank, primary_details: Dict, 
                               secondary_details: Dict, experience_details: Dict,
                               certification_details: Dict) -> str:
        recommendation = []
        
        if rank == MatchRank.PERFECT:
            recommendation.append("Strongly recommended - Perfect match")
        elif rank == MatchRank.EXCELLENT:
            recommendation.append("Recommended - Excellent match")
        elif rank == MatchRank.GOOD:
            recommendation.append("Consider - Good match")
        elif rank == MatchRank.MODERATE:
            recommendation.append("Review - Moderate match")
        else:
            recommendation.append("Not recommended - Poor match")

        # Add detailed skill gap analysis
        if primary_details["missing_skills"]:
            recommendation.append(f"Missing primary skills: {', '.join(primary_details['missing_skills'])}")
            if primary_details["proficiency_scores"]:
                avg_proficiency = sum(primary_details["proficiency_scores"]) / len(primary_details["proficiency_scores"])
                recommendation.append(f"Average proficiency in matched skills: {avg_proficiency:.1f}%")
        
        if secondary_details["missing_skills"]:
            recommendation.append(f"Missing secondary skills: {', '.join(secondary_details['missing_skills'])}")
            if secondary_details["proficiency_scores"]:
                avg_proficiency = sum(secondary_details["proficiency_scores"]) / len(secondary_details["proficiency_scores"])
                recommendation.append(f"Average proficiency in matched secondary skills: {avg_proficiency:.1f}%")

        # Add detailed experience analysis
        if experience_details["level"] != "Not specified":
            if experience_details["resource_level"] != experience_details["required_level"]:
                recommendation.append(
                    f"Experience level: {experience_details['resource_level']} "
                    f"(Required: {experience_details['required_level']})"
                )
            recommendation.append(f"Weighted experience: {experience_details['weighted_experience']:.1f} years")

        # Add certification analysis
        if certification_details["missing"]:
            recommendation.append(f"Missing certifications: {', '.join(certification_details['missing'])}")
        if certification_details["additional"]:
            recommendation.append(f"Additional relevant certifications: {', '.join(certification_details['additional'])}")

        return " | ".join(recommendation)

    def find_matches(self, project_id: str, automated: bool = True, filters: Optional[Dict] = None) -> List[Dict]:
        if project_id not in self.projects:
            return []

        project = self.projects[project_id]
        matches = []

        for resource in self.resources.values():
            # Apply filters if provided
            if filters:
                if filters.get("location") and resource.location != filters["location"]:
                    continue
                if filters.get("work_type") and resource.preferred_work_type != filters["work_type"]:
                    continue
                if filters.get("min_experience"):
                    min_exp = filters["min_experience"]
                    if not any(s.years_experience >= min_exp for s in resource.primary_skills):
                        continue

            # Calculate various match scores
            primary_match, primary_details = self._calculate_skill_match(
                resource.primary_skills, project.required_primary_skills)
            secondary_match, secondary_details = self._calculate_skill_match(
                resource.secondary_skills, project.required_secondary_skills)
            experience_match, experience_details = self._calculate_experience_match(resource, project)
            certification_match, certification_details = self._calculate_certification_match(resource, project)
            location_match = self._calculate_location_match(resource, project)
            work_type_match = self._calculate_work_type_match(resource, project)

            # Calculate overall match score using weights
            match_score = (
                primary_match * self.weights["primary_skills"] +
                secondary_match * self.weights["secondary_skills"] +
                experience_match * self.weights["experience"] +
                location_match * self.weights["location"] +
                work_type_match * self.weights["work_type"] +
                certification_match * self.weights["certifications"]
            )

            # Ensure score doesn't exceed 100%
            match_score = min(match_score, 100.0)

            match_rank = self._determine_match_rank(primary_match, secondary_match, experience_match)

            match_data = {
                "resource_id": resource.id,
                "resource_name": resource.name,
                "match_rank": match_rank.name,
                "match_score": match_score,
                "primary_match": primary_match,
                "secondary_match": secondary_match,
                "experience_match": experience_match,
                "certification_match": certification_match,
                "location_match": location_match,
                "work_type_match": work_type_match,
                "skill_analysis": {
                    "primary": primary_details,
                    "secondary": secondary_details
                },
                "experience_analysis": experience_details,
                "certification_analysis": certification_details
            }

            if not automated:
                match_data.update({
                    "recommendation": self._generate_recommendation(
                        match_rank, primary_details, secondary_details, 
                        experience_details, certification_details
                    )
                })

            matches.append(match_data)

        # Sort matches by rank and score
        matches.sort(key=lambda x: (MatchRank[x["match_rank"]].value, -x["match_score"]))
        return matches

    def export_matches(self, project_id: str, output_format: OutputFormat = OutputFormat.JSON) -> str:
        matches = self.find_matches(project_id, automated=False)
        if not matches:
            return ""

        # Clear old files before creating new ones
        self._clear_old_files()

        # Get the fixed filename for this format
        filename = self.output_files[output_format]
        file_path = self.output_dir / filename

        if output_format == OutputFormat.JSON:
            with open(file_path, 'w') as f:
                json.dump(matches, f, indent=2)
            return str(file_path)

        elif output_format == OutputFormat.CSV:
            df = pd.DataFrame(matches)
            df.to_csv(file_path, index=False)
            return str(file_path)

        elif output_format == OutputFormat.EXCEL:
            df = pd.DataFrame(matches)
            df.to_excel(file_path, index=False)
            return str(file_path)

        elif output_format == OutputFormat.HTML:
            df = pd.DataFrame(matches)
            df.to_html(file_path, index=False)
            return str(file_path)

        elif output_format == OutputFormat.VISUAL:
            df = pd.DataFrame(matches)
            
            # Create visualizations
            # Match score distribution
            plt.figure(figsize=(10, 6))
            sns.histplot(data=df, x='match_score', bins=10)
            plt.title('Match Score Distribution')
            plt.savefig(f"{file_path}_scores.png")
            plt.close()
            
            # Skill match heatmap
            plt.figure(figsize=(12, 8))
            skill_data = df[['primary_match', 'secondary_match', 'experience_match', 
                           'certification_match', 'location_match', 'work_type_match']]
            sns.heatmap(skill_data, annot=True, cmap='YlOrRd')
            plt.title('Match Criteria Heatmap')
            plt.savefig(f"{file_path}_criteria.png")
            plt.close()
            
            return str(file_path)

        return "" 