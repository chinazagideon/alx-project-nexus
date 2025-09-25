"""
Management command to seed the application with real data.
Usage: python manage.py seed_data [--reset] [--sample-size=100]
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker
import random
from datetime import datetime, timedelta
from django.utils import timezone

from company.models import Company
from job.models import Job
from skill.models import Skill, JobSkill, UserSkill
from promotion.models import Promotion
from address.models import Address, Country, State, City

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Seed the application with realistic test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset all data before seeding (WARNING: This will delete all existing data)',
        )
        parser.add_argument(
            '--sample-size',
            type=int,
            default=100,
            help='Number of records to create for each model (default: 100)',
        )
        parser.add_argument(
            '--companies',
            type=int,
            default=20,
            help='Number of companies to create (default: 20)',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)',
        )
        parser.add_argument(
            '--admins',
            type=int,
            default=1,
            help='Number of admins to create (default: 1)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(
                self.style.WARNING('Resetting all data...')
            )
            self.reset_data()

        self.stdout.write('Starting data seeding...')
        
        with transaction.atomic():
            # Create in dependency order
            self.create_admin_account(options['admins'])
            self.create_skills(options['sample_size'])
            self.create_addresses(options['sample_size'])
            self.create_companies(options['companies'])
            self.create_users(options['users'])
            self.create_jobs(options['sample_size'])
            self.create_promotions(options['sample_size'])
            self.create_job_skills()
            self.create_user_skills()

        self.stdout.write(
            self.style.SUCCESS('Data seeding completed successfully!')
        )

    def reset_data(self):
        """Reset all data in dependency order"""
        UserSkill.objects.all().delete()
        JobSkill.objects.all().delete()
        Job.objects.all().delete()
        Promotion.objects.all().delete()
        Company.objects.all().delete()
        Address.objects.all().delete()
        City.objects.all().delete()
        State.objects.all().delete()
        Country.objects.all().delete()
        Skill.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_admin_account(self, count):
        """Create a default admin account for testing"""
        admin_username = 'admin'
        admin_email = 'admin@example.com'
        admin_password = 'admin123'
        
        if User.objects.filter(username=admin_username).exists():
            self.stdout.write(self.style.WARNING(f'Admin account "{admin_username}" already exists'))
            return
        
        User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name='Admin',
            last_name='User',
            role='admin',
            phone='1234567890'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'Admin created: {admin_username}/{admin_password}')
        )

    def create_skills(self, count):
        """Create realistic skills"""
        self.stdout.write(f'Creating {count} skills...')
        
        skill_categories = {
            'Programming Languages': [
                'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Go', 'Rust', 'PHP',
                'Ruby', 'Swift', 'Kotlin', 'TypeScript', 'Scala', 'R', 'MATLAB'
            ],
            'Frameworks': [
                'Django', 'Flask', 'FastAPI', 'React', 'Vue.js', 'Angular',
                'Spring Boot', 'Laravel', 'Express.js', 'Next.js', 'Nuxt.js'
            ],
            'Databases': [
                'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
                'SQLite', 'Oracle', 'SQL Server', 'Cassandra', 'DynamoDB'
            ],
            'Cloud & DevOps': [
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
                'Jenkins', 'GitLab CI', 'GitHub Actions', 'Ansible'
            ],
            'Data Science': [
                'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
                'Pandas', 'NumPy', 'Scikit-learn', 'Jupyter', 'Tableau', 'Power BI'
            ],
            'Soft Skills': [
                'Leadership', 'Communication', 'Project Management', 'Agile',
                'Problem Solving', 'Teamwork', 'Time Management', 'Critical Thinking'
            ]
        }

        skills_created = 0
        for category, skills in skill_categories.items():
            for skill_name in skills:
                if skills_created >= count:
                    break
                Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={
                        'status': True
                    }
                )
                skills_created += 1

    def create_addresses(self, count):
        """Create realistic addresses"""
        self.stdout.write(f'Creating {count} addresses...')
        
        # First, create some countries, states, and cities
        countries_data = [
            {'name': 'United States', 'code': 'US'},
            {'name': 'Canada', 'code': 'CA'},
            {'name': 'United Kingdom', 'code': 'GB'},
            {'name': 'Germany', 'code': 'DE'},
            {'name': 'Australia', 'code': 'AU'},
        ]
        
        countries = {}
        for country_data in countries_data:
            country, created = Country.objects.get_or_create(
                code=country_data['code'],
                defaults={'name': country_data['name']}
            )
            countries[country_data['code']] = country
        
        # Create states for each country
        states_data = [
            {'name': 'California', 'country': 'US'},
            {'name': 'New York', 'country': 'US'},
            {'name': 'Texas', 'country': 'US'},
            {'name': 'Ontario', 'country': 'CA'},
            {'name': 'British Columbia', 'country': 'CA'},
            {'name': 'England', 'country': 'GB'},
            {'name': 'Bavaria', 'country': 'DE'},
            {'name': 'New South Wales', 'country': 'AU'},
        ]
        
        states = {}
        for state_data in states_data:
            state, created = State.objects.get_or_create(
                name=state_data['name'],
                country=countries[state_data['country']]
            )
            states[state_data['name']] = state
        
        # Create cities for each state
        cities_data = [
            {'name': 'San Francisco', 'state': 'California'},
            {'name': 'Los Angeles', 'state': 'California'},
            {'name': 'New York', 'state': 'New York'},
            {'name': 'Austin', 'state': 'Texas'},
            {'name': 'Toronto', 'state': 'Ontario'},
            {'name': 'Vancouver', 'state': 'British Columbia'},
            {'name': 'London', 'state': 'England'},
            {'name': 'Munich', 'state': 'Bavaria'},
            {'name': 'Sydney', 'state': 'New South Wales'},
        ]
        
        cities = {}
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                name=city_data['name'],
                state=states[city_data['state']]
            )
            cities[city_data['name']] = city
        
        # Now create addresses using the created cities
        city_list = list(cities.values())
        
        for _ in range(count):
            city = random.choice(city_list)
            Address.objects.create(
                location=fake.street_address(),
                city=city,
                state=city.state,
                country=city.state.country,
                zip_code=fake.postcode(),
                content_type_id=1,  # Generic content type
                object_id=1
            )

    def create_companies(self, count):
        """Create realistic companies"""
        self.stdout.write(f'Creating {count} companies...')
        
        company_types = ['Technology', 'Finance', 'Healthcare', 'Education', 'Retail', 'Manufacturing']
        company_sizes = ['Startup', 'Small', 'Medium', 'Large', 'Enterprise']
        
        addresses = list(Address.objects.all())
        
        # Get a recruiter user to be the company owner
        recruiter_user = User.objects.filter(role='recruiter').first()
        if not recruiter_user:
            # Create a recruiter user if none exists
            recruiter_user = User.objects.create_user(
                username='recruiter_admin',
                email='recruiter@example.com',
                first_name='Recruiter',
                last_name='Admin',
                role='recruiter',
                phone='1234567890',
                password='testpassword123'
            )
        
        for _ in range(count):
            Company.objects.create(
                name=fake.company(),
                description=fake.text(max_nb_chars=500),
                user=recruiter_user,
                website=fake.url(),
                contact_details=fake.phone_number(),
                status=random.choice([True, True, True, False])  # 75% active
            )

    def create_users(self, count):
        """Create realistic users"""
        self.stdout.write(f'Creating {count} users...')
        
        roles = ['talent', 'recruiter']
        
        for _ in range(count):
            role = random.choice(roles)
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                role=role,
                phone=fake.phone_number(),
                password='testpassword123'  # Same password for all test users
            )
            
            # User is already saved by create_user

    def create_jobs(self, count):
        """Create realistic job postings"""
        self.stdout.write(f'Creating {count} jobs...')
        
        job_titles = [
            'Software Engineer', 'Senior Developer', 'Full Stack Developer',
            'Data Scientist', 'DevOps Engineer', 'Product Manager',
            'UX Designer', 'Backend Developer', 'Frontend Developer',
            'Machine Learning Engineer', 'Cloud Architect', 'Security Engineer'
        ]
        
        companies = list(Company.objects.all())
        cities = list(City.objects.all())
        
        for _ in range(count):
            company = random.choice(companies) if companies else None
            city = random.choice(cities) if cities else None
            
            if not company or not city:
                continue  # Skip if we don't have required fields
            
            # Create realistic salary ranges
            salary_min = random.randint(50000, 80000)
            salary_max = random.randint(salary_min + 10000, 200000)
            
            # Create physical address as JSON
            physical_address = {
                'street': fake.street_address(),
                'city': city.name,
                'state': city.state.name,
                'country': city.state.country.name,
                'zip_code': fake.postcode()
            }
                
            Job.objects.create(
                title=random.choice(job_titles),
                description=fake.text(max_nb_chars=1000),
                company=company,
                city=city,
                physical_address=physical_address,
                salary_min=salary_min,
                salary_max=salary_max,
                close_date=timezone.make_aware(fake.date_time_between(start_date='now', end_date='+30d'))
            )

    def create_promotions(self, count):
        """Create realistic promotions"""
        self.stdout.write(f'Creating {count} promotions...')
        
        promotion_types = ['Job Boost', 'Featured Company', 'Premium Listing', 'Urgent Hiring']
        
        companies = list(Company.objects.all())
        jobs = list(Job.objects.all())
        
        # Skip promotion creation for now as it requires complex setup
        # with PromotionPackage and proper content types
        self.stdout.write('Skipping promotion creation (requires complex setup)')

    def create_job_skills(self):
        """Create job-skill relationships"""
        self.stdout.write('Creating job-skill relationships...')
        
        jobs = list(Job.objects.all())
        skills = list(Skill.objects.all())
        
        for job in jobs:
            # Each job gets 3-8 random skills
            num_skills = random.randint(3, 8)
            job_skills = random.sample(skills, min(num_skills, len(skills)))
            
            for skill in job_skills:
                JobSkill.objects.get_or_create(
                    job=job,
                    skill=skill
                )

    def create_user_skills(self):
        """Create user-skill relationships"""
        self.stdout.write('Creating user-skill relationships...')
        
        users = list(User.objects.filter(role='talent'))
        skills = list(Skill.objects.all())
        
        for user in users:
            # Each user gets 5-15 random skills
            num_skills = random.randint(5, 15)
            user_skills = random.sample(skills, min(num_skills, len(skills)))
            
            for skill in user_skills:
                UserSkill.objects.get_or_create(
                    user=user,
                    skill=skill
                )
