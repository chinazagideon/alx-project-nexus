"""
Management command to seed the application with production-like data.
This creates more realistic, interconnected data suitable for testing.
Usage: python manage.py seed_production_data [--reset] [--companies=50] [--users=200] [--jobs=500]
"""

import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from address.models import Address
from company.models import Company
from job.models import Job
from promotion.models import Promotion
from skill.models import JobSkill, Skill, UserSkill

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed the application with production-like test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset all data before seeding",
        )
        parser.add_argument(
            "--companies",
            type=int,
            default=50,
            help="Number of companies to create (default: 50)",
        )
        parser.add_argument(
            "--users",
            type=int,
            default=200,
            help="Number of users to create (default: 200)",
        )
        parser.add_argument(
            "--jobs",
            type=int,
            default=500,
            help="Number of jobs to create (default: 500)",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            self.stdout.write(self.style.WARNING("Resetting all data..."))
            self.reset_data()

        self.stdout.write("Starting production-like data seeding...")

        with transaction.atomic():
            # Create in dependency order
            self.create_realistic_skills()
            self.create_realistic_addresses()
            self.create_realistic_companies(options["companies"])
            self.create_realistic_users(options["users"])
            self.create_realistic_jobs(options["jobs"])
            self.create_realistic_promotions()
            self.create_realistic_relationships()

        self.stdout.write(self.style.SUCCESS("Production-like data seeding completed!"))

    def reset_data(self):
        """Reset all data in dependency order"""
        UserSkill.objects.all().delete()
        JobSkill.objects.all().delete()
        Job.objects.all().delete()
        Promotion.objects.all().delete()
        Company.objects.all().delete()
        Address.objects.all().delete()
        Skill.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_realistic_skills(self):
        """Create a comprehensive skill set"""
        self.stdout.write("Creating realistic skills...")

        # Tech skills with realistic categories
        tech_skills = {
            "Programming Languages": {
                "Python": {"demand": "high", "difficulty": "medium"},
                "JavaScript": {"demand": "high", "difficulty": "medium"},
                "Java": {"demand": "high", "difficulty": "hard"},
                "TypeScript": {"demand": "high", "difficulty": "medium"},
                "Go": {"demand": "medium", "difficulty": "medium"},
                "Rust": {"demand": "medium", "difficulty": "hard"},
                "C++": {"demand": "medium", "difficulty": "hard"},
                "C#": {"demand": "medium", "difficulty": "medium"},
                "PHP": {"demand": "medium", "difficulty": "easy"},
                "Ruby": {"demand": "low", "difficulty": "medium"},
                "Swift": {"demand": "medium", "difficulty": "medium"},
                "Kotlin": {"demand": "medium", "difficulty": "medium"},
            },
            "Web Frameworks": {
                "Django": {"demand": "high", "difficulty": "medium"},
                "Flask": {"demand": "medium", "difficulty": "easy"},
                "FastAPI": {"demand": "high", "difficulty": "medium"},
                "React": {"demand": "high", "difficulty": "medium"},
                "Vue.js": {"demand": "medium", "difficulty": "medium"},
                "Angular": {"demand": "medium", "difficulty": "hard"},
                "Next.js": {"demand": "high", "difficulty": "medium"},
                "Express.js": {"demand": "high", "difficulty": "easy"},
                "Spring Boot": {"demand": "high", "difficulty": "hard"},
                "Laravel": {"demand": "medium", "difficulty": "medium"},
            },
            "Databases": {
                "PostgreSQL": {"demand": "high", "difficulty": "medium"},
                "MySQL": {"demand": "high", "difficulty": "easy"},
                "MongoDB": {"demand": "medium", "difficulty": "medium"},
                "Redis": {"demand": "high", "difficulty": "easy"},
                "Elasticsearch": {"demand": "medium", "difficulty": "hard"},
                "SQLite": {"demand": "medium", "difficulty": "easy"},
                "DynamoDB": {"demand": "medium", "difficulty": "medium"},
            },
            "Cloud & DevOps": {
                "AWS": {"demand": "high", "difficulty": "hard"},
                "Docker": {"demand": "high", "difficulty": "medium"},
                "Kubernetes": {"demand": "high", "difficulty": "hard"},
                "Terraform": {"demand": "medium", "difficulty": "hard"},
                "Jenkins": {"demand": "medium", "difficulty": "medium"},
                "GitLab CI": {"demand": "medium", "difficulty": "medium"},
                "GitHub Actions": {"demand": "high", "difficulty": "medium"},
                "Azure": {"demand": "medium", "difficulty": "hard"},
                "GCP": {"demand": "medium", "difficulty": "hard"},
            },
            "Data Science & ML": {
                "Machine Learning": {"demand": "high", "difficulty": "hard"},
                "Python": {"demand": "high", "difficulty": "medium"},
                "TensorFlow": {"demand": "medium", "difficulty": "hard"},
                "PyTorch": {"demand": "medium", "difficulty": "hard"},
                "Pandas": {"demand": "high", "difficulty": "medium"},
                "NumPy": {"demand": "high", "difficulty": "medium"},
                "Scikit-learn": {"demand": "high", "difficulty": "medium"},
                "Jupyter": {"demand": "high", "difficulty": "easy"},
                "Tableau": {"demand": "medium", "difficulty": "medium"},
                "Power BI": {"demand": "medium", "difficulty": "medium"},
            },
            "Soft Skills": {
                "Leadership": {"demand": "high", "difficulty": "hard"},
                "Communication": {"demand": "high", "difficulty": "medium"},
                "Project Management": {"demand": "high", "difficulty": "medium"},
                "Agile": {"demand": "high", "difficulty": "medium"},
                "Problem Solving": {"demand": "high", "difficulty": "medium"},
                "Teamwork": {"demand": "high", "difficulty": "medium"},
                "Time Management": {"demand": "high", "difficulty": "medium"},
                "Critical Thinking": {"demand": "high", "difficulty": "hard"},
            },
        }

        for category, skills in tech_skills.items():
            for skill_name, metadata in skills.items():
                Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={
                        "category": category,
                        "description": f'{skill_name} - {metadata["demand"]} demand, {metadata["difficulty"]} difficulty',
                        "is_technical": category != "Soft Skills",
                    },
                )

    def create_realistic_addresses(self):
        """Create realistic addresses for major tech cities"""
        self.stdout.write("Creating realistic addresses...")

        tech_cities = [
            {"city": "San Francisco", "state": "CA", "country": "US"},
            {"city": "New York", "state": "NY", "country": "US"},
            {"city": "Seattle", "state": "WA", "country": "US"},
            {"city": "Austin", "state": "TX", "country": "US"},
            {"city": "Boston", "state": "MA", "country": "US"},
            {"city": "Denver", "state": "CO", "country": "US"},
            {"city": "Chicago", "state": "IL", "country": "US"},
            {"city": "Los Angeles", "state": "CA", "country": "US"},
            {"city": "London", "state": "England", "country": "GB"},
            {"city": "Berlin", "state": "Berlin", "country": "DE"},
            {"city": "Amsterdam", "state": "North Holland", "country": "NL"},
            {"city": "Toronto", "state": "ON", "country": "CA"},
            {"city": "Vancouver", "state": "BC", "country": "CA"},
            {"city": "Sydney", "state": "NSW", "country": "AU"},
            {"city": "Melbourne", "state": "VIC", "country": "AU"},
        ]

        for city_info in tech_cities:
            # Create 3-5 addresses per city
            for _ in range(random.randint(3, 5)):
                Address.objects.create(
                    street_address=fake.street_address(),
                    city=city_info["city"],
                    state=city_info["state"],
                    postal_code=fake.postcode(),
                    country=city_info["country"],
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                )

    def create_realistic_companies(self, count):
        """Create realistic tech companies"""
        self.stdout.write(f"Creating {count} realistic companies...")

        company_templates = [
            {"name": "TechCorp", "industry": "Technology", "size": "Large"},
            {"name": "DataFlow", "industry": "Technology", "size": "Medium"},
            {"name": "CloudScale", "industry": "Technology", "size": "Large"},
            {"name": "AI Solutions", "industry": "Technology", "size": "Medium"},
            {"name": "FinTech Pro", "industry": "Finance", "size": "Medium"},
            {"name": "HealthTech", "industry": "Healthcare", "size": "Medium"},
            {"name": "EduTech", "industry": "Education", "size": "Small"},
            {"name": "RetailTech", "industry": "Retail", "size": "Large"},
        ]

        addresses = list(Address.objects.all())

        for i in range(count):
            if i < len(company_templates):
                template = company_templates[i]
                name = template["name"]
            else:
                name = fake.company()
                template = {"industry": "Technology", "size": random.choice(["Small", "Medium", "Large"])}

            company = Company.objects.create(
                name=name,
                description=fake.text(max_nb_chars=500),
                website=fake.url(),
                industry=template["industry"],
                size=template["size"],
                founded_year=fake.year(),
                address=random.choice(addresses) if addresses else None,
                is_active=random.choice([True, True, True, False]),
                phone=fake.phone_number(),
                email=fake.company_email(),
            )

    def create_realistic_users(self, count):
        """Create realistic users with proper skill distributions"""
        self.stdout.write(f"Creating {count} realistic users...")

        # 70% talent, 30% recruiters
        talent_count = int(count * 0.7)
        recruiter_count = count - talent_count

        companies = list(Company.objects.all())

        # Create talent users
        for _ in range(talent_count):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role="talent",
                phone=fake.phone_number(),
                password="testpassword123",
                bio=fake.text(max_nb_chars=200),
                experience_years=random.randint(0, 20),
            )

        # Create recruiter users
        for _ in range(recruiter_count):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role="recruiter",
                phone=fake.phone_number(),
                password="testpassword123",
                company=random.choice(companies) if companies else None,
            )

    def create_realistic_jobs(self, count):
        """Create realistic job postings with proper skill requirements"""
        self.stdout.write(f"Creating {count} realistic jobs...")

        job_templates = [
            {"title": "Senior Python Developer", "type": "Full-time", "level": "Senior"},
            {"title": "Full Stack Engineer", "type": "Full-time", "level": "Mid"},
            {"title": "React Frontend Developer", "type": "Full-time", "level": "Mid"},
            {"title": "DevOps Engineer", "type": "Full-time", "level": "Senior"},
            {"title": "Data Scientist", "type": "Full-time", "level": "Senior"},
            {"title": "Machine Learning Engineer", "type": "Full-time", "level": "Senior"},
            {"title": "Product Manager", "type": "Full-time", "level": "Senior"},
            {"title": "UX Designer", "type": "Full-time", "level": "Mid"},
            {"title": "Backend Developer", "type": "Full-time", "level": "Mid"},
            {"title": "Cloud Architect", "type": "Full-time", "level": "Senior"},
        ]

        companies = list(Company.objects.all())
        addresses = list(Address.objects.all())

        for i in range(count):
            if i < len(job_templates):
                template = job_templates[i]
            else:
                template = {
                    "title": fake.job(),
                    "type": random.choice(["Full-time", "Part-time", "Contract"]),
                    "level": random.choice(["Entry", "Mid", "Senior", "Lead"]),
                }

            job = Job.objects.create(
                title=template["title"],
                description=fake.text(max_nb_chars=1000),
                requirements=fake.text(max_nb_chars=500),
                location=random.choice(addresses) if addresses else None,
                job_type=template["type"],
                experience_level=template["level"],
                salary_min=random.randint(50000, 80000),
                salary_max=random.randint(80000, 200000),
                company=random.choice(companies) if companies else None,
                is_active=random.choice([True, True, True, False]),
                date_posted=fake.date_time_between(start_date="-30d", end_date="now"),
                application_deadline=fake.date_time_between(start_date="now", end_date="+30d"),
            )

    def create_realistic_promotions(self):
        """Create realistic promotions"""
        self.stdout.write("Creating realistic promotions...")

        companies = list(Company.objects.all())
        jobs = list(Job.objects.all())

        # Create 20-30 promotions
        for _ in range(random.randint(20, 30)):
            Promotion.objects.create(
                title=fake.catch_phrase(),
                description=fake.text(max_nb_chars=300),
                promotion_type=random.choice(["Job Boost", "Featured Company", "Premium Listing"]),
                discount_percentage=random.randint(10, 50),
                start_date=fake.date_time_between(start_date="-7d", end_date="now"),
                end_date=fake.date_time_between(start_date="now", end_date="+30d"),
                is_active=random.choice([True, True, False]),
                company=random.choice(companies) if companies else None,
                job=random.choice(jobs) if jobs else None,
            )

    def create_realistic_relationships(self):
        """Create realistic skill relationships"""
        self.stdout.write("Creating realistic relationships...")

        # Job-Skill relationships
        jobs = list(Job.objects.all())
        skills = list(Skill.objects.all())

        for job in jobs:
            # Each job gets 3-8 relevant skills
            num_skills = random.randint(3, 8)
            job_skills = random.sample(skills, min(num_skills, len(skills)))

            for skill in job_skills:
                JobSkill.objects.get_or_create(
                    job=job,
                    skill=skill,
                    defaults={"required": random.choice([True, True, False]), "experience_years": random.randint(1, 5)},
                )

        # User-Skill relationships
        users = list(User.objects.filter(role="talent"))

        for user in users:
            # Each user gets 5-15 skills
            num_skills = random.randint(5, 15)
            user_skills = random.sample(skills, min(num_skills, len(skills)))

            for skill in user_skills:
                UserSkill.objects.get_or_create(
                    user=user,
                    skill=skill,
                    defaults={
                        "proficiency_level": random.choice(["Beginner", "Intermediate", "Advanced", "Expert"]),
                        "years_experience": random.randint(1, 10),
                    },
                )
