"""
Tests for the feed app
"""

from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from address.models import City, Country, State
from company.models import Company
from feed.models import FeedItem
from job.models import Job

User = get_user_model()


class FeedItemModelTest(TestCase):
    """Test cases for FeedItem model"""

    def setUp(self):
        """Set up test data"""
        from address.models import City, Country, State
        from company.models import Company
        
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        
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
            title="Test Job",
            description="Test job description",
            company=self.company,
            city=self.city,
            salary_min=50000,
            salary_max=80000,
        )

    def test_feed_item_creation_job_posted(self):
        """Test feed item creation for job posted event"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED,
            content_object=self.job,
            score=Decimal("0.80"),
            is_active=True,
            meta={"priority": "high"},
        )
        self.assertEqual(feed_item.event_type, FeedItem.EVENT_JOB_POSTED)
        self.assertEqual(feed_item.content_object, self.job)
        self.assertEqual(feed_item.score, Decimal("0.80"))
        self.assertTrue(feed_item.is_active)

    def test_feed_item_creation_company_joined(self):
        """Test feed item creation for company joined event"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_COMPANY_JOINED, 
            content_object=self.company, 
            score=Decimal("0.90"), 
            is_active=True
        )
        self.assertEqual(feed_item.event_type, FeedItem.EVENT_COMPANY_JOINED)
        self.assertEqual(feed_item.content_object, self.company)
        self.assertEqual(feed_item.score, Decimal("0.90"))

    def test_feed_item_creation_promotion_active(self):
        """Test feed item creation for promotion active event"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_PROMOTION_ACTIVE, 
            content_object=self.job, 
            score=Decimal("0.75"), 
            is_active=True
        )
        self.assertEqual(feed_item.event_type, FeedItem.EVENT_PROMOTION_ACTIVE)
        self.assertEqual(feed_item.content_object, self.job)
        self.assertEqual(feed_item.score, Decimal("0.75"))

    def test_feed_item_default_values(self):
        """Test feed item default values"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.50")
        )
        self.assertTrue(feed_item.is_active)
        self.assertEqual(feed_item.meta, {})

    def test_feed_item_str_representation(self):
        """Test feed item string representation"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.60"), 
            is_active=True
        )
        expected_str = f"FeedItem[{feed_item.id}] job_posted -> job.job:{self.job.id}"
        self.assertEqual(str(feed_item), expected_str)

    def test_feed_item_auto_timestamps(self):
        """Test that timestamps are automatically set"""
        before_creation = datetime.now()
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_COMPANY_JOINED, 
            content_object=self.company, 
            score=Decimal("0.70")
        )
        after_creation = datetime.now()

        self.assertIsNotNone(feed_item.created_at)
        self.assertGreaterEqual(feed_item.created_at, before_creation)
        self.assertLessEqual(feed_item.created_at, after_creation)

    def test_feed_item_meta_field(self):
        """Test feed item meta field functionality"""
        meta_data = {"priority": "high", "category": "tech"}
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.85"), 
            meta=meta_data
        )
        self.assertEqual(feed_item.meta, meta_data)

    def test_feed_item_ordering(self):
        """Test feed item ordering by score and id"""
        # Create feed items with different scores
        feed_item1 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.70"), 
            is_active=True
        )
        feed_item2 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_COMPANY_JOINED, 
            content_object=self.company, 
            score=Decimal("0.90"), 
            is_active=True
        )
        feed_item3 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_PROMOTION_ACTIVE, 
            content_object=self.job, 
            score=Decimal("0.70"), 
            is_active=True
        )

        # Test ordering (highest score first, then by id)
        feed_items = list(FeedItem.objects.all())
        self.assertEqual(feed_items[0], feed_item2)  # Highest score
        self.assertEqual(feed_items[1], feed_item3)  # Same score, higher id
        self.assertEqual(feed_items[2], feed_item1)  # Same score, lower id

    def test_feed_item_unique_constraint(self):
        """Test unique constraint for active feed items per object"""
        # Create first active feed item
        FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.80"), 
            is_active=True
        )

        # Try to create another active feed item for same object and event type
        with self.assertRaises(IntegrityError):
            FeedItem.objects.create(
                event_type=FeedItem.EVENT_JOB_POSTED, 
                content_object=self.job, 
                score=Decimal("0.90"), 
                is_active=True
            )

    def test_feed_item_inactive_allows_duplicates(self):
        """Test that inactive feed items allow duplicates"""
        # Create first active feed item
        FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.80"), 
            is_active=True
        )

        # Create inactive feed item with same event type and object
        feed_item2 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.90"), 
            is_active=False
        )
        self.assertFalse(feed_item2.is_active)

    def test_feed_item_different_event_types_allowed(self):
        """Test that different event types are allowed for same object"""
        # Create feed items with different event types for same job
        job_feed = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, 
            content_object=self.job, 
            score=Decimal("0.80"), 
            is_active=True
        )
        promotion_feed = FeedItem.objects.create(
            event_type=FeedItem.EVENT_PROMOTION_ACTIVE, 
            content_object=self.job, 
            score=Decimal("0.90"), 
            is_active=True
        )

        self.assertEqual(job_feed.event_type, FeedItem.EVENT_JOB_POSTED)
        self.assertEqual(promotion_feed.event_type, FeedItem.EVENT_PROMOTION_ACTIVE)
        self.assertEqual(job_feed.content_object, self.job)
        self.assertEqual(promotion_feed.content_object, self.job)