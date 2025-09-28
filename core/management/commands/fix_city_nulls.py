"""
Management command to fix null city_id values in jobs.
This can be run on Render if needed.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Fix null city_id values in job_job table"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check for null values
            cursor.execute("SELECT COUNT(*) FROM job_job WHERE city_id IS NULL")
            null_count = cursor.fetchone()[0]

            if null_count == 0:
                self.stdout.write(self.style.SUCCESS("No null city_id values found"))
                return

            self.stdout.write(f"Found {null_count} jobs with null city_id, fixing...")

            # Create default city using raw SQL
            cursor.execute(
                """
                INSERT INTO address_country (name, code) 
                VALUES ('United States', 'US') 
                ON CONFLICT (code) DO NOTHING
            """
            )

            cursor.execute(
                """
                INSERT INTO address_state (name, country_id) 
                SELECT 'Unknown State', id FROM address_country WHERE code = 'US'
                ON CONFLICT DO NOTHING
            """
            )

            cursor.execute(
                """
                INSERT INTO address_city (name, state_id) 
                SELECT 'Unknown City', id FROM address_state WHERE name = 'Unknown State'
                ON CONFLICT DO NOTHING
            """
            )

            # Make column nullable temporarily
            cursor.execute(
                """
                ALTER TABLE job_job 
                ALTER COLUMN city_id DROP NOT NULL
            """
            )

            # Update null values
            cursor.execute(
                """
                UPDATE job_job 
                SET city_id = (
                    SELECT id FROM address_city 
                    WHERE name = 'Unknown City' 
                    LIMIT 1
                )
                WHERE city_id IS NULL
            """
            )

            # Make column NOT NULL again
            cursor.execute(
                """
                ALTER TABLE job_job 
                ALTER COLUMN city_id SET NOT NULL
            """
            )

            # Verify fix
            cursor.execute("SELECT COUNT(*) FROM job_job WHERE city_id IS NULL")
            remaining_nulls = cursor.fetchone()[0]

            if remaining_nulls == 0:
                self.stdout.write(self.style.SUCCESS(f"Successfully fixed {null_count} null city_id values"))
            else:
                self.stdout.write(self.style.ERROR(f"Warning: {remaining_nulls} null values still exist"))
