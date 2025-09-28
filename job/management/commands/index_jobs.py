"""
Management command to index jobs for search optimization
"""

from django.core.management.base import BaseCommand
from django.db import connection

from job.models import Job


class Command(BaseCommand):
    help = "Index jobs for search optimization"

    def add_arguments(self, parser):
        parser.add_argument(
            "--rebuild",
            action="store_true",
            help="Rebuild all indexes",
        )
        parser.add_argument(
            "--app",
            type=str,
            help="Specific app to index (job)",
        )

    def handle(self, *args, **options):
        if options["rebuild"]:
            self.stdout.write("Rebuilding search indexes...")
            self.rebuild_indexes()
        else:
            self.stdout.write("Updating search indexes...")
            self.update_indexes()

        self.stdout.write(self.style.SUCCESS("Successfully indexed jobs for search"))

    def rebuild_indexes(self):
        """Rebuild all search indexes"""

        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                # Create search vector index
                cursor.execute(
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS job_search_vector_idx 
                    ON job_job USING gin(
                        to_tsvector('english', 
                            COALESCE(title, '') || ' ' || 
                            COALESCE(description, '') || ' ' || 
                            COALESCE(location, '')
                        )
                    );
                """
                )

                # Create other useful indexes
                cursor.execute(
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS job_company_name_idx 
                    ON job_job (company_id);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS job_location_idx 
                    ON job_job (location);
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX CONCURRENTLY IF NOT EXISTS job_date_posted_idx 
                    ON job_job (date_posted);
                """
                )

    def update_indexes(self):
        """Update search indexes for new/modified jobs"""
        self.rebuild_indexes()
