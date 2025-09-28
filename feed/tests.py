import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from datetime import datetime, timedelta

from feed.models import FeedItem
from job.models import Job
from company.models import Company
from promotion.models import Promotion, PromotionPackage, PromotionType, PromotionPlacement, PromotionStatus

User = get_user_model()


class FeedItemModelTest(TestCase):
    """Test cases for FeedItem model"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.job = Job.objects.create(
            title="Test Job",
            description="Test job description",
            company_name="Test Company",
            location="Test Location",
            salary_min=50000,
            salary_max=80000,
            user=self.user,
        )
        self.company = Company.objects.create(
            name="Test Company", description="Test company description", user=self.user, contact_details="test@company.com"
        )

    def test_feed_item_creation_job_posted(self):
        """Test feed item creation for job posted event"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED,
            content_object=self.job,
            score=Decimal("0.95"),
            is_active=True,
            meta={"priority": "high"},
        )
        self.assertEqual(feed_item.event_type, FeedItem.EVENT_JOB_POSTED)
        self.assertEqual(feed_item.content_object, self.job)
        self.assertEqual(feed_item.score, Decimal("0.95"))
        self.assertTrue(feed_item.is_active)
        self.assertEqual(feed_item.meta["priority"], "high")

    def test_feed_item_creation_company_joined(self):
        """Test feed item creation for company joined event"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_COMPANY_JOINED, content_object=self.company, score=Decimal("0.80"), is_active=True
        )
        self.assertEqual(feed_item.event_type, FeedItem.EVENT_COMPANY_JOINED)
        self.assertEqual(feed_item.content_object, self.company)
        self.assertEqual(feed_item.score, Decimal("0.80"))

    def test_feed_item_str_representation(self):
        """Test feed item string representation"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.90"), is_active=True
        )
        expected_str = f"FeedItem[{feed_item.id}] job_posted -> job.job:{self.job.id}"
        self.assertEqual(str(feed_item), expected_str)

    def test_feed_item_default_values(self):
        """Test feed item default values"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.75")
        )
        self.assertTrue(feed_item.is_active)
        self.assertEqual(feed_item.meta, {})

    def test_feed_item_event_choices(self):
        """Test feed item event type choices"""
        # Test valid event types
        valid_events = [FeedItem.EVENT_JOB_POSTED, FeedItem.EVENT_COMPANY_JOINED, FeedItem.EVENT_PROMOTION_ACTIVE]

        for event_type in valid_events:
            feed_item = FeedItem.objects.create(event_type=event_type, content_object=self.job, score=Decimal("0.50"))
            self.assertEqual(feed_item.event_type, event_type)

    def test_feed_item_auto_timestamps(self):
        """Test that timestamps are automatically set"""
        before_creation = datetime.now()
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.60")
        )
        after_creation = datetime.now()

        self.assertIsNotNone(feed_item.created_at)
        self.assertGreaterEqual(feed_item.created_at, before_creation)
        self.assertLessEqual(feed_item.created_at, after_creation)

    def test_feed_item_meta_field(self):
        """Test feed item meta field functionality"""
        meta_data = {"priority": "high", "tags": ["urgent", "remote"], "source": "admin"}
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.85"), meta=meta_data
        )
        self.assertEqual(feed_item.meta, meta_data)
        self.assertEqual(feed_item.meta["priority"], "high")
        self.assertEqual(feed_item.meta["tags"], ["urgent", "remote"])

    def test_feed_item_ordering(self):
        """Test feed item ordering by score and id"""
        # Create feed items with different scores
        feed_item1 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.70"), is_active=True
        )
        feed_item2 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.90"), is_active=True
        )
        feed_item3 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.70"), is_active=True
        )

        # Get ordered feed items
        ordered_items = list(FeedItem.objects.all())

        # Should be ordered by score (desc) then id (desc)
        self.assertEqual(ordered_items[0], feed_item2)  # Highest score
        # For same score, higher id should come first
        self.assertEqual(ordered_items[1], feed_item3)
        self.assertEqual(ordered_items[2], feed_item1)

    def test_feed_item_unique_constraint(self):
        """Test unique constraint for active feed items per object"""
        # Create first active feed item
        FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.80"), is_active=True
        )

        # Try to create another active feed item for same object and event type
        with self.assertRaises(IntegrityError):
            FeedItem.objects.create(
                event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.90"), is_active=True
            )

    def test_feed_item_inactive_allows_duplicates(self):
        """Test that inactive feed items allow duplicates"""
        # Create first active feed item
        FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.80"), is_active=True
        )

        # Create inactive feed item for same object and event type - should work
        feed_item2 = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.90"), is_active=False
        )
        self.assertFalse(feed_item2.is_active)

    def test_feed_item_different_event_types_allowed(self):
        """Test that different event types are allowed for same object"""
        # Create job posted feed item
        job_feed = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.80"), is_active=True
        )

        # Create company joined feed item for same job - should work
        company_feed = FeedItem.objects.create(
            event_type=FeedItem.EVENT_COMPANY_JOINED, content_object=self.job, score=Decimal("0.70"), is_active=True
        )

        self.assertEqual(job_feed.event_type, FeedItem.EVENT_JOB_POSTED)
        self.assertEqual(company_feed.event_type, FeedItem.EVENT_COMPANY_JOINED)


@pytest.mark.django_db
class FeedItemIntegrationTest(TestCase):
    """Integration tests for feed item functionality"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        self.job = Job.objects.create(
            title="Test Job",
            description="Test job description",
            company_name="Test Company",
            location="Test Location",
            salary_min=50000,
            salary_max=80000,
            user=self.user,
        )
        self.company = Company.objects.create(
            name="Test Company", description="Test company description", user=self.user, contact_details="test@company.com"
        )

    def test_feed_item_with_promotion(self):
        """Test feed item creation with promotion"""
        # Create promotion package
        package = PromotionPackage.objects.create(
            name="Premium Job Package",
            description="Premium job promotion package",
            price=Decimal("99.99"),
            duration_days=30,
            priority_weight=10,
            placement=PromotionPlacement.FEED,
        )

        # Create promotion
        promotion = Promotion.objects.create(
            owner=self.user,
            content_object=self.job,
            type=PromotionType.JOB,
            package=package,
            placement=PromotionPlacement.FEED,
            start_at=datetime.now(),
            end_at=datetime.now() + timedelta(days=30),
            status=PromotionStatus.ACTIVE,
        )

        # Create feed item for promotion
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_PROMOTION_ACTIVE,
            content_object=promotion,
            score=Decimal("0.95"),
            is_active=True,
            meta={"promotion_id": promotion.id, "package_name": package.name},
        )

        self.assertEqual(feed_item.event_type, FeedItem.EVENT_PROMOTION_ACTIVE)
        self.assertEqual(feed_item.content_object, promotion)
        self.assertEqual(feed_item.meta["promotion_id"], promotion.id)

    def test_feed_item_filtering_by_event_type(self):
        """Test filtering feed items by event type"""
        # Create different types of feed items
        FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.80"), is_active=True
        )
        FeedItem.objects.create(
            event_type=FeedItem.EVENT_COMPANY_JOINED, content_object=self.company, score=Decimal("0.70"), is_active=True
        )

        # Filter by job posted events
        job_feed_items = FeedItem.objects.filter(event_type=FeedItem.EVENT_JOB_POSTED)
        self.assertEqual(job_feed_items.count(), 1)
        self.assertEqual(job_feed_items.first().event_type, FeedItem.EVENT_JOB_POSTED)

        # Filter by company joined events
        company_feed_items = FeedItem.objects.filter(event_type=FeedItem.EVENT_COMPANY_JOINED)
        self.assertEqual(company_feed_items.count(), 1)
        self.assertEqual(company_feed_items.first().event_type, FeedItem.EVENT_COMPANY_JOINED)

    def test_feed_item_filtering_by_active_status(self):
        """Test filtering feed items by active status"""
        # Create active and inactive feed items
        active_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.80"), is_active=True
        )
        inactive_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.70"), is_active=False
        )

        # Filter active items
        active_items = FeedItem.objects.filter(is_active=True)
        self.assertEqual(active_items.count(), 1)
        self.assertIn(active_item, active_items)
        self.assertNotIn(inactive_item, active_items)

        # Filter inactive items
        inactive_items = FeedItem.objects.filter(is_active=False)
        self.assertEqual(inactive_items.count(), 1)
        self.assertIn(inactive_item, inactive_items)
        self.assertNotIn(active_item, inactive_items)

    def test_feed_item_score_ordering(self):
        """Test feed item ordering by score"""
        # Create feed items with different scores
        low_score = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.50"), is_active=True
        )
        high_score = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.90"), is_active=True
        )
        medium_score = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.70"), is_active=True
        )

        # Get ordered feed items
        ordered_items = list(FeedItem.objects.all())

        # Should be ordered by score descending
        self.assertEqual(ordered_items[0], high_score)
        self.assertEqual(ordered_items[1], medium_score)
        self.assertEqual(ordered_items[2], low_score)

    def test_feed_item_content_type_relationship(self):
        """Test feed item content type relationship"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.85"), is_active=True
        )

        # Test content type
        self.assertEqual(feed_item.content_type.model, "job")
        self.assertEqual(feed_item.object_id, self.job.id)
        self.assertEqual(feed_item.content_object, self.job)

    def test_feed_item_deactivation(self):
        """Test feed item deactivation"""
        feed_item = FeedItem.objects.create(
            event_type=FeedItem.EVENT_JOB_POSTED, content_object=self.job, score=Decimal("0.80"), is_active=True
        )

        # Deactivate feed item
        feed_item.is_active = False
        feed_item.save()

        # Verify deactivation
        self.assertFalse(feed_item.is_active)

        # Should not appear in active feed items
        active_items = FeedItem.objects.filter(is_active=True)
        self.assertNotIn(feed_item, active_items)
