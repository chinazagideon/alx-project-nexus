"""
Skill matching services for job recommendations and analysis
"""

from django.db.models import Q, Prefetch
from django.core.cache import cache
from django.conf import settings
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SkillMatchingService:
    """
    Simple but scalable skill matching service
    """

    CACHE_TIMEOUT = 300  # 5 minutes
    MIN_MATCH_PERCENTAGE = 50  # Minimum match percentage to show recommendations

    @classmethod
    def get_user_skill_match_percentage(cls, user_skills: List[Dict], job_skills: List[Dict]) -> float:
        """
        Calculate skill match percentage between user and job
        """
        if not job_skills:
            return 0.0

        user_skill_ids = {skill["skill_id"] for skill in user_skills}
        job_skill_ids = {skill["skill_id"] for skill in job_skills}

        # Calculate matches
        exact_matches = len(user_skill_ids.intersection(job_skill_ids))
        total_required = len(job_skill_ids)

        if total_required == 0:
            return 0.0

        return round((exact_matches / total_required) * 100, 2)

    @classmethod
    def get_detailed_skill_analysis(cls, user_skills: List[Dict], job_skills: List[Dict]) -> Dict[str, Any]:
        """
        Get detailed skill match analysis
        """
        user_skill_map = {skill["skill_id"]: skill for skill in user_skills}
        job_skill_map = {skill["skill_id"]: skill for skill in job_skills}

        matches = []
        missing_skills = []

        # Check each job skill
        for job_skill in job_skills:
            skill_id = job_skill["skill_id"]
            skill_name = job_skill["skill_name"]

            if skill_id in user_skill_map:
                user_skill = user_skill_map[skill_id]
                match_score = cls._calculate_skill_match_score(user_skill, job_skill)
                matches.append(
                    {
                        "skill_id": skill_id,
                        "skill_name": skill_name,
                        "user_proficiency": user_skill.get("proficiency_level", 1),
                        "job_required": job_skill.get("required_proficiency", 1),
                        "match_score": match_score,
                        "status": "match" if match_score >= 50 else "partial_match",
                    }
                )
            else:
                missing_skills.append(
                    {
                        "skill_id": skill_id,
                        "skill_name": skill_name,
                        "required_proficiency": job_skill.get("required_proficiency", 1),
                        "importance": job_skill.get("importance", 3),
                    }
                )

        return {
            "matches": matches,
            "missing_skills": missing_skills,
            "total_required": len(job_skills),
            "exact_matches": len(matches),
            "missing_count": len(missing_skills),
        }

    @classmethod
    def _calculate_skill_match_score(cls, user_skill: Dict, job_skill: Dict) -> float:
        """
        Calculate individual skill match score
        """
        user_proficiency = user_skill.get("proficiency_level", 1)
        job_required = job_skill.get("required_proficiency", 1)
        importance = job_skill.get("importance", 3)

        # Base score from proficiency match
        if user_proficiency >= job_required:
            proficiency_score = 100
        else:
            proficiency_score = (user_proficiency / job_required) * 100

        # Apply importance weight
        importance_weight = importance / 5.0
        final_score = proficiency_score * importance_weight

        return round(min(final_score, 100), 2)

    @classmethod
    def get_user_skill_profile(cls, user_id: int) -> Dict[str, Any]:
        """
        Get user skill profile with insights
        """
        from .models import UserSkill, JobSkill

        # Get user skills
        user_skills = UserSkill.objects.filter(user_id=user_id).select_related("skill")

        # Get skill demand in job market
        skill_demand = {}
        job_skills = JobSkill.objects.values("skill_id", "skill__name").distinct()

        for job_skill in job_skills:
            skill_id = job_skill["skill_id"]
            skill_name = job_skill["skill__name"]  # Use skill__name directly
            demand_count = JobSkill.objects.filter(skill_id=skill_id).count()
            skill_demand[skill_id] = {"name": skill_name, "demand_count": demand_count}

        # Build profile
        profile = {"user_id": user_id, "skills": [], "skill_demand": skill_demand, "total_skills": user_skills.count()}

        for user_skill in user_skills:
            skill_data = {
                "skill_id": user_skill.skill.id,
                "skill_name": user_skill.skill.name,
                "proficiency_level": user_skill.proficiency_level,
                "years_experience": user_skill.years_experience,
                "last_used": user_skill.last_used,
                "demand_count": skill_demand.get(user_skill.skill.id, {}).get("demand_count", 0),
            }
            profile["skills"].append(skill_data)

        return profile

    @classmethod
    def get_job_recommendations(cls, user_id: int, limit: int = 20, min_match: float = None) -> List[Dict[str, Any]]:
        """
        Get job recommendations for user based on skill matching
        """
        from .models import UserSkill, JobSkill
        from job.models import Job

        # Get user skills
        user_skills = list(
            UserSkill.objects.filter(user_id=user_id).values(
                "skill_id", "skill__name", "proficiency_level", "years_experience"
            )
        )

        if not user_skills:
            return []

        # Get all jobs with their skills
        jobs = Job.objects.prefetch_related(Prefetch("jobskill_set", queryset=JobSkill.objects.select_related("skill"))).all()[
            :100
        ]  # Limit for performance

        recommendations = []
        min_match_threshold = min_match or cls.MIN_MATCH_PERCENTAGE

        for job in jobs:
            job_skills = list(
                job.jobskill_set.values("skill_id", "skill__name", "required_proficiency", "importance", "years_required")
            )

            # Rename skill__name to skill_name for consistency
            for job_skill in job_skills:
                job_skill["skill_name"] = job_skill.pop("skill__name")

            if not job_skills:
                continue

            match_percentage = cls.get_user_skill_match_percentage(user_skills, job_skills)

            if match_percentage >= min_match_threshold:
                detailed_analysis = cls.get_detailed_skill_analysis(user_skills, job_skills)

                recommendations.append(
                    {
                        "job_id": job.id,
                        "job_title": job.title,
                        "company_name": job.company.name,
                        "match_percentage": match_percentage,
                        "skill_analysis": detailed_analysis,
                        "date_posted": job.date_posted,
                        "salary_min": job.salary_min,
                        "salary_max": job.salary_max,
                    }
                )

        # Sort by match percentage and return top results
        recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
        return recommendations[:limit]

    @classmethod
    def get_job_skill_match(cls, user_id: int, job_id: int) -> Dict[str, Any]:
        """
        Get detailed skill match analysis for a specific job
        """
        from .models import UserSkill, JobSkill
        from job.models import Job

        # Get user skills
        user_skills = list(
            UserSkill.objects.filter(user_id=user_id).values(
                "skill_id", "skill__name", "proficiency_level", "years_experience"
            )
        )

        # Get job and its skills
        try:
            job = Job.objects.prefetch_related(
                Prefetch("jobskill_set", queryset=JobSkill.objects.select_related("skill"))
            ).get(id=job_id)
        except Job.DoesNotExist:
            return {"error": "Job not found"}

        job_skills = list(
            job.jobskill_set.values("skill_id", "skill__name", "required_proficiency", "importance", "years_required")
        )

        # Rename skill__name to skill_name for consistency
        for job_skill in job_skills:
            job_skill["skill_name"] = job_skill.pop("skill__name")

        match_percentage = cls.get_user_skill_match_percentage(user_skills, job_skills)
        detailed_analysis = cls.get_detailed_skill_analysis(user_skills, job_skills)

        return {
            "job_id": job.id,
            "job_title": job.title,
            "company_name": job.company.name,
            "user_id": user_id,
            "overall_match": match_percentage,
            "skill_analysis": detailed_analysis,
            "recommendations": cls._generate_skill_recommendations(detailed_analysis),
        }

    @classmethod
    def _generate_skill_recommendations(cls, analysis: Dict[str, Any]) -> List[str]:
        """
        Generate skill improvement recommendations
        """
        recommendations = []

        # Check for missing critical skills
        critical_missing = [skill for skill in analysis["missing_skills"] if skill.get("importance", 3) >= 4]

        if critical_missing:
            skill_names = [skill["skill_name"] for skill in critical_missing[:3]]
            recommendations.append(f"Learn critical skills: {', '.join(skill_names)}")

        # Check for proficiency gaps
        low_proficiency = [
            skill
            for skill in analysis["matches"]
            if skill["match_score"] < 70 and skill["user_proficiency"] < skill["job_required"]
        ]

        if low_proficiency:
            skill_names = [skill["skill_name"] for skill in low_proficiency[:2]]
            recommendations.append(f"Improve proficiency in: {', '.join(skill_names)}")

        return recommendations
