import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import date, timedelta

from skill.models import Skill, JobSkill, UserSkill
from job.models import Job

User = get_user_model()


class SkillModelTest(TestCase):
    """Test cases for Skill model"""

    def setUp(self):
        """Set up test data"""
        self.skill_data = {"name": "Python Programming", "status": True}

    def test_skill_creation(self):
        """Test skill creation with valid data"""
        skill = Skill.objects.create(**self.skill_data)
        self.assertEqual(skill.name, "Python Programming")
        self.assertTrue(skill.status)
        self.assertIsNotNone(skill.created_at)
        self.assertIsNotNone(skill.updated_at)

    def test_skill_str_representation(self):
        """Test skill string representation"""
        skill = Skill.objects.create(**self.skill_data)
        self.assertEqual(str(skill), "Python Programming")

    def test_skill_unique_name(self):
        """Test that skill names must be unique"""
        Skill.objects.create(**self.skill_data)
        with self.assertRaises(IntegrityError):
            Skill.objects.create(**self.skill_data)

    def test_skill_default_status(self):
        """Test skill default status is True"""
        skill = Skill.objects.create(name="JavaScript")
        self.assertTrue(skill.status)

    def test_skill_required_fields(self):
        """Test that required fields are enforced"""
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            skill = Skill(status=True)  # Missing name
            skill.full_clean()  # This will trigger validation


class JobSkillModelTest(TestCase):
    """Test cases for JobSkill model"""

    def setUp(self):
        """Set up test data"""
        from company.models import Company
        from address.models import City, State, Country
        
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.skill = Skill.objects.create(name="Python Programming")
        
        # Create required related objects
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.state = State.objects.create(name="Test State", country=self.country)
        self.city = City.objects.create(name="Test City", state=self.state)
        self.company = Company.objects.create(
            name="Test Company",
            description="Test company description",
            user=self.user,
            contact_details="test@company.com"
        )
        
        self.job = Job.objects.create(
            title="Python Developer",
            description="Python development role",
            company=self.company,
            city=self.city,
            salary_min=50000,
            salary_max=80000,
        )

    def test_job_skill_creation(self):
        """Test job skill creation with valid data"""
        job_skill = JobSkill.objects.create(
            job=self.job, skill=self.skill, required_proficiency=3, importance=4, years_required=2.5
        )
        self.assertEqual(job_skill.job, self.job)
        self.assertEqual(job_skill.skill, self.skill)
        self.assertEqual(job_skill.required_proficiency, 3)
        self.assertEqual(job_skill.importance, 4)
        self.assertEqual(job_skill.years_required, 2.5)

    def test_job_skill_str_representation(self):
        """Test job skill string representation"""
        job_skill = JobSkill.objects.create(job=self.job, skill=self.skill, required_proficiency=3, importance=4)
        expected_str = f"{self.job.title} - {self.skill.name} (Intermediate)"
        self.assertEqual(str(job_skill), expected_str)

    def test_job_skill_unique_together(self):
        """Test that job-skill combination must be unique"""
        JobSkill.objects.create(job=self.job, skill=self.skill, required_proficiency=3, importance=4)
        with self.assertRaises(IntegrityError):
            JobSkill.objects.create(job=self.job, skill=self.skill, required_proficiency=4, importance=5)

    def test_job_skill_proficiency_choices(self):
        """Test proficiency level choices"""
        job_skill = JobSkill.objects.create(job=self.job, skill=self.skill, required_proficiency=5, importance=3)
        self.assertEqual(job_skill.get_required_proficiency_display(), "Expert")

    def test_job_skill_importance_choices(self):
        """Test importance level choices"""
        job_skill = JobSkill.objects.create(job=self.job, skill=self.skill, required_proficiency=3, importance=5)
        self.assertEqual(job_skill.get_importance_display(), "Critical")

    def test_job_skill_default_values(self):
        """Test default values for job skill"""
        job_skill = JobSkill.objects.create(job=self.job, skill=self.skill)
        self.assertEqual(job_skill.required_proficiency, 1)  # Beginner
        self.assertEqual(job_skill.importance, 3)  # Important
        self.assertEqual(job_skill.years_required, 0.0)


class UserSkillModelTest(TestCase):
    """Test cases for UserSkill model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.skill = Skill.objects.create(name="Python Programming")

    def test_user_skill_creation(self):
        """Test user skill creation with valid data"""
        user_skill = UserSkill.objects.create(
            user=self.user, skill=self.skill, proficiency_level=4, years_experience=3.5, last_used=date.today()
        )
        self.assertEqual(user_skill.user, self.user)
        self.assertEqual(user_skill.skill, self.skill)
        self.assertEqual(user_skill.proficiency_level, 4)
        self.assertEqual(user_skill.years_experience, 3.5)
        self.assertEqual(user_skill.last_used, date.today())

    def test_user_skill_str_representation(self):
        """Test user skill string representation"""
        user_skill = UserSkill.objects.create(user=self.user, skill=self.skill, proficiency_level=4, years_experience=3.5)
        expected_str = f"{self.user.username} - {self.skill.name} (Advanced)"
        self.assertEqual(str(user_skill), expected_str)

    def test_user_skill_unique_together(self):
        """Test that user-skill combination must be unique"""
        UserSkill.objects.create(user=self.user, skill=self.skill, proficiency_level=3, years_experience=2.0)
        with self.assertRaises(IntegrityError):
            UserSkill.objects.create(user=self.user, skill=self.skill, proficiency_level=4, years_experience=3.0)

    def test_user_skill_proficiency_choices(self):
        """Test proficiency level choices"""
        user_skill = UserSkill.objects.create(user=self.user, skill=self.skill, proficiency_level=5, years_experience=5.0)
        self.assertEqual(user_skill.get_proficiency_level_display(), "Expert")

    def test_user_skill_default_values(self):
        """Test default values for user skill"""
        user_skill = UserSkill.objects.create(user=self.user, skill=self.skill)
        self.assertEqual(user_skill.proficiency_level, 1)  # Beginner
        self.assertEqual(user_skill.years_experience, 0.0)
        self.assertIsNone(user_skill.last_used)

    def test_user_skill_optional_last_used(self):
        """Test that last_used field is optional"""
        user_skill = UserSkill.objects.create(
            user=self.user, skill=self.skill, proficiency_level=3, years_experience=2.0, last_used=None
        )
        self.assertIsNone(user_skill.last_used)


@pytest.mark.django_db
class SkillIntegrationTest(TestCase):
    """Integration tests for skill-related functionality"""

    def setUp(self):
        """Set up test data"""
        from company.models import Company
        from address.models import City, State, Country
        
        self.user = User.objects.create_user(username="testuser", email="test@uniqueexample.com", password="testpass123")
        self.skill1 = Skill.objects.create(name="Python Programming")
        self.skill2 = Skill.objects.create(name="JavaScript")
        
        # Create required related objects
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.state = State.objects.create(name="Test State", country=self.country)
        self.city = City.objects.create(name="Test City", state=self.state)
        self.company = Company.objects.create(
            name="Test Company",
            description="Test company description",
            user=self.user,
            contact_details="test@company.com"
        )
        
        self.job = Job.objects.create(
            title="Full Stack Developer",
            description="Full stack development role",
            company=self.company,
            city=self.city,
            salary_min=60000,
            salary_max=90000,
        )

    def test_skill_matching_scenario(self):
        """Test a realistic skill matching scenario"""
        # Create job skills
        JobSkill.objects.create(job=self.job, skill=self.skill1, required_proficiency=4, importance=5, years_required=3.0)
        JobSkill.objects.create(job=self.job, skill=self.skill2, required_proficiency=3, importance=3, years_required=2.0)

        # Create user skills
        UserSkill.objects.create(user=self.user, skill=self.skill1, proficiency_level=5, years_experience=4.0)
        UserSkill.objects.create(user=self.user, skill=self.skill2, proficiency_level=2, years_experience=1.5)

        # Verify relationships
        self.assertEqual(self.job.jobskill_set.count(), 2)
        self.assertEqual(self.user.userskill_set.count(), 2)
        self.assertEqual(self.skill1.jobskill_set.count(), 1)
        self.assertEqual(self.skill1.userskill_set.count(), 1)

    def test_skill_cascade_deletion(self):
        """Test cascade deletion behavior"""
        # Create job skill
        job_skill = JobSkill.objects.create(job=self.job, skill=self.skill1, required_proficiency=3, importance=4)

        # Create user skill
        user_skill = UserSkill.objects.create(user=self.user, skill=self.skill1, proficiency_level=4, years_experience=3.0)

        # Delete skill - should cascade to job skills and user skills
        skill_id = self.skill1.id
        self.skill1.delete()

        # Verify cascade deletion
        self.assertFalse(JobSkill.objects.filter(skill_id=skill_id).exists())
        self.assertFalse(UserSkill.objects.filter(skill_id=skill_id).exists())
        self.assertFalse(Skill.objects.filter(id=skill_id).exists())

    def test_skill_status_filtering(self):
        """Test filtering skills by status"""
        active_skill = Skill.objects.create(name="Active Skill", status=True)
        inactive_skill = Skill.objects.create(name="Inactive Skill", status=False)

        active_skills = Skill.objects.filter(status=True)
        inactive_skills = Skill.objects.filter(status=False)

        self.assertIn(active_skill, active_skills)
        self.assertIn(inactive_skill, inactive_skills)
        self.assertNotIn(inactive_skill, active_skills)
        self.assertNotIn(active_skill, inactive_skills)
