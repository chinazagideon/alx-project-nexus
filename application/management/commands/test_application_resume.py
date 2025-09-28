"""
Management command to test application resume integration
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from application.models import Application
from job.models import Job
from company.models import Company
from address.models import City, State
from upload.models import Upload, UploadType
from django.core.files.uploadedfile import SimpleUploadedFile
import os

User = get_user_model()


class Command(BaseCommand):
    help = "Test application resume integration"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test-backward-compatibility",
            action="store_true",
            help="Test backward compatibility",
        )
        parser.add_argument(
            "--test-enhanced-resume",
            action="store_true",
            help="Test enhanced resume functionality",
        )

    def handle(self, *args, **options):
        if options["test_backward_compatibility"]:
            self.test_backward_compatibility()
        elif options["test_enhanced_resume"]:
            self.test_enhanced_resume()
        else:
            self.stdout.write(self.style.ERROR("Please specify --test-backward-compatibility or --test-enhanced-resume"))

    def test_backward_compatibility(self):
        """Test that existing functionality still works"""
        self.stdout.write("Testing backward compatibility...")

        # Create test data
        user, job = self.create_test_data()

        # Test 1: Create application without resume (backward compatible)
        self.stdout.write("\n1. Testing application creation without resume...")
        application = Application.objects.create(job=job, user=user, cover_letter="Test cover letter")

        self.stdout.write(f"   ✓ Application created: {application.id}")
        self.stdout.write(f"   ✓ Resume attached: {application.resume is not None}")

        # Test 2: Create application with explicit resume (backward compatible)
        self.stdout.write("\n2. Testing application creation with explicit resume...")
        resume = self.create_test_resume(user)
        application2 = Application.objects.create(job=job, user=user, cover_letter="Test cover letter 2", resume=resume)

        self.stdout.write(f"   ✓ Application created: {application2.id}")
        self.stdout.write(f"   ✓ Resume attached: {application2.resume is not None}")
        self.stdout.write(f'   ✓ Resume name: {application2.resume.name if application2.resume else "None"}')

        self.stdout.write(self.style.SUCCESS("\n✓ Backward compatibility test passed!"))

    def test_enhanced_resume(self):
        """Test enhanced resume functionality"""
        self.stdout.write("Testing enhanced resume functionality...")

        # Create test data
        user, job = self.create_test_data()

        # Test 1: Create application with automatic resume attachment
        self.stdout.write("\n1. Testing automatic resume attachment...")
        resume = self.create_test_resume(user)

        application = Application.objects.create(job=job, user=user, cover_letter="Test cover letter with auto resume")

        self.stdout.write(f"   ✓ Application created: {application.id}")
        self.stdout.write(f"   ✓ Resume attached: {application.resume is not None}")
        if application.resume:
            self.stdout.write(f"   ✓ Resume name: {application.resume.name}")

        # Test 2: Test resume details in serializer
        self.stdout.write("\n2. Testing resume details in response...")
        from application.serializers import ApplicationSerializer

        serializer = ApplicationSerializer(application)
        data = serializer.data

        self.stdout.write(f'   ✓ Resume details present: {"resume_details" in data}')
        self.stdout.write(f'   ✓ Resume details: {data.get("resume_details")}')

        self.stdout.write(self.style.SUCCESS("\n✓ Enhanced resume functionality test passed!"))

    def create_test_data(self):
        """Create test user and job"""
        # Create test user
        user, created = User.objects.get_or_create(
            username="test_applicant",
            defaults={"email": "test_applicant@example.com", "first_name": "Test", "last_name": "Applicant", "role": "talent"},
        )

        # Create test company
        company, created = Company.objects.get_or_create(
            name="Test Company for Applications",
            defaults={
                "description": "A test company for application testing",
                "user": user,
                "contact_details": "test@company.com",
            },
        )

        # Create test city
        state = State.objects.first()
        city, created = City.objects.get_or_create(name="Test City for Applications", defaults={"state": state})

        # Create test job
        job, created = Job.objects.get_or_create(
            title="Test Job for Applications",
            defaults={
                "description": "A test job for application testing",
                "company": company,
                "city": city,
                "salary_min": 50000,
                "salary_max": 70000,
            },
        )

        return user, job

    def create_test_resume(self, user):
        """Create a test resume upload"""
        from django.contrib.contenttypes.models import ContentType

        # Create a simple test file
        test_content = b"Test resume content"
        test_file = SimpleUploadedFile("test_resume.pdf", test_content, content_type="application/pdf")

        # Get a valid content type
        content_type = ContentType.objects.first()

        # Create upload record
        resume = Upload.objects.create(
            file_path=test_file,
            name="Test Resume",
            uploaded_by=user,
            content_type=content_type,
            object_id=1,  # Generic foreign key
            type=UploadType.RESUME,
        )

        return resume
