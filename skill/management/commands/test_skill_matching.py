"""
Management command to test skill matching functionality
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from skill.services import SkillMatchingService
from skill.models import Skill, UserSkill, JobSkill
from job.models import Job
from company.models import Company
from address.models import City
import json

User = get_user_model()


class Command(BaseCommand):
    help = 'Test skill matching functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to test with',
        )
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Create test data for skill matching',
        )

    def handle(self, *args, **options):
        if options['create_test_data']:
            self.create_test_data()
            return

        user_id = options.get('user_id')
        if not user_id:
            self.stdout.write(
                self.style.ERROR('Please provide --user-id or use --create-test-data')
            )
            return

        self.test_skill_matching(user_id)

    def create_test_data(self):
        """Create test data for skill matching"""
        self.stdout.write('Creating test data...')

        # Create skills
        skills_data = [
            'Python', 'Django', 'JavaScript', 'React', 'Node.js',
            'PostgreSQL', 'MongoDB', 'AWS', 'Docker', 'Git',
            'Machine Learning', 'Data Analysis', 'SQL', 'HTML', 'CSS'
        ]

        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills.append(skill)
            if created:
                self.stdout.write(f'Created skill: {skill_name}')

        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'testuser@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'talent'
            }
        )
        if created:
            self.stdout.write(f'Created test user: {user.username}')

        # Create company
        company, created = Company.objects.get_or_create(
            name='Test Company',
            defaults={
                'description': 'A test company for skill matching',
                'user': user,
                'contact_details': 'test@company.com'
            }
        )
        if created:
            self.stdout.write(f'Created company: {company.name}')

        # Create city
        from address.models import State
        state = State.objects.first()  # Get first available state
        city, created = City.objects.get_or_create(
            name='Test City',
            defaults={'state': state}
        )
        if created:
            self.stdout.write(f'Created city: {city.name}')

        # Create test jobs
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'description': 'Looking for a senior Python developer with Django experience',
                'skills': ['Python', 'Django', 'PostgreSQL', 'AWS'],
                'proficiency_requirements': [4, 4, 3, 3]
            },
            {
                'title': 'Full Stack Developer',
                'description': 'Full stack developer with React and Node.js',
                'skills': ['JavaScript', 'React', 'Node.js', 'MongoDB'],
                'proficiency_requirements': [4, 4, 3, 3]
            },
            {
                'title': 'Data Scientist',
                'description': 'Data scientist with ML and analysis skills',
                'skills': ['Python', 'Machine Learning', 'Data Analysis', 'SQL'],
                'proficiency_requirements': [4, 4, 4, 3]
            }
        ]

        for job_data in jobs_data:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                defaults={
                    'description': job_data['description'],
                    'company': company,
                    'city': city,
                    'salary_min': 80000,
                    'salary_max': 120000
                }
            )
            if created:
                self.stdout.write(f'Created job: {job.title}')

            # Add skills to job
            for i, skill_name in enumerate(job_data['skills']):
                skill = Skill.objects.get(name=skill_name)
                job_skill, created = JobSkill.objects.get_or_create(
                    job=job,
                    skill=skill,
                    defaults={
                        'required_proficiency': job_data['proficiency_requirements'][i],
                        'importance': 4,
                        'years_required': 2.0
                    }
                )
                if created:
                    self.stdout.write(f'Added skill {skill_name} to job {job.title}')

        # Add skills to user
        user_skills_data = [
            ('Python', 4, 3.0),
            ('Django', 3, 2.0),
            ('JavaScript', 4, 4.0),
            ('React', 3, 1.5),
            ('PostgreSQL', 3, 2.0),
            ('Git', 4, 3.0)
        ]

        for skill_name, proficiency, years in user_skills_data:
            skill = Skill.objects.get(name=skill_name)
            user_skill, created = UserSkill.objects.get_or_create(
                user=user,
                skill=skill,
                defaults={
                    'proficiency_level': proficiency,
                    'years_experience': years
                }
            )
            if created:
                self.stdout.write(f'Added skill {skill_name} to user {user.username}')

        self.stdout.write(
            self.style.SUCCESS('Test data created successfully!')
        )
        self.stdout.write(f'Test user ID: {user.id}')

    def test_skill_matching(self, user_id):
        """Test skill matching for a user"""
        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(f'Testing skill matching for user: {user.username}')

            # Test job recommendations
            self.stdout.write('\n=== Job Recommendations ===')
            recommendations = SkillMatchingService.get_job_recommendations(
                user_id=user_id, limit=5, min_match=50
            )

            for i, rec in enumerate(recommendations, 1):
                self.stdout.write(
                    f'{i}. {rec["job_title"]} at {rec["company_name"]} '
                    f'(Match: {rec["match_percentage"]}%)'
                )

            # Test skill profile
            self.stdout.write('\n=== Skill Profile ===')
            profile = SkillMatchingService.get_user_skill_profile(user_id)
            self.stdout.write(f'Total skills: {profile["total_skills"]}')
            
            for skill in profile['skills'][:5]:  # Show first 5 skills
                self.stdout.write(
                    f'- {skill["skill_name"]} (Level {skill["proficiency_level"]}, '
                    f'{skill["years_experience"]} years, Demand: {skill["demand_count"]} jobs)'
                )

            # Test job match analysis for first job
            if recommendations:
                job_id = recommendations[0]['job_id']
                self.stdout.write(f'\n=== Job Match Analysis for Job {job_id} ===')
                match_analysis = SkillMatchingService.get_job_skill_match(user_id, job_id)
                
                if 'error' not in match_analysis:
                    self.stdout.write(f'Overall Match: {match_analysis["overall_match"]}%')
                    self.stdout.write(f'Exact Matches: {match_analysis["skill_analysis"]["exact_matches"]}')
                    self.stdout.write(f'Missing Skills: {match_analysis["skill_analysis"]["missing_count"]}')
                    
                    if match_analysis['recommendations']:
                        self.stdout.write('Recommendations:')
                        for rec in match_analysis['recommendations']:
                            self.stdout.write(f'- {rec}')

            self.stdout.write(
                self.style.SUCCESS('\nSkill matching test completed successfully!')
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with ID {user_id} does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error testing skill matching: {str(e)}')
            )
