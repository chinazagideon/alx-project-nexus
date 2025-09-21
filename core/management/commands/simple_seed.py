"""
Simple management command to seed the application with basic data.
Usage: python manage.py simple_seed [--reset]
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker
import random

from company.models import Company
from job.models import Job
from skill.models import Skill, JobSkill, UserSkill
from address.models import Address, Country, State, City

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Seed the application with basic test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Resetting all data...'))
            self.reset_data()

        self.stdout.write('Starting simple data seeding...')
        
        with transaction.atomic():
            # Create in dependency order
            self.create_basic_skills()
            self.create_basic_locations()
            self.create_basic_users()
            self.create_basic_companies()
            self.create_basic_jobs()
            self.create_basic_relationships()

        self.stdout.write(
            self.style.SUCCESS('Simple data seeding completed!')
        )

    def reset_data(self):
        """Reset all data in dependency order"""
        UserSkill.objects.all().delete()
        JobSkill.objects.all().delete()
        Job.objects.all().delete()
        Company.objects.all().delete()
        Address.objects.all().delete()
        City.objects.all().delete()
        State.objects.all().delete()
        Country.objects.all().delete()
        Skill.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_basic_skills(self):
        """Create basic skills"""
        self.stdout.write('Creating basic skills...')
        
        skills = [
            'Python', 'JavaScript', 'Java', 'React', 'Django', 'Node.js',
            'PostgreSQL', 'MongoDB', 'AWS', 'Docker', 'Git', 'Linux',
            'Communication', 'Leadership', 'Problem Solving', 'Teamwork'
        ]
        
        for skill_name in skills:
            Skill.objects.get_or_create(
                name=skill_name,
                defaults={'status': True}
            )

    def create_basic_locations(self):
        """Create basic locations"""
        self.stdout.write('Creating basic locations...')
        
        # Create countries
        countries_data = [
            {'name': 'United States', 'code': 'US'},
            {'name': 'Canada', 'code': 'CA'},
            {'name': 'United Kingdom', 'code': 'GB'},
        ]
        
        countries = {}
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                code=country_data['code'],
                defaults={'name': country_data['name']}
            )
            countries[country_data['code']] = country
        
        # Create states
        states_data = [
            {'name': 'California', 'country': 'US'},
            {'name': 'New York', 'country': 'US'},
            {'name': 'Texas', 'country': 'US'},
            {'name': 'Ontario', 'country': 'CA'},
            {'name': 'England', 'country': 'GB'},
        ]
        
        states = {}
        for state_data in states_data:
            state, created = State.objects.get_or_create(
                name=state_data['name'],
                country=countries[state_data['country']]
            )
            states[state_data['name']] = state
        
        # Create cities
        cities_data = [
            {'name': 'San Francisco', 'state': 'California'},
            {'name': 'New York', 'state': 'New York'},
            {'name': 'Austin', 'state': 'Texas'},
            {'name': 'Toronto', 'state': 'Ontario'},
            {'name': 'London', 'state': 'England'},
        ]
        
        cities = {}
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                state=states[city_data['state']]
            )
            cities[city_data['name']] = city
        
        # Create addresses
        for city_name, city in cities.items():
            Address.objects.get_or_create(
                location=fake.street_address(),
                city=city,
                state=city.state,
                country=city.state.country,
                zip_code=fake.postcode(),
                content_type_id=1,  # Generic content type
                object_id=1
            )

    def create_basic_users(self):
        """Create basic users"""
        self.stdout.write('Creating basic users...')
        
        # Create a recruiter user
        recruiter_user, created = User.objects.get_or_create(
            username='recruiter1',
            defaults={
                'email': 'recruiter@example.com',
                'first_name': 'John',
                'last_name': 'Recruiter',
                'role': 'recruiter',
                'phone': '1234567890',
                'password': 'testpassword123'
            }
        )
        if created:
            recruiter_user.set_password('testpassword123')
            recruiter_user.save()
        
        # Create talent users
        for i in range(10):
            username = f'talent{i+1}'
            User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'talent{i+1}@example.com',
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'role': 'talent',
                    'phone': fake.phone_number(),
                    'password': 'testpassword123'
                }
            )

    def create_basic_companies(self):
        """Create basic companies"""
        self.stdout.write('Creating basic companies...')
        
        recruiter_user = User.objects.filter(role='recruiter').first()
        if not recruiter_user:
            return
        
        companies_data = [
            'TechCorp', 'DataFlow Inc', 'CloudScale', 'AI Solutions',
            'FinTech Pro', 'HealthTech', 'EduTech', 'RetailTech'
        ]
        
        for company_name in companies_data:
            Company.objects.get_or_create(
                name=company_name,
                user=recruiter_user,
                defaults={
                    'description': fake.text(max_nb_chars=200),
                    'website': fake.url(),
                    'contact_details': fake.phone_number(),
                    'status': True
                }
            )

    def create_basic_jobs(self):
        """Create basic jobs"""
        self.stdout.write('Creating basic jobs...')
        
        companies = list(Company.objects.all())
        addresses = list(Address.objects.all())
        
        if not companies or not addresses:
            self.stdout.write('Skipping job creation - no companies or addresses')
            return
        
        job_titles = [
            'Software Engineer', 'Senior Developer', 'Full Stack Developer',
            'Data Scientist', 'DevOps Engineer', 'Product Manager',
            'UX Designer', 'Backend Developer', 'Frontend Developer'
        ]
        
        for i in range(20):
            Job.objects.create(
                title=random.choice(job_titles),
                description=fake.text(max_nb_chars=500),
                company=random.choice(companies),
                address=random.choice(addresses),
                location=fake.city(),
                salary_range=f"{random.randint(50000, 80000)}-{random.randint(80000, 150000)}"
            )

    def create_basic_relationships(self):
        """Create basic skill relationships"""
        self.stdout.write('Creating basic relationships...')
        
        skills = list(Skill.objects.all())
        jobs = list(Job.objects.all())
        users = list(User.objects.filter(role='talent'))
        
        # Create job-skill relationships
        for job in jobs:
            job_skills = random.sample(skills, min(3, len(skills)))
            for skill in job_skills:
                JobSkill.objects.get_or_create(job=job, skill=skill)
        
        # Create user-skill relationships
        for user in users:
            user_skills = random.sample(skills, min(5, len(skills)))
            for skill in user_skills:
                UserSkill.objects.get_or_create(user=user, skill=skill)
